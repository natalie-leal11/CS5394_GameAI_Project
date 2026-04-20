## Prompt Title: Game loop — update order under entity churn

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
Entities added and removed during iteration must not corrupt update order.

---

### FILES TO CREATE OR EXTEND ###
- `tests/concurrency/test_update_loop_order_stable.py`

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones. If the folder does not exist, create it along with an
empty `__init__.py` only if the rest of `tests/` uses one.

---

### TEST CASES ###
- `test_add_during_iteration`
- `test_remove_during_iteration`
- `test_simultaneous_add_remove`

---

### IMPLEMENTATION NOTES ###
- Use a fake scene with a list of stub entities.
- Do NOT use real threads — pygame/pyglet loop is single-threaded.

---

### CONCURRENCY (IF APPLICABLE) ###
- Mutation-during-iteration safe via snapshot or deferred ops.

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- No while-True loops in tests; cap frames to 120.

---

### ACCEPTANCE ###
- All listed tests pass locally via `pytest tests/concurrency`.
- The full suite (`pytest tests`) still passes — no regressions.
- No flaky behavior across 3 consecutive runs.
- No edits under `src/`.

---

### CRITICAL END ###
ONLY create or extend the test file listed above.
DO NOT modify production code.
DO NOT overwrite existing tests.
