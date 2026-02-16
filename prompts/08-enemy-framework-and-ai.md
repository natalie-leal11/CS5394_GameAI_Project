# CRITICAL REQUIREMENTS — 08 Enemy Framework

### MANDATORY DIRECTIVE ###
You are an expert Python programmer.

**CRITICAL**: Implement enemy archetypes exactly as defined in Section 10 of the Parameters Spec.


## **MANDATORY**: OBJECTIVE 
Create simple, deterministic, room-confined enemy entities. 


## **MANDATORY**: FILES TO CREATE OR MODIFY 

- `src/game/entities/enemy_base.py`
- `src/game/entities/enemies.py`


## **CRITICAL**: IMPLEMENTATION REQUIREMENTS 

Implement the following archetypes exactly:

### Swarm
- HP: 30 
- Speed 190 px/sec
- Damage: 8

### Flanker 
- HP: 40
- Speed: 260 px/sec
- Damage: 10

### Brute 
- HP: 110
- Speed: 120 px/sec
- Damage: 16
- Windup: 2.0 sec
- Cooldown: 4.0 sec

### Heavy
- HP: 160
- Speed: 100 px/sec
- Damage 18

### Ranged Suppressor
- HP: 60
- Speed: 150 px/sec
- Projectile Damage: 10
- Fire Interval: 1.5 sec

### Elite Summon Constraint
- Each elite enemy may summon once per encounter.
- Total elite summons across entire run must not exceed 3.
- Mini boss may summon once per fight.
- Final boss may summon once (at phase 2 start).
- Boss summons do NOT count toward elite summon cap.

### General Rules
- Enemies remain confined to current room 
- Simple chase/attack only
- No patrol logic
- No advanced AI systems
- Deterministic timers only

### **MANDATORY**: Parameter Source
Values must match Section 10 of the Parameters Spec. 


## **MANDATORY**: ARCHITECTURE CONSTRAINTS

- Enemy stats must not be altered by AI Director
- Archetypes must be reusable by spawner


## **MANDATORY**: VERIFICATION

- [ ] Each archetype has correct HP
- [ ] Speeds match defined values
- [ ] Behavior remains simple and deterministic


### CRITICAL REMINDER ###
- Do not invent new archetypes 
- Use only defined stat blocks
