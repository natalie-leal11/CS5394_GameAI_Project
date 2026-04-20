# CRITICAL: Dungeon Game — Test Prompts Hierarchy Generator (testing/prompts)

**MANDATORY:** Generate a complete hierarchy of structured prompts that will create a full testing suite (unit, integration, concurrency, regression, performance, error, RL) for the dungeon game. These prompts must be additive and executable sequentially.

---

## 1. Scope and Folder Structure

**CRITICAL:** Create a root folder:


test_prompts/


Inside it, create subfolders:
- `unit/`
- `integration/`
- `concurrency/`
- `regression/`
- `performance/`
- `error/`
- `rl/`

Each subfolder must contain **multiple prompt files** (collectively 50–100+ prompts).

---

## 2. Prompt Purpose

Each prompt will:
- Create or extend test files inside:


tests/<same_category>/


- Add missing test cases  
- Never overwrite existing test code  

---

## 3. Core Rules (MANDATORY)

| Rule | Description |
|------|------------|
| **ONLY tests** | Prompts must generate test code only |
| **NO src changes** | Never modify production code |
| **ADDITIVE ONLY** | Do not overwrite existing test files |
| **CREATE IF MISSING** | Create folders/files if they don’t exist |
| **EXTEND IF EXISTS** | Add tests to existing files |
| **DETERMINISTIC** | Use seeds where needed |
| **FAST EXECUTION** | No heavy loops or long RL training |

---

## 4. Prompt Content Structure

Each prompt file MUST follow this format:

### Prompt Title: `<Component/System Name>`

---

### CRITICAL REQUIREMENTS ###
- ONLY write test code (pytest)
- DO NOT modify `src/`
- DO NOT overwrite existing tests
- ADD missing tests only
- Ensure deterministic behavior

---

### OBJECTIVE ###
Define what component/system is being tested.

---

### FILES TO CREATE OR EXTEND ###
Example:


tests/unit/test_player.py


---

### TEST CASES ###
List clearly:
- `test_<normal_case>`
- `test_<edge_case>`
- `test_<failure_case>`

---

### IMPLEMENTATION NOTES ###
- Use fixtures if needed  
- Use mocks/stubs for complex systems (GameScene, RL)  
- Avoid heavy computation  
- Simulate behavior minimally  

---

### CONCURRENCY (IF APPLICABLE) ###
- Test update loops  
- Test shared list mutation safety  
- Test timing/cooldowns  

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
- Ensure no infinite loops  
- Ensure no blocking conditions  

---

### ACCEPTANCE ###
- Tests pass  
- No flaky behavior  
- Existing tests remain intact  

---

### CRITICAL END ###
ONLY create or extend test files  
DO NOT modify production code  
DO NOT overwrite existing tests  

---

## 5. Prompt Distribution

**CRITICAL:** Cover all categories:

### UNIT (largest)
- Player, enemies, combat, movement, AI, metrics  

### INTEGRATION
- GameScene, rooms, spawn, doors, safe rooms  

### CONCURRENCY
- Game loop, timing, shared state  

### REGRESSION
- Known bugs (enemy disappearance, door issues)  

### PERFORMANCE
- Game loop timing, high load scenarios  

### ERROR
- Invalid inputs, missing configs  

### RL
- Environment, observation, reward logic  

---

## 6. Execution Behavior

When these prompts are executed:
- If `tests/<category>/` exists → extend it  
- If not → create it  

Ensure all tests are runnable via:


pytest tests


---

## 7. Verification

- Prompts generate a **complete test hierarchy**  
- No existing files are overwritten  
- Tests are grouped correctly by category  
- Full suite runs from root folder  

---

# CRITICAL (REPEAT): Dungeon Game Testing Prompts

**MANDATORY:** Generate only prompts (not test code) that will create a full, structured, additive test suite. Prompts must enforce no changes to production code and must support incremental test generation across all categories.