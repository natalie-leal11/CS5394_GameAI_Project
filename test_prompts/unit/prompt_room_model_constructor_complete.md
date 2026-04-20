## Prompt Title: Room model — dataclass constructor & invariants (replaces skipped tests)

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
Replace the two skipped tests in `tests/unit/test_room_model_unit_audit.py` with real constructor/invariant tests for `dungeon/room.py`.

---

### CONTEXT — EXISTING GAPS ###
File has `pytest.skip("Room dataclass constructor")` and `pytest.skip("Requires Room instance")`. Room class is stable.

---

### FILES TO CREATE OR EXTEND ###
- `tests/unit/test_room_model_unit_audit.py`

If the file already exists, **append** new test functions; **do not** remove
or rewrite existing passing tests. When replacing a skipped stub, keep the
function name and only swap the body.

---

### TEST CASES ###
- `test_room_constructs_with_minimum_fields`
- `test_room_constructs_with_doors_and_spawns`
- `test_room_id_is_stable_across_copies`
- `test_room_cleared_defaults_false`
- `test_room_bounds_are_positive_dimensions`

---

### IMPLEMENTATION NOTES ###
- Read only the public dataclass fields; do not touch internals.
- If geometry is optional, cover both the minimal and full ctor forms.

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
