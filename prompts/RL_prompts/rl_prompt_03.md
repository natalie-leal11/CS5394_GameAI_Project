# rl_prompt_03 — Real observation vector (`build_observation`)

**Sequence:** 3 of 18 — *Policy inputs for PPO (fixed-size vector).*

**Implementation (repo):** `src/rl/obs.py` (`build_observation`), `src/rl/env.py` observation space, `src/rl/test_env.py` assertions; contract in `src/rl/README_step2.md`. Spec: `ai_prompts/rl_integration_prompts/RL Agent Prompts/RL-Agent Step2.md`.

---

## Objective

Replace the placeholder observation with a **stable, fixed-size float32** vector: player state, room/progression, nearest enemy, light hazard/risk—normalized and clamped—so PPO receives meaningful state each step.

## Scope

- **Included:** `obs.py`, `env.py` and test updates; feature mappings (room type, enemy type); `OBS_DIM` contract.
- **Not included:** Full tile grid / layout tensors; reward; PPO/training code.

## Changes required

- Implement `build_observation(game_scene) -> np.ndarray` with helpers for normalization.
- Update `observation_space` to final dimension; same shape on `reset` and `step`.
- Tests: `float32`, fixed shape, no NaN/inf.

## Constraints

- No raw `tile_grid`; no PPO/model in this step; prefer public player APIs; document private field use.

## Implementation steps

1. Add mappings and `build_observation` in `obs.py`.
2. Wire `DungeonEnv` to use real observations.
3. Extend smoke tests with stricter assertions.

## Deliverables

- Documented observation dimension and ordered feature list (see README + agent prompt report section).

## Sources

- `ai_prompts/rl_integration_prompts/RL Agent Prompts/RL-Agent Step2.md`
- `src/rl/README_step2.md`
