## Prompt Title: RL — `CurriculumSuccessWrapper` reset options & scenario switch (`rl/curriculum_wrappers.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, **append**; otherwise create it.
- Keep every test fast (< 2 s). Prefer **mocked** base env; only use real `DungeonEnv` if a thin wrapper test needs it.

---

### OBJECTIVE ###
- `reset` **requires** a curriculum scenario: passing `options={"curriculum_scenario": "interact"}` (or `safe_heal`) vs. missing scenario raises (per implementation).
- After `reset` with a scenario, `info` contains `"curriculum_scenario"` and matches the requested value.
- Switching scenario on a **new** `reset` updates `wrapper.scenario` and prev counters sync behavior does not crash (smoke).
- (Optional) When success bonus fires, `terminated` becomes `True` and `info["curriculum_success"]` is `True` — if achievable with a **mock** metrics object attached to a fake `unwrapped` env **without** editing `src/`.

---

### FILES TO CREATE OR EXTEND ###
- `tests/rl/test_rl_curriculum.py`

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones (the existing `prompt_rl_curriculum.md` file covers **layout**; this prompt adds **wrapper lifecycle**).

---

### TEST CASES ###
- `test_reset_without_scenario_raises_or_uses_default_per_implementation`
- `test_reset_with_curriculum_scenario_sets_info_key`
- `test_second_reset_switches_scenario_string`

---

### IMPLEMENTATION NOTES ###
- Construct `CurriculumSuccessWrapper(Env, default_scenario=...)` per constructor signature in source.
- Use `pytest.raises` if `ValueError` is documented for missing scenario.

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
