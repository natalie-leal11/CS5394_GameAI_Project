# CRITICAL REQUIREMENTS — 04 Player Attacks

### MANDATORY DIRECTIVE ###
You are an expert Python programmer using **Pygame**.

**CRITICAL**: Implement player short-range and long-range attacks only.


## **MANDATORY**: OBJECTIVE 
Add melee and projectile attacks using deterministic combat parameters.


## **MANDATORY**: FILES TO CREATE OR MODIFY

- `src/game/entities/projectiles.py`
- `src/game/systems/combat.py`
- `src/game/entities/player.py`
- `src/game/scenes/run_scene.py`


## **CRITICAL**: IMPLEMENTATION REQUIREMENTS 

### Short Attack (Melee)
- Damage Range: **8–12**
- Cooldown: **0.50 sec**
- Hitbox Range: **50 px**
- Hitbox Width: **70 px**
- Knockback: **8 px**

### Long Attack (Projectile)
- Damage Range: **15–25**
- Cooldown: **0.80 sec**
- Projectile Speed: **520 px/sec**
- Lifetime: **1.2 sec**
- Projectile Radius: **6 px**
- Max Active Projectiles: **3**

### Damage Rules
- Damage must use centralized seeded RNG
- No 'random' usage outside 'rng.py'
- Damage must not exceed defined ranges

### **MANDATORY**: Damage Resolution Order

All damage applications must follow this exact order:

1. Check collision / hit confirmation
2. Apply block/parry logic
3. Apply damage reduction modifiers
4. Apply health change (HP -= final_damage)
5. Check death condition (HP <= 0 triggers death state)
6. Parry overrides block.
7. Environmental hazards follow the same order except block/parry may not apply.

### **MANDATORY**: Parameter Source
- All numerical values must match Section 4 of AI_Dungeon_Parameters_discuss_FULL.md.


## **MANDATORY**: ARCHITECTURE CONSTRAINTS

- No enemy scaling logic here beyond dummy target
- No AI Director logic here
- Combat must remain reusable


## **MANDATORY**: VERIFICATION 

- [ ] J performs melee attack
- [ ] K fires projectile
- [ ] Short attack deals 8-12 damage
- [ ] Long attack deals 15-25 damage
- [ ] Cooldowns enforced
- [ ] Projectile limits enforced
- [ ] No randomness outside RNG module
- [ ] Damage always within required ranges

### CRITICAL REMINDER ###
- Do not invent damage values
- Keep deterministic structure
