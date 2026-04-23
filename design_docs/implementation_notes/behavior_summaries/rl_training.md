---
# RL Training — Behavior Implementation Summary

## Overview

The RL system wraps the dungeon game as a standard Gymnasium environment and
trains a PPO (Proximal Policy Optimization) agent using Stable-Baselines3. The
agent receives 36 normalized observation features per frame, selects one of 17
discrete actions, and receives a scalar reward. It begins with a random policy
and learns through repeated play, with no human demonstrations or hardcoded
rules.

---

## Why PPO

PPO constrains how much the policy is allowed to change in a single update by
clipping the ratio of new-to-old action probabilities to within ±20%
(`clip_range = 0.2`). This prevents any single batch of bad experience from
catastrophically overwriting learned behavior — the primary failure mode of
simpler RL algorithms on long-episode environments like the dungeon. PPO is also
on-policy, which suits the sequential room-clearing structure of the game better
than replay-buffer methods like DQN.

---

## Environment — DungeonEnv

`DungeonEnv` runs the real `GameScene` in headless mode by setting two flags:

- `gs._rl_controlled = True` — routes all player input through `gs._rl_action`
  (an integer 0–16) instead of the keyboard.
- `gs._rl_skip_draw = True` — suppresses rendering for training speed.

Every `step(action)` call advances the game by exactly one tick at `dt = 1/60`
seconds, takes before/after state snapshots, and returns the standard Gymnasium
5-tuple: `(obs, reward, terminated, truncated, info)`.

---

## Observation Space — 36 Features

`Box(shape=(36,), dtype=float32)`, all values normalized to approximately
`[-1, 1]` or `[0, 1]`:

| Group | Indices | Features |
|---|---|---|
| Player self-state | 0–15 | HP ratio, max HP, lives, life index, position x/y, velocity x/y, facing x/y, dash active, dash cooldown, long attack cooldown, is blocking, is parrying, invuln timer |
| Room and campaign | 16–24 | Room index progress, biome index, room type, enemies alive, room cleared, boss room flag, campaign progress fraction, victory flag, defeat flag |
| Nearest enemy | 25–31 | Enemy present, distance, relative x/y, enemy HP ratio, enemy type, near-threat flag (within 400px) |
| Hazards and heal | 32–34 | Adjacent hazard tile, current tile hazard, reserve heal cooldown |
| Swarm density | 35 | Combat enemies within 280px ÷ 12, clamped to `[0, 1]` |

---

## Action Space — 17 Discrete Actions

`Discrete(17)` — one action per frame, no combinations:

| Index | Action | Index | Action |
|---|---|---|---|
| 0 | no-op | 9 | parry (K) |
| 1 | move up | 10 | interact (E) |
| 2 | move down | 11 | safe room heal (F) |
| 3 | move left | 12 | reserve heal (H) |
| 4 | move right | 13 | upgrade choice 1 |
| 5 | short attack | 14 | upgrade choice 2 |
| 6 | long attack | 15 | upgrade choice 3 |
| 7 | dash | 16 | upgrade choice 4 |
| 8 | block | | |

---

## Reward Function — Priority Hierarchy

Rewards are computed by diffing a `RewardSnapshot` taken before and after each
tick. The step reward is clipped to ±3.0 to prevent gradient explosions.

**Terminal (once per episode):**
- Victory: +1.5 · Defeat: −1.5 · Life lost: −0.5

**Macro progression:**
- Room clear: +0.58 · Forward room entry: +0.24

**Interaction mechanics:**
- E interact success: +0.20 · F safe room heal: +0.16 · Upgrade selected: +0.20

**Combat:**
- Normal kill: +0.12 · Boss kill: +0.55
- HP damage taken: −0.006 × (damage / max HP)
- HP healed: +0.04 × (heal / max HP), capped at +0.02/step

**Navigation shaping (per step, capped to prevent farming):**
- Approaching nearest combat enemy: +0.00034/px closed, max 55px/step
- Approaching nearest open forward door: +0.00048/px closed, max 55px/step

