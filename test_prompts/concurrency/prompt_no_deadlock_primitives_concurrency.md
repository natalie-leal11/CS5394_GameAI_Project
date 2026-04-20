## Prompt Title: No deadlock primitives — runtime check

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
Existing unit-level audit is static. Add a RUNTIME test that wraps sync primitives and asserts they are never invoked during a fake frame update.

---

### CONTEXT — EXISTING GAPS ###
Unit-level `test_no_deadlock_primitives_in_gameloop.py` is static-only.

---

### FILES TO CREATE OR EXTEND ###
- `tests/concurrency/test_no_deadlock_primitives_runtime.py`

If the file already exists, **append** new test functions; **do not** remove
or rewrite existing passing tests. When replacing a skipped stub, keep the
function name and only swap the body.

---

### TEST CASES ###
- `test_no_lock_acquired_during_update`
- `test_no_blocking_get_during_update`
- `test_no_sleep_during_update`

---

### IMPLEMENTATION NOTES ###
- Monkeypatch `threading.Lock.__enter__`, `queue.Queue.get`, `time.sleep`.
- Run 60 fake frames.

---

### CONCURRENCY (IF APPLICABLE) ###
- Frame update path must be lock-free and non-blocking.

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- Any lock acquisition during update is a test failure.

---

### ACCEPTANCE ###
- All listed tests pass locally via `pytest tests/concurrency`.
- The full suite (`pytest tests`) still passes — no regressions.
- Zero skipped tests among the ones listed above (unless genuinely unsupported on CI, in which case skip only with a clear reason string).
- No flaky behavior across 3 consecutive runs.
- No edits under `src/`.

---

### CRITICAL END ###
ONLY create or extend the test file listed above.
DO NOT modify production code.
DO NOT overwrite existing tests.
