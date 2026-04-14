## Prompt Title: Door system (`dungeon/door_system.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §5 Door system, §8 Door unlock

---

### OBJECTIVE ###
Integration/regression tests: locked during combat, unlock after clear + delay per audit §5 + §8 door unlock.

---

### FILES TO CREATE ###
- `tests/integration/test_door_system.py`

---

### TEST CASES (MANDATORY) ###
- `test_doors_locked_while_enemies_alive`
- `test_unlock_after_clear_with_delay`
- `test_edge_last_enemy_and_player_death_same_frame`

---

### CONCURRENCY / TIMING TESTS (IF APPLICABLE) ###
- Unlock timer vs frame order.

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
