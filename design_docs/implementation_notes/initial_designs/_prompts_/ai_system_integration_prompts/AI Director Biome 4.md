Implement AI Director application for Biome 4.

Goal:
Create an adaptive, fair, and intense final experience for Biome 4,
with special handling for the Final Boss encounter.

Keep all behavior deterministic and aligned with current implementation.

---------------------------------------
BIOME 4 CONSTRAINTS
---------------------------------------

Room types:
- COMBAT
- AMBUSH
- ELITE
- SAFE
- FINAL_BOSS

Enemy types:
- Swarm
- Flanker
- Brute
- Heavy
- Ranged

Important:
- Final Boss exists (Room 29)
- Final Boss has:
  - multiple attack types (fireball, meteor, lava wave, teleport)
  - phase transition
  - revive mechanic

Do NOT:
- change boss attack types
- change revive logic
- change core mechanics
- add new enemies

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
- boss_pressure ("low" / "medium" / "high")
- pacing_bias ("relaxed" / "normal" / "intense")

Mapping:

STRUGGLING:
- difficulty_modifier = 0.85
- enemy_adjustment = -1
- reinforcement_chance = 0.05
- pressure_level = "low"
- composition_bias = "safe"
- boss_pressure = "low"
- pacing_bias = "relaxed"

STABLE:
- difficulty_modifier = 1.0
- enemy_adjustment = 0
- reinforcement_chance = 0.15
- pressure_level = "medium"
- composition_bias = "balanced"
- boss_pressure = "medium"
- pacing_bias = "normal"

DOMINATING:
- difficulty_modifier = 1.15
- enemy_adjustment = +1
- reinforcement_chance = 0.35
- pressure_level = "high"
- composition_bias = "aggressive"
- boss_pressure = "high"
- pacing_bias = "intense"

---------------------------------------
2. APPLY ONLY IN BIOME 4
---------------------------------------

Apply when:
- biome_index == 4

Split logic:
- normal rooms (COMBAT / AMBUSH / ELITE)
- FINAL_BOSS room (special handling)

---------------------------------------
3. NORMAL ROOM ADAPTATION
---------------------------------------

Same base as Biome 2/3, but stronger:

Enemy count:
- -1 / 0 / +1

Composition:
- safe → fewer Heavy/Ranged
- aggressive → ensure Heavy + Ranged presence

Pressure:
- low → slower waves, more spacing
- high → tighter spawns, faster waves

Reinforcement:
- up to 2 enemies
- high pressure allows mixed types (Flanker/Brute/Ranged)

---------------------------------------
4. PACING CONTROL (IMPORTANT)
---------------------------------------

Biome 4 introduces pacing control:

relaxed:
- longer delays between waves
- fewer simultaneous threats

normal:
- unchanged

intense:
- overlapping waves (slightly)
- reduced delay between spawns

Do NOT create chaos:
- keep bounded adjustments only

---------------------------------------
5. FINAL BOSS ADAPTATION (CORE PART)
---------------------------------------

Only apply SMALL parameter adjustments.

Use boss_pressure:

LOW (STRUGGLING):
- increase telegraph durations (+15%)
- reduce attack frequency slightly
- increase recovery time between attacks
- reduce projectile frequency slightly

MEDIUM:
- default behavior

HIGH (DOMINATING):
- reduce telegraph durations (-10%)
- increase attack frequency slightly
- reduce recovery time
- allow slightly more frequent meteor usage

---------------------------------------
6. REVIVE PHASE FAIRNESS (VERY IMPORTANT)
---------------------------------------

When boss revives:

STRUGGLING:
- delay aggression for ~1–2 seconds after revive
- reduce immediate pressure

DOMINATING:
- no delay
- faster re-engagement

---------------------------------------
7. SAFE ROOM ADAPTATION (BIOME 4 UNIQUE)
---------------------------------------

Biome 4 safe room is critical.

STRUGGLING:
- ensure better upgrade experience:
  - encourage defensive options
  - slightly increase healing effect

DOMINATING:
- slightly reduce healing impact

Do NOT:
- change UI
- change upgrade options

---------------------------------------
8. HAZARD CONTROL
---------------------------------------

Biome 4 hazards are important.

LOW:
- reduce hazards (~15%)

HIGH:
- increase hazards (~15%)

Keep within caps.

---------------------------------------
9. REWARD CONTROL
---------------------------------------

STRUGGLING:
- higher heal chance
- better recovery

DOMINATING:
- reduced rewards slightly

---------------------------------------
10. FINAL BOSS PRESSURE BALANCING
---------------------------------------

Ensure:

- player is NEVER overwhelmed instantly
- difficulty ramps gradually

Add soft rules:
- avoid stacking meteor + teleport immediately for struggling players
- allow tighter combos for dominating players

---------------------------------------
11. DEBUG OUTPUT
---------------------------------------

Extend debug:

{
    player_state,
    difficulty_modifier,
    enemy_adjustment,
    reinforcement_chance,
    pressure_level,
    composition_bias,
    boss_pressure,
    pacing_bias
}

---------------------------------------
12. SAFETY RULES
---------------------------------------

Do NOT:
- change boss mechanics
- change revive logic
- add randomness without seed
- break determinism
- modify other biomes

---------------------------------------
13. SUCCESS CRITERIA
---------------------------------------

- Final boss feels adaptive but fair
- Struggling players get relief
- Dominating players get challenge
- No chaotic difficulty spikes
- Fully deterministic
- Game remains stable

Implement minimally and safely.