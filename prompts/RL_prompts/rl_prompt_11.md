# rl_prompt_11 — Iteration 2: per-milestone eval, human demo, optional `compare_ppo_models`

**Sequence:** 11 of 18 — *Validate and compare milestone policies.*

**Implementation (repo):** `eval_ppo`, `demo_ppo`, `compare_ppo_models` CLI; default `eval_summary.md` / `demo_run.md` paths via experiment layout; `src/rl/README_step11_iteration2.md`.

---

## Objective

After each iter2 milestone, run **headless eval** with `--experiment` + `--stage`, record **human demos** (`demo_ppo` + `--notes`), and optionally **compare** multiple checkpoints in one eval pass.

## Scope

- **Included:** Eval with multi-seed settings; demo into `demo_{stage}/demo_run.md`; optional `compare_ppo_models` with three model paths; CLI reference table for experiment/stage defaults.
- **Not included:** Automatic video recording (manual link in Notes).

## Changes required

- Swap `--stage` and model paths for 300k, 600k, 900k; do not overwrite prior stage folders.

## Constraints

- Preserve checklist: `milestone_train.md`, `eval_summary.md`, `demo_run.md` per stage.

## Implementation steps

1. Eval each trained checkpoint with the same protocol for fair comparison.
2. Demo for qualitative behavior notes.
3. Optionally run multi-checkpoint comparison script.

## Deliverables

- Per-stage `eval_summary.md`, `demo_run.md`, optional comparison output.

## Sources

- `src/rl/README_step11_iteration2.md` (eval, demo, compare, CLI reference, checklist)
