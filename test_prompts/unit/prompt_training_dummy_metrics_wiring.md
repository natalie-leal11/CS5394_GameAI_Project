## Prompt Title: Training dummy — MetricsTracker wiring (replaces skipped test)

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
Replace the skipped MetricsTracker-wiring test in `tests/unit/test_training_dummy.py` with a real implementation using a lightweight MetricsTracker stub.

---

### CONTEXT — EXISTING GAPS ###
`tests/unit/test_training_dummy.py` currently contains `pytest.skip("Wire MetricsTracker in integration when available")`. MetricsTracker already has passing unit tests elsewhere, so it IS available.

---

### FILES TO CREATE OR EXTEND ###
- `tests/unit/test_training_dummy.py`

If the file already exists, **append** new test functions; **do not** remove
or rewrite existing passing tests. When replacing a skipped stub, keep the
function name and only swap the body.

---

### TEST CASES ###
- `test_dummy_damage_events_are_recorded_in_metrics`
- `test_dummy_multiple_hits_increment_counters`
- `test_dummy_reset_does_not_zero_metrics`
- `test_dummy_zero_damage_not_recorded`

---

### IMPLEMENTATION NOTES ###
- Inject a fake/real `MetricsTracker` into the dummy via its public API.
- Assert monotonic counters and per-frame dedup.
- Do not add integration-level scene objects — unit-level only.

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
