## Prompt Title: Swarm & Flanker enemies

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §1 Swarm, Flanker

---

### OBJECTIVE ###
Tests for `entities/swarm.py` and `entities/flanker.py`: movement/attack patterns and damage to player (mocked) per audit.

---

### FILES TO CREATE ###
- `tests/unit/test_swarm_flanker.py`

---

### TEST CASES (MANDATORY) ###
- `test_swarm_instantiation_and_update_smoke`
- `test_flanker_approach_smoke`
- `test_edge_many_swarm_instances_no_overflow_invariants`

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
