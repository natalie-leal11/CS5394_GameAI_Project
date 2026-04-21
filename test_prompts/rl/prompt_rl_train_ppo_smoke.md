## Prompt Title: `rl/train_ppo.py` — smoke (CLI arg parsing + 1-step dry-run)

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
No tests target `train_ppo.py`. Add arg-parsing + dry-run (0 training steps) smoke.

---

### CONTEXT — EXISTING GAPS ###
Uncovered RL script.

---

### FILES TO CREATE OR EXTEND ###
- `tests/rl/test_rl_train_ppo_smoke.py`

If the file already exists, **append** new test functions; **do not** remove
or rewrite existing passing tests. When replacing a skipped stub, keep the
function name and only swap the body.

---

### TEST CASES ###
- `test_train_ppo_argparser_parses_defaults`
- `test_train_ppo_argparser_rejects_unknown_args`
- `test_train_ppo_dry_run_creates_output_dir`

---

### IMPLEMENTATION NOTES ###
- Invoke the module via `runpy.run_module` with `--total-timesteps 0` (or equivalent); redirect output to `tmp_path`.
- No real training.

---

### CONCURRENCY (IF APPLICABLE) ###
- N/A

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- N/A

---

### ACCEPTANCE ###
- All listed tests pass locally via `pytest tests/rl`.
- The full suite (`pytest tests`) still passes — no regressions.
- Zero skipped tests among the ones listed above (unless genuinely unsupported on CI, in which case skip only with a clear reason string).
- No flaky behavior across 3 consecutive runs.
- No edits under `src/`.

---

### CRITICAL END ###
ONLY create or extend the test file listed above.
DO NOT modify production code.
DO NOT overwrite existing tests.
