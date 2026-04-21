## Prompt Title: Player — Movement, dash cooldown, dash i-frames

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
Unit tests for movement velocity, dash trigger, dash cooldown timer, and dash-granted invulnerability window.

---

### FILES TO CREATE OR EXTEND ###
- `tests/unit/test_player_movement_dash.py`

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones. If the folder does not exist, create it along with an
empty `__init__.py` only if the rest of `tests/` uses one.

---

### TEST CASES ###
- `test_movement_velocity_applied_per_frame`
- `test_dash_triggers_on_input`
- `test_dash_cooldown_blocks_re_trigger`
- `test_dash_cooldown_expires`
- `test_dash_grants_iframes`

---

### IMPLEMENTATION NOTES ###
- Use a fake dt of 1/60.
- Avoid pyglet window; manipulate state via method calls.

---

### CONCURRENCY (IF APPLICABLE) ###
- Timer decrement monotonic per tick; never goes negative.

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
