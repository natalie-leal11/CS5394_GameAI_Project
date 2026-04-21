## Prompt Title: Player model — threshold tuning & room history (replaces skipped tests)

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
Replace `Tune thresholds with real summary` and `Needs room history` skips with deterministic tests using canned summary dicts and a fake room-history list.

---

### CONTEXT — EXISTING GAPS ###
Lines 20 and 23 of `tests/unit/test_player_model_classification.py`.

---

### FILES TO CREATE OR EXTEND ###
- `tests/unit/test_player_model_classification.py`

If the file already exists, **append** new test functions; **do not** remove
or rewrite existing passing tests. When replacing a skipped stub, keep the
function name and only swap the body.

---

### TEST CASES ###
- `test_classifier_boundary_just_below_aggressive_threshold`
- `test_classifier_boundary_just_above_cautious_threshold`
- `test_history_smoothing_reduces_flip_flop`
- `test_history_window_size_respected`

---

### IMPLEMENTATION NOTES ###
- Feed the classifier canned `summary` dicts — do not spin up a real scene.
- Assert classification is stable under small noise within threshold band.

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
