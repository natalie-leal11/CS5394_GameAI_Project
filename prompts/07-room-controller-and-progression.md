# CRITICAL REQUIREMENTS — 07 Room Controller

### MANDATORY DIRECTIVE ###
You are an expert Python programmer.

**CRITICAL**: Implement deterministic room progression logic based on room type.


## **MANDATORY**: OBJECTIVE 
Control room entry, completion, and progression.


## **MANDATORY**: FILES TO CREATE OR MODIFY 

- `src/game/dungeon/room_controller.py`
- `src/game/scenes/run_scene.py`


## **CRITICAL**: IMPLEMENTATION REQUIREMENTS 

### Room Completion Rules

Start: 
- No combat 
- Immediately marked clear (or key press)

Corridor / Transition:
- No combat
- Immidiately clear

Safe / Rest:
- No combat 
- Must trigger healing + upgrade selection (Prompt 11)

Combat:
- Clear only when all enemies are defeated

Ambush:
- Immediate pressure
- Clear only when all enemies defeated

Elite:
- Harder encounter
- Clear only when all enemies defeated

Mini Boss:
- Fixed at 7, 15, 23
- Clear when boss defeated

Final Boss: 
- Fixed at 29
- Clear when defeated -> triggers win

### Progression Rules

- Room index increments sequentially.
- Cannot exceed index 29.
- Milestone rooms cannot change type.

### **MANDATORY**: Dterminism

- No RNG in progression logic.
- Pure state-driven progression.


## **MANDATORY**: ARCHITECTURE CONSTRAINTS

- No layout logic here.
- No enemy spawning logic here (delegated to spanwner).


## **MANDATORY**: VERIFICATION 

- [ ] Rooms advance sequentially
- [ ] Combat rooms block progression
- [ ] Milestone rooms fixed 
- [ ] No index overflow 


### CRITICAL REMINDER ###
- Room progression must be deterministic
- Milestones cannot move