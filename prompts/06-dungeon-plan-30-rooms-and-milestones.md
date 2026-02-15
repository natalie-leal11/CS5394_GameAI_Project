# CRITICAL REQUIREMENTS — 06 Dungeon Plan (30 Rooms & Biomes)

### MANDATORY DIRECTIVE ###
You are an expert Python programmer.

**CRITICAL**: Implement a deterministic 30-room dungeon plan with fixed biome structure and milestone placement.


## **MANDATORY**: OBJECTIVE 
Generate a deterministic dungeon plan consisting of exactly 30 rooms, organized into 4 fixed biomes with predefined milestone positions.


## **MANDATORY**: FILES TO CREATE OR MODIFY 

- `src/game/dungeon/room_types.py`
- `src/game/dungeon/room_plan.py`
- `src/game/dungeon/dungeon_generator.py`

No other files may be modified.


## **CRITICAL**: IMPLEMENTATION REQUIREMENTS 

### **MANDATORY**: Fixed Structure

Total Rooms: **30 (constant)**

Biome Ranges:
- Biome 1 -> rooms 0-7
- Biome 2 -> rooms 8-15
- Biome 3 -> rooms 16-23
- Biome 4 -> rooms 24-29

Milestones: 
- Room 0 -> Start 
- Room 7 -> Mini Boss
- Room 15 -> Mini Boss
- Room 23 -> Mini Boss
- Room 29 -> Final Boss

These indices are fixed and cannot change.

### **MANDATORY**: Supported Room Types

Only these rooms types may be used:
- Start 
- Corridor / Transition
- Combat 
- Ambush
- Safe / Rest
- Elite 
- Mini Boss
- Final Boss


### **MANDATORY**: Per-Biome Distribution Bounds

Room type counts per biome must stay within defined bounds.

Seed may vary order and distribution **within bounds only**.

### Flexible Encounter Slots

Seed may mark rooms as Flexible Encounter Slots.
Flexible slots may become:
- Combat 
- Ambush

AI Director determines final encounter type at runtime. 

Seed must not exceed biome bounds.

### **MANDATORY**: Determinism

- Same seed -> identical dungeon plan.
- No randomness outside centralized RNG.
- Dungeon plan must be pure data (no rendering or combat logic).


## **MANDATORY**: ARCHITECTURE CONSTRAINTS 

- No layout generation here.
- No hazard logic here.
- No AI Director logic here.


## **MANDATORY**: VERIFICATION 

- [ ] Exactly 30 rooms generated
- [ ] Milestone rooms at correct indices
- [ ] Same seed → identical plan
- [ ] Room types within biome bounds


### CRITICAL REMINDER ###
- 30 rooms fixed
- Biome structure fixed 
- Milestone indices fixed
- Deterministic generation only
