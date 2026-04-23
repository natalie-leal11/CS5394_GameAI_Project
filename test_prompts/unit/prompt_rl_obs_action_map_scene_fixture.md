## Prompt Title: RL obs + action map — minimal scene fixture (replaces skipped tests)

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
Replace the two `Needs GameScene instance` skips with tests driven by a minimal headless scene fixture (from `rl/headless.py`) so observations and action-map round-trips can be asserted without rendering.

---

### CONTEXT — EXISTING GAPS ###
Current skips: lines 8 & 14 in `tests/unit/test_rl_obs_action_map.py`.

---

### FILES TO CREATE OR EXTEND ###
- `tests/unit/test_rl_obs_action_map.py`

If the file already exists, **append** new test functions; **do not** remove
or rewrite existing passing tests. When replacing a skipped stub, keep the
function name and only swap the body.

---

### TEST CASES ###
- `test_observation_from_headless_scene_has_expected_shape`
- `test_observation_has_no_nan_or_inf_across_first_k_steps`
- `test_action_round_trip_noop_produces_noop`
- `test_action_map_covers_all_discrete_indices`

---

### IMPLEMENTATION NOTES ###
- Use `rl.headless` or the existing `rl.test_env` DungeonEnv for the fixture.
- Hard-cap K = 8 steps; fixed seed = 0.

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
