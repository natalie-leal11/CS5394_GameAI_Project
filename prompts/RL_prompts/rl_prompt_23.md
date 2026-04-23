# rl_prompt_23 — Compare PPO checkpoints (`compare_ppo_models`) for regression triage

**Sequence:** 23 — *Side-by-side or sequential evaluation of multiple saved policies.*

**Implementation (repo):** `src/rl/compare_ppo_models.py`, `src/rl/eval_ppo.py` patterns, model paths under `models/ppo/` or experiment folders.

---

## Objective

Give implementers a **small tool** to load two or more **Stable-Baselines3** `.zip` checkpoints against the same env configuration and print or save **comparable metrics** (mean return, episode length, success rate) so training regressions are easy to spot after hyperparameter or reward tweaks.

## Scope

- **Included:** Argument parsing for multiple model paths; shared env seed; optional scenario id; tabular stdout or single JSON summary.
- **Not included:** Retraining, hyperparameter search, or plotting beyond optional simple text tables.

## Changes required

- Reuse the same `DungeonEnv` + wrapper construction as `eval_ppo` to avoid **train/eval skew**.
- Normalize output column names (model path basename vs full path) for logs.

## Constraints

- Read-only with respect to game logic; no changes to `src/game/` behavior except existing RL hooks.
- Runs must complete in reasonable time on CPU for default episode caps.

## Implementation steps

1. Mirror `eval_ppo` env creation inside `compare_ppo_models` or import a shared factory.
2. Run N episodes per model; aggregate statistics.
3. Document example: comparing `dungeon_ppo_final.zip` vs an older checkpoint.

## Deliverables

- One command that compares at least two models on the same env+seed and prints a summary line per model.

## Sources

- `src/rl/compare_ppo_models.py`, `src/rl/eval_ppo.py`, `src/rl/config.py`
