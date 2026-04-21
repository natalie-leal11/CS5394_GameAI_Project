## Prompt Title: Deferred frame ops — add/remove queue draining

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
Add tests for deferred-operation queues used to mutate entity lists safely. Queue drained at end of frame; no op lost; order preserved.

---

### CONTEXT — EXISTING GAPS ###
No existing prompt targets deferred queue semantics.

---

### FILES TO CREATE OR EXTEND ###
- `tests/concurrency/test_deferred_frame_ops_queue.py`

If the file already exists, **append** new test functions; **do not** remove
or rewrite existing passing tests. When replacing a skipped stub, keep the
function name and only swap the body.

---

### TEST CASES ###
- `test_deferred_adds_applied_end_of_frame`
- `test_deferred_removes_applied_end_of_frame`
- `test_deferred_queue_preserves_enqueue_order`
- `test_deferred_queue_empty_after_drain`

---

### IMPLEMENTATION NOTES ###
- Use minimal fixtures; avoid full `GameScene` construction unless required.
- Mock pyglet/pygame surfaces and RL dependencies.
- Seed all RNG (`random.seed(0)`, `numpy.random.seed(0)`).

---

### CONCURRENCY (IF APPLICABLE) ###
- Enqueue-during-drain goes to next frame, not current.

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- Drain terminates deterministically.

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
