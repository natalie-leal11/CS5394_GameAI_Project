# CRITICAL REQUIREMENTS — 09 Encounter Spawner

### MANDATORY DIRECTIVE ###
You are an expert Python programmer.


## **MANDATORY**: OBJECTIVE 
Spawn enemies using defined archetypes per room and lock progression until cleared.


## **MANDATORY**: FILES TO CREATE OR MODIFY 

- `src/game/systems/spawner.py`
- `src/game/scenes/run_scene.py`


## **CRITICAL**: IMPLEMENTATION REQUIREMENTS 

Spawner must:

- Spawn only defined archetypes from Section 10
- Control enemy count
- Support ambush delay
- Remove enemies upon room clear

### Composition Rules
Spawner may vary:
- Number of enemies
- Mix of archetypes
- Elite modifier appliaction

Spawner may NOT modify:
- Base HP
- Base Damage
- Base Speed

### Elite Modifier
- HP +40%
- Damage +20%
- Visual indicator required

### CRITICAL: Global Combat Limits
- MAX_ACTIVE_ENEMIES_PER_ROOM = 10
- MAX_REINFORCEMENT_WAVES_PER_ROOM = 2

If active enemy cap is reached:
- Skip or delay reinforcement/summon.
All summons count toward active enemy cap.

## **MANDATORY**: ARCHITECTURE CONSTRAINTS

- No AI Director logic inside spawner
- Spawner responds to directives only
- Combat pacing should aim to align with target duration ranges defined in design specification.

## **MANDATORY**: VERIFICATION 

- [ ] Enemies spawn correctly
- [ ] Room remains locked until cleared
- [ ] Elite modifiers apply correctly


### CRITICAL REMINDER ###
- Composition scaling only
- No stat rewriting
