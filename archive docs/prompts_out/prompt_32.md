## Prompt Title: Spawn system & spawn_helper — timing and reinforcements

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §5 Spawn system, §7 Spawn delay

---

### OBJECTIVE ###
Integration + concurrency-oriented tests for spawn lists, reinforcements, cap per audit §5 Spawn system + §7 spawn delay.

---

### FILES TO CREATE ###
- `tests/integration/test_spawn_system.py`

---

### TEST CASES (MANDATORY) ###
- `test_spawn_matches_directive`
- `test_reinforcement_only_when_flag_set`
- `test_no_spawn_after_room_clear`
- `test_edge_max_enemy_cap`

---

### CONCURRENCY / TIMING TESTS (IF APPLICABLE) ###
- Spawn mid-frame vs update order; reinforcement timing.

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
