## Prompt Title: GameScene — full harness coverage (unblock skipped tests)

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
Create a minimal `GameScene` harness (headless, no display) and use it to implement the broad set of tests currently skipped in `tests/_generate_remaining_prompt_tests.py` as real integration tests.

---

### CONTEXT — EXISTING GAPS ###
Dozens of skips (lines 79, 96, 128, 131, 159, 191, 194, 288, 291, 294, 330, 333, 336, 343, 346, 349, 458, 461, 464, 489, 492, 495, 539, 542, 591, 597, ...) all cite 'Requires GameScene' / 'Scene'.

---

### FILES TO CREATE OR EXTEND ###
- `tests/integration/test_game_scene_full_harness.py`

If the file already exists, **append** new test functions; **do not** remove
or rewrite existing passing tests. When replacing a skipped stub, keep the
function name and only swap the body.

---

### TEST CASES ###
- `test_scene_update_loop_runs_fixed_frames`
- `test_scene_player_enemy_interaction_end_to_end`
- `test_scene_room_transition_cleans_entities`
- `test_scene_terminal_state_fires_once`
- `test_scene_teardown_releases_references`

---

### IMPLEMENTATION NOTES ###
- Use `os.environ['SDL_VIDEODRIVER']='dummy'` in a fixture.
- Do not import from `_generate_remaining_prompt_tests.py`; build a new file.

---

### CONCURRENCY (IF APPLICABLE) ###
- N/A

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- N/A

---

### ACCEPTANCE ###
- All listed tests pass locally via `pytest tests/integration`.
- The full suite (`pytest tests`) still passes — no regressions.
- Zero skipped tests among the ones listed above (unless genuinely unsupported on CI, in which case skip only with a clear reason string).
- No flaky behavior across 3 consecutive runs.
- No edits under `src/`.

---

### CRITICAL END ###
ONLY create or extend the test file listed above.
DO NOT modify production code.
DO NOT overwrite existing tests.
