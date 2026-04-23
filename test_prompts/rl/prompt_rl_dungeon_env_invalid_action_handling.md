## Prompt Title: RL — `DungeonEnv` out-of-range or invalid `action` handling (`rl/env.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, **append**; otherwise create it.
- Keep every test fast (< 2 s). No training.

---

### OBJECTIVE ###
Document and assert **one** consistent policy for disallowed `action` values: e.g. negative index, index at or above `action_space.n`, or wrong dtype — whether the env **raises**, **clips**, or **asserts** (match **actual** `step` implementation; **test behavior, not desired behavior**).

---

### FILES TO CREATE OR EXTEND ###
- `tests/rl/test_rl_dungeon_env_invalid_actions.py` **(new file)**

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones.

---

### TEST CASES ###
- `test_out_of_range_action_is_handled_as_documented` *(use `pytest.raises` or assert stable step return, per implementation)*
- `test_valid_action_index_range_matches_action_space` *(smoke: max legal index)*

---

### IMPLEMENTATION NOTES ###
- Prefer one env instance with `reset(seed=0)` then a **single** invalid `step` if the env aborts; otherwise use separate subprocess patterns only if required (avoid).
- `render_mode=None`.

---

### CONCURRENCY (IF APPLICABLE) ###
- N/A

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- N/A

---

### ACCEPTANCE ###
- `pytest tests/rl` passes; no `src/` edits.

---

### CRITICAL END ###
ONLY create or extend the test file listed above.
DO NOT modify production code.
DO NOT overwrite existing tests.
