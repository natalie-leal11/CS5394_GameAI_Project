## Prompt Title: RL — `compute_step_reward` damage & healing terms + caps (`rl/reward.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, **append**; otherwise create it.
- Keep every test fast (< 2 s). Use **synthetic** `RewardSnapshot` / `RewardState` only.

---

### OBJECTIVE ###
Targeted unit tests: **solely** vary HP / heal events between `prev` and `curr` snapshots and assert the **sign** and **magnitude** (approximate if floating noise) of the corresponding breakdown keys, including **per-step caps** (`R_HEAL_PER_STEP_CAP`, `R_BENEFIT_HEAL_STEP_CAP`, etc. — import constant names from `rl.reward`).

---

### FILES TO CREATE OR EXTEND ###
- `tests/rl/test_rl_reward_breakdown.py`

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones.

---

### TEST CASES ###
- `test_hp_drop_yields_non_positive_damage_contribution`
- `test_single_heal_event_respects_benefit_cap`
- `test_heal_per_step_capped` *(or merge with event cap if one path)*

---

### IMPLEMENTATION NOTES ###
- Use `compute_step_reward(..., terminated=False)` unless testing terminal.
- Tolerance: `1e-4` or `1e-2` for summed breakdown vs `total` (match existing tests).

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
