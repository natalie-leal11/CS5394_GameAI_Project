# rl_prompt_02 — Run smoke test and module path (`README` Step 1)

**Sequence:** 2 of 18 — *Operational verification after `DungeonEnv` exists.*

**Implementation (repo):** Runbook in `src/rl/README_step1.md`; smoke via `python -m rl.test_env` with `PYTHONPATH=src`.

---

## Objective

Document how to execute the Step 1 smoke test from the repo root (bash/PowerShell), including `PYTHONPATH` so `rl` imports resolve.

## Scope

- **Included:** Commands, dependency notes, project-root convention (directory containing `assets/`).
- **Not included:** New gameplay or env semantics beyond Step 1.

## Changes required

- From project root: set `PYTHONPATH=src` (or equivalent), then `python -m rl.test_env`.

## Constraints

- Follow current `README_step1.md` if flags or layout change.

## Implementation steps

1. Set `PYTHONPATH` per shell.
2. Run `python -m rl.test_env`.
3. Fix import/path issues until the smoke test passes.

## Deliverables

- Successful smoke test run documented in README.

## Sources

- `src/rl/README_step1.md`
