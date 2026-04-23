## Prompt Title: RL — `game.rl.reward_eval` + `game.rl.dataset_export` (columns, errors, known totals) — `tests/rl` target

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **MANDATORY:** Tests must live under `tests/rl/` (single file or split by topic under `tests/rl/`), **per project convention for this workstream**.
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if `tests/rl/test_rl_dataset_export_and_reward_eval.py` exists, **append**; otherwise create it.
- Keep every test fast (< 2 s). Use **tmp_path** for CSV/JSONL.

---

### OBJECTIVE ###
Complement (not replace) `prompt_rl_dataset_export_and_reward_eval.md`:

1. **Columns:** A minimal **valid** export row set includes all columns required by `reward_eval` (or assert **clear** error for missing column).
2. **Malformed file:** non-numeric / wrong delimiter → assert **documented** exception or error path (read from module behavior).
3. **Known trajectory:** 2–3 **hand-built** rows where **offline** evaluation reproduces a **precomputed** total / component sum (if `reward_eval` API exposes row-wise scoring — match **public** API only).
4. If modules live under `src/game/rl/`, use imports like `from game.rl.reward_eval import ...` with `conftest` / `src` on `sys.path` as other tests do.

---

### FILES TO CREATE OR EXTEND ###
- `tests/rl/test_rl_dataset_export_and_reward_eval.py`

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing passing tests except **replacing** `pytest.skip` stubs that this prompt lists by name (same function names as in existing stub file).

---

### TEST CASES ###
- `test_reward_eval_valid_columns_minimal_file`
- `test_reward_eval_malformed_value_raises`
- `test_offline_total_matches_baseline_for_tiny_synthetic_file`

---

### IMPLEMENTATION NOTES ###
- Do not duplicate `tests/error/test_reward_eval_errors.md` if those tests are error-folder-specific; this file focuses on **RL tooling** and **regression** of totals under `tests/rl` for discoverability in RL suites.

---

### CONCURRENCY (IF APPLICABLE) ###
- N/A

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- N/A

---

### ACCEPTANCE ###
- `pytest tests/rl` passes; `pytest tests` passes; no `src/` edits.

---

### CRITICAL END ###
ONLY create or extend the test file listed above.
DO NOT modify production code.
DO NOT overwrite existing tests.
