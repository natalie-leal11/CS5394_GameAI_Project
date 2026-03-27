Implement AI Director application for Biome 2.

Goal:
Extend AI Director to provide more adaptive difficulty for Biome 2,
while keeping behavior deterministic and aligned with current implementation.

Do NOT redesign gameplay.
Do NOT affect Biome 1, 3, or 4.

---------------------------------------
BIOME 2 CURRENT CONSTRAINTS
---------------------------------------

Respect existing Biome 2 system:
- Enemy types available:
  Swarm, Flanker, Brute, Heavy

- Room types:
  COMBAT, AMBUSH, ELITE, SAFE, MINI_BOSS

- Do NOT:
  - modify boss logic
  - change room order
  - add new enemy types
  - modify core combat

---------------------------------------
1. AI DIRECTOR OUTPUT EXTENSION
---------------------------------------

Reuse existing outputs:
- difficulty_modifier
- enemy_adjustment
- reinforcement_chance

Add Biome 2 specific:
- pressure_level ("low" / "medium" / "high")
- composition_bias ("lighter" / "balanced" / "aggressive")

Mapping:

STRUGGLING:
- difficulty_modifier = 0.85
- enemy_adjustment = -1
- reinforcement_chance = 0.05
- pressure_level = "low"
- composition_bias = "lighter"

STABLE:
- difficulty_modifier = 1.0
- enemy_adjustment = 0
- reinforcement_chance = 0.15
- pressure_level = "medium"
- composition_bias = "balanced"

DOMINATING:
- difficulty_modifier = 1.15
- enemy_adjustment = +1
- reinforcement_chance = 0.35
- pressure_level = "high"
- composition_bias = "aggressive"

---------------------------------------
2. APPLY ONLY IN BIOME 2
---------------------------------------

Apply only when:
- biome_index == 2
- room_type in COMBAT / AMBUSH / ELITE

Do NOT apply to:
- SAFE
- MINI_BOSS

---------------------------------------
3. ENEMY COUNT + PRESSURE
---------------------------------------

Use enemy_adjustment:

- -1 → remove last enemy (min 1)
- +1 → add one enemy (respect max limits)

Pressure effect:

IF pressure_level == "low":
- increase spacing between spawns (delay +20%)

IF pressure_level == "high":
- reduce spacing between spawns (delay -20%)

Clamp delays safely.

---------------------------------------
4. ENEMY COMPOSITION (SMARTER)
---------------------------------------

Use composition_bias:

Lighter:
- prefer Swarm + Flanker
- avoid Heavy unless already present
- example:
  Swarm, Flanker, Swarm

Balanced:
- keep original composition

Aggressive:
- ensure at least 1 Heavy or Brute
- example:
  Swarm, Brute, Heavy, Flanker

Rules:
- deterministic only
- do NOT exceed 1 Heavy in early rooms if not present
- do NOT break room identity

---------------------------------------
5. REINFORCEMENT (IMPROVED)
---------------------------------------

Biome 2 allows slightly more dynamic reinforcement:

IF reinforcement_chance triggered:
- spawn 1–2 extra enemies

Rules:
- deterministic RNG:
  rng = Random(SEED + room_index * 999 + biome_index)

- STRUGGLING → max 1 reinforcement
- DOMINATING → allow up to 2

Reinforcement types:
- low pressure → Swarm
- medium → Swarm / Flanker
- high → Flanker / Brute

Spawn after last wave + 0.5–1.0 sec

---------------------------------------
6. SPAWN PATTERN ADJUSTMENT
---------------------------------------

Without changing core system:

- low pressure:
  more spread-out spawn positions

- high pressure:
  slightly tighter clustering

Do NOT rewrite spawn system,
only adjust existing parameters if available.

---------------------------------------
7. HAZARD CONTROL (BETTER THAN BIOME 1)
---------------------------------------

Biome 2 supports slightly stronger hazard tuning:

- STRUGGLING:
  reduce hazards by ~10–15%

- DOMINATING:
  increase hazards by ~10–15%

Keep within caps.
Do NOT regenerate grid randomly.

---------------------------------------
8. REWARD + RECOVERY CONTROL
---------------------------------------

Biome 2 should feel more responsive:

STRUGGLING:
- increase heal drop chance
- increase safe room effectiveness slightly

DOMINATING:
- reduce heal drops slightly

STABLE:
- unchanged

---------------------------------------
9. SAFETY RULES
---------------------------------------

Do NOT:
- modify enemy stats
- change boss mechanics
- change RNG system
- add new enemies
- affect other biomes
- break determinism

---------------------------------------
10. DEBUG OUTPUT
---------------------------------------

Extend debug output:

{
    player_state,
    difficulty_modifier,
    enemy_adjustment,
    reinforcement_chance,
    pressure_level,
    composition_bias
}

---------------------------------------
11. SUCCESS CRITERIA
---------------------------------------

- Biome 2 feels more adaptive than Biome 1
- Difficulty reacts to player behavior
- No crashes
- Deterministic results
- No gameplay redesign

Implement cleanly and minimally.

What changed vs Biome 1
Feature	Biome 1	Biome 2
Enemy count	±1	±1 + pressure
Composition	basic	smarter
Reinforcement	1 enemy	1–2 adaptive
Spawn timing	simple	pressure-based
Hazards	light	stronger
Player feel	basic	adaptive