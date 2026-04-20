## Prompt Title: Game loop — additional deadlock-primitive audits (extends existing)

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
Extend the existing audit to cover threading primitives (`Lock`, `RLock`, `Semaphore`, `Event`, `threading.Thread`, `asyncio.run`, `queue.Queue.get`) across ALL `src/` files, not just the game loop file.

---

### CONTEXT — EXISTING GAPS ###
Existing file is narrow (349 bytes). Expand static-audit scope.

---

### FILES TO CREATE OR EXTEND ###
- `tests/unit/test_no_deadlock_primitives_in_gameloop.py`

If the file already exists, **append** new test functions; **do not** remove
or rewrite existing passing tests. When replacing a skipped stub, keep the
function name and only swap the body.

---

### TEST CASES ###
- `test_no_lock_in_update_path`
- `test_no_blocking_queue_get_in_update_path`
- `test_no_threading_thread_in_src`
- `test_no_asyncio_run_in_src`
- `test_no_time_sleep_in_update_path`

---

### IMPLEMENTATION NOTES ###
- Use AST parsing over `src/**/*.py`.
- Allow an explicit allowlist for e.g. tool scripts under `tools/`.

---

### CONCURRENCY (IF APPLICABLE) ###
- N/A

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- Static audit — guarantees no runtime blocking primitives.

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
