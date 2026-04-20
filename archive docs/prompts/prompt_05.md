## Prompt Title: Brute & Heavy enemies

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §1 Brute, Heavy

---

### OBJECTIVE ###
Tests for `entities/brute.py` and `entities/heavy.py`: windups, HP pools, elite stacking edge cases per audit.

---

### FILES TO CREATE ###
- `tests/unit/test_brute_heavy.py`

---

### TEST CASES (MANDATORY) ###
- `test_brute_attack_timing_smoke`
- `test_heavy_damage_mitigation_or_hp_pool`
- `test_edge_overlapping_hitboxes_no_double_count_same_frame`

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
