## Prompt Title: Biome 4 visuals — without real pygame surface (replaces skipped tests)

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
Replace `Room + pygame surface` and `Optional` skips with tests that drive `biome4_visuals` via a fake surface / recording mock.

---

### CONTEXT — EXISTING GAPS ###
Lines 5 and 8 in `tests/unit/test_biome4_visuals.py`.

---

### FILES TO CREATE OR EXTEND ###
- `tests/unit/test_biome4_visuals.py`

If the file already exists, **append** new test functions; **do not** remove
or rewrite existing passing tests. When replacing a skipped stub, keep the
function name and only swap the body.

---

### TEST CASES ###
- `test_biome4_draw_calls_expected_layers`
- `test_biome4_draw_handles_empty_room`
- `test_biome4_draw_does_not_crash_on_missing_optional_assets`

---

### IMPLEMENTATION NOTES ###
- Use `unittest.mock.MagicMock()` in place of a pygame `Surface`.
- Assert draw-call sequence, not pixel output.

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
