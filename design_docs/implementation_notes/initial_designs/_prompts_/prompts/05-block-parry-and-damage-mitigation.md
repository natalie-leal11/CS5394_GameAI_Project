# CRITICAL REQUIREMENTS — 05 Block and Parry

### MANDATORY DIRECTIVE ###
You are an expert Python programmer.

**CRITICAL**: Implement deterministic defensive mechanics.


## **MANDATORY**: OBJECTIVE 
Implement timing-based block/parry with damage reduction.


## **MANDATORY**: FILES TO CREATE OR MODIFY

- `src/game/entities/player.py`
- `src/game/systems/combat.py`


## **CRITICAL**: IMPLEMENTATION REQUIREMENTS 

### Defensive Parameters
- Block key: L
- Block Reduction: **60%**
- Parry Reduction: **100%**
- Parry Window: **120 ms**

### Rules
- If hit occurs inside parry window -> 100% reduction
- If blocking outside window -> 60% reduction
- Otherwise -> full damage
- No random chance allowed
- Block/parry must integrate with the global Damage Resolution Order defined in Prompt 04.

### **MANDATORY**: Parameter Source
Values must match Section 4 of AI_Dungeon_Parameters_discuss_FULL.md.


## **MANDATORY**: ARCHITECTURE CONSTRAINTS

- No randomness in defense logic
- Must integrate cleanly with combat system


## **MANDATORY**: VERIFICATION

- [ ] Block reduces damage by 60%
- [ ] Parry negates damage completely 
- [ ] Timing window behaves deterministically


### CRITICAL REMINDER ###
- Defensive values are fixed
- Deterministic timing required
