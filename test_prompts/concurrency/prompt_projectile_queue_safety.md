## Prompt Title: Projectile queue safety

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
Projectiles spawning other projectiles does not recurse unboundedly.

---

### FILES TO CREATE OR EXTEND ###
- `tests/concurrency/test_projectile_queue_safety.py`

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones. If the folder does not exist, create it along with an
empty `__init__.py` only if the rest of `tests/` uses one.

---

### TEST CASES ###
- `test_projectile_spawn_capped_per_frame`
- `test_no_infinite_projectile_recursion`

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
- Hard cap on projectiles per frame enforced.

---

### ACCEPTANCE ###
- All listed tests pass locally via `pytest tests/concurrency`.
- The full suite (`pytest tests`) still passes — no regressions.
- No flaky behavior across 3 consecutive runs.
- No edits under `src/`.

---

### CRITICAL END ###
ONLY create or extend the test file listed above.
DO NOT modify production code.
DO NOT overwrite existing tests.
