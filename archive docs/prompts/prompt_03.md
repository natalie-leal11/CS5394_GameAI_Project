## Prompt Title: Enemy base — lifecycle, HP, death, elite/normal

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §1 Enemy base

---

### OBJECTIVE ###
Tests for `entities/enemy_base.py` and shared contracts: spawn alive, take damage, die, removal from combat set.

---

### FILES TO CREATE ###
- `tests/unit/test_enemy_base_lifecycle.py`

---

### TEST CASES (MANDATORY) ###
- `test_enemy_starts_alive_with_positive_hp`
- `test_damage_reduces_hp`
- `test_at_zero_hp_marks_dead_or_triggers_removal_hook`
- `test_no_damage_after_death`

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
