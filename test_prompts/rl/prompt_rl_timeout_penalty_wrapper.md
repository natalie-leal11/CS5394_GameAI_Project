## Prompt Title: RL — `TimeoutPenaltyWrapper` on `truncated` (`rl/wrappers.py`, `rl/reward.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, **append**; otherwise create it.
- Keep every test fast (< 2 s). Use a **trivial** `gym.Env` stub with **forced** `truncated=True` for one `step` (or wrap `TimeLimit` with 1 step on a dummy env) — **no** need for full `DungeonEnv` if the wrapper is pure.

---

### OBJECTIVE ###
When the inner environment returns `truncated=True` from `step`, the wrapper:
- adds `R_TIMEOUT_PENALTY` to the **scalar** reward; and
- updates `info["reward_breakdown"]` via `merge_timeout_penalty_into_breakdown` (or equivalent keys present).

---

### FILES TO CREATE OR EXTEND ###
- `tests/rl/test_rl_timeout_penalty_wrapper.py` **(new file)**

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones.

---

### TEST CASES ###
- `test_truncated_adds_r_timeout_penalty_to_reward`
- `test_truncated_merges_timeout_into_reward_breakdown_dict`
- `test_non_truncated_passes_through_unchanged`

---

### IMPLEMENTATION NOTES ###
- Define a minimal `gymnasium.Env` subclass with fixed `observation_space` / `action_space` that returns `truncated=True` on the first `step` after `reset` (or always after step 1), `terminated=False`, base reward 0, empty info `{}` or with existing breakdown dict.
- Import `TimeoutPenaltyWrapper`, `R_TIMEOUT_PENALTY` from `rl.wrappers` / `rl.reward`.

---

### CONCURRENCY (IF APPLICABLE) ###
- N/A

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- N/A

---

### ACCEPTANCE ###
- `pytest tests/rl` passes; no `src/` edits.

---

### CRITICAL END ###
ONLY create or extend the test file listed above.
DO NOT modify production code.
DO NOT overwrite existing tests.