**Anti-stagnation:**
- Per-step cost: −0.002
- Stall penalty: −0.045 after 30 seconds of no macro progress, repeating every 10s
- Micro-idle penalty: −0.0012 every 60 steps of near-zero movement with no progress
- Timeout penalty: −0.65 on episode truncation (applied by `TimeoutPenaltyWrapper`)

---

## Wrapper Stack

```
TimeoutPenaltyWrapper(        ← adds −0.65 when TimeLimit fires truncated=True
  TimeLimit(                  ← sets truncated=True at max_episode_steps=5000
    DungeonEnv(render_mode=None)
  )
)
```

`DungeonEnv` itself never sets `truncated=True`. `TimeoutPenaltyWrapper` is
necessary because `DungeonEnv.step()` cannot see the truncation flag set by the
outer `TimeLimit` wrapper — the penalty must be injected at the outermost layer.

---

## Curriculum Pre-Training

Before full-game training the agent is pre-trained on two isolated micro-scenarios:

- **E-interact (altar in Room 0)** — agent must press interact at the correct
  position to proceed. Without curriculum, this is rarely discovered by random
  play in a 17-action space.
- **F safe room heal** — agent must press heal in a safe room context.

`CurriculumScenarioSamplerWrapper` alternates between the two scenarios each
episode (50/50). `CurriculumSuccessWrapper` gives a +3.0 bonus on success and
immediately terminates the episode. The +3.0 signal is larger than any other
reward in the system, ensuring the agent learns these mechanics before full-game
training begins.

---

## Staged Training

Training runs in 300k-step stages, each resuming from the previous stage's best
checkpoint. `BestProgressionEvalCallback` evaluates every `eval_freq` steps on
a separate environment and saves `dungeon_ppo_best.zip` when
`mean_final_room_index` strictly improves — not reward, but actual dungeon
progression. This ensures the saved model is the one that went furthest, not the
one that happened to accumulate the most reward.

TensorBoard logs are written per experiment and stage to `logs/ppo/`.

---

## PPO Hyperparameters

| Parameter | Value | Purpose |
|---|---|---|
| `learning_rate` | 3e-4 | Adam optimizer step size |
| `n_steps` | 2048 | Steps collected per rollout before any update |
| `batch_size` | 64 | Mini-batch size for gradient updates |
| `n_epochs` | 10 | Times each rollout batch is reused per update |
| `gamma` | 0.99 | Discount factor — very long-sighted for long episodes |
| `gae_lambda` | 0.95 | GAE smoothing between bias and variance |
| `clip_range` | 0.2 | Maximum per-update policy change (±20%) |
| `ent_coef` | 0.0 | No explicit entropy bonus |
| `max_grad_norm` | 0.5 | Gradient clipping cap |
| `max_episode_steps` | 5000 | Episode length cap before truncation |

---

## Primary File Locations

| File | Contents |
|---|---|
| `src/rl/env.py` | `DungeonEnv`, `reset()`, `step()`, RL game hook flags |
| `src/rl/obs.py` | `build_observation()`, all 36 feature definitions |
| `src/rl/reward.py` | `compute_step_reward()`, `RewardSnapshot`, full reward hierarchy |
| `src/rl/action_map.py` | 17-action space, integer → game input translation |
| `src/rl/wrappers.py` | `TimeoutPenaltyWrapper`, `TimeLimit` wrapper stack |
| `src/rl/config.py` | `PPOConfig` dataclass, all hyperparameter defaults |
| `src/rl/best_progress_callback.py` | `BestProgressionEvalCallback`, saves by room index |
| `src/rl/curriculum_wrappers.py` | `CurriculumSuccessWrapper`, `CurriculumScenarioSamplerWrapper` |
| `src/rl/train_ppo.py` | Training orchestrator, staged resume, checkpoint management |
| `src/rl/train_curriculum_ppo.py` | Curriculum pre-training script |
| `src/rl/eval_ppo.py` | Headless multi-seed evaluation, writes `eval_summary.md` |
| `src/rl/demo_ppo.py` | Visible window playback of trained model |
| `src/rl/test_env.py` | Environment smoke test (obs/action/reward shape check) |
