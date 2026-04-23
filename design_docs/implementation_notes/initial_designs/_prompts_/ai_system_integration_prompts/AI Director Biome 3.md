Implement AI Director application for Biome 3.

Goal:
Introduce advanced adaptive difficulty for Biome 3, including:
- ranged enemy awareness
- hazard interaction awareness
- mini-boss phase handling
- smarter pacing

Keep everything deterministic and aligned with current implementation.

---------------------------------------
BIOME 3 CONSTRAINTS
---------------------------------------

Enemy types available:
- Swarm
- Flanker
- Brute
- Ranged

Room types:
- COMBAT
- AMBUSH
- ELITE
- SAFE
- MINI_BOSS

Important:
- Ranged enemies exist (new vs Biome 1/2)
- Mini boss has Phase 2 adds
- Hazards (lava/slow) more impactful

Do NOT:
- change boss mechanics
- change attack logic
- add new enemy types
- break spawn system

---------------------------------------
1. AI DIRECTOR EXTENDED OUTPUT
---------------------------------------

Use existing:
- difficulty_modifier
- enemy_adjustment
- reinforcement_chance

Add new:
- pressure_level ("low" / "medium" / "high")
- composition_bias ("safe" / "balanced" / "aggressive")
- ranged_bias ("low" / "medium" / "high")
- hazard_bias ("low" / "normal" / "high")

Mapping:

STRUGGLING:
- difficulty_modifier = 0.85
- enemy_adjustment = -1
- reinforcement_chance = 0.05
- pressure_level = "low"
- composition_bias = "safe"
- ranged_bias = "low"
- hazard_bias = "low"

STABLE:
- difficulty_modifier = 1.0
- enemy_adjustment = 0
- reinforcement_chance = 0.15
- pressure_level = "medium"
- composition_bias = "balanced"
- ranged_bias = "medium"
- hazard_bias = "normal"

DOMINATING:
- difficulty_modifier = 1.15
- enemy_adjustment = +1
- reinforcement_chance = 0.35
- pressure_level = "high"
- composition_bias = "aggressive"
- ranged_bias = "high"
- hazard_bias = "high"

---------------------------------------
2. APPLY ONLY IN BIOME 3
---------------------------------------

Apply when:
- biome_index == 3
- room_type in COMBAT / AMBUSH / ELITE

Do NOT apply to:
- SAFE
- MINI_BOSS (only limited tuning)

---------------------------------------
3. ENEMY COUNT + PRESSURE
---------------------------------------

Same base logic as Biome 2.

Additionally:

pressure_level affects:
- spawn density
- spacing between waves

low pressure:
- slower waves (+20% delay)
- more recovery time

high pressure:
- faster waves (-20% delay)
- tighter grouping

---------------------------------------
4. COMPOSITION (RANGED-AWARE)
---------------------------------------

Use composition_bias + ranged_bias.

Safe (struggling):
- avoid ranged-heavy setups
- prefer Swarm + Flanker
- max 1 Ranged

Balanced:
- mix of melee + ranged
- example:
  Swarm + Flanker + Ranged + Brute

Aggressive:
- ensure ranged pressure
- example:
  Ranged + Ranged + Flanker + Brute

Rules:
- deterministic selection
- do not exceed reasonable counts
- do not break spawn patterns

---------------------------------------
5. RANGED PRESSURE CONTROL
---------------------------------------

If player struggles vs ranged:

- reduce ranged frequency
- increase spacing from player

If dominating:

- increase ranged count
- reduce spacing (more pressure)

---------------------------------------
6. REINFORCEMENT (SMARTER)
---------------------------------------

Biome 3 allows adaptive reinforcement:

STRUGGLING:
- max 1 reinforcement (Swarm)

STABLE:
- 1 reinforcement (Swarm/Flanker)

DOMINATING:
- up to 2 reinforcement (include Ranged)

Spawn:
- after last wave + 0.5–1.0 sec
- deterministic RNG

---------------------------------------
7. HAZARD INTERACTION (IMPORTANT)
---------------------------------------

Biome 3 hazards are meaningful.

Use hazard_bias:

low:
- reduce hazard tiles ~15%

normal:
- unchanged

high:
- increase hazard tiles ~15%

Additionally:

If player takes high hazard damage:
- temporarily reduce hazard intensity next room

---------------------------------------
8. MINI BOSS ADJUSTMENT (LIMITED)
---------------------------------------

Do NOT modify core boss behavior.

Allowed adjustments:

STRUGGLING:
- increase telegraph duration slightly (+10–15%)
- reduce fireball frequency slightly

DOMINATING:
- reduce telegraph duration slightly
- increase attack frequency slightly

Do NOT:
- change attack types
- change phase mechanics

---------------------------------------
9. PACING CONTROL
---------------------------------------

Biome 3 introduces pacing control:

STRUGGLING:
- longer recovery between waves
- fewer simultaneous threats

DOMINATING:
- more overlapping threats
- shorter downtime

---------------------------------------
10. DEBUG OUTPUT
---------------------------------------

Extend debug state:

{
    player_state,
    difficulty_modifier,
    enemy_adjustment,
    reinforcement_chance,
    pressure_level,
    composition_bias,
    ranged_bias,
    hazard_bias
}

---------------------------------------
11. SAFETY RULES
---------------------------------------

Do NOT:
- modify enemy stats directly
- change boss logic
- add randomness without seed
- break determinism
- affect other biomes

---------------------------------------
12. SUCCESS CRITERIA
---------------------------------------

- Biome 3 feels more dynamic than Biome 2
- Ranged enemies create adaptive pressure
- Hazards influence difficulty
- Mini boss feels responsive but unchanged
- System remains deterministic
- No crashes

Implement minimally and safely.