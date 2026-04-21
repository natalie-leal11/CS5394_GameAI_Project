## Prompt Title: TrainingDummy

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §1 TrainingDummy

---

### OBJECTIVE ###
Unit tests for `entities/training_dummy.py`: damage absorption; not counted as kill in metrics if applicable per audit.

---

### FILES TO CREATE ###
- `tests/unit/test_training_dummy.py`

---

### TEST CASES (MANDATORY) ###
- `test_dummy_accepts_damage_without_invalid_state`
- `test_dummy_not_in_kill_count_if_metrics_wired`

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
