## Prompt Title: MiniBoss & MiniBoss2

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §1 MiniBoss, MiniBoss2

---

### OBJECTIVE ###
Integration-style tests for `entities/mini_boss.py` and `entities/mini_boss_2.py`: defeat conditions and room pairing per audit.

---

### FILES TO CREATE ###
- `tests/integration/test_miniboss_variants.py`

---

### TEST CASES (MANDATORY) ###
- `test_miniboss_defeat_sets_expected_flags`
- `test_miniboss2_distinct_from_miniboss_smoke`
- `test_edge_defeat_during_transition_no_double_reward`

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
