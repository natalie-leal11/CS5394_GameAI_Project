# CRITICAL REQUIREMENTS — Adaptive Dungeon (Python / Pygame) Complete Implementation Guide

### MANDATORY DIRECTIVE ###
You are an expert Python programmer.

**CRITICAL**: Follow this complete implementation guide to create the Adaptive Dungeon game using the provided prompts in the exact order specified.

This guide reflects:
- Fixed 30-room biome structure
- Deterministic AI Director
- Hazard generation system
- Safe-room upgrade system
- Milestone boss enforcement 
- Offline RL-compatible parameter architecture


## **CRITICAL**
Access the prompts referenced below in files with corresponding filenames in directory `prompts` located in the root project directory.
Each file name must match exactly.


## IMPLEMENTATION EXECUTION ORDER

### **CRITICAL**: Execute prompts in this exact sequence:

1. **01-project-setup.md** — Create project structure and minimal runnable window
2. **02-window-loop-and-scenes.md** — Implement scene system (Menu → Run → End)
3. **03-player-controller.md** — Implement player movement + dash + HP
4. **04-combat-attacks-and-projectiles.md** — Implement short/long attacks + projectiles
5. **05-block-parry-and-damage-mitigation.md** — Implement block/parry timing-based reduction
6. **06-dungeon-plan-30-rooms-and-milestones.md** — Implement deterministic 30-room plan generation
7. **07-room-controller-and-progression.md** — Implement room progression and clearing rules
8. **13-room-rendering-and-hazards-system.md** — Implement room rendering and hazard placement.
9. **08-enemy-framework-and-ai.md** — Implement enemies (room-confined)
10. **09-encounter-spawner-and-room-battles.md** — Implement encounter spawning + lock-until-clear
11. **10-ai-director-metrics-and-difficulty-decisions.md** — Implement deterministic AI Director + metrics
12. **11-rest-rooms-healing-and-pacing.md** — Implement rest rooms + healing + pacing knobs
13. **12-final-boss-win-loss-and-determinism-tests.md** — Implement mini bosses + final boss + win/loss + determinism checks



## **MANDATORY**: VERIFICATION BETWEEN STEPS

### **CRITICAL**: After completing each prompt:

1. Run the application:
   - `python -m src.game.main`
2. Fix any runtime errors before continuing
3. Verify:
   - Correct files were created in correct paths
   - No missing imports or module errors
   - No scope-breaking features were introduced
   - No random usage outside rng.py

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
- 4 fixed biomes:
   - 0-7
   - 8-15
   - 16-23
   - 24-29
- Milestones: 
   - Room 0 -> **START**
   - Room 7 -> **MINI BOSS**
   - Room 15 -> **MINI BOSS** 
   - Room 23 -> **MINI BOSS**
   - Room 29 is **FINAL BOSS**
- Biome distribution bounds respected
- At least one **REST/CHECKPOINT** room exists every 4-6 rooms.
- Same seed produces the same dungeon plan

#### Room Layout & Hazards
Room sizes: 
- Small (8x8)
- Medium (12x12)
- Large (16x16)

Hazards caps enforced per biome:
- Lava %
- Slow terrain %
- Wall %
- Minimum safe area %

Final boss arena override:
- Lava ≤ 20%
- Walls ≤ 20%
- Safe Area ≥ 65%

Global safety constraints:
- Spawn safe
- Exit safe
- 3x3 safe zone exists
- Valid path spawn -> exit

Hazards must be deterministic.

AI Director cannot modify hazards.

#### AI Director Rules
- Fully deterministic 
- No internal random calls
- Pure function of: 
   - Metrics 
   difficulty_params.py

Tracks:
  - HP %
  - Death count
  - Room clear time
  - Combat performance

May adjust:
- Enemy count
- Archetype mix
- Elite bias
- Ambush probability
- Healing bias

May NOT adjust:
- Player base stats
- Enemy base stats
- Dungeon structure
- Biome hazard caps

RL tuning: 
- Offline only
- Runtime loads fixed parameters

#### Safe Room & Upgrade System

Safe Rooms:
- Heal **25% max** HP
- Present **exactly 3** upgrade options
- Player select **exactly 1**
- **No lava allowed**

Director bias:
- Struggling -> defense/HP
- Stable -> balanced
- Dominating -> offense/speed

Upgrades must remain bounded and parameter-driven.

#### Player Mechanics
- Base HP = 100
- Short attack damage range: 8–12
- Long attack damage range: 15–25
- Dash implemented
- Block/parry timing-based reduction: 60–100%

#### Enemy System

Archetypes:
- Swarm
- Flanker
- Brute
- Heavy
- Ranged Suppressor

Rules: 
- Room confined
- Simple chase/attack
- Deterministic timers only
- No patrol
- No cross-room logic

Elite modifier:
- +40% HP
- +20% damage

Global combat limits enforced.

#### Boss System

Mini bosses: 
- Rooms 7, 15, 23

Final boss:
- Room 29 only

Final boss phases: 
- Phase 1: 100–50%
- Phase 2: 50–0%
- 2-second invulnerability at transition
- Single summon at phase start
- No HP reset

Win:
- Final boss defeated

Loss:
- HP reaches 0 → full run reset

Run summary logging required.


## **MANDATORY**: ARCHITECTURE VERIFICATION

### **CRITICAL**: Verify separation of responsibilities:

- **DungeonGenerator**: builds 30-room plan using seed
- **RoomLayoutGenerator**: Generates tile grid + hazards
- **RoomController**: manages current room state + progression
- **EncounterSpawner**: spawns enemies based on directives
- **MetricsTracker**: records player performance signals
- **AIDirector**: outputs deterministic difficulty directives (no randomness)
- **Enemies**: simple chase/attack logic only

No cross-responsibility leakage


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

5. **Hazards exceeding biome caps**
   - Regenerate layout using same seed + deterministic retry counter. 
   - Retry generation using 'seed + room_index + retry_counter'; retry_counter increments deterministically.
   - Abort after 10 tries and fallback to safe template layout (predefined biome-valid layout).

6. **Boss appearing outside milestone index**
   - Enforce milestone override inside 'DungeonGenerator':
      - Before returning room plan, hard-set:
         - room[7] = MINI_BOSS
         - room[15] = MINI_BOSS
         - room[23] = MINI_BOSS
         - room[29] = FINAL_BOSS
   - Add defensive assertion inside 'RoomController':
      - If room_index == 29: assert room.type == FINAL_BOSS


## **MANDATORY**: SUCCESS CRITERIA

### **CRITICAL**: The project is complete when:

- The game runs without errors
- All prompts were executed in order
- Dungeon is always 30 rooms with correct milestones
- Biome structure correct
- Hazards obey caps
- AI Director is deterministic and high-level
- Mini bosses appear correctly 
- Final boss win/loss works
- No stat mutation from Director



### CRITICAL REQUIREMENT ###
**MANDATORY**: Follow each prompt exactly as specified. Do not reorder steps. Do not change file paths. Do not add scope-breaking features.
