## Prompt Title: RL — `TimeLimit` + `truncated` on headless `DungeonEnv` (integration-style, `tests/rl` only)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, **append**; otherwise create it.
- Keep every test fast (< 2 s; allow slightly higher for single env if still < 5 s wall clock).
- Use **very small** `max_episode_steps` on `gymnasium.wrappers.TimeLimit`.

---

### OBJECTIVE ###
Wrap `DungeonEnv(render_mode=None)` in `TimeLimit(max_episode_steps=K)` with small **K** (e.g. 2–8). After **K** steps without natural termination, assert `truncated is True` (and `terminated` is False if no death/victory). Optionally compose **outer** `TimeoutPenaltyWrapper` and assert `truncated` still triggers the timeout penalty from the dedicated wrapper prompt (may **share** one test file with `test_rl_timeout_penalty_wrapper.py` **or** a combined `test_rl_timelimit_stack.py` — **one** new file only to avoid sprawl).

---

### FILES TO CREATE OR EXTEND ###
- `tests/rl/test_rl_timelimit_truncation.py` **(new file)**

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones.

---

### TEST CASES ###
- `test_timelimit_truncates_at_max_episode_steps`
- `test_optional_timeout_wrapper_composes_on_truncation` *(if combined in same file, import wrapper stack)*

---

### IMPLEMENTATION NOTES ###
- Reuse a **noop** or small random `action` sequence of length K.
- If `DungeonEnv` always terminates before K steps, reduce K or `pytest.skip` with reason (environment-dependent; **no** `src/` change).

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
