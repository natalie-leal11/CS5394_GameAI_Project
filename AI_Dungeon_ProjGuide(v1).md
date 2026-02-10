# CRITICAL REQUIREMENTS — Adaptive Dungeon (Python / Pygame) Complete Implementation Guide

### MANDATORY DIRECTIVE ###
You are an expert Python programmer.

**CRITICAL**: Follow this complete implementation guide to create the Adaptive Dungeon game using the provided prompts in the exact order specified.



## **CRITICAL**
Access the prompts referenced below in files with corresponding filenames in directory `prompts` located in the root project directory.



## IMPLEMENTATION EXECUTION ORDER

### **CRITICAL**: Execute prompts in this exact sequence:

1. **01-project-setup.md** — Create project structure and minimal runnable window
2. **02-window-loop-and-scenes.md** — Implement scene system (Menu → Run → End)
3. **03-player-controller.md** — Implement player movement + dash + HP
4. **04-combat-attacks-and-projectiles.md** — Implement short/long attacks + projectiles
5. **05-block-parry-and-damage-mitigation.md** — Implement block/parry timing-based reduction
6. **06-dungeon-plan-30-rooms-and-milestones.md** — Implement deterministic 30-room plan generation
7. **07-room-controller-and-progression.md** — Implement room progression and clearing rules
8. **08-enemy-framework-and-ai.md** — Implement simple aggressive enemies (room-confined)
9. **09-encounter-spawner-and-room-battles.md** — Implement encounter spawning + lock-until-clear
10. **10-ai-director-metrics-and-difficulty-decisions.md** — Implement deterministic AI Director + metrics
11. **11-rest-rooms-healing-and-pacing.md** — Implement rest rooms + healing + pacing knobs
12. **12-final-boss-win-loss-and-determinism-tests.md** — Implement final boss + win/loss + determinism checks



## **MANDATORY**: VERIFICATION BETWEEN STEPS

### **CRITICAL**: After completing each prompt:

1. Run the application:
   - `python -m src.game.main`
2. Fix any runtime errors before continuing
3. Verify:
   - Correct files were created in correct paths
   - No missing imports or module errors
   - No scope-breaking features were introduced

**MANDATORY**: Do not proceed to the next prompt until the game runs successfully.



## **MANDATORY**: FINAL APPLICATION TESTING

### **CRITICAL**: After completing all steps, verify the full game loop:

1. Run:
   - `python -m src.game.main`
2. Verify the loop:
   - Menu → Run → Final Boss → Win/Loss → Restart



## **MANDATORY**: EXPECTED APPLICATION BEHAVIOR

### **CRITICAL**: The completed game must satisfy all of the following:

#### Dungeon Structure
- Exactly **30 rooms per run**
- Room 0 is **START**
- Room 29 is **FINAL BOSS**
- At least one **REST/CHECKPOINT** room exists
- Same seed produces the same dungeon plan

#### AI Director Rules
- AI Director is **deterministic** at runtime
- AI Director **does not directly control enemy AI**
- AI Director tracks:
  - Player health
  - Death count
  - Speed of progression
  - Recent combat outcomes
- AI Director outputs decisions about:
  - Spawn timing
  - Enemy count
  - Group composition
  - Ambush frequency
  - Healing/safe room rates
- RL tuning is **offline-only** (runtime loads fixed parameters)

#### Enemy Constraints
- Enemies are simple/aggressive
- Enemies do NOT patrol, hide, inspect sounds, or move between rooms
- Enemies remain in-room until defeated

#### Player Mechanics
- Base HP = 100
- Short attack damage range: 8–12
- Long attack damage range: 15–25
- Dash implemented
- Block/parry timing-based reduction: 60–100%

#### Win/Loss
- Win occurs only by defeating the final boss
- Loss occurs when player HP reaches 0
- Loss results in run reset (roguelike reset)



## **MANDATORY**: ARCHITECTURE VERIFICATION

### **CRITICAL**: Verify separation of responsibilities:

- **DungeonGenerator**: builds 30-room plan using seed
- **RoomController**: manages current room state + progression
- **EncounterSpawner**: spawns enemies based on directives
- **MetricsTracker**: records player performance signals
- **AIDirector**: outputs deterministic difficulty directives (no randomness)
- **Enemies**: simple chase/attack logic only



## **MANDATORY**: COMMON ISSUES AND SOLUTIONS

### **CRITICAL**: If execution fails:

1. **Import/module errors**
   - Ensure paths match exactly: `src/game/...`
   - Run using: `python -m src.game.main`

2. **Randomness violations**
   - Ensure only `src/game/rng.py` uses Python `random`
   - Replace any `random.*` usage elsewhere with calls into `rng.py`

3. **Room count issues**
   - Verify dungeon plan always returns length 30
   - Verify room 0 START and room 29 BOSS

4. **AI Director nondeterminism**
   - Ensure AI Director contains no random calls
   - Ensure decisions are pure functions of metrics + params



## **MANDATORY**: SUCCESS CRITERIA

### **CRITICAL**: The project is complete when:

- The game runs without errors
- All prompts were executed in order
- Dungeon is always 30 rooms with correct milestones
- AI Director is deterministic and high-level
- Enemies are room-confined and simple
- Win/loss conditions function correctly



### CRITICAL REQUIREMENT ###
**MANDATORY**: Follow each prompt exactly as specified. Do not reorder steps. Do not change file paths. Do not add scope-breaking features.
