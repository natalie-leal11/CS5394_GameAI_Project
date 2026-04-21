## Prompt Title: Biome3MiniBoss & FinalBoss

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §1 Biome3MiniBoss, FinalBoss

---

### OBJECTIVE ###
Integration tests for `entities/biome3_miniboss.py` and `entities/final_boss.py`: campaign end linkage and phase hooks per audit.

---

### FILES TO CREATE ###
- `tests/integration/test_bosses_biome3_final.py`

---

### TEST CASES (MANDATORY) ###
- `test_biome3_miniboss_defeat_smoke`
- `test_final_boss_defeat_triggers_victory_path_smoke`
- `test_edge_timeout_vs_boss_death_ordering_mocked`

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
