Implement AI Director application for Biome 1 only.

Goal:
Apply small, deterministic Biome 1 difficulty adjustments using the existing AI Director outputs and current game implementation.
Do NOT redesign gameplay.
Do NOT change boss logic.
Do NOT affect Biome 2, 3, or 4.

Files to update minimally:
- src/game/scenes/game_scene.py
- src/game/ai/ai_director.py
- optionally spawn-related helper code only if absolutely necessary

--------------------------------------------------
BIOME 1 CURRENT IMPLEMENTATION CONSTRAINTS
--------------------------------------------------

Respect current Biome 1 behavior:

- Supported non-boss enemies in Biome 1:
  - Swarm
  - Flanker
  - Brute

- Current room patterns:
  - COMBAT -> spread
  - AMBUSH -> ambush
  - ELITE -> triangle
  - SAFE -> no enemies
  - MINI_BOSS -> unchanged

- Do NOT introduce:
  - Heavy
  - Ranged
  - new enemy classes
  - new room types

- Do NOT modify:
  - MiniBoss behavior
  - room structure
  - milestone room positions
  - UI flow
  - player combat

--------------------------------------------------
1. AI DIRECTOR OUTPUT RULES FOR BIOME 1
--------------------------------------------------

Use current player_state to deterministically set Biome 1 decisions.

If player_state == "STRUGGLING":
- difficulty_modifier = 0.85
- enemy_adjustment = -1
- reinforcement_chance = 0.0
- reward_bias = "more_help"
- hazard_bias = "lower"
- composition_bias = "lighter"

If player_state == "STABLE":
- difficulty_modifier = 1.0
- enemy_adjustment = 0
- reinforcement_chance = 0.1
- reward_bias = "normal"
- hazard_bias = "normal"
- composition_bias = "normal"

If player_state == "DOMINATING":
- difficulty_modifier = 1.15
- enemy_adjustment = +1
- reinforcement_chance = 0.3
- reward_bias = "lower_help"
- hazard_bias = "higher"
- composition_bias = "harder"

Important:
- enemy_adjustment = +1 only when player_state == DOMINATING
- enemy_adjustment = -1 only when player_state == STRUGGLING
- enemy_adjustment = 0 when player_state == STABLE

Store these values in AI Director for the current room.

--------------------------------------------------
2. APPLY ONLY IN BIOME 1 ELIGIBLE ROOMS
--------------------------------------------------

Apply AI Director only when:
- biome_index == 1
- room_type in COMBAT / AMBUSH / ELITE

Do NOT apply to:
- START
- SAFE
- MINI_BOSS

--------------------------------------------------
3. ENEMY COUNT ADJUSTMENT
--------------------------------------------------

Use the existing spawn_specs as the base.

If enemy_adjustment == -1:
- remove the last spawn entry
- but keep at least 1 enemy
- do not reduce MINI_BOSS
- do not reduce SAFE/START

If enemy_adjustment == +1:
- add exactly 1 extra enemy
- choose extra enemy deterministically based on room_type and composition_bias
- never exceed reasonable Biome 1 bounds:
  - COMBAT max 4
  - AMBUSH max 4
  - ELITE max 4

Do not add more than one extra enemy.

--------------------------------------------------
4. BIOME 1 ENEMY COMPOSITION ADJUSTMENT
--------------------------------------------------

Adjust composition using only:
- Swarm
- Flanker
- Brute

Use deterministic rules, no unseeded randomness.

COMBAT rooms:
- base composition is existing spread lineup
- if composition_bias == "lighter":
  prefer more Swarm / Flanker, avoid adding Brute if possible
  examples:
  - Swarm + Flanker
  - Swarm + Swarm + Flanker
- if composition_bias == "normal":
  preserve current composition
  example:
  - Swarm + Flanker + Brute
- if composition_bias == "harder":
  keep Brute present and use stronger bounded mix
  examples:
  - Swarm + Flanker + Brute + Swarm
  - Swarm + Brute + Flanker + Brute only if current code safely supports duplicate class entries

AMBUSH rooms:
- lighter:
  prefer Swarm-heavy ambush
  examples:
  - Swarm + Swarm
  - Swarm + Flanker
