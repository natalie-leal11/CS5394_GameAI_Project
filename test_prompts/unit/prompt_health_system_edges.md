## Prompt Title: Health system — edge cases (extends existing)

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify any code under `src/`.
- **CRITICAL:** DO NOT overwrite, rename, or delete existing test files.
- Tests must be **additive only** — if the target file exists, extend it; otherwise create it.
- **REPLACE SKIPPED TESTS** listed below with real implementations (remove the `pytest.skip(...)` line and add a working body).
- Use fixed seeds for anything RNG-sensitive (`random.seed(0)`, `numpy.random.seed(0)`).
- Mock heavy systems (pyglet/pygame window, RL training, full `GameScene`) where applicable.
- Keep every test fast (< 2 s). No long training loops, no real rendering.

---

### OBJECTIVE ###
Extend `tests/unit/test_health_system.py` with edge cases not currently covered: negative damage, overheal, death-during-invuln, and heal-after-death.

---

### CONTEXT — EXISTING GAPS ###
File exists (542 bytes) with basic cases only — no prompt currently targets it.

---

### FILES TO CREATE OR EXTEND ###
- `tests/unit/test_health_system.py`

If the file already exists, **append** new test functions; **do not** remove
or rewrite existing passing tests. When replacing a skipped stub, keep the
function name and only swap the body.

---

### TEST CASES ###
- `test_negative_damage_is_rejected_or_treated_as_heal_consistently`
- `test_overheal_clamps_to_max`
- `test_damage_during_invuln_is_noop`
- `test_heal_after_death_does_not_revive_without_respawn`

---

### IMPLEMENTATION NOTES ###
- Use the same fixtures as existing tests to stay consistent.
- Do NOT remove existing asserts.

---

### CONCURRENCY (IF APPLICABLE) ###
- N/A

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- N/A

---

### ACCEPTANCE ###
- All listed tests pass locally via `pytest tests/unit`.
- The full suite (`pytest tests`) still passes — no regressions.
- Zero skipped tests among the ones listed above (unless genuinely unsupported on CI, in which case skip only with a clear reason string).
- No flaky behavior across 3 consecutive runs.
- No edits under `src/`.

---

### CRITICAL END ###
ONLY create or extend the test file listed above.
DO NOT modify production code.
DO NOT overwrite existing tests.
