# Adaptive AI Dungeon — Final Parameters (Master Combined Specification)

(Group Members: Natalie Cristina Leal Blanco, Maham Asif)

---

# SECTION 1 — CORE DUNGEON STRUCTURE

# Adaptive AI Dungeon — Final Parameters (Shareable Spec)

**Group Members:** Natalie Cristina Leal Blanco, Maham Asif  
**Run Length:** 30 rooms (fixed)  
**Core Principle:** Seed controls variation; AI Director controls pacing/difficulty; RL tunes parameters offline only.  
Sources: Project Description + SRS + Proposed Parameters + Final Parameters doc.  

---

## 1) Biomes and Room Structure

### 1.1 Biome Breakdown (Fixed Skeleton)

The dungeon run is always **30 rooms**, divided into **4 biomes**:

| Biome | Room Range | Rooms | Milestone |
|------:|------------|------:|----------|
| Biome 1 | 0–7 | 8 | Mini Boss |
| Biome 2 | 8–15 | 8 | Mini Boss |
| Biome 3 | 16–23 | 8 | Mini Boss |
| Biome 4 | 24–29 | 6 | Final Boss |

**Fixed milestones**
- Room 0 = Start Room  
- Room 29 = Final Boss  
- Biome boundaries do not change during gameplay.  

---

### 1.2 Room Types (Supported)

- Start Room — no combat  
- Corridor / Transition — path choice / pacing buffer  
- Combat Room — standard encounter  
- Ambush Room — immediate pressure on entry  
- Safe / Rest Room — recovery + upgrades  
- Elite Room — stronger encounter or reinforcements  
- Boss Room — milestone encounter  

---

### 1.3 Room Type Distribution per Biome (Counts / Ranges)

Room order and exact distribution can vary by seed **within these bounds**.

#### ✅ Biome 1 (Rooms 0–7) — Intro / Learning
| Room Type | Count (Range) |
|---|---:|
| Start | 1 (fixed) |
| Combat | 3–4 |
| Ambush | 0–1 (soft ambush only) |
| Safe / Rest | 1 |
| Corridor / Transition | 0–1 |
| Elite | 1 |
| Mini Boss | 1 (fixed at end biome) |

**Goal:** easier pacing; low hazard; teach combat + dash.

---

#### ✅ Biome 2 (Rooms 8–15) — Pressure Increase
| Room Type | Count (Range) |
|---|---:|
| Combat | 3–4 |
| Ambush | 1–2 |
| Safe / Rest | 1 |
| Corridor / Transition | 0–1 |
| Elite | 1 |
| Mini Boss | 1 (fixed at end biome) |

**Goal:** moderate pressure; introduce tighter rooms + more hazards.

---

#### ✅ Biome 3 (Rooms 16–23) — High Pressure
| Room Type | Count (Range) |
|---|---:|
| Combat | 2–4 |
| Ambush | 2–3 |
| Safe / Rest | 1 |
| Corridor / Transition | 0–1 |
| Elite | 1 |
| Mini Boss | 1 (fixed at end biome) |

**Goal:** high pressure; clustered hazards; aggressive encounters.

---

#### ✅ Biome 4 (Rooms 24–29) — Endgame
| Room Type | Count (Range) |
|---|---:|
| Combat | 2–3 |
| Ambush | 1 |
| Safe / Rest | 1 (checkpoint before final boss) |
| Corridor / Transition | 0–1 |
| Elite | 1 |
| Final Boss | 1 (fixed at Room 29) |

**Goal:** intense pacing; ensure player reaches final boss with a fair checkpoint.

---

### 1.4 Safe Room Frequency (Global Rule)

Safe/Rest rooms occur approximately **1 every 4–6 rooms** across the run (controlled but within fixed structure).  
Safe rooms provide:
- Partial health restore
- Pacing break
- Upgrade selection (player chooses 1 upgrade)

---

## 2) Room Sizes and Environmental Blocks

### 2.1 Room Sizes

