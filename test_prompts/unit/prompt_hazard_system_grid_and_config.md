## Prompt Title: Hazard system — grid & config wiring (replaces skipped tests)

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
Replace `Config wiring` and `Grid` skips with real grid-placement and config-driven hazard tests.

---

### CONTEXT — EXISTING GAPS ###
Lines 9 and 12 in `tests/unit/test_hazard_system.py`.

---

### FILES TO CREATE OR EXTEND ###
- `tests/unit/test_hazard_system.py`

If the file already exists, **append** new test functions; **do not** remove
or rewrite existing passing tests. When replacing a skipped stub, keep the
function name and only swap the body.

---

### TEST CASES ###
- `test_hazard_reads_damage_from_config`
- `test_hazard_reads_tick_interval_from_config`
- `test_hazard_grid_placement_inside_room_bounds`
- `test_hazard_grid_no_overlap_with_spawn_slots`

---

### IMPLEMENTATION NOTES ###
- Build a minimal room-like namespace with bounds + spawn slots.
- Config: construct an in-memory dict, not a file.

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
