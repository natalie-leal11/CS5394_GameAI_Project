## Prompt Title: RL — Stall schedule, micro-idle & idle timers (`rl/reward.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, **append**; otherwise create it.
- Keep every test fast (< 2 s). Synthetic `RewardState` + snapshots only.

---

### OBJECTIVE ###
- **Stall:** advance or simulate the internal `RewardState` fields so that the **stall penalty** path fires at and after `R_STALL_THRESHOLD_STEPS` and repeat cadence (e.g. +600) **as implemented**; assert a **negative** contribution in breakdown or total on those transitions.
- **Micro-idle / stationary combat / short-attack spam:** construct snapshots + state deltas that trigger **each** penalty branch at least once (or document a skip if a branch requires `GameScene` data not exposed — **no** `src/` edits).

---

### FILES TO CREATE OR EXTEND ###
- `tests/rl/test_rl_reward_breakdown.py`

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones.

---

### TEST CASES ###
- `test_stall_penalty_applied_after_threshold_and_schedule`
- `test_micro_idle_or_stationary_combat_penalty_contribution_exists_when_triggered`
- `test_short_attack_spam_branch_when_triggered`

---

### IMPLEMENTATION NOTES ###
- Read `RewardState` in `rl/reward.py` to see which fields to bump between steps.
- If full triggers need scene metrics, use **smallest** `RewardSnapshot` fields (`player_x`/`_y` deltas) matching code paths.

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
