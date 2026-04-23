## Prompt Title: RL — Short headless rollout + fixed-seed regression hash (`rl/env.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **MANDATORY:** **ONLY** create/extend under `tests/rl/`.
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, **append**; otherwise create it.
- Keep every test fast (< 2 s). Bound steps ≤ 32.

---

### OBJECTIVE ###
1. **Stability:** Run a **short** `DungeonEnv` rollout (random or fixed `action` 0) with `render_mode=None`; assert no exception; each `float(reward)` is **finite**; `obs` shape `(OBS_DIM,)` for every `reset`/`step` until done or cap.
2. **Regression:** For a **fixed** `seed` and a **fixed** list of `action` integers (scripted, length 8–16), compute a stable fingerprint: e.g. `hash(tuple(int(round(x*1e4)) for x in obs) ...)` *across all steps* **or** sum of rewards rounded — store **constants** in the test file. If the **implementation** output changes, the test should fail (update constants only when behavior change is **intended**; document in commit message, still **no** `src/` in test PR).

---

### FILES TO CREATE OR EXTEND ###
- `tests/rl/test_rl_headless_rollout_regression.py` **(new file)** *or* append `tests/rl/test_rl_headless_smoke.py` with **clear** function prefix `regression_` to avoid conflating smoke naming — prefer **dedicated** new file for snapshot constants.

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones.

---

### TEST CASES ###
- `test_short_rollout_finite_reward_and_obs_shape`
- `test_scripted_action_sequence_snapshot_matches` *(name may include `seed42` in docstring)*

---

### IMPLEMENTATION NOTES ###
- If `DungeonEnv` is nondeterministic for the chosen sequence, use `pytest.xfail` with reason **or** skip — **not** for flakiness; prefer deterministic actions + seed.
- This complements `test_rl_headless_smoke.md` (adds **snapshot**).

---

### CONCURRENCY (IF APPLICABLE) ###
- N/A

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- N/A

---

### ACCEPTANCE ###
- `pytest tests/rl` passes; full `pytest tests` passes; no `src/` edits.

---

### CRITICAL END ###
ONLY create or extend the test file listed above.
DO NOT modify production code.
DO NOT overwrite existing tests.
