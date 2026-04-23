## Prompt Title: RL — Observation bounds and documented invariants (`rl/obs.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, **append**; otherwise create it.
- Keep every test fast (< 2 s).

---

### OBJECTIVE ###
Beyond shape/dtype (existing schema prompt), add assertions that key observation components lie in **documented** ranges: e.g. [0,1] normalized, [-1,1] vectors, or binary flags in {0,1} **as specified in `rl/obs.py` or `gym.spaces` definitions** (read from source in tests, assert match).

---

### FILES TO CREATE OR EXTEND ###
- `tests/rl/test_rl_observation_schema.py`

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones.

---

### TEST CASES ###
- `test_observation_components_respect_box_low_high_or_docs`
- `test_observed_slice_matches_builder_contract_minimal` *(e.g. first k dims for a fixture obs)*

---

### IMPLEMENTATION NOTES ###
- Prefer building one observation from any **public** factory in `rl/obs` if one exists; else document skip with “requires full scene” and use **mocked** `GameScene` **without** `src/` edits.
- `numpy` assertions for bounds.

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
