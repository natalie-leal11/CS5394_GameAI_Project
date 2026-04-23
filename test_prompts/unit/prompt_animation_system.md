## Prompt Title: Animation system (`systems/animation.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, extend it; otherwise create it.
- Use fixed seeds for anything RNG-sensitive (`random.seed(0)`, `numpy.random.seed(0)`).
- Mock heavy systems (pyglet window, RL training, full GameScene) where applicable.
- Keep every test fast (< 2 s). No long training loops, no real rendering.

---

### OBJECTIVE ###
Frame advance, loop/non-loop modes, and event on end.

---

### FILES TO CREATE OR EXTEND ###
- `tests/unit/test_animation_system.py`

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones. If the folder does not exist, create it along with an
empty `__init__.py` only if the rest of `tests/` uses one.

---

### TEST CASES ###
- `test_frame_advances_with_dt`
- `test_non_loop_stops_on_last_frame`
- `test_loop_wraps_around`
- `test_animation_finished_event_fires_once`

---

### IMPLEMENTATION NOTES ###
- Use minimal fixtures; avoid full `GameScene` construction unless required.
- Mock pyglet/display surfaces and RL dependencies.
- Seed all RNG (`random.seed(0)`, `numpy.random.seed(0)`).

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
- No flaky behavior across 3 consecutive runs.
- No edits under `src/`.

---

### CRITICAL END ###
ONLY create or extend the test file listed above.
DO NOT modify production code.
DO NOT overwrite existing tests.
