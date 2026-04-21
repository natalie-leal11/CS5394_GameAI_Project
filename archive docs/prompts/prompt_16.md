## Prompt Title: PlayerModel — DOMINATING / STABLE / STRUGGLING

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §3 Player state model

---

### OBJECTIVE ###
Unit tests for `game/ai/player_model.py`: threshold boundaries, deterministic classification per audit §3.

---

### FILES TO CREATE ###
- `tests/unit/test_player_model_classification.py`

---

### TEST CASES (MANDATORY) ###
- `test_same_inputs_same_state_deterministic`
- `test_boundary_equality_struggling_vs_stable`
- `test_spike_damage_single_frame`

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