- Large: **16×16** (Start, Elite, Boss arenas)
- Medium: **12×12** (standard combats, safe/rest)
- Small: **8×8** (ambush/tight pressure rooms; later biomes more likely)

---

### 2.2 Block Types

- Normal Floor — standard movement  
- Lava — high damage over time; avoided by enemies  
- Slow terrain (mud/water) — reduced movement speed  
- Walls — block movement

## 2.3 Graphics Baseline (Hard Constraint)

- Top-down 2D pixel style
- Tile-based rendering (32x32 tiles)
- Rendering layer must be separated from gameplay logic
- No isometric perspective
- No dynamic lighting engine
- Visual clarity prioritized over realism

---

## 3) Seed Generator System

### 3.1 One Global Seed Per Run

- One global seed is generated when the run starts.
- Using that one seed, the game generates all **4 biomes sequentially**.
- Seed controls *variation*; it **does not** change the fixed skeleton (30 rooms / milestones).

---

### 3.2 What Seed Controls

Seed determines:
- Room layout template variants (walls + hazard shapes)
- Hazard density (within biome caps)
- Exact hazard placement pattern
- Visual theme styling (land/water/lava vibe)
- Enemy spawn positions/layout patterns
- Minor encounter layout presentation (not difficulty decisions)

- In predefined flexible room slots, the seed may mark a room as a **Flexible Encounter Slot**, allowing it to later function as either a Combat Room or Ambush Room.
- The seed defines which rooms are eligible for Combat/Ambush variation but does not decide the final encounter type at runtime.

Seed may also determine the **distribution/order** of room types within each biome *only within the allowed per-biome bounds above*.

---

### 3.3 What Seed Cannot Control (Fixed)

- Total rooms (always 30)
- Biome count (always 4)
- Boss positions (mini bosses at biome ends; final boss at Room 29)
- Safety constraints and hazard caps
- AI Director decisions

---

## 4) Hazard Constraints (Biome Caps + Room-Level Variability)

### 4.1 Global Safety Constraints (Always True)

- Minimum walkable safe area must be respected (per biome)
- Player spawn tile is always safe
- Exit tile is always safe
- Safe rooms have 0 lava
- At least one **3×3 safe zone** exists per room
- A valid path exists from spawn → exit (no blocked progression)

---

### 4.2 Biome Hazard Caps (Per Room)

#### 🟢 Biome 1 (Intro)
| Hazard | Range per Room |
|---|---|
| Lava | 0–5% |
| Slow Terrain | 5–10% |
| Walls | 10–15% |
| Minimum Safe Area | ≥ 70% |

#### 🔵 Biome 2 (Pressure)
| Hazard | Range per Room |
|---|---|
| Lava | 5–15% |
| Slow Terrain | 5–15% |
| Walls | 15–20% |
| Minimum Safe Area | ≥ 60% |

#### 🔴 Biome 3 (High Pressure)
| Hazard | Range per Room |
|---|---|
| Lava | 15–25% |
| Slow Terrain | 10–20% |
| Walls | 20–25% |
| Minimum Safe Area | ≥ 50% |

#### ⚫ Biome 4 (Endgame)
| Hazard | Range per Room |
|---|---|
| Lava | 20–30% |
| Slow Terrain | 10–20% |
| Walls | 20–30% |
| Minimum Safe Area | ≥ 45% |

**Final Boss Arena (special cap):**
- Lava ≤ 20%
- Walls ≤ 20%
- Minimum safe area ≥ 65% (fair arena movement)

---

### 4.3 How Much Hazards Can Vary Room-to-Room (Seed Variability)

Within each biome cap:
- Lava can vary about **±3–5%** between rooms  
- Walls can vary about **±5%** between rooms  
- Slow terrain can vary about **±5%** between rooms  
Validation rules always enforce minimum safe area + connectivity.

---

## 5) AI Director (Deterministic Difficulty + Pacing Controller)

### 5.1 What AI Director Tracks

