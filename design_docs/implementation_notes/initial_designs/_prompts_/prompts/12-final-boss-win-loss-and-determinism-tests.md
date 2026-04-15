# CRITICAL REQUIREMENTS — 12 Mini Boss, Final Boss and Determinism.

### MANDATORY DIRECTIVE ###
You are an expert Python programmer.

**CRITICAL**: Implement milestone bosses and win/loss conditions deterministically.


## **MANDATORY**: OBJECTIVE 

Implement: 
- Mini Boss encounters
- Final Boss encounter
- Win/Loss state transitions
- Determinism validation


## **MANDATORY**: FILES TO CREATE OR MODIFY 

- `src/game/entities/boss.py`
- `src/game/scenes/run_scene.py`
- `src/game/scenes/end_scene.py`


## **CRITICAL**: IMPLEMENTATION REQUIREMENTS 

### Milestone Bosses

Mini Bosses:
- Room 7
- Room 15
- Room 23

Final Boss:
- Room 29 only

Placement is fixed.

### Win/Loss Conditions

Win:
- Final boss defeated

Loss:
- Player HP reaches 0
- Reset run (roguelike reset)

### Run Summary Logging
On win or loss, append run summary to:

- `logs/summary.json`

Summary must include:

- seed
- win_or_loss
- total_rooms_cleared
- total_time
- total_damage_taken

This data is used for offline difficulty analysis and RL tuning.
No runtime reading of summary files allowed.

### Boss Determinism

- Boss patterns must be deterministic.
- No internal random calls.
- Variation must come from seeded RNG at run start only.

### Final Boss Arena Rules (If Hazards Active)

- Lava ≤ 20%
- Walls ≤ 20%
- Safe Area ≥ 65%

Must satisfy global safety constraints.

### Final Boss Phase Rules (Hard Lock)
Phase 1: 100% → 50% HP  
Phase 2: 50% → 0% HP  

Trigger: HP ≤ 50%  
- 2 seconds invulnerability  
- Visual transformation  
- No HP reset  

Phase 2:
- Cooldown reduced by 20%
- Movement speed increased by 10%
- One summon event at phase start
- No further summons

## **MANDATORY**: ARCHITECTURE CONSTRAINTS

- Boss logic separate from AI Director. 
- AI Director does not modify boss stats directly. 


## **MANDATORY**: VERIFICATION 

- [ ] Mini bosses appear at correct indices
- [ ] Final boss only at room 29
- [ ] Win triggers correctly
- [ ] Loss resets correctly 
- [ ] Same seed -> identical behavior


### CRITICAL REMINDER ###
- Milestone indices fixed
- Deterministic logic only
- No stat mutation from Director
