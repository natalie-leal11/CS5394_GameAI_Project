## Prompt Title: Gameplay metrics hooks — kills, room clear, victory/defeat

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §2 Gameplay reward / metrics hooks

---

### OBJECTIVE ###
Integration tests tying combat outcomes to metrics / scene flags per audit §2 Gameplay reward/metrics hooks.

---

### FILES TO CREATE ###
- `tests/integration/test_gameplay_metrics_hooks.py`

---

### TEST CASES (MANDATORY) ###
- `test_kill_increments_metric_once`
- `test_room_clear_event_fires_once`
- `test_victory_and_defeat_mutually_exclusive`

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