- Player health trend
- Death count in current run
- Progression speed (clear time)
- Recent combat outcomes (damage taken / clean clears)

AI Director is deterministic: no randomness inside the Director.

---

### 5.2 Player State Classification

| State | Typical Signal |
|---|---|
| Struggling | HP < 40% OR recent death OR heavy damage OR slow clears |
| Stable | HP 40–75% and average clears |
| Dominating | HP > 75% + fast clears + low damage + no recent deaths |

---

### 5.3 What AI Director Can Decide (Per Upcoming Slot)

AI Director chooses (within bounds):
- Encounter variant in flexible slots (Combat vs Ambush, etc.)
- In rooms marked by the seed as Flexible Encounter Slots, the AI Director decides      whether the room will function as a Combat Room or an Ambush Room based on player performance state.
- This decision is deterministic and must remain within biome-specific room distribution bounds.
- Enemy spawn timing (delayed/normal/instant)
- Enemy count (low/baseline/high within biome limits)
- Enemy composition (melee/fast/heavy mix, elite-lite chance)
- Reinforcement waves (enable/disable)
- Ambush intensity (soft vs hard)
- Safe room availability bias (within schedule constraints)
- Healing item drop rate / amount (bounded)
- **Safe-room upgrade offerings** (what upgrades appear as options)

AI Director does NOT:
- Directly control enemy AI behavior
- Change total room count / milestones
- Exceed hazard caps or violate safety rules

---

### 5.4 Safe Room Control (Healing + Upgrades)

Safe rooms provide:
1) **Partial health restore**
2) **1 upgrade selection** (player chooses one)

**Upgrades (examples / supported set):**
- Health Upgrade: +15–25% max health  
- Speed Boost: +10% movement speed  
- Attack Boost: +10–15% damage  
- Cooldown Reduction: faster attacks  
- Defense Boost: reduced incoming damage  

**How AI Director influences Safe Rooms**
- If player is **Struggling**:
  - Increase likelihood of offering **Health** / **Defense** upgrades
  - Increase healing amount or healing-drop bias
- If player is **Stable**:
  - Offer balanced mix (Health/Attack/Defense)
- If player is **Dominating**:
  - Offer more offensive options (Attack/Cooldown/Speed)
  - Slightly reduce healing bias (still within fairness constraints)

This fulfills: “AI Director adjusts healing item and safe room availability” and “decides which item/power-up is most appropriate.”  

---

### 5.5 Per-Biome Policy (High-Level Summary)

- **Biome 1:** gentle adaptation; avoid frequent ambush; small changes mostly in enemy count + spawn delay  
- **Biome 2:** moderate adaptation; ambush allowed; elite-lite occasionally  
- **Biome 3:** strong adaptation; more ambush + reinforcements when dominating; recovery bias when struggling  
- **Biome 4:** endgame pressure; still prevent unwinnable boss entry (force checkpoint + reasonable recovery)

---

## 6) Reinforcement Learning (RL) — Offline Tuning Only

RL is used **offline** to tune numeric parameters of the AI Director.  
No learning happens during gameplay.

### 6.1 What RL Can Tune

RL can tune:
- Enemy count multipliers per biome/state
- Elite probability per biome/state
- Ambush bias strength
- Reinforcement wave probability
- Safe room recovery bias strength
- Healing amount/drop bias
- Thresholds for Struggling/Stable/Dominating

### 6.2 Reward Objective (Example)

Reward encourages:
- Balanced target win rate (example: ~55–65%)
- Penalize early deaths (especially Biome 1)
- Avoid extreme difficulty spikes
- Prevent trivial late-game (Biome 4 too easy)

Example signals:
- + reward for completing a biome with appropriate challenge
- - penalty for dying too early
- - penalty for too many consecutive “no damage” clears (too easy)
- - penalty if win rate becomes too high (>~80%) or too low

### 6.3 What RL Cannot Change

