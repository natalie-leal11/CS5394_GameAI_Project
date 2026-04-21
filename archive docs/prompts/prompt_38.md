## Prompt Title: DungeonEnv (`rl/env.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §6 DungeonEnv

---

### OBJECTIVE ###
Integration tests for Gymnasium API: reset, step, obs shape, terminal flags per audit §6.

---

### FILES TO CREATE ###
- `tests/integration/test_rl_dungeon_env.py`

---

### TEST CASES (MANDATORY) ###
- `test_reset_returns_valid_obs`
- `test_step_after_terminal_requires_reset`
- `test_headless_no_display_smoke`

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
