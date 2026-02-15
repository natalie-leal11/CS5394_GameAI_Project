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

### Run Data Logging (Required for Future RL Tuning)
The MetricsTracker must log per-room data to disk for offline analysis.

Create folder:
- `logs/runs/`

For each room completion, log:

- run_id
- seed
- biome_index
- room_index
- room_type
- chosen_encounter_type (combat/ambush/etc.)
- enemy_count
- elite_count
- player_hp_start
- player_hp_end
- damage_taken
- clear_time
- director_state (struggling/stable/dominating)

At end of run, log summary:

- win_or_loss
- rooms_cleared
- total_damage_taken
- total_run_time

Logging format: JSON or CSV.
Logging must NOT influence gameplay or determinism.
AI Director must never read from log files during runtime.
Metrics logging must trigger only once upon room completion.
No per-frame logging allowed.

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

### Future RL Integration Compatibility (Do Not Implement Training Here)
- AI Director decision thresholds and multipliers must be read from `difficulty_params.py`.
- No hard-coded threshold values (e.g., HP < 40%) may exist inside `ai_director.py`.
- RL may only modify external parameter values.
- All decision logic must depend only on:
    - Current metrics
    - External parameter values from difficulty_params.py

This ensures thresholds can later be replaced by learned weights from an offline RL policy without changing core logic.

RL may tune:
- enemy count multipliers
- elite probability bias
- ambush probability bias
- healing bias
- threshold weights

RL may NOT tune:
- dungeon structure (30 rooms, 4 biomes)
- boss positions
- base player stats
- base enemy archetypes
- biome hazard caps
- dungeon layout rules

RL-adjustable parameters must not include biome hazard caps or dungeon layout rules.

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
