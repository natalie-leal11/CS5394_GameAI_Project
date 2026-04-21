## Prompt Title: RL — Env reset determinism (`rl/env.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, extend it; otherwise create it.
- Use fixed seeds for anything RNG-sensitive (`random.seed(0)`, `numpy.random.seed(0)`).
- Mock heavy systems (pyglet window, RL training, full GameScene) where applicable.
- Keep every test fast (< 2 s). No long training loops, no real rendering.

---

### OBJECTIVE ###
`reset(seed=s)` yields identical initial observation across calls.

---

### FILES TO CREATE OR EXTEND ###
- `tests/rl/test_rl_env_reset.py`

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones. If the folder does not exist, create it along with an
empty `__init__.py` only if the rest of `tests/` uses one.

---

### TEST CASES ###
- `test_reset_same_seed_same_obs`
- `test_reset_different_seed_different_obs`
- `test_reset_info_schema_stable`

---

### IMPLEMENTATION NOTES ###
- Use headless env.
- Do NOT run real training loops.

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
- No flaky behavior across 3 consecutive runs.
- No edits under `src/`.

---

### CRITICAL END ###
ONLY create or extend the test file listed above.
DO NOT modify production code.
DO NOT overwrite existing tests.
