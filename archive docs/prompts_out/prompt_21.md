## Prompt Title: Victory / defeat / death — GameScene integration

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §3 Victory/defeat

---

### OBJECTIVE ###
Integration tests for terminal outcomes from `game/scenes/game_scene.py` per audit §3.

---

### FILES TO CREATE ###
- `tests/integration/test_game_scene_terminal_states.py`

---

### TEST CASES (MANDATORY) ###
- `test_player_death_ends_run_smoke`
- `test_final_victory_single_terminal`
- `test_edge_death_and_victory_same_frame_rejected_or_ordered`

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
