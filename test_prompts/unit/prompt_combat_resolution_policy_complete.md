## Prompt Title: Combat resolution — policy & enemy-list harness (replaces 2 skipped tests)

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
Replace `Combat policy test — needs harness` and `Requires scene enemy list` with real tests using a minimal combat harness and a plain enemy list.

---

### CONTEXT — EXISTING GAPS ###
Lines 18 and 21 in `tests/unit/test_combat_resolution.py`.

---

### FILES TO CREATE OR EXTEND ###
- `tests/unit/test_combat_resolution.py`

If the file already exists, **append** new test functions; **do not** remove
or rewrite existing passing tests. When replacing a skipped stub, keep the
function name and only swap the body.

---

### TEST CASES ###
- `test_combat_policy_same_frame_single_hit`
- `test_combat_policy_ordering_player_first`
- `test_combat_resolves_multiple_enemies_in_list`
- `test_combat_skips_dead_enemies`

---

### IMPLEMENTATION NOTES ###
- Build a small `list[enemy_stub]` fixture; do not use GameScene.
- Assert HP deltas and kill count.

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
