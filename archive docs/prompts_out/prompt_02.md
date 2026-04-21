## Prompt Title: Player — Cooldowns, dash, block, parry, attack states

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §1 Player

---

### OBJECTIVE ###
Unit tests for dash/attack cooldown timers and state transitions (movement, attack, block, parry, hurt) per audit §1 Player.

---

### FILES TO CREATE ###
- `tests/unit/test_player_combat_states.py`

---

### TEST CASES (MANDATORY) ###
- `test_dash_cooldown_counts_down`
- `test_attack_cooldown_respects_config`
- `test_block_parry_mutual_exclusion_if_designed`
- `test_invulnerability_window_monotonic`

---

### CONCURRENCY / TIMING TESTS (IF APPLICABLE) ###
- Timer expiry exactly once per tick.

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
