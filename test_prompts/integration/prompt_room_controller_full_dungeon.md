## Prompt Title: RoomController — full dungeon walk (replaces skipped tests)

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
Walk a full scripted dungeon (4 biomes, safe rooms, mini-boss, boss) via RoomController and assert room transitions, enemy clears, and terminal state.

---

### CONTEXT — EXISTING GAPS ###
`Needs full dungeon` skip in `_generate_remaining_prompt_tests.py`.

---

### FILES TO CREATE OR EXTEND ###
- `tests/integration/test_room_controller_full_dungeon.py`

If the file already exists, **append** new test functions; **do not** remove
or rewrite existing passing tests. When replacing a skipped stub, keep the
function name and only swap the body.

---

### TEST CASES ###
- `test_full_dungeon_walk_completes`
- `test_full_dungeon_walk_hits_every_biome_once`
- `test_full_dungeon_walk_mini_boss_and_boss_fire_once`

---

### IMPLEMENTATION NOTES ###
- Cap total frames at 5000 with a hard assertion.

---

### CONCURRENCY (IF APPLICABLE) ###
- N/A

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- Frame cap prevents infinite loops.

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
