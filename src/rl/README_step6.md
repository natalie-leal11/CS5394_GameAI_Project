# Step 6: Progress-oriented reward shaping

Additive changes on top of Step 3 (`src/rl/reward.py`). Manual gameplay is unchanged.

## Goals

- Discourage **timeout-only** policies (survive until `TimeLimit` with no progress).
- Give **early guidance** toward **combat** (nearest enemy) or **exit** (forward door) using **delta** distance only (potential-style, capped per step).
- Reward **damage dealt** to combat enemies (aggregate HP reduction).
- Add a light **anti-idle** signal when the player barely moves and there is no macro progress or enemy damage.

## Constants (see `reward.py`)

| Symbol | Value | Role |
|--------|-------|------|
| `R_TIMEOUT_PENALTY` | −0.5 | Applied when outer `TimeLimit` truncates (`TimeoutPenaltyWrapper`) |
| `R_ALIVE_BONUS` | **0** | Removed (was +0.0005) to reduce passive survival incentive |
| `R_APPROACH_ENEMY_COEF` | 0.00022 | × min(Δpx toward nearest enemy, cap) when combat remains |
| `R_APPROACH_DOOR_COEF` | 0.00028 | × min(Δpx toward nearest open forward door, cap) when no combat enemies |
| `R_ENEMY_DAMAGE_COEF` | 0.00012 | × aggregate enemy HP lost (same room), capped per step |
| `R_ANTI_IDLE_EXTRA` | −0.0012 | Every 60 steps after ~180 steps of micro-idle |
| `R_STEP_CLIP` | ±3.0 | Non-terminal per-step clamp (raised from 2.5) |

Per-step caps (`R_APPROACH_*_MAX_DELTA_PX`, `R_ENEMY_DAMAGE_MAX_PER_STEP`) limit farming via oscillation.

## `RewardSnapshot` additions

- `player_x`, `player_y` — world position.
- `nearest_enemy_dist` — distance to nearest **combat** enemy (`inf` if none).
- `enemy_hp_sum` — sum of HP over combat enemies.
- `door_goal_dist` — distance to nearest **open** forward door (`inf` if none).

Door centers use `GameScene._iter_doorways` (same geometry as gameplay).

## `info["reward_breakdown"]` keys

New / relevant: `timeout_penalty` (from wrapper), `enemy_approach`, `door_approach`, `enemy_damage`, `anti_idle`. `alive_bonus` remains **0**.

## Timeout penalty and wrappers

`DungeonEnv.step()` runs **before** an outer `TimeLimit` sets `truncated`, so **truncation penalty** is not known inside `compute_step_reward`.  
`rl/wrappers.TimeoutPenaltyWrapper` sits **outside** `TimeLimit` and adds `R_TIMEOUT_PENALTY` to the returned reward and breakdown when `truncated=True`.

Wired in: `train_ppo.py`, `eval_ppo.py`, `demo_ppo.py` (only when `TimeLimit` is enabled).

## Tests

`rl/test_env.py`: smoke test checks new breakdown keys; `test_timeout_penalty_wrapper` verifies finite reward and timeout component on truncation.

## Step 12: Interact (E) and safe-room heal (F) shaping

Small, **delta/event-only** terms in `reward.py` (no PPO / obs changes). Counters live on `MetricsTracker.run` and are incremented from `GameScene` when RL uses actions **10 = interact (E)** and **11 = safe_room_heal (F)** (`action_map.py`).

| Symbol | Value | Role |
|--------|-------|------|
| `R_BENEFIT_INTERACT` | 0.08 | Per successful interact success this step (capped by `R_BENEFIT_INTERACT_STEP_CAP` = 0.12) |
| `R_BENEFIT_SAFE_ROOM_HEAL_EXTRA` | 0.06 | Extra on top of `benefit_heal` when safe-room F actually heals (cap 0.08/step) |
| `R_FAILED_INTERACT_PER` | −0.002 | Per RL E keydown with no interact success (anti-spam; combined failed terms capped per step) |
| `R_FAILED_SAFE_HEAL_PER` | −0.001 | Per safe-room F with no heal applied |
| `R_FAILED_SPAM_STEP_CAP` | 0.015 | Max combined \|failed_interact\| + \|failed_safe_heal\| per step |

**Successful interact** (increments `rl_interact_success_count`): e.g. closing the Room 0 story with **E**, or opening the altar story panel with **E**. Not counted for blind **E** spam (failed attempts increment `rl_interact_failed_e_count`).

**Successful safe-room heal** (increments `rl_safe_room_heal_success_count`): **F** when heal is applied (`record_healing`); also receives normal `benefit_heal` from `healing_orb_collected_count`. Failed **F** (full HP, etc.) increments `rl_safe_room_heal_failed_count`.

`info["reward_breakdown"]` keys: `benefit_interact`, `benefit_safe_heal`, `failed_interact`, `failed_safe_heal`.

## Revert

Restore prior `reward.py`, remove `rl/wrappers.py`, unwrap `train_ppo` / `eval_ppo` / `demo_ppo`, and revert `test_env.py` assertions.
