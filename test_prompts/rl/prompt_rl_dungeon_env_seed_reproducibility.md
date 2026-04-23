## Prompt Title: RL — `DungeonEnv` reproducibility with same seed and action list (`rl/env.py`)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, **append**; otherwise create it.
- Keep every test fast (< 2 s). No training.

---

### OBJECTIVE ###
With **fixed** `reset(seed=…)` and the **same** list of integer actions, two fresh `DungeonEnv` instances (or the same instance reset twice) produce **identical** observation sequences and terminal flags for the bounded sequence **where the environment’s RNG and physics are expected to be deterministic** (if any nondeterminism is inherent, assert equality of the first k steps with `pytest` or document skip with code reference — **no** `src/` changes).

---

### FILES TO CREATE OR EXTEND ###
- `tests/rl/test_rl_dungeon_env_reproducibility.py` **(new file)**

If the file already exists, **append** new test functions; **do not** remove or
rewrite existing ones.

---

### TEST CASES ###
- `test_same_seed_same_action_sequence_replays_obs_path`
- `test_different_seeds_may_diverge_or_document_identical` *(pick one: either assert non-equal after first step or only document — match actual env behavior.)*

---

### IMPLEMENTATION NOTES ###
- Use a **short** scripted list of `action` ints (e.g. length 8–32).
- `render_mode=None`.

---

### CONCURRENCY (IF APPLICABLE) ###
- N/A

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- N/A

---

### ACCEPTANCE ###
- `pytest tests/rl` passes; full `pytest tests` passes; no `src/` edits.

---

### CRITICAL END ###
ONLY create or extend the test file listed above.
DO NOT modify production code.
DO NOT overwrite existing tests.
