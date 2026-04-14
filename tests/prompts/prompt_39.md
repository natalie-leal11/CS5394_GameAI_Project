## Prompt Title: Observation builder & action map (`rl/obs.py`, `rl/action_map.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §6 obs, action_map

---

### OBJECTIVE ###
Unit tests: no NaN/inf, fixed length, action indices in range per audit §6.

---

### FILES TO CREATE ###
- `tests/unit/test_rl_obs_action_map.py`

---

### TEST CASES (MANDATORY) ###
- `test_build_observation_shape_dtype`
- `test_all_action_indices_map_defined`
- `test_no_nan_inf_for_empty_enemy_case`

---

### CONCURRENCY / TIMING TESTS (IF APPLICABLE) ###
- N/A

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- N/A

---

### ACCEPTANCE CRITERIA ###
- **MANDATORY:** Tests pass without editing `src/` except test utilities if already allowed by project.
- **CRITICAL:** No flaky tests; fixed seeds for RNG-dependent assertions.
- **CRITICAL:** Same seed + inputs ⇒ same observable outcomes.

---

### CRITICAL REMINDER ###
ONLY create or extend test files listed above.
NO production code edits.
NO refactoring.
NO design changes.

---

### CRITICAL END ###
Execute this prompt as a single Cursor task; then run `pytest` on new tests.
