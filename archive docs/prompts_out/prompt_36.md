## Prompt Title: GameScene — update order & enemy list safety

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §5 GameScene, §7 Shared collections, §7 Main loop

---

### OBJECTIVE ###
Integration + concurrency tests for `game/scenes/game_scene.py`: player→enemies→combat order; list mutation safety per audit §5 + §7.

---

### FILES TO CREATE ###
- `tests/integration/test_game_scene_update_order.py`

---

### TEST CASES (MANDATORY) ###
- `test_update_order_documented`
- `test_enemy_list_no_modify_during_iteration_violation`
- `test_rl_rl_step_path_smoke_headless`

---

### CONCURRENCY / TIMING TESTS (IF APPLICABLE) ###
- Deferred removal; copy-while-iterate patterns.

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
