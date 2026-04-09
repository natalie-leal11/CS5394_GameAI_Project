# Step 3: Reward shaping (`rl/reward.py`)

## Overview

- **Per-step** reward is computed from **two snapshots** of game state: before `SceneManager.update(dt)` and after.
- **No** mutation of gameplay; reads `GameScene`, `_metrics.run`, and enemy list identity.
- **`info["reward_breakdown"]`**: component-wise floats that sum to the returned reward (within float noise).

## Constants (tunable in `reward.py`)

| Symbol | Value | Role |
|--------|-------|------|
| `R_VICTORY` | +1.5 | Terminal (one-shot) |
| `R_DEFEAT` | −1.5 | Terminal (one-shot) |
| `R_LIFE_LOSS_PER` | −0.5 | Per life lost vs previous step |
| `R_KILL_NORMAL` | +0.12 | Per normal enemy removed from combat set |
| `R_KILL_BOSS` | +0.55 | Per miniboss/final boss (class name set) |
| `R_ROOM_CLEAR` | +0.35 | Per `metrics.run.rooms_cleared` increment |
| `R_ROOM_ENTRY_FORWARD` | +0.08 | Per forward room index step (`Δroom_index`) |
| `R_DAMAGE_HP_RATIO_COEF` | −0.006 | × (HP lost / max_hp) when lives unchanged |
| `R_HEAL_HP_RATIO_COEF` | +0.04 | × (HP gained / max_hp), capped by `R_HEAL_PER_STEP_CAP` |
| `R_HEAL_PER_STEP_CAP` | +0.02 | Anti-exploit cap on heal reward |
| `R_ALIVE_BONUS` | **0** (Step 6) | Was +0.0005; removed passive survival bonus |
| `R_STEP_COST` | −0.002 | Per step (skipped when `terminated`) |
| `R_STALL_THRESHOLD_STEPS` | 1800 | ~30 s at 60 FPS without progress |
| `R_STALL_PENALTY` | −0.03 | At threshold and every +600 stagnant steps |
| `R_STEP_CLIP` | ±3.0 | Clamp non-terminal total (Step 6) |

## One-time vs repeating

| Component | Behavior |
|-----------|----------|
| Victory / defeat | **Once** per episode via `RewardState.paid_victory` / `paid_defeat` |
| Room clear | When `rooms_cleared` **increases** (typically once per cleared room) |
| Room entry | When `room_index` **increases** (forward progress only) |
| Kills | When `id(enemy)` leaves the combat set (one reward per kill) |
| Damage / heal | **Every** step with applicable HP delta |
| Alive bonus / step cost | **Every** step while not `terminated` |
| Stall | When stagnation counter hits threshold and every +600 steps without progress |

## Progress reset (stagnation)

Stagnation resets when any of: `kill_total` increases, `room_index` changes, or `rooms_cleared` increases.

## Assumptions

- Boss kill uses **class name** (`MiniBoss`, `MiniBoss2`, `Biome3MiniBoss`, `FinalBoss`).
- Kill detection uses **object identity** in `_enemies`; edge cases with list replacement are rare.
- `reset()` must be called before `step()`; `reset()` re-syncs `RewardState` and the pre-step snapshot.

## Revert

Remove `src/rl/reward.py`, restore `reward = 0.0` and `_build_info()` without breakdown in `env.py`, and drop Step 3 tests.

## Step 6 extensions

Progress shaping, timeout penalty wrapper, and updated constants are documented in **`README_step6.md`**.
