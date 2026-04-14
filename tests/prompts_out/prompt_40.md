## Prompt Title: RL wrappers, curriculum, headless, experiment layout, PPO CLI smoke, deadlock guard

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `docs/game_testing_high_level_audit.md` — components: §6 Wrappers, curriculum, headless, experiment_layout, best_progress, train/eval/demo, §7 Threading/locks

---

### OBJECTIVE ###
Tests for `rl/wrappers.py`, `rl/curriculum_wrappers.py`, `rl/headless.py`, `rl/experiment_layout.py`, `rl/best_progress_callback.py`; argparse smoke for train/eval/demo **without** long training; static check for no threading locks in hot path per audit §6 + §7 threading.

---

### FILES TO CREATE ###
- `tests/unit/test_rl_wrappers_and_layout.py`
- `tests/unit/test_rl_cli_smoke.py`
- `tests/unit/test_no_deadlock_primitives_in_gameloop.py`

---

### TEST CASES (MANDATORY) ###
- `test_timeout_penalty_only_when_truncated`
- `test_curriculum_success_requires_min_steps`
- `test_experiment_paths_no_path_traversal`
- `test_train_ppo_help_exits_zero`
- `test_no_threading_lock_import_in_game_scene_hot_path_static`

---

### CONCURRENCY / TIMING TESTS (IF APPLICABLE) ###
- Wrapper order TimeLimit then TimeoutPenalty.

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- **CRITICAL:** No `acquire()` blocking in game loop; infinite loop guard on eval callback patience smoke with mocks.

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