- normal:
  preserve current ambush composition
- harder:
  include Brute when possible but preserve ambush pattern
  examples:
  - Swarm + Flanker + Brute
  - Swarm + Flanker + Brute + Swarm

ELITE rooms:
- preserve elite identity
- do not remove elite nature of ELITE room
- lighter:
  reduce total count if needed, but keep at least 1 elite enemy
- normal:
  preserve current elite setup
- harder:
  add one extra non-elite support enemy OR keep all current elites and add one bounded support enemy
  do not exceed total cap of 4

Rules:
- composition changes must be deterministic
- do not invent new archetypes
- do not break room pattern identity
- do not rewrite spawn system architecture

--------------------------------------------------
5. SPAWN TIMING ADJUSTMENT
--------------------------------------------------

Adjust spawn delays using difficulty_modifier.

For each spawn entry delay:
- new_delay = original_delay / difficulty_modifier

Clamp:
- minimum delay = 0.2 sec
- maximum delay = original_delay * 1.5

Interpretation:
- STRUGGLING -> slower pacing
- STABLE -> unchanged
- DOMINATING -> faster pacing

Keep order deterministic.

--------------------------------------------------
6. REINFORCEMENT LOGIC (BOUNDed)
--------------------------------------------------

Biome 1 only.
Eligible only in COMBAT rooms.

If reinforcement_chance > 0:
- deterministically evaluate using seeded RNG:
  rng = random.Random(SEED + room_index * 999 + biome_index)
- if rng.random() < reinforcement_chance:
  add 1 delayed reinforcement spawn

Reinforcement rules:
- max 1 reinforcement
- reinforcement enemy must be Swarm
- spawn after last existing spawn delay + 0.5 sec
- no chaining
- no reinforcement in SAFE, START, ELITE, MINI_BOSS, or AMBUSH unless already explicitly allowed
- deterministic for same seed and same room

--------------------------------------------------
7. HAZARD BIAS (LIGHT ONLY)
--------------------------------------------------

Biome 1 only.
Do not regenerate room structure.

If hazard adjustment is easy in current code:
- STRUGGLING -> slightly reduce hazard amount
- DOMINATING -> slightly increase hazard amount
- STABLE -> unchanged

Rules:
- keep within existing hazard caps
- only small adjustment, around 10 percent of current hazard count
- do not modify START or SAFE
- if hazard adjustment is risky in current architecture, skip this feature rather than forcing a rewrite

--------------------------------------------------
8. REWARD / RECOVERY BIAS
--------------------------------------------------

Adjust Biome 1 heal-drop behavior only, deterministically and minimally.

If player_state == STRUGGLING:
- increase heal drop help slightly
- effective heal drop chance = min(base + 0.10, 0.50)

If player_state == DOMINATING:
- decrease heal drop help slightly
- effective heal drop chance = max(base - 0.10, 0.10)

If player_state == STABLE:
- keep base chance unchanged

Do not change:
- reward type
- safe room UI
- mini boss reward structure

--------------------------------------------------
9. IMPLEMENTATION SAFETY RULES
--------------------------------------------------

Do NOT:
- modify enemy stats directly
- modify MiniBoss logic
- modify player stats
- change room order
- change seed system
- add new mechanics
- affect Biome 2/3/4
- redesign spawn system

Only apply bounded, deterministic adjustments on top of current Biome 1 spawning/reward flow.

--------------------------------------------------
10. DEBUG / INSPECTION
--------------------------------------------------

Expose the Biome 1 AI Director decisions for the current room in a compact debug dictionary, including:
- player_state
- difficulty_modifier
- enemy_adjustment
- reinforcement_chance
- composition_bias
- reward_bias
- hazard_bias

--------------------------------------------------
11. SUCCESS CRITERIA
--------------------------------------------------

- Game still runs
- Only Biome 1 changes
- Biome 1 encounter difficulty adapts deterministically
- DOMINATING can lead to enemy_adjustment = +1
- STRUGGLING can lead to enemy_adjustment = -1
- composition shifts stay inside Swarm / Flanker / Brute only
- no boss changes
- no architecture rewrite

Implement minimally and safely.