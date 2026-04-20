# rl_prompt_01 — Gymnasium `DungeonEnv` (headless, placeholder observation)

**Sequence:** 1 of 18 — *Agent integration pipeline (how the playable game became a trainable env).*

**Implementation (repo):** `src/rl/env.py`, `src/rl/test_env.py`, optional `src/rl/action_map.py`, hooks in game code; see `ai_prompts/rl_integration_prompts/RL Agent Prompts/RL-Agent Step1.md`.

---

## Objective

Convert the Pygame dungeon into a **Gymnasium-compatible** environment with **headless** stepping, isolated under `src/rl/`, without reward shaping, PPO, or training yet.

## Scope

- **Included:** `DungeonEnv`, smoke tests, discrete action space, placeholder `Box` observation, RL hooks marked for reversibility.
- **Not included:** Real observations, reward design, PPO, checkpoints, policy code.

## Changes required

- `DungeonEnv` with `gymnasium`: `Discrete(8)` actions (no-op, moves, short/long attack, dash); `Box` shape `(20,)` placeholder `float32`.
- `reset` / `step` / `render` / `close`; `step` advances one fixed tick; `reward = 0.0`; `terminated` on win/loss.
- Headless: no display flip/update; full **game logic** (collision, combat, rooms) still runs.
- RL path uses passed actions; keyboard unused on RL path; manual play unchanged.

## Constraints

- No PPO, Q-learning, policies, replay buffers, training scripts, or real observation engineering beyond placeholder.
- Prefer additive, minimal hooks in existing files (`# RL hook`).

## Implementation steps

1. Implement `src/rl/env.py` and `src/rl/test_env.py`.
2. Add small hooks so core update runs without the normal infinite UI loop.
3. Run smoke test: reset, many random steps, assert obs shape.

## Deliverables

- Runnable `DungeonEnv(render_mode=None)`; 100+ step smoke test; manual gameplay intact.

## Sources

- `ai_prompts/rl_integration_prompts/RL Agent Prompts/RL-Agent Step1.md`