RL cannot change:
- 30-room structure
- number of biomes
- milestone placement
- hazard caps and safety constraints
- runtime determinism requirements
- Biome hazard caps
- Layout safety rules
- Minimum safe area guarantees


At runtime, the game loads fixed tuned parameters and remains deterministic.

---

## 7) Final System Summary (Architecture)

| Layer | Responsible For |
|---|---|
| Skeleton | 30 rooms + milestones + biome boundaries |
| Seed | Layout templates + hazard patterns + room-type order within bounds |
| AI Director | Deterministic encounter pacing (spawns, composition, ambush freq, healing/upgrades) |
| Validation | Guarantees playability (safe area, connectivity, no blocked exits) |
| RL (Offline) | Tunes AI Director numeric parameters only |
| Rendering Layer | Pure visual drawing only; no gameplay logic |

---

## 8) Key Guarantees

- Same seed ⇒ same dungeon plan and room layouts (pre-game generation)
- AI Director decisions are deterministic (pure rule-based)
- Difficulty adjustments always remain within predefined bounds
- No unwinnable runs due to hazard placement or blocked progression

# SECTION 2 — Final Missing Details Patch v2 (Lock + Completeness)
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
- Projectile caps must be enforced every frame.
- If cap is reached, new projectiles are not spawned.

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
- Contact damage timer must use deterministic frame-based timing.
- No random intervals permitted.


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
- No module may import Python's random directly.
- All randomness must go through src/game/rng.py.

# SECTION 3 — Hades Enemies Details

Hades enemies details
# MELEE ENEMIES
These create close-range pressure and force constant movement.
## 1A. Small Melee (Swarm Type)
   
Visual Identity
•	Small, aggressive creature
•	Sharp limbs or claws
•	Quick twitch animations
•	Slight glow in eyes
•	Low armor appearance
Role in Combat
•	Surround player
•	Force dodging
•	Create chaos
Characteristics
•	HP: Low
•	Damage: Low (6–10)
•	Speed: Medium
•	Attack Cooldown: 1–2 sec
•	No armor
Behavior
•	Direct chase
•	Quick strike
•	No retreat
Purpose: They are annoying, not deadly alone — dangerous in groups.

## 1B. Giant Melee (Brute Type)
Visual Identity
•	Large body
•	Thick armor plates
•	Heavy weapon (club, hammer)
•	Slow walking animation
•	Strong attack telegraph
Role in Combat
•	Area denial
•	Punishes bad timing
Characteristics
•	HP: Very High
•	Damage: High (12–20)
•	Speed: Slow
•	Windup: 2–3 sec
•	Cooldown: 4–6 sec
Attack Style
•	Ground slam (small AoE)
•	Heavy forward swing
Purpose: Player must read telegraph and dash correctly.
FAST ENEMIES
These punish poor positioning.
 
## 2A. Light Fast (Flanker):

Visual Identity
•	Lean body
•	Light armor
•	Spear or blade
•	Quick dash animation
Role
•	Hit-and-run
•	Attacks from angles
Characteristics
•	HP: Low-Medium
•	Damage: 8–12
•	Speed: High
•	Quick dash ability
Behavior
•	Circle player
•	Dash in
•	Strike
•	Slight retreat
Purpose: Forces awareness of surroundings.
## 2B. Armored Fast (Advanced Flanker):
 
Visual Identity
•	Medium armor plating
•	Energy shield glow
•	Aggressive stance
Role
•	Disrupt player rhythm
Characteristics
•	HP: Medium
•	Damage: 10–14
•	Speed: High
•	Armor shield (absorbs damage first)
Ability
•	Multi-hit combo
•	Short invulnerable dash
Purpose: Forces target prioritization.
HEAVY ENEMIES
 
Control space and limit movement.
## 3A. Standard Heavy
Visual Identity
•	Thick armored body
•	Large hammer
•	Slow animation
•	Glowing attack windup
Role
•	Area control
Characteristics
•	HP: High
•	Damage: 14–18
•	Speed: Slow
•	AoE slam
Purpose: Limits safe zones.

