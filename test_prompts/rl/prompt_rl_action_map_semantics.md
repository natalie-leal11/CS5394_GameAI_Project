## Prompt Title: RL — Action index to game / control semantics (`rl/action_map.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, **append**; otherwise create it.
- Keep every test fast (< 2 s).

---

### OBJECTIVE ###
For **each** discrete action id in the supported range, assert a **documented mapping** (constants, dict, or function) to a **named** effect: e.g. move direction, attack, interact, menu — **as defined in `action_map.py`** (no gameplay `src/` changes; tests may read **public** symbols only).

---

### FILES TO CREATE OR EXTEND ###
- `tests/rl/test_rl_action_map.py`

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones.

---

### TEST CASES ###
- `test_each_action_id_has_documented_semantic_label`
- `test_action_id_count_matches_discrete_space_documentation`

---

### IMPLEMENTATION NOTES ###
- Complement (not replace) existing coverage in the same file (`test_action_total_coverage`, etc.).
- If the module exports a list of action names, iterate it; else build from `Action` enum / dict keys if present.

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
