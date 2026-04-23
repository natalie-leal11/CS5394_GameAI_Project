## Prompt Title: Player — HP, lives, and damage intake (`entities/player.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §1 Player

---

### OBJECTIVE ###
Unit and focused integration tests for HP bounds, life loss, respawn transitions, healing at full HP, last life, and frame-boundary damage per audit §1 Player.

---

### FILES TO CREATE ###
- `tests/unit/test_player_hp_lives.py`

---

### TEST CASES (MANDATORY) ###
- `test_hp_never_exceeds_max_when_clamped`
- `test_damage_reduces_hp_monotonically`
- `test_life_decrement_on_run_failure_if_applicable`
- `test_heal_at_full_hp_is_noop_or_clamped`
- `test_edge_last_life_death`

---

### CONCURRENCY / TIMING TESTS (IF APPLICABLE) ###
- N/A unless multi-step update harness used.

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