## 3B. Armored Heavy (Advanced)
 
Visual Identity
•	Larger armor
•	Strong glow accents
•	Intimidating posture
Role
•	High battlefield presence
Characteristics
•	HP: Very High
•	Damage: 18–22
•	Strong armor layer
•	Large shockwave AoE
 Purpose: Creates high pressure rooms.

ELITE VARIANT (Modifier)
Elite enemies look:
•	Larger
•	Glowing aura
•	Unique color tint
•	Extra visual effect
Stat Modifiers
•	+40% HP
•	+20% Damage
•	Unique ability (rage / shockwave / speed burst)
Summon Rule (Balanced)
Each elite enemy may summon once per encounter.
Total elite summons across the entire run must not exceed 

## MINI BOSS
Visual:
•	Unique silhouette
•	Unique weapon
•	Dramatic animation
Characteristics
•	HP: 4–6× baseline
•	2–3 abilities
•	1 summon at 50% HP
Summon:
•	2–4 small melee

## FINAL BOSS
Visual:
•	Largest model
•	Multi-phase transformation
•	Strong visual telegraph
Phase Structure
Phase 1: Controlled combat
Phase 2: Faster, more aggressive
Summon:
•	Once per phase

# SECTION 4 — Player and Enemy Parameter Proposal
# Player and Enemy Parameter Proposal
* If approved, to be added to AI_Dungeon_Parameters_discussion.md

## 9) Player Characteristics & Combat Paramters
This section desfines baseline player combat behavior and interaction rules. These values prevent ambiguity during implementation and must remain deterministic at runtime. 

All numerical values below are **initial tuning defaults** and may be adjusted later without architectural changes.

### 9.1 Player Core Stats
| Parameter | Initial Value | Rule |
|------:|------------|------:|
| Base Max HP | 100 | Fixed requirement |
| Move Speed | 220 px/sec | Scaled by delta-time |
| Collision Radius | 16 px | Used for hit detection |
| Contact Damage Allowed | Yes | Only in combat rooms |

### 9.2 Dash Mechanics
| Parameters | Initial Value |
| ----- | -------:|
| Dash Speed Multiplier | 2.2x more speed |
| Dash Duration | 0.18 sec |
| Dash Cooldown | 1.0 sec |


**Rules**
- Dash cannot stack.
- Dash cannot exceed room bounds.
- Dash behavior must use deterministic timers.

### 9.3 Player Attacks

#### 9.3.1 Short Range Attack (Melee)
| Parameter | Initial Value |
| ---- | ----: |
| Damage Range | 8-12 |
| Cooldown | 0.50 sec |
| Hitbox Range | 50 px |
| Hitbox Width | 70 px arc/rectangle |
| Knockback | 8 px |

**Role:** Sustained DPS. 

#### 9.3.2 Long-Range Attack (Projectile)
| Parameter | Initial Value | 
| --- | ----: |
| Damage Range | 15-25 |
| Cooldown | 0.80 sec |
| Projectile Speed | 520 px/sec |
| Lifetime | 1.2 sec |
| Radius | 6 px |
| Max Active Projectiles | 3 |

**Role:** Burst + spacing tool.

### 9.4 Block & Parry System
| Parameter | Initial Value |
| ---- | ----: |
| Block Reduction | 60% |
| Parry Reduction | 100% |
| Parry Timing Window | 120 ms |

**Rules**
- If hit occurs during parry window -> 100% reduction.
- If blocking outside window -> 60% reduction.
- If not blocking -> full damage.
- No randomness permitted in damage reduction calculations.

### 9.5 Hit Feedback 
| Mechanic | Initial Value |
| ---- | ----: |
| Enemy Knockback | 8 px |
| Player Knockback | 12 px |
| Hit Flash Duration | 0.10 sec |
| Stun | Disabled (MVP) |

## 10 Enemy Archetypes & Combat Roles
Enemy behavior is inspired by role-based combat archetyppes, adapted for deterministic room-based encounters. 

