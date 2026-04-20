# Final Missing Details Patch v2 (Lock + Completeness)

This patch consolidates all remaining missing details into one place:
visual identity, combat bounds, boss phases, hazard values, logging for RL, and determinism locks.

---

## A) Combat Duration Targets (Balancing Reference)

Target average durations:

- Standard Room: 20–40 seconds  
- Elite Room: 40–60 seconds  
- Mini Boss: 45–75 seconds  
- Final Boss: 60–120 seconds  

These are balancing references and should not be hard-coded as strict timers.

---

## B) Global Combat Limits (Hard Caps)

To prevent uncontrolled escalation:

MAX_ACTIVE_ENEMIES_PER_ROOM = 10
MAX_REINFORCEMENT_WAVES_PER_ROOM = 2
MAX_ACTIVE_PROJECTILES_PLAYER = 3
MAX_ACTIVE_PROJECTILES_ENEMY = 6


Rules:
- Reinforcement spawns must respect `MAX_ACTIVE_ENEMIES_PER_ROOM`.
- Summoned enemies count toward the active enemy cap.
- If the cap is reached, reinforcement/summon events are delayed or skipped.

---

## C) Damage Resolution Order (MANDATORY)

All damage applications must follow this order:

1. Check collision / hit confirmation  
2. Apply block/parry logic  
3. Apply damage reduction modifiers  
4. Apply health change (HP -= final_damage)  
5. Check death (HP <= 0 triggers death state)  

Notes:
- Parry overrides block.  
- Environmental hazards follow the same order except block/parry may not apply.

---

## D) Player Visual & Weapon Identity (Hades-Inspired, Simplified for Pygame)

### Player Identity
- Archetype: Agile dungeon warrior
- Theme: Light armor, readable silhouette (top-down)
- Accent color: Blue/teal energy (strong contrast vs lava/red biomes)

### Weapon Kit
- Primary weapon: One-handed sword  
- Short Attack: quick frontal slash (small arc)  
- Long Attack: charged heavy slash (wider arc + longer reach)  
- Optional ranged: short-range energy projectile (bounded by projectile cap)

### Player Visual Feedback
- Short attack: small hit spark
- Long attack: bigger spark + slight screen shake
- Dash: faint blue trail (0.2s fade)
- Parry: brief white flash + stun effect

### Player Animations (Minimum)
- Idle (2–4 frames)
- Walk (4–6 frames)
- Short attack (4 frames)
- Long attack (6 frames + wind-up)
- Dash (trail + motion)
- Hit flash overlay
- Death (fade-out or fall)

---

## E) Enemy Visual Specification (Aligned with Hades-Inspired Roles)

### Global Enemy Visual Rules
- Enemies must be distinguishable by silhouette and size.
- Enemies must telegraph attacks visually (wind-up / flash / ground marker).
- Elite enemies must be instantly identifiable (glow/tint + aura).

### Swarm (Small Melee)
- Size: smaller than player
- Color: dark red/brown
- Motion: fast scuttle
- Telegraph: brief red flash before strike

### Flanker (Fast Enemy)
- Size: slightly smaller than player
- Color: purple/dark blue
- Motion: dash-like movement
- Telegraph: directional streak before lunge

### Brute (Large Melee)
- Size: ~1.5x player
- Color: stone grey / dark armored
- Motion: heavy stomp
- Telegraph: ground highlight circle before slam

### Heavy (Armored)
- Size: equal or larger than brute
- Color: metallic grey with armor plating
- Telegraph: long wind-up animation

### Elite Variant
- Glow outline or aura (gold/red tint)
- Subtle particle effect
- Slight size increase (5–10%)

### Mini Boss
- Larger than brute
- Biome-themed unique sprite variant
- Unique telegraph for special attack

### Final Boss (Two Phases)
- Largest enemy, unique sprite set
- Phase 2 must visually transform (stronger glow/cracks/aura)

Minimum enemy animations:
- Idle (2–4), Move (4–6), Attack (4–6), Hit flash, Death (2–4 or fade)

---

## F) Final Boss — Exact Two-Phase Mechanics (Hard Lock)

### Phase Structure
- Phase 1: 100% → 50% HP  
- Phase 2: 50% → 0% HP  

### Phase Transition
- Trigger: HP ≤ 50%
- Invulnerability: 2 seconds
- Visual transition: flash/glow intensifies
- HP does NOT reset

### Phase 2 Modifiers
- Attack cooldown reduced by 20%
- Movement speed increased by 10%
- One summon event at phase start
- No additional summons allowed in phase 2

---

## G) Summon Rules (Clarified)

- Each elite enemy may summon once per encounter.
- Total elite summons across the entire run must not exceed 3.
- Mini boss: summon once per fight
- Final boss: summon once total (at phase 2 start)
- Boss summons do NOT count toward elite summon cap
- All summons respect global enemy cap

---

## H) Contact Damage Rules (Explicit)

- Contact damage applies only to:
  - Swarm
  - Brute
  - Heavy
- Tick interval: once per 0.5 seconds while colliding
- Block reduces contact damage
- Perfect parry negates contact damage
- Dash invulnerability prevents contact damage

---

## I) Hazard Mechanics (Explicit Values)

### Lava
- Damage: 8 HP per second
- Ignores block/parry
- Dash invulnerability applies
- AI avoids lava unless forced by path

### Slow Terrain (Mud/Water)
- Movement speed reduced by 30%
- Applies to player and enemies
- Dash unaffected

### Walls
- Fully block movement
- Fully block projectiles

---

## J) Roguelike Reset Behavior

On player death:
- Run ends immediately
- No carry-over stats
- New run generates new seed
- No meta-progression in this version

Optionally display seed in UI for reproducibility.

---

## K) Run Data Logging (For Future RL)

Logging is required for offline difficulty tuning and future RL training.

### Per-Room Log Fields
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
- director_state

### End-of-Run Summary
- win_or_loss
- rooms_cleared
- total_damage_taken
- total_run_time

### Storage
- `logs/runs/` (per-room logs)
- `logs/summary.json` (run summaries)

Logging must never influence runtime gameplay (no reading logs during play).

---

## L) RL Integration (Offline Only)

RL is used only to tune AI Director parameters offline.

RL may tune:
- enemy count multipliers
- ambush probability bias
- elite probability bias
- reinforcement probability
- healing/upgrades bias
- thresholds defining struggling/stable/dominating

RL may NOT change:
- dungeon structure (30 rooms, 4 biomes)
- boss positions
- hazard caps
- base player kit
- base enemy archetypes
- determinism constraints

Runtime behavior:
- Load tuned parameters from `difficulty_params.py` or `difficulty_policy.json`
- No online learning
- Deterministic inference only

---

## M) Determinism Enforcement (Hard Lock)

- All randomness must come from a single centralized seeded RNG.
- AI Director decisions must be a pure function of:
  - current metrics
  - external parameter values loaded at start
- No runtime random calls outside RNG module.
- Same seed + same inputs → identical run structure and Director decisions.

# Appendix A — Hades Enemies Details