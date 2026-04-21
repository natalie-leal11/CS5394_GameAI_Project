## Prompt Title: Player — HP bounds and clamping (`entities/player.py`)

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
Verify HP never exceeds max_hp, never goes below 0, and heal/damage ordering is monotonic and deterministic.

---

### FILES TO CREATE OR EXTEND ###
- `tests/unit/test_player_hp_bounds.py`

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones. If the folder does not exist, create it along with an
empty `__init__.py` only if the rest of `tests/` uses one.

---

### TEST CASES ###
- `test_hp_starts_at_max`
- `test_damage_reduces_hp`
- `test_damage_past_zero_clamps_to_zero`
- `test_heal_clamps_to_max_hp`
- `test_heal_at_full_is_noop`

---

### IMPLEMENTATION NOTES ###
- Instantiate `Player` with defaults from `game/config.py`.
- Do not call `update()` — drive HP via direct public methods only.
- Use `pytest.approx` for float HP comparisons if applicable.

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
