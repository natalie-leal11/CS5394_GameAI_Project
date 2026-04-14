## Prompt Title: Ranged enemy & Projectile

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §1 Ranged, Projectile

---

### OBJECTIVE ###
Tests for `entities/ranged.py` and `entities/projectile.py`: firing, travel, despawn, hit registration, projectile after shooter death per audit.

---

### FILES TO CREATE ###
- `tests/unit/test_ranged_projectile.py`

---

### TEST CASES (MANDATORY) ###
- `test_ranged_spawn_projectile_smoke`
- `test_projectile_despawn_on_lifetime`
- `test_edge_projectile_after_shooter_death_no_ghost_owner`
- `test_multiple_hits_same_frame_documented`

---

### CONCURRENCY / TIMING TESTS (IF APPLICABLE) ###
- Projectile update order vs collision in one frame.

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
