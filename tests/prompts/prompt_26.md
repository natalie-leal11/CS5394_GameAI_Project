## Prompt Title: Biome spawn helpers (biome1–biome4)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §4 Biome spawn helpers

---

### OBJECTIVE ###
Integration tests for spawn composition bounds and seed determinism per audit §4 Biome spawn helpers.

---

### FILES TO CREATE ###
- `tests/integration/test_biome_director_spawns.py`

---

### TEST CASES (MANDATORY) ###
- `test_spawn_count_non_negative`
- `test_same_seed_same_composition_smoke`
- `test_zero_enemy_edge_if_allowed`

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
