# rl_prompt_06 — PPO evaluation, demo, `TimeLimit`, and wrapper stack

**Sequence:** 6 of 18 — *Measure and visualize the trained policy.*

**Implementation (repo):** `src/rl/eval_ppo.py`, `src/rl/demo_ppo.py`, `EvalConfig` / `DemoConfig`, `TimeLimit` + `TimeoutPenaltyWrapper` wiring in scripts (not inside base `DungeonEnv`); `src/rl/README_step4.md`.

---

## Objective

**Evaluate** policies headlessly (`eval_ppo`) and run **human demos** (`demo_ppo`), with multi-seed aggregates, deterministic/stochastic policy options, and documented metrics (`mean_final_room_index`, rooms cleared, timeouts, etc.). Document why **`TimeLimit`** wraps the env for finite episodes and how it interacts with training.

## Scope

- **Included:** Eval CLI (`--seeds`, `--episodes`, `--deterministic`), demo `--max-episode-steps` for longer viewing; default `max_episode_steps` alignment across train/eval/demo.
- **Not included:** Changing base env truncation without wrappers.

## Changes required

- Wrap stack: `TimeLimit` then `TimeoutPenaltyWrapper` (Step 6/7 reward) when enabled—see README for ordering rationale.

## Constraints

- Use `--no-time-limit` only when matching a training configuration that disabled `TimeLimit`.

## Implementation steps

1. Run `eval_ppo` with multi-seed settings for stable metrics.
2. Run `demo_ppo` to qualitatively inspect behavior.
3. Record summary metrics for reports and milestone comparison.

## Deliverables

- Reproducible eval summaries and optional demo notes (`demo_run.md` when using experiment layout).

## Sources

- `src/rl/README_step4.md` (evaluate, demo, TimeLimit, config)
