# CRITICAL REQUIREMENTS — 10 AI Director

### MANDATORY DIRECTIVE ###
You are an expert Python programmer.

**CRITICAL**: AI Director must remain deterministic and high-level.


## **MANDATORY**: OBJECTIVE 
Implement deterministic AI Director and MetricsTracker.


## **MANDATORY**: FILES TO CREATE OR MODIFY

- `src/game/ai/metrics_tracker.py`
- `src/game/ai/ai_director.py`
- `src/game/ai/difficulty_params.py`


## **CRITICAL**: IMPLEMENTATION REQUIREMENTS 

### Metrics Tracked
- Player health %
- Death count
- Room clear time
- Recent combat performance

### AI Director May Adjust
- Spawn timing
- Enemy count
- Archetype mix
- Ambush frequency
- Healing drop rate
- Elite modifier usage

### AI Director May NOT Modify
- Player base stats
- Enemy base damage
- Damage ranges
- Core combat mechanics

### Determinism rule
- No random calls inside AI Director
- Decisions must be pure functions of metrics + config

### **MANDATORY**: Parameter Source
All archetypes and base values from Section 9-10 of Parameters Spec.


## **MANDATORY**: ARCHITECTURE CONSTRAINTS

- AI Director outputs spawn directives only
- No direct enemy control


## **MANDATORY**: VERIFICATION

- [ ] Same metrics -> same directives
- [ ] Low HP reduces enemy count
- [ ] Director does not alter base stats


### CRITICAL REMINDER ###
- Deterministic AI Director only
- No stat mutation allowed
