## Prompt Title: Offline RL — dataset export & reward eval

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §4 Offline RL dataset / reward eval

---

### OBJECTIVE ###
Unit tests for `game/rl/dataset_export.py`, `reward_eval.py`, `offline_tuning_spec.py` with temp files per audit §4.

---

### FILES TO CREATE ###
- `tests/unit/test_offline_rl_tools.py`

---

### TEST CASES (MANDATORY) ###
- `test_export_produces_parseable_rows`
- `test_evaluate_deterministic_on_fixed_csv`
- `test_empty_input_handled_gracefully`

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
