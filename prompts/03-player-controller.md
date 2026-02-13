# CRITICAL REQUIREMENTS — 03 Player Controller (Movement + Dash)

### MANDATORY DIRECTIVE ###
You are an expert Python programmer using **Pygame**.

**CRITICAL**: Implement player movement and dash only. Do not implement combat or enemies in this step.


## **MANDATORY**: OBJECTIVE
Create a controllable player entity with deterministic movement and dash mechanics.


## **MANDATORY**: FILES TO CREATE OR MODIFY

- `src/game/entities/entity.py`
- `src/game/entities/player.py`
- `src/game/systems/movement.py`
- `src/game/scenes/run_scene.py`

No other files may be modified.


## **CRITICAL**: IMPLEMENTATION REQUIREMENTS

### Movement
- WASD movement
- Base Move Speed: **220 px/sec**
- Use delta-time scaling
- Clamp player within room bounds

### Base Stats
- Base HP: **100**
- Collision radius: **16 px**

### Dash 
- Dash Speed Multipleier: **2.2 move speed**
- Dash Duration: **0.18 sec**
- Dash Cooldown: **1.0 sec**
- Dash must use dterministic timers
- Dash cannot stack
- Dash cannot exit boundaries

### **MANDATORY**: Parameter Source
All numerical values must match SEction 9 of the Parameters Spec.
Do NOT invent alternate values/


## **MANDATORY**: ARCHITECTURE CONSTRAINTS

- No combat logic in this step
- No damage logic
- No randomness
- No AI Director integration


## **MANDATORY**: VERIFICATION

1. Run 'python -m src.game.main'
2. Verify: 
    - [ ] Player moves with WASD
    - [ ] Player moves with consistent speed
    - [ ] Dash speed multiplier applier correctly 
    - [ ] Dash cooldown enforced
    - [ ] HP initialized to 100
    - [ ] Player cannot leave screen bounds
    - [ ] No runtime errors


### CRITICAL REMINDER ###
- Player HP must be 100
- Movement and dash must use defined numeric parameters
- Deterministic logic only
- 30-room structure and AI Director remain untouched
