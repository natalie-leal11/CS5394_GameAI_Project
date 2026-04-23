## Prompt Title: RL — Hazards, progression, travel, and interact penalties (`rl/reward.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, **append**; otherwise create it.
- Keep every test fast (< 2 s). Synthetic snapshots only.

---

### OBJECTIVE ###
Add **targeted** tests (one behavior group per function or a small set):

1. **Hazard:** `damage_from_hazards` and/or `time_in_hazard_tiles` delta produces **non-positive** terms; combined step reward respects `R_HAZARD_*_CAP` constants.
2. **Room / door / clear:** Deltas in `room_index`, `rooms_cleared`, and/or door distance fields produce **expected sign** in breakdown for progression / `door_goal_dist` *improvement* (per `compute_step_reward` logic).
3. **Failed interact / reserve:** Increment `rl_interact_failed_e_count` / `rl_reserve_heal_failed_count` and assert **non-positive** contributions; when multiple failures occur in a step, **spam cap** (`R_FAILED_SPAM_STEP_CAP` or related) is not exceeded in absolute value.

---

### FILES TO CREATE OR EXTEND ###
- `tests/rl/test_rl_reward_breakdown.py`

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones.

---

### TEST CASES ###
- `test_hazard_damage_and_time_terms_respect_caps`
- `test_room_entry_or_clear_delta_positive_in_breakdown`
- `test_door_approach_improvement_bonuses_when_closer` *(or name matching implementation)*
- `test_failed_interact_and_reserve_spam_capped`

---

### IMPLEMENTATION NOTES ###
- Use **minimal** `RewardSnapshot` diffs; import coef names from `rl.reward` for expected bounds.
- If a path is unreachable with synthetic data alone, **one** `pytest.skip` with reason referring to which metric is missing (still no `src/` change).

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
