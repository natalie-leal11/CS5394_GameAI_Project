## Prompt Title: RL — `DungeonEnv` observation finiteness on `reset`/`step` (`rl/env.py`, `rl/obs.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, **append**; otherwise create it.
- Use fixed seeds for anything RNG-sensitive (`random.seed(0)`, `numpy.random.seed(0)`).
- Keep every test fast (< 2 s). No long training loops, no real rendering.

---

### OBJECTIVE ###
After `reset` and a bounded number of `step` calls in headless mode, the observation vector contains **no NaN and no Inf** (or, if a known exception is documented in code comments only, `pytest.skip` with a **pointer to the docstring/comment in `src/`** — still **no** `src/` edits).

---

### FILES TO CREATE OR EXTEND ###
- `tests/rl/test_rl_dungeon_env_obs_finiteness.py` **(new file)**

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones.

---

### TEST CASES ###
- `test_reset_obs_is_finite`
- `test_step_observables_finite_for_bounded_rollout`

---

### IMPLEMENTATION NOTES ###
- Use `from rl.obs import OBS_DIM` for shape checks.
- Bound rollout length (e.g. ≤ 32 steps).

---

### CONCURRENCY (IF APPLICABLE) ###
- N/A

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- N/A

---

### ACCEPTANCE ###
- All listed tests pass (or a single well-justified skip) via `pytest tests/rl`.
- Full `pytest tests` still passes; no `src/` changes.

---

### CRITICAL END ###
ONLY create or extend the test file listed above.
DO NOT modify production code.
DO NOT overwrite existing tests.
