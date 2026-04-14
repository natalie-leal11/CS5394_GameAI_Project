### CRITICAL REQUIREMENTS ###
You are an expert Python testing architect and automation engineer.

CRITICAL: Generate 30–40 structured prompts for Cursor IDE Agent to implement COMPLETE TESTING COVERAGE for the dungeon game.
CRITICAL: Testing includes UNIT, INTEGRATION, CONCURRENCY, DEADLOCK, and REGRESSION testing.
CRITICAL: Use the provided HIGH-LEVEL AUDIT document as the ONLY source of truth.
CRITICAL: DO NOT modify or refactor any production code.
CRITICAL: ALL prompts must create TEST CODE ONLY.

---

### OBJECTIVE ###
Create a sequence of 30–40 prompts that Cursor can execute one-by-one to build a full testing suite.

Each prompt should target:
- One component OR
- A small logically grouped set of components

The prompts must be ORDERED logically:
1. Core unit tests
2. Integration tests
3. Concurrency/timing tests
4. Deadlock safety tests
5. Regression tests

---

### INPUT ###
You are given:
- `docs/game_testing_high_level_audit.md`

CRITICAL: Extract components ONLY from this audit.
DO NOT invent new components.

---

### OUTPUT STRUCTURE (MANDATORY) ###

Create a folder:

tests/prompts/


Inside it, generate files:

prompt_01.md
prompt_02.md
...
prompt_40.md


Each prompt MUST follow this EXACT format:

---

## Prompt Title: <Component / System Name>

### CRITICAL REQUIREMENTS ###
- ONLY write test code
- DO NOT modify production code
- DO NOT change game logic
- Tests must be additive and isolated
- Use pytest (Python) or JUnit-style structure conceptually
- Ensure deterministic behavior using seeds where required

---

### OBJECTIVE ###
Describe what this prompt must implement (tests for which component)

---

### FILES TO CREATE ###
Example:
- tests/test_player.py
- tests/test_combat.py

---

### TEST CASES (MANDATORY) ###
List clearly:
- test_<behavior_1>
- test_<behavior_2>
- test_<edge_case>

Include:
- Normal cases
- Edge cases
- Failure scenarios

---

### CONCURRENCY / TIMING TESTS (IF APPLICABLE) ###
- Frame update order
- Spawn/despawn timing
- Shared list mutation safety

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- No blocking loops
- No infinite waits
- No state freeze across updates

---

### ACCEPTANCE CRITERIA ###
- Tests pass without modifying game logic
- No flaky tests
- Deterministic outputs for same seed/input

---

### CRITICAL REMINDER ###
ONLY create test files.
NO production code edits.
NO refactoring.
NO design changes.

---

### PROMPT DESIGN RULES (MANDATORY) ###

Each prompt MUST follow:

1. Sandwich Method  
   → Critical rules at top and bottom

2. Attention Anchoring  
   → Use **MANDATORY**, **CRITICAL** keywords

3. Clear Sections  
   → Use ### headers

4. Focus Scope  
   → One component per prompt (or tightly grouped)

5. Coverage Mapping  
   → Ensure ALL audit components are covered across prompts

---

### PROMPT DISTRIBUTION STRATEGY ###

Ensure coverage:

- Player (multiple prompts: HP, lives, actions)
- Enemies (group by type)
- Bosses (mini + final)
- Combat system
- Movement & collisions
- AI Director & PlayerModel
- Metrics & rewards
- Room & seed generation
- Door & hazard system
- GameScene & SceneManager
- RL environment (env, obs, actions, wrappers)
- Concurrency systems (update loop, lists, timers)
- Deadlock safety checks
- Regression tests (bugs: despawn, door unlock, overlaps)

---

### FINAL OUTPUT ###
Return ONLY the prompts (30–40).
NO explanation.
NO summary.
NO extra text.

---

### CRITICAL END ###
These prompts will be executed sequentially.
They must be COMPLETE, NON-OVERLAPPING, and SAFE.
NO GAME LOGIC CHANGES ALLOWED.
ONLY TEST IMPLEMENTATION.