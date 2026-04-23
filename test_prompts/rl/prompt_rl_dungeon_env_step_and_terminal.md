## Prompt Title: RL — `DungeonEnv` step tuple, terminal, and `step` after `done` (`rl/env.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, **append**; otherwise create it.
- Use fixed seeds for anything RNG-sensitive (`random.seed(0)`, `numpy.random.seed(0)`).
- Mock heavy systems (pyglet window, RL training) where applicable; **headless** `render_mode=None`.
- Keep every test fast (< 2 s). No long training loops, no real rendering.

---

### OBJECTIVE ###
Verify Gymnasium contract for `DungeonEnv`: `reset`/`step` return shapes, `terminated`/`truncated` are mutually well-behaved, and after a terminal or truncated end state, further `step` calls behave consistently until `reset` (as implemented — document expected behavior in assertions).

---

### FILES TO CREATE OR EXTEND ###
- `tests/rl/test_rl_dungeon_env_step_contract.py` **(new file; do not conflate with integration-only modules unless you also keep tests in `tests/rl/`)**

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones.

---

### TEST CASES ###
- `test_step_returns_five_tuple_obs_scalar_bool_bool_dict`
- `test_terminal_or_truncated_ends_episode_with_consistent_info_keys_minimal`
- `test_steps_after_terminal_stay_done_until_reset`

---

### IMPLEMENTATION NOTES ###
- Use `DungeonEnv(render_mode=None)`.
- Cap inner loop steps at a small N (e.g. 32–64) per test.
- Assert observation shape `(OBS_DIM,)` from `rl.obs` where applicable.
- If full env stepping is too heavy, document skip reason; prefer thin harness over `src/` edits.

---

### CONCURRENCY (IF APPLICABLE) ###
- N/A

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- N/A

---

### ACCEPTANCE ###
- All listed tests pass locally via `pytest tests/rl/test_rl_dungeon_env_step_contract.py` (or `pytest tests/rl`).
- The full suite (`pytest tests`) still passes — no regressions.
- No flaky behavior across 3 consecutive runs.
- No edits under `src/`.

---

### CRITICAL END ###
ONLY create or extend the test file listed above.
DO NOT modify production code.
DO NOT overwrite existing tests.