Enemies must:
- Remain confined to the current room.
- Use simple chase/attack logic.
- Not use advanced AI (no patrol, hiding, sound detection).
- Remain deterministic.
- All enemies must remain confined within the active room bounds.
- Enemies may not path outside room geometry.
- Room exit unlocks only when active enemy count reaches zero.


### 10.1 Swarm (Small Melee)
**Role:** Surround + pressure.
| Parameter | Value |
| ---- | ----: |
| HP | 30 |
| Speed | 190 px/sec |
| Damage | 8 |
| Attack Cooldown | 1.2 sec |

**Expected Hit to Kill**
- Short (~10 dmg midpoint) -> ~3 hits
- Long (~20 dmg midpoint) -> ~2 hits

### 10.2 Flanker (Fast Attacker)
**Role:** Angle disruption
| Parameter | Value |
| ---- | ----: |
| HP | 40 |
| Speed | 260 px/sec |
| Damage | 10 |
| Dash Cooldown | 3 sec |

**Behavior**
- Circles player briefly. 
- Dashes inward.
- Retreats slightly.

### 10.3 Brute (Telegraphed Heavy Strike)
**Role:** Runish mistimed movement.
| Parameter | Value |
| ---- | ----:|
| HP | 110 |
| Speed | 120 px/sec |
| Damage | 16 |
| Windup | 2.0 sec |
| Cooldown | 4.0 sec |

### 10.4 Heavy (Area Control)
**Role:** Space denial.
| Parameter | Value |
| ---- | ----: |
| HP | 160 |
| Speed | 100 px/sec | 
| Damage | 18 |
| AoE Radius | 70 px |
| Cooldown | 3.5 sec |

### 10.5 Ranged Suppressor 
**Role:** Projectile pressure.
| Parameter | Value | 
| ---- | ----: | 
| HP | 60 |
| Speed | 150 px/sec |
| Projectile Damage | 10 |
| Fire Interval | 1.5 sec |

**Behavior**
- Fires toward player.
- Minimal chase behavior.

### 10.6 Elite Modifier System
Elite enemies modify exxisting archetypes.
| Modifier | Value |
| ---- | ----: |
| HP Bonus | +40% |
| Damage Bonus | +20% |
| Visual Indicator | Glow / Size increase |
| Max Elites per Run | 3 |

**Optional Elite Abilities:**
- Speed burst.
- Shockwave on death.
- Rage below 30% HP.

### 10.7 Mini Boss
| Parameter | Value |
| ---- | ----: |
| HP | 600-700 |
| Abilities | 2-3 simple behaviors |
| Summon Trigger | At 50% HP |

Used mid-run to spike difficulty.

### 10.8 Final Boss
| Parameter | Value |
| ---- | ----: |
| HP | 1200 |
| Speed | 140 px/sec |
| Damage | 20 |
| Phases | 2 |

**Phase 2:**
- Increased agression.
- Reduced cooldowns.
- One summon event.

All transitions must be deterministic.


## 11) Player-to-Enemy Balance Matrix
Use midpoint player damaage values: 
| Enemy | HP | Short Hits | Long Hits | Role |
| ---- | ---- | ---- | ---- | ---- |
| Swarm | 30 | 3 | 2 | Pressure |
| Flanker | 40 | 4 | 2 | Disruption |
| Brute | 110 | 11 | 6 | Punish |
| Heavy | 160 | 16 | 8 | Area control |
| Mini Boss | 650 | 65 | 33 | Mid Spike |
| Final Boss | 1200 | 120 | 60 | Final test |

These are pacing targets, not guarantees. 

## 12) Determinism & Balance Guarantees
The following must always hold: 
- Player HP = 100
- Short damage range = 8-12
- Long damage range = 15-25
- Enemy stats remain within defined tiers
- AI Director does not override base combat rules
- All randomnes centralized in seeded RNG
- AI Director contains no randomness




