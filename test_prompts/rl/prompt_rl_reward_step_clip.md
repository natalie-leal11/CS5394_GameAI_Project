## Prompt Title: RL — `R_STEP_CLIP` for extreme per-step changes (`rl/reward.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, **append**; otherwise create it.
- Keep every test fast (< 2 s). Synthetic `RewardSnapshot` / `RewardState` only.
- `terminated=False` for clip tests (terminal may bypass clip per module docstring).

---

### OBJECTIVE ###
Construct a **synthetic** `prev` / `curr` pair that would produce a very large *raw* per-step total before clipping; assert `abs(compute_step_reward(...)[0]) <= R_STEP_CLIP + small epsilon` (or exact equality to clip boundary if the implementation always clips non-terminal steps).

---

### FILES TO CREATE OR EXTEND ###
- `tests/rl/test_rl_reward_breakdown.py`

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones.

---

### TEST CASES ###
- `test_nonterminal_step_total_bounded_by_r_step_clip`

---

### IMPLEMENTATION NOTES ###
- Import `R_STEP_CLIP` from `rl.reward`.
- If only breakdown keys clip but total is separate, assert on the **returned** `total` float and optionally `sum(breakdown.values())`.

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
