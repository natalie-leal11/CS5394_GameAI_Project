## Prompt Title: RL DungeonEnv — extended integration (extends test_rl_dungeon_env)

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
Existing file is 895 bytes with basic smoke only. Add reset→step→done cycles, multi-episode stats, and truncation semantics.

---

### CONTEXT — EXISTING GAPS ###
`DungeonEnv in rl.test_env` skip in generator; existing test is minimal.

---

### FILES TO CREATE OR EXTEND ###
- `tests/integration/test_rl_dungeon_env_extended.py`

If the file already exists, **append** new test functions; **do not** remove
or rewrite existing passing tests. When replacing a skipped stub, keep the
function name and only swap the body.

---

### TEST CASES ###
- `test_env_reset_step_done_cycle`
- `test_env_done_on_player_death`
- `test_env_truncates_at_max_steps`
- `test_env_multi_episode_seeds_independent`

---

### IMPLEMENTATION NOTES ###
- Hard-cap steps at 64 per episode; 3 episodes.

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
