## Prompt Title: Combat system (`systems/combat.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §2 Combat system

---

### OBJECTIVE ###
Unit/integration tests for hit detection, damage amounts, kill registration; double-hit and list-mutation edge cases per audit §2.

---

### FILES TO CREATE ###
- `tests/unit/test_combat_resolution.py`

---

### TEST CASES (MANDATORY) ###
- `test_hitbox_overlap_applies_damage`
- `test_kill_increments_once`
- `test_edge_double_hit_one_swing_if_forbidden`
- `test_edge_hit_after_removal_from_list`

---

### CONCURRENCY / TIMING TESTS (IF APPLICABLE) ###
- Combat pass order vs removal list.

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
