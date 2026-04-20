## Prompt Title: Offline RL tools — dataset_export & reward_eval (replaces 3 skipped tests)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, extend it; otherwise create it.
- **REPLACE SKIPPED TESTS** listed below with real implementations (remove the `pytest.skip(...)` line and add a working body).
- Use fixed seeds for anything RNG-sensitive (`random.seed(0)`, `numpy.random.seed(0)`).
- Mock heavy systems (pyglet/pygame window, RL training, full `GameScene`) where applicable.
- Keep every test fast (< 2 s). No long training loops, no real rendering.

---

### OBJECTIVE ###
Replace all three skipped tests (`dataset_export integration`, `reward_eval` x2) with real unit tests using small in-memory fake episodes.

---

### CONTEXT — EXISTING GAPS ###
Lines 5, 8, 11 in `tests/unit/test_offline_rl_tools.py`.

---

### FILES TO CREATE OR EXTEND ###
- `tests/unit/test_offline_rl_tools.py`

If the file already exists, **append** new test functions; **do not** remove
or rewrite existing passing tests. When replacing a skipped stub, keep the
function name and only swap the body.

---

### TEST CASES ###
- `test_dataset_export_writes_expected_columns`
- `test_dataset_export_empty_input_produces_empty_output`
- `test_reward_eval_recomputes_step_reward`
- `test_reward_eval_matches_env_reward_on_fixed_trajectory`

---

### IMPLEMENTATION NOTES ###
- Use `tmp_path` for any file output.
- Construct fake trajectories as plain lists of dicts.

---

### CONCURRENCY (IF APPLICABLE) ###
- N/A

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- N/A

---

### ACCEPTANCE ###
- All listed tests pass locally via `pytest tests/unit`.
- The full suite (`pytest tests`) still passes — no regressions.
- Zero skipped tests among the ones listed above (unless genuinely unsupported on CI, in which case skip only with a clear reason string).
- No flaky behavior across 3 consecutive runs.
- No edits under `src/`.

---

### CRITICAL END ###
ONLY create or extend the test file listed above.
DO NOT modify production code.
DO NOT overwrite existing tests.
