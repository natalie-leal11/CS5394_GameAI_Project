# CRITICAL REQUIREMENTS — 11 Rest Rooms, Healing, and Upgrades.

### MANDATORY DIRECTIVE ###
You are an expert Python programmer.

**CRITICAL**: Implement Safe/REst rooms with healing and upgrade selection.


## **MANDATORY**: OBJECTIVE 
Implement deterministic healing and upgrade selection in Safe rooms.


## **MANDATORY**: FILES TO CREATE OR MODIFY 

- `src/game/entities/pickups.py`
- `src/game/systems/collisions.py`
- `src/game/systems/hud.py`
- 'src/game/ai/ai_director.py' (if upgrade bias logic needed)


## **CRITICAL**: IMPLEMENTATION REQUIREMENTS 

### Safe Room Behavior

Safe rooms must:
1) Restore partial HP (baseline: 25% max HP)
2) Present 3 upgrade options
3) Allow player to select exactly 1 upgrade

Safe rooms must contain zero lava.

## Supported Upgrades

- +15-25% Max HP
- +10% Move Speed
- +10-15% Attack Damage
- Cooldown Reduction
- Damage Reduction Boost

Upgrades must be parameter-driven.

### Target Combat Durations (Balancing Reference)
- Standard: 20–40 seconds
- Elite: 40–60 seconds
- Mini Boss: 45–75 seconds
- Final Boss: 60–120 seconds

These values are references only and must not enforce timers.

### AI Director Bias

Director may bias upgrade offerings:

- Struggling -> favor HP/Defense
- Stable -> balanced
-> Dominating -> favor offense/speed

Director does NOT auto-apply upgrades.

### **MANDATORY**: Determinism 

- Same seed + same performance -> same upgrade offering.
- No randomness outside centralized RNG.


## **MANDATORY**: ARCHITECTURE CONSTRAINTS

- Upgrades must modify player stats via centralized stat system.
- No permanent stat mutation outside defined upgrade system.


## **MANDATORY**: VERIFICATION 

- [ ] Safe room heals player
- [ ] Exactly 3 upgrades shown
- [ ] Player selects 1
- [ ] AI Director bias visible
- [ ] Deterministic behavior verified


### CRITICAL REMINDER ###
- Safe rooms must not spawn enemies
- Upgrades must remain bounded
