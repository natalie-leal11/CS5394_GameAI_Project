# **1. Seed Definition and Generation**

## **1.1 Definition of Seed**

A **seed** is a deterministic integer value generated at the start of each game run.  
It serves as the single source of controlled variation for encounter composition, spawn behavior, and dungeon variant selection.

The seed ensures:
- Reproducibility of a run when the same seed is reused  
- Controlled variability across different runs  

---

## **1.2 Design Principle**

The system uses a **finite variant-based seed model**, inspired by structured procedural systems (e.g., Hades-style design).

- The seed does **not create infinite layouts**
- Instead, it maps each run to one of a **fixed number of predefined variants**

---

## **1.3 Number of Seed Variants**

The system shall support:


TOTAL_SEED_VARIANTS = 3


Each variant represents a predefined gameplay pattern, such as:
- Variant 0 → Balanced encounters  
- Variant 1 → Combat-heavy encounters  
- Variant 2 → Ambush-heavy encounters  

> These variants define high-level encounter tendencies.  
> Detailed composition is handled in later sections.

---

## **1.4 Seed Generation Mechanism**

The seed shall be generated **internally by the system**, without user input.

### Generation Method:
```python
import time
raw_seed = int(time.time() * 1000)

Uses system time in milliseconds

Ensures a different seed for each run

## **1.5 Variant Mapping**

The generated seed is mapped to a variant using modulo:

variant_id = raw_seed % TOTAL_SEED_VARIANTS

This ensures:

Only 3 possible high-level dungeon variants

Deterministic mapping from seed → variant

## **1.6 Seed Storage and Access**

The system shall store the seed globally for consistent access:

run_seed → stores the generated seed

variant_id → stores the selected variant

Example:
RUN_SEED = raw_seed
VARIANT_ID = RUN_SEED % TOTAL_SEED_VARIANTS

These values must be:

Initialized at run start

Accessible across all systems (room generation, spawning, AI logic)

## **1.7 Determinism Requirement**

For a given seed:

The same RUN_SEED must always produce:

The same VARIANT_ID

The same encounter structure (within defined bounds)

All randomness in the system must derive from:

RUN_SEED

Deterministic transformations of RUN_SEED

## **1.8 Scope of This Section**

This section defines:
What a seed is
How it is generated
How many variants are allowed
How it is stored
The following are defined in later sections:
Room composition rules
Enemy spawn behavior
Encounter variation constraints

# 2. Seed-Controlled Room Composition Constraints

## 2.1 Safe Room Placement (Seed-Constrained)

### Overview

Each biome SHALL contain exactly **one SAFE room**.

The SAFE room placement is **partially constrained** and **partially seed-controlled**, but MUST always remain within predefined valid positions.

---

### Fixed Rules (Non-Negotiable)

The SAFE room SHALL:

- Appear exactly **once per biome**
- NOT appear as:
  - First room of biome
  - Last room of biome (mini-boss / final boss room)
- NOT override boss placement
- NOT alter total room count

These constraints are **independent of seed value** and MUST always be enforced.

---

### Allowed Placement Range

The SAFE room SHALL only appear in the **mid-region of the biome**.

#### For Biomes with 8 Rooms (Biome 1–3):

Allowed SAFE room indices:

- Room 3
- Room 4

#### For Biome with 6 Rooms (Biome 4):

Allowed SAFE room indices:

- Room 4 (second last before final boss)
- Room 5 (last before final boss)

---

### Seed-Controlled Selection

The seed SHALL deterministically select the SAFE room position from the allowed set:

| Seed Value | SAFE Room Position |
|-----------|-------------------|
| 0         | First valid midpoint position |
| 1         | Second valid midpoint position |
| 2         | Deterministic selection between allowed positions |

Example:

- Biome (8 rooms):
  - Seed 0 → Room 3
  - Seed 1 → Room 4
  - Seed 2 → Either Room 3 or 4 (deterministic via RNG)

- Biome (6 rooms):
  - Seed 0 → Room 4
  - Seed 1 → Room 5
  - Seed 2 → Either Room 4 or 5 (deterministic)

---

### Determinism Requirement

For a given:

- Seed value
- Biome index

The SAFE room position MUST always be:

- Reproducible
- Consistent across runs

---

### Design Rationale

This constraint ensures:

- Balanced pacing (recovery occurs mid-biome)
- Prevention of unfair late or early healing advantage
- Deterministic yet controlled variation
- Alignment with gameplay flow (pre-boss preparation)

---

### Summary

- SAFE room is **mandatory per biome**
- SAFE room is **mid-biome only**
- SAFE room position is **bounded + seed-controlled**
- SAFE room can NEVER:
  - Appear at start
  - Replace boss rooms
  - Break biome structure

## 2.2 Fixed Room Positions (Non-Seed Controlled)

### Overview

Certain room positions within the dungeon are **strictly fixed** and SHALL NOT be influenced by the seed under any circumstances.

These rooms define the **core structure and progression** of the dungeon and must remain invariant across all runs.

---

### Fixed Room Constraints

The system SHALL enforce the following rules:

#### 1. Start Room

- Room index **0** SHALL always be:
  - `START`
- This room SHALL:
  - Contain no enemies
  - Serve as the entry point for every run
- The START room is **completely independent of seed**

---

#### 2. Mini Boss Rooms (Biome 1–3)

- Each biome (1–3) SHALL contain exactly **one MINI_BOSS room**
- The MINI_BOSS room SHALL always be:
  - The **last room of the biome**

Example:
- Biome 1 → Room 7
- Biome 2 → Room 15
- Biome 3 → Room 23

- MINI_BOSS rooms:
  - Cannot be moved
  - Cannot be replaced
  - Cannot be influenced by seed

---

#### 3. Final Boss Room (Biome 4)

- The FINAL_BOSS room SHALL always be:
  - The **last room of the dungeon**

Example:
- Room 29 → FINAL_BOSS

- This room SHALL:
  - Contain only the final boss encounter
  - Follow fixed boss logic and phases
- Seed SHALL NOT:
  - Change its position
  - Alter its structure
  - Replace the boss

---

#### 4. Safe Room Count (Per Biome)

- Each biome SHALL contain exactly:
  - **1 SAFE room**

- This rule is **fixed and non-negotiable**

- The seed MAY:
  - Select its position within allowed bounds (defined in Section 2.1)

- The seed SHALL NOT:
  - Add additional SAFE rooms
  - Remove SAFE rooms

---

### Non-Seed Guarantees

The following properties are strictly invariant:

- Total number of rooms per biome
- Position of START room
- Position of MINI_BOSS rooms
- Position of FINAL_BOSS room
- Number of SAFE rooms per biome

---

### Determinism Requirement

All fixed rooms MUST remain identical across:

- All seed values (0, 1, 2)
- All runs
- All environments

---

### Design Rationale

This ensures:

- Stable dungeon structure
- Predictable progression checkpoints
- Proper pacing (start → build → boss)
- Compatibility with AI Director and testing

---

### Summary

- START room → always Room 0  
- MINI_BOSS → last room of Biome 1–3  
- FINAL_BOSS → last room of dungeon  
- SAFE rooms → exactly 1 per biome  
- Seed has **NO control** over these positions

## 2.3 Flexible Encounter Slots (Seed-Controlled)

### Overview

This section defines how the seed influences **non-fixed rooms** within each biome.  
Flexible encounter slots exclude START, SAFE, MINI_BOSS, and FINAL_BOSS rooms.

The seed SHALL deterministically assign encounter types (COMBAT / ELITE / AMBUSH) within predefined biome-specific bounds.

Each biome will be defined separately, specifying:
- total flexible slots
- allowed room type counts
- seed-based distribution rules

### 2.3.1 Biome 1 — Flexible Encounter Slot Distribution

#### Overview

Biome 1 consists of **8 rooms**, of which the following are fixed:

- Room 0 → START (fixed)
- Room 7 → MINI_BOSS (fixed)
- SAFE room → exactly 1 (Section 2.1)

This leaves **5 flexible encounter slots**.

---

#### Flexible Slot Composition (Fixed Counts)

The system SHALL enforce the following distribution in Biome 1:

| Room Type | Count | Control |
|----------|------|---------|
| COMBAT   | 3    | Seed-controlled placement |
| ELITE    | 1    | Seed-controlled placement |
| AMBUSH   | 1    | Seed-controlled placement |

Total flexible slots = 5

👉 These counts are **fixed** and MUST NOT change across seeds.

---

#### Flexible Slot Indices

Flexible slots exist at:

- Rooms: 1, 2, 3, 4, 5, 6  
- Excluding SAFE room position (seed-controlled from Section 2.1)

So effective flexible positions = 5 slots after SAFE placement

---

#### Seed-Controlled Ordering

The seed SHALL determine the **ordering of encounter types** within the flexible slots.

The system SHALL use **3 deterministic seed variants**:

---

### Seed = 0 (Baseline Implementation-Aligned)

This seed SHALL closely match the **current implementation behavior**.

Example composition:

COMBAT → COMBAT → SAFE → COMBAT → ELITE → AMBUSH


Characteristics:
- Gradual introduction of difficulty
- Elite appears later
- Ambush near end

---

### Seed = 1 (Slight Early Pressure)

The seed MAY shift difficulty slightly earlier while respecting bounds.

Example composition:

COMBAT → ELITE → SAFE → COMBAT → AMBUSH → COMBAT


Characteristics:
- Earlier elite encounter
- Maintains total counts
- No structural violation

---

### Seed = 2 (Late Spike)

The seed MAY push difficulty towards later slots.

Example composition:

COMBAT → COMBAT → SAFE → AMBUSH → ELITE → COMBAT


Characteristics:
- Easier early rooms
- Stronger late encounters
- Prepares for mini-boss

---

#### Allowed Variation Rules

The seed MAY:

- Permute COMBAT / ELITE / AMBUSH ordering
- Shift ELITE earlier or later
- Shift AMBUSH position
- Keep SAFE fixed within allowed positions

The seed SHALL NOT:

- Change total counts of each room type
- Introduce new room types
- Move MINI_BOSS or START
- Move SAFE outside allowed bounds
- Create consecutive ELITE overload (fairness constraint optional)

---

#### Determinism Requirement

Given:

SEED + BIOME_INDEX (1)


The system MUST produce:

- Same room ordering
- Same encounter distribution

across all runs.

---

#### Implementation Alignment

- Current implementation uses a fixed ordering:
  ['START', 'COMBAT', 'COMBAT', 'SAFE', 'COMBAT', 'ELITE', 'AMBUSH', 'MINI_BOSS']

- Seed-based variation SHALL:
  - Stay within this structure
  - Only reorder flexible encounters
  - Preserve counts and constraints

---

#### Summary

- Total flexible slots: 5  
- Distribution: 3 COMBAT, 1 ELITE, 1 AMBUSH  
- SAFE: exactly 1 (mid-position constrained)  
- Seed controls ordering ONLY  
- Implementation remains bounded and deterministic

### 2.3.2 Biome 2 — Flexible Encounter Slot Distribution

#### Overview

Biome 2 consists of **8 rooms**, of which the following are fixed:

- First room of biome → entry transition (from previous biome)
- Last room → MINI_BOSS (fixed)
- SAFE room → exactly 1 (Section 2.1)

This leaves **5 flexible encounter slots**.

---

#### Flexible Slot Composition (Bounded Counts)

Unlike Biome 1, Biome 2 allows **bounded variation in counts**.

The system SHALL enforce the following limits:

| Room Type | Allowed Count | Control |
|----------|--------------|---------|
| COMBAT   | Remaining (minimum 2) | Seed-controlled placement |
| ELITE    | 1–2          | Seed-controlled |
| AMBUSH   | 1–2          | Seed-controlled |

Total flexible slots = 5

👉 Exact composition SHALL be selected by seed within these bounds.

---

#### Flexible Slot Indices

Flexible slots exist at:

- Rooms within biome excluding:
  - SAFE room (seed-controlled position)
  - MINI_BOSS room (fixed)

Effective flexible positions = 5 slots

---

#### Seed-Controlled Composition + Ordering

The seed SHALL determine:

1. Exact count selection within allowed bounds  
2. Ordering of encounter types within flexible slots  

The system SHALL use **3 deterministic seed variants**:

---

### Seed = 0 (Balanced — Implementation-Aligned)

This seed SHALL closely reflect current implementation behavior.

Example composition:

COMBAT → COMBAT → SAFE → COMBAT → ELITE → AMBUSH


Counts:
- COMBAT: 3  
- ELITE: 1  
- AMBUSH: 1  

Characteristics:
- Smooth progression
- Introduction of stronger enemies (Heavy)
- Moderate difficulty increase from Biome 1

---

### Seed = 1 (Higher Aggression)

The seed MAY increase encounter intensity by raising ELITE presence.

Example composition:

COMBAT → ELITE → SAFE → COMBAT → ELITE → AMBUSH


Counts:
- COMBAT: 2  
- ELITE: 2  
- AMBUSH: 1  

Characteristics:
- More elite pressure
- Earlier difficulty spike
- Increased challenge pacing

---

### Seed = 2 (Ambush-Focused Variation)

The seed MAY emphasize ambush-based encounters.

Example composition:

COMBAT → AMBUSH → SAFE → COMBAT → ELITE → AMBUSH


Counts:
- COMBAT: 2  
- ELITE: 1  
- AMBUSH: 2  

Characteristics:
- More positional pressure
- Frequent ambush scenarios
- Higher unpredictability

---

#### Allowed Variation Rules

The seed MAY:

- Select ELITE count within 1–2  
- Select AMBUSH count within 1–2  
- Adjust COMBAT count accordingly  
- Permute ordering of all encounter types  

The seed SHALL NOT:

- Reduce COMBAT below 2  
- Exceed total flexible slots  
- Introduce unsupported room types  
- Move SAFE or MINI_BOSS  
- Break biome structure  

---

#### Determinism Requirement

Given:

SEED + BIOME_INDEX (2)


The system MUST produce:

- Same composition (counts)
- Same ordering

across all runs.

---

#### Implementation Alignment

- Current implementation example:
  ['COMBAT', 'COMBAT', 'AMBUSH', 'SAFE', 'COMBAT', 'ELITE', 'AMBUSH', 'MINI_BOSS']

- Observations:
  - COMBAT dominant
  - AMBUSH appears multiple times
  - ELITE limited

👉 Seed variation SHALL:
- Stay within observed bounds
- Not exceed tested difficulty limits
- Maintain fairness

---

#### Difficulty Scaling Note

Compared to Biome 1:

- Higher enemy counts per room
- Introduction of **Heavy enemies**
- Increased ELITE / AMBUSH frequency

---

#### Summary

- Total flexible slots: 5  
- Distribution: bounded (not fixed)  
- ELITE: 1–2  
- AMBUSH: 1–2  
- COMBAT: remaining (≥2)  
- SAFE: exactly 1  
- Seed controls:
  - counts (within bounds)
  - ordering  
- System remains deterministic and bounded

### 2.3.3 Biome 3 — Flexible Encounter Slot Distribution

#### Overview

Biome 3 consists of **8 rooms**, of which the following are fixed:

- First room of biome → entry transition
- Last room → MINI_BOSS (fixed)
- SAFE room → exactly 1 (Section 2.1)

This leaves **5 flexible encounter slots**.

---

#### Flexible Slot Composition (Bounded Counts)

Biome 3 increases difficulty by allowing **higher pressure and tighter bounds**.

The system SHALL enforce:

| Room Type | Allowed Count | Control |
|----------|--------------|---------|
| COMBAT   | 1–2          | Seed-controlled |
| ELITE    | 2            | Fixed (within flexible slots) |
| AMBUSH   | 1–2          | Seed-controlled |

Total flexible slots = 5

👉 ELITE count is increased and stabilized to enforce difficulty scaling.

---

#### Flexible Slot Indices

Flexible slots exist at:

- Rooms within biome excluding:
  - SAFE room (seed-controlled position)
  - MINI_BOSS room (fixed)

Effective flexible positions = 5 slots

---

#### Seed-Controlled Composition + Ordering

The seed SHALL determine:

1. AMBUSH count within allowed bounds  
2. COMBAT count accordingly  
3. Ordering of encounter types  

The system SHALL use **3 deterministic seed variants**:

---

### Seed = 0 (Balanced High Pressure)

Example composition:

COMBAT → ELITE → SAFE → COMBAT → ELITE → AMBUSH


Counts:
- COMBAT: 2  
- ELITE: 2  
- AMBUSH: 1  

Characteristics:
- Balanced but harder than Biome 2
- Elite consistently present
- Moderate ambush pressure

---

### Seed = 1 (Ambush-Heavy Pressure)

Example composition:

AMBUSH → ELITE → SAFE → COMBAT → ELITE → AMBUSH


Counts:
- COMBAT: 1  
- ELITE: 2  
- AMBUSH: 2  

Characteristics:
- High positional pressure
- Frequent ambush encounters
- Forces movement and awareness

---

### Seed = 2 (Elite-Cluster Late Spike)

Example composition:

COMBAT → AMBUSH → SAFE → ELITE → ELITE → COMBAT


Counts:
- COMBAT: 2  
- ELITE: 2  
- AMBUSH: 1  

Characteristics:
- Easier early rooms
- Strong elite clustering near end
- Prepares for mini-boss intensity

---

#### Allowed Variation Rules

The seed MAY:

- Select AMBUSH count within 1–2  
- Adjust COMBAT count within 1–2  
- Permute encounter ordering  
- Position ELITE earlier or later (but count fixed at 2)

The seed SHALL NOT:

- Reduce ELITE below 2  
- Exceed AMBUSH limit of 2  
- Introduce unsupported room types  
- Move SAFE or MINI_BOSS  
- Break biome structure  

---

#### Determinism Requirement

Given:

SEED + BIOME_INDEX (3)


The system MUST produce:

- Same composition (counts)
- Same ordering

across all runs.

---

#### Implementation Alignment

- Current implementation example:
  ['COMBAT', 'COMBAT', 'AMBUSH', 'COMBAT', 'ELITE', 'SAFE', 'COMBAT', 'MINI_BOSS']

- Observations:
  - Strong COMBAT presence
  - ELITE introduced late
  - AMBUSH present but limited

👉 Updated SRS ensures:
- Increased ELITE frequency (2 guaranteed)
- Better difficulty scaling
- Still compatible with implementation bounds

---

#### Difficulty Scaling Note

Compared to Biome 2:

- Introduction of **Ranged enemies**
- More elite-heavy encounters
- Higher encounter complexity (mixed enemy pressure)
- Increased ambush frequency

---

#### Summary

- Total flexible slots: 5  
- ELITE: fixed at 2  
- AMBUSH: 1–2  
- COMBAT: 1–2  
- SAFE: exactly 1  
- Seed controls:
  - composition within bounds
  - ordering  
- Higher difficulty than Biome 2, deterministic and bounded

### 2.3.4 Biome 4 — Flexible Encounter Slot Distribution

#### Overview

Biome 4 consists of **6 rooms**, of which the following are fixed:

- First room of biome → entry transition
- Last room → FINAL_BOSS (fixed)
- SAFE room → exactly 1 (Section 2.1)

This leaves **3 flexible encounter slots**.

---

#### Flexible Slot Composition (Bounded Counts)

Biome 4 represents **maximum difficulty**, but within strict limits due to reduced room count.

The system SHALL enforce:

| Room Type | Allowed Count | Control |
|----------|--------------|---------|
| COMBAT   | 0–1          | Seed-controlled |
| ELITE    | 1–2          | Seed-controlled |
| AMBUSH   | 1–2          | Seed-controlled |

Total flexible slots = 3

👉 At least **2 high-pressure encounters (ELITE / AMBUSH)** MUST exist.

---

#### Flexible Slot Indices

Flexible slots exist at:

- Rooms within biome excluding:
  - SAFE room (seed-controlled position)
  - FINAL_BOSS room (fixed)

Effective flexible positions = 3 slots

---

#### Seed-Controlled Composition + Ordering

The seed SHALL determine:

1. Exact distribution within bounds  
2. Ordering of encounter types  

The system SHALL use **3 deterministic seed variants**:

---

### Seed = 0 (Balanced Final Preparation)

Example composition:

COMBAT → SAFE → ELITE → AMBUSH → FINAL_BOSS


Counts:
- COMBAT: 1  
- ELITE: 1  
- AMBUSH: 1  

Characteristics:
- Balanced final preparation
- Gradual buildup to boss
- Moderate pressure

---

### Seed = 1 (High Elite Pressure)

Example composition:

ELITE → SAFE → ELITE → AMBUSH → FINAL_BOSS


Counts:
- COMBAT: 0  
- ELITE: 2  
- AMBUSH: 1  

Characteristics:
- Strong elite presence
- High damage pressure
- Forces precise play before boss

---

### Seed = 2 (Ambush + Chaos Pressure)

Example composition:

AMBUSH → SAFE → ELITE → AMBUSH → FINAL_BOSS


Counts:
- COMBAT: 0–1 (optional, depending on variant)
- ELITE: 1  
- AMBUSH: 2  

Characteristics:
- High positional chaos
- Frequent ambush pressure
- Unpredictable encounters before boss

---

#### Allowed Variation Rules

The seed MAY:

- Select ELITE count within 1–2  
- Select AMBUSH count within 1–2  
- Include COMBAT only if total slots allow  
- Permute ordering of encounters  

The seed SHALL NOT:

- Exceed total flexible slots (3)  
- Reduce ELITE + AMBUSH combined below 2  
- Introduce unsupported room types  
- Move SAFE or FINAL_BOSS  
- Alter boss room structure or logic  

---

#### Determinism Requirement

Given:

SEED + BIOME_INDEX (4)


The system MUST produce:

- Same composition (counts)
- Same ordering

across all runs.

---

#### Implementation Alignment

- Current implementation example:
  ['COMBAT', 'COMBAT', 'AMBUSH', 'ELITE', 'SAFE', 'FINAL_BOSS']

- Observations:
  - SAFE near end
  - Strong pre-boss pressure
  - Mix of combat + elite + ambush

👉 Updated SRS ensures:
- Tighter bounds (only 3 flexible slots)
- Higher elite/ambush density
- Consistent boss preparation flow

---

#### Difficulty Scaling Note

Compared to Biome 3:

- Fewer rooms but higher intensity
- Highest elite density
- Maximum ambush pressure
- Designed to prepare player for FINAL_BOSS

---

#### Summary

- Total flexible slots: 3  
- ELITE: 1–2  
- AMBUSH: 1–2  
- COMBAT: 0–1  
- SAFE: exactly 1  
- FINAL_BOSS: fixed  
- Seed controls:
  - composition within bounds
  - ordering  
- Highest difficulty, deterministic and bounded

# 3. Seed-Controlled Enemy Spawn Composition

## 3.1 Overview

This section defines how the seed influences **enemy spawn composition within encounters**, after room types have been determined.

The seed SHALL control:
- enemy type selection (within biome-allowed pool)
- enemy count within predefined bounds
- spawn pattern selection (spread / ambush / triangle)
- encounter intensity variation

The seed SHALL NOT control:
- boss identity or behavior
- phase-based boss mechanics
- allowed enemy archetypes per biome
- global spawn safety constraints

Each biome will be defined separately, specifying:
- allowed enemy pools
- spawn count ranges
- seed-based composition rules

## 3.2 Biome 1 — Seed-Controlled Enemy Spawn Composition

### Overview

This section defines how the seed influences **enemy spawn composition inside Biome 1 encounters** after room types have already been assigned.  
The seed may vary only the **enemy mix, spawn count within allowed bounds, spawn ordering, and formation realization**. The seed must not change room type legality, fixed rooms, boss identity, or any global spawn-safety rules. Biome 1 supports only **Swarm, Flanker, and Brute** for non-boss encounters, with allowed bounds of **COMBAT: 1–3**, **AMBUSH: 2–3**, **ELITE: 2–3**, **SAFE: 0**, and **MINI_BOSS: 1**. 

### Spawn Safety Rules (Invariant Across All Seeds)

The following rules SHALL remain unchanged for all seed values:

- Enemy spawn points must remain inside the playable room area.
- Enemy spawn points must not overlap blocked wall regions.
- Enemy spawn points must maintain required separation from player spawn.
- Enemy spawn points must maintain required separation from each other.
- Enemy spawn realization must remain deterministic for the same seed and room index.
- Enemy spawn points shall maintain a minimum distance of **128 pixels** from the player spawn location.
- Enemy spawn points shall maintain a minimum distance of **64 pixels** from each other at spawn time.
- Enemy spawn points shall not overlap hazard tiles.
- Enemy spawn selection shall use predefined anchor points (8–12 per room), and invalid anchors shall fall back in deterministic order. :contentReference[oaicite:1]{index=1}

### Biome 1 Allowed Enemy Pool

Supported non-boss enemy archetypes in Biome 1:

- Swarm
- Flanker
- Brute

The seed SHALL NOT introduce:

- Heavy
- Ranged
- Any unsupported archetype outside the Biome 1 pool. :contentReference[oaicite:2]{index=2}

### Biome 1 Room-Type Spawn Bounds

| Room Type  | Allowed Enemy Count | Allowed Enemy Types      | Elite Allowed | Allowed Spawn Patterns |
|-----------|---------------------|--------------------------|---------------|------------------------|
| COMBAT    | 1–3                 | Swarm, Flanker, Brute    | No            | Spread                 |
| AMBUSH    | 2–3                 | Swarm, Flanker, Brute    | No            | Ambush                 |
| ELITE     | 2–3                 | Swarm, Flanker, Brute    | Yes           | Triangle               |
| SAFE      | 0                   | None                     | No            | None                   |
| MINI_BOSS | 1                   | MiniBoss                 | No            | Single                 |

:contentReference[oaicite:3]{index=3}

### Current Implementation Reference

Current Biome 1 implementation already behaves as follows:

- Non-beginner **COMBAT** uses **Swarm + Flanker + Brute** with spread pattern and delays **0.0, 0.4, 0.8**.
- Non-beginner **AMBUSH** uses **Swarm + Flanker + Brute** with ambush pattern and delays **0.0, 0.4, 0.8**.
- Non-beginner **ELITE** uses **Swarm elite + Flanker elite + Brute elite** with triangle pattern and delays **0.0, 0.4, 0.8**.
- **MINI_BOSS** uses exactly one MiniBoss with single spawn and delay **2.0**.
- Ambush uses radius **200 px** in the current implementation. :contentReference[oaicite:4]{index=4}

### Seed Mapping for Biome 1 Spawn Composition

The system shall support exactly three seed variants for Biome 1 spawn composition:

- **Seed = 0**
- **Seed = 1**
- **Seed = 2**

These seed values SHALL NOT change the legal room-type bounds above.  
They SHALL only select among deterministic composition profiles inside those bounds.

---

### Seed = 0 (Baseline / Implementation-Aligned)

This profile SHALL remain closest to the current implementation.

#### COMBAT
- Enemy count: **3**
- Composition: **Swarm, Flanker, Brute**
- Pattern: **Spread**
- Spawn delays: **0.0, 0.4, 0.8**
- Telegraph: default

#### AMBUSH
- Enemy count: **3**
- Composition: **Swarm, Flanker, Brute**
- Pattern: **Ambush**
- Spawn delays: **0.0, 0.4, 0.8**
- Telegraph: default

#### ELITE
- Enemy count: **3**
- Composition: **Swarm elite, Flanker elite, Brute elite**
- Pattern: **Triangle**
- Spawn delays: **0.0, 0.4, 0.8**

#### SAFE
- Enemy count: **0**

#### MINI_BOSS
- Enemy count: **1**
- Composition: **MiniBoss**
- Pattern: **Single**
- Spawn delay: **2.0**

---

### Seed = 1 (Lighter Early Pressure Variant)

This profile SHALL keep the same enemy pool but slightly reduce early pressure while staying inside Biome 1 bounds.

#### COMBAT
- Enemy count: **2**
- Composition: **Swarm, Flanker**
- Pattern: **Spread**
- Spawn delays: **0.0, 0.4**

#### AMBUSH
- Enemy count: **2**
- Composition: **Swarm, Flanker**
- Pattern: **Ambush**
- Spawn delays: **0.0, 0.4**

#### ELITE
- Enemy count: **2**
- Composition: **Brute elite, Swarm**
- Pattern: **Triangle**
- Spawn delays: **0.0, 0.4**

#### SAFE
- Enemy count: **0**

#### MINI_BOSS
- Enemy count: **1**
- Composition: **MiniBoss**
- Pattern: **Single**
- Spawn delay: **2.0**

---

### Seed = 2 (Brute-Heavier Late Pressure Variant)

This profile SHALL keep Biome 1 legal bounds but push slightly stronger composition inside those limits.

#### COMBAT
- Enemy count: **3**
- Composition: **Swarm, Swarm, Flanker** or **Swarm, Flanker, Brute**
- Pattern: **Spread**
- Spawn delays: **0.0, 0.4, 0.8**

#### AMBUSH
- Enemy count: **2–3**
- Composition: **Swarm, Swarm** or **Swarm, Flanker, Brute**
- Pattern: **Ambush**
- Spawn delays: **0.0, 0.4, 0.8** when 3 enemies

#### ELITE
- Enemy count: **2–3**
- Composition: **Brute elite, Swarm** or **Swarm elite, Flanker elite, Brute elite**
- Pattern: **Triangle**
- Spawn delays: **0.0, 0.4, 0.8**

#### SAFE
- Enemy count: **0**

#### MINI_BOSS
- Enemy count: **1**
- Composition: **MiniBoss**
- Pattern: **Single**
- Spawn delay: **2.0**

---

### Seed-Controlled Elements (Biome 1)

Within Biome 1 bounds, the seed MAY control:

- exact enemy composition within the allowed pool
- enemy count within the allowed lower/upper bound
- spawn slot ordering
- spread / ambush / triangle realization
- final validated spawn positions

### Non-Seed Elements (Biome 1)

The seed SHALL NOT control:

- fixed room positions
- SAFE room enemy presence
- MINI_BOSS identity
- boss behavior or boss phases
- global spawn safety rules
- global hazard caps
- allowed enemy pool for Biome 1

### Determinism Requirement

For the same:

- seed value
- biome index
- room index
- room type

the system MUST produce the same:

- enemy composition
- enemy count
- spawn ordering
- formation realization
- final validated spawn positions. 

## 3.3 Biome 2 — Seed-Controlled Enemy Spawn Composition

### Overview

This section defines how the seed influences **enemy spawn composition inside Biome 2 encounters** after room types have been assigned.

Biome 2 introduces **higher difficulty and new enemy archetype (Heavy)** while maintaining deterministic and bounded variation.

The seed SHALL control:
- enemy composition within allowed pool
- enemy count within bounds
- spawn ordering and formation realization

The seed SHALL NOT:
- violate spawn safety rules
- introduce unsupported enemy types
- alter boss behavior or phase logic

---

### Spawn Safety Rules (Invariant Across All Seeds)

The following rules SHALL always be enforced:

- Enemy spawn points must remain inside playable area
- Must not overlap walls or blocked tiles
- Must maintain minimum distance from player spawn (≥ 128 px)
- Must maintain minimum distance between enemies (≥ 64 px)
- Must not spawn on hazard tiles
- Must use predefined anchor points with deterministic fallback
- Spawn realization MUST be deterministic per seed + room index

---

### Biome 2 Allowed Enemy Pool

Supported non-boss enemy archetypes:

- Swarm
- Flanker
- Brute
- Heavy

The seed SHALL NOT introduce:
- Ranged (only allowed starting Biome 3)
- Any unsupported archetype

---

### Biome 2 Room-Type Spawn Bounds

| Room Type  | Allowed Enemy Count | Allowed Enemy Types                | Elite Allowed | Pattern   |
|-----------|---------------------|------------------------------------|---------------|----------|
| COMBAT    | 3–4                 | Swarm, Flanker, Brute, Heavy       | No            | Spread   |
| AMBUSH    | 2–3                 | Swarm, Flanker, Brute, Heavy       | No            | Ambush   |
| ELITE     | 2–3                 | Swarm, Brute, Heavy                | Yes           | Triangle |
| SAFE      | 0                   | None                               | No            | None     |
| MINI_BOSS | 1 + optional adds   | MiniBoss2 + standard enemies       | No            | Mixed    |

---

### Current Implementation Reference

Observed behavior:

- COMBAT includes mixed enemies with Heavy introduction
- AMBUSH uses mixed composition with controlled radius spawn
- ELITE includes stronger units (Brute / Heavy elite)
- MINI_BOSS may include **scheduled adds (0–4)** depending on fight phase

👉 Compared to Biome 1:
- Enemy density increases
- Heavier units introduced
- Higher encounter pressure

---

### Seed Mapping for Biome 2 Spawn Composition

Supported seed variants:

- **Seed = 0**
- **Seed = 1**
- **Seed = 2**

Seed SHALL select composition within bounds — NOT exceed them.

---

### Seed = 0 (Balanced Implementation-Aligned)

#### COMBAT
- Enemy count: **3**
- Composition: **Swarm, Flanker, Brute**
- Pattern: **Spread**
- Spawn delays: **0.0, 0.4, 0.8**

#### AMBUSH
- Enemy count: **2–3**
- Composition: **Swarm, Flanker, Brute**
- Pattern: **Ambush**
- Spawn delays: **0.0, 0.4, 0.8**

#### ELITE
- Enemy count: **2**
- Composition: **Brute elite, Swarm**
- Pattern: **Triangle**
- Spawn delays: **0.0, 0.4**

#### MINI_BOSS
- Primary: **MiniBoss2**
- Adds: **0–2 optional**
- Add composition: **Swarm / Flanker**
- Spawn style: **Scheduled (not random)**

---

### Seed = 1 (Heavy-Focused Pressure)

#### COMBAT
- Enemy count: **3–4**
- Composition: **Swarm, Flanker, Heavy** or **Swarm, Brute, Heavy**
- Pattern: **Spread**
- Spawn delays: **0.0, 0.4, 0.8, 1.2 (if 4 enemies)**

#### AMBUSH
- Enemy count: **2–3**
- Composition: **Swarm, Heavy** or **Swarm, Flanker, Heavy**
- Pattern: **Ambush**

#### ELITE
- Enemy count: **2–3**
- Composition: **Heavy elite, Brute elite**
- Pattern: **Triangle**

#### MINI_BOSS
- Primary: **MiniBoss2**
- Adds: **2–4 scheduled**
- Add composition: **Swarm / Flanker / Brute**

---

### Seed = 2 (Mixed Ambush + Pressure Variant)

#### COMBAT
- Enemy count: **3**
- Composition: **Swarm, Swarm, Heavy** or **Flanker, Brute, Heavy**
- Pattern: **Spread**

#### AMBUSH
- Enemy count: **3**
- Composition: **Swarm, Flanker, Heavy**
- Pattern: **Ambush**
- Higher positional pressure

#### ELITE
- Enemy count: **2–3**
- Composition: **Brute elite, Heavy elite**
- Pattern: **Triangle**

#### MINI_BOSS
- Primary: **MiniBoss2**
- Adds: **1–3 scheduled**
- Add composition: **Mixed standard enemies**

---

### Seed-Controlled Elements (Biome 2)

The seed MAY control:

- enemy composition within allowed pool
- enemy count within bounds
- spawn ordering
- pattern realization (spread / ambush / triangle)
- add count within allowed range for mini boss

---

### Non-Seed Elements (Biome 2)

The seed SHALL NOT control:

- MINI_BOSS identity or behavior
- add spawn timing logic (only realization count)
- spawn safety constraints
- allowed enemy pool
- SAFE room enemy presence
- room type structure

---

### Determinism Requirement

Given:

SEED + BIOME_INDEX (2) + ROOM_INDEX


The system MUST produce identical:

- enemy composition
- spawn count
- spawn ordering
- formation realization
- add count (if applicable)

across all runs.

---

### Difficulty Scaling Note

Compared to Biome 1:

- Higher enemy density (3–4 vs 1–3)
- Introduction of **Heavy units**
- Stronger ELITE encounters
- First appearance of **multi-entity pressure**

---

### Summary

- New enemy: **Heavy introduced**
- COMBAT: 3–4 enemies
- AMBUSH: 2–3 enemies
- ELITE: 2–3 enemies
- MINI_BOSS: 1 + bounded adds
- Seed controls:
  - composition
  - count within bounds
  - ordering
- Fully deterministic and bounded

## 3.4 Biome 3 — Seed-Controlled Enemy Spawn Composition

### Overview

This section defines how the seed influences **enemy spawn composition inside Biome 3 encounters** after room types have already been assigned.

Biome 3 marks the transition to **high-pressure mixed encounters**. It introduces **Ranged enemies** into the standard encounter pool and increases encounter complexity through stronger combinations, higher counts, and mini-boss phase-based adds.

The seed SHALL control only:
- enemy composition within the legal Biome 3 pool
- enemy count within defined bounds
- spawn ordering
- formation realization

The seed SHALL NOT:
- violate spawn safety rules
- introduce unsupported enemy types
- alter mini-boss phase logic
- alter fixed boss identity or core behavior

---

### Spawn Safety Rules (Invariant Across All Seeds)

The following rules SHALL remain unchanged for all seed values:

- Enemy spawn points must remain inside the playable room area
- Enemy spawn points must not overlap blocked wall regions
- Enemy spawn points must maintain required separation from player spawn
- Enemy spawn points must maintain required separation from each other
- Enemy spawn points must not overlap invalid hazard or wall placements
- Spawn realization must remain deterministic for the same seed and room index

These rules are fixed and SHALL NOT be modified by seed-controlled variation.

---

### Biome 3 Allowed Enemy Pool

Supported non-boss enemy archetypes in Biome 3:

- Swarm
- Flanker
- Brute
- Heavy
- Ranged

The seed SHALL NOT introduce:
- any archetype outside the Biome 3 allowed pool

---

### Biome 3 Room-Type Spawn Bounds

| Room Type  | Allowed Enemy Count | Allowed Enemy Types                     | Elite Allowed | Allowed Spawn Patterns |
|-----------|---------------------|-----------------------------------------|---------------|------------------------|
| COMBAT    | 3–4                 | Swarm, Flanker, Brute, Heavy, Ranged    | No            | Spread                 |
| AMBUSH    | 3–4                 | Swarm, Flanker, Brute, Heavy, Ranged    | No            | Ambush                 |
| ELITE     | 2–3                 | Swarm, Brute, Heavy, Ranged             | Yes           | Triangle               |
| SAFE      | 0                   | None                                    | No            | None                   |
| MINI_BOSS | 1 primary boss + fixed phase-based adds | Biome3MiniBoss primary; Swarm/Flanker adds | No | Single for boss; ring adds |

---

### Current Implementation Reference

Current Biome 3 implementation shows:

- **COMBAT** commonly using 3–4 enemies with mixed pressure
- **Ranged** introduced as a standard encounter enemy
- **AMBUSH** using 3-enemy pressure with ambush formation
- **ELITE** using strong mixed compositions such as Brute elite + Ranged elite + Swarm
- **MINI_BOSS** using `Biome3MiniBoss` with fixed phase-based adds:
  - 2 Swarm
  - 1 Flanker

Observed implementation examples include:
- COMBAT: Swarm + Flanker + Ranged
- COMBAT: Flanker + Ranged + Brute
- COMBAT: Brute + Ranged + Heavy
- COMBAT: Swarm + Flanker + Ranged + Heavy
- AMBUSH: Swarm + Flanker + Ranged
- ELITE: Brute elite + Ranged elite + Swarm non-elite :contentReference[oaicite:0]{index=0}

---

### Seed Mapping for Biome 3 Spawn Composition

The system shall support exactly three seed variants for Biome 3 spawn composition:

- **Seed = 0**
- **Seed = 1**
- **Seed = 2**

These variants SHALL remain within Biome 3 legal bounds and SHALL preserve the intended increase in difficulty from Biome 2.

---

### Seed = 0 (Balanced High-Pressure Variant)

This profile SHALL remain closest to the current implementation while keeping pressure evenly distributed.

#### COMBAT
- Enemy count: **4**
- Composition examples:
  - **Swarm, Flanker, Ranged, Brute**
  - **Swarm, Flanker, Ranged, Heavy**
- Pattern: **Spread**
- Spawn delays: **0.0, 0.4, 0.8, 1.2**

#### AMBUSH
- Enemy count: **3**
- Composition:
  - **Swarm, Flanker, Ranged**
- Pattern: **Ambush**
- Spawn delays: **0.0, 0.4, 0.8**
- Telegraph: longer ambush telegraph allowed

#### ELITE
- Enemy count: **3**
- Composition:
  - **Brute elite, Ranged elite, Swarm**
- Pattern: **Triangle**
- Spawn delays: **0.0, 0.4, 0.8**

#### SAFE
- Enemy count: **0**

#### MINI_BOSS
- Primary:
  - **Biome3MiniBoss**
- Adds:
  - **2 Swarm + 1 Flanker**
- Add behavior:
  - fixed phase-based ring spawn
- Seed control:
  - boss spawn realization only, not phase-add logic

---

### Seed = 1 (Ranged/Pressure-Focused Variant)

This profile SHALL increase ranged pressure and force stronger positional play.

#### COMBAT
- Enemy count: **4**
- Composition examples:
  - **Flanker, Ranged, Brute, Heavy**
  - **Swarm, Ranged, Brute, Heavy**
- Pattern: **Spread**
- Spawn delays: **0.0, 0.4, 0.8, 1.2**

#### AMBUSH
- Enemy count: **3–4**
- Composition examples:
  - **Swarm, Flanker, Ranged**
  - **Swarm, Flanker, Ranged, Heavy**
- Pattern: **Ambush**

#### ELITE
- Enemy count: **3**
- Composition:
  - **Brute elite, Ranged elite, Heavy**
  - or **Brute elite, Ranged elite, Swarm**
- Pattern: **Triangle**

#### SAFE
- Enemy count: **0**

#### MINI_BOSS
- Primary:
  - **Biome3MiniBoss**
- Adds:
  - fixed phase-based adds only
- Seed SHALL NOT change:
  - add identities
  - add count
  - add trigger condition

---

### Seed = 2 (Heavy/Elite Pressure Variant)

This profile SHALL shift Biome 3 toward heavier late-room pressure while preserving fairness.

#### COMBAT
- Enemy count: **3–4**
- Composition examples:
  - **Brute, Ranged, Heavy**
  - **Swarm, Ranged, Heavy, Flanker**
- Pattern: **Spread**

#### AMBUSH
- Enemy count: **3**
- Composition examples:
  - **Swarm, Ranged, Heavy**
  - **Flanker, Ranged, Heavy**
- Pattern: **Ambush**

#### ELITE
- Enemy count: **3**
- Composition:
  - **Brute elite, Heavy elite, Ranged**
  - or **Brute elite, Ranged elite, Swarm**
- Pattern: **Triangle**

#### SAFE
- Enemy count: **0**

#### MINI_BOSS
- Primary:
  - **Biome3MiniBoss**
- Adds:
  - fixed phase-based ring adds
- Seed control:
  - none beyond valid deterministic spawn realization

---

### Seed-Controlled Elements (Biome 3)

Within Biome 3 bounds, the seed MAY control:

- exact enemy composition within the allowed pool
- enemy count within the allowed lower/upper bounds
- spawn slot ordering
- spread / ambush / triangle realization
- final validated spawn positions

---

### Non-Seed Elements (Biome 3)

The seed SHALL NOT control:

- mini-boss identity
- mini-boss phase structure
- phase-change trigger
- phase-add identities and fixed count
- safe room enemy presence
- allowed Biome 3 enemy pool
- global spawn safety constraints

---

### Determinism Requirement

For the same:

- seed value
- biome index
- room index
- room type

the system MUST produce the same:

- enemy composition
- enemy count
- spawn ordering
- formation realization
- final validated spawn positions

across all runs.

---

### Difficulty Scaling Note

Compared to Biome 2, Biome 3 increases difficulty by:

- introducing **Ranged** as a standard encounter enemy
- increasing mixed-pressure encounters
- making COMBAT rooms consistently denser
- adding a stronger mini-boss with **phase-based adds**
- increasing positional and projectile pressure

---

### Summary

- New standard pressure source: **Ranged**
- COMBAT: **3–4**
- AMBUSH: **3–4**
- ELITE: **2–3**
- MINI_BOSS: **Biome3MiniBoss + fixed phase-based adds**
- Seed controls:
  - composition within bounds
  - count within bounds
  - ordering
  - formation realization
- System remains deterministic, bounded, and harder than Biome 2

## 3.5 Biome 4 — Seed-Controlled Enemy Spawn Composition

### Overview

This section defines how the seed influences **enemy spawn composition inside Biome 4 encounters** after room types have been assigned.

Biome 4 represents the **final difficulty stage** and leads directly into the **FINAL_BOSS encounter**.

The seed SHALL control only:
- enemy composition within allowed pool
- enemy count within strict bounds
- spawn ordering and formation realization

The seed SHALL NOT:
- modify FINAL_BOSS behavior or phases
- introduce unsupported enemy types
- violate spawn safety rules
- alter boss encounter structure

---

### Spawn Safety Rules (Invariant Across All Seeds)

The following rules SHALL always be enforced:

- Enemy spawn points must remain inside playable area
- Must not overlap walls or blocked tiles
- Must maintain minimum distance from player spawn (≥ 128 px)
- Must maintain minimum distance between enemies (≥ 64 px)
- Must not spawn on invalid hazard tiles
- Must use predefined anchor points with deterministic fallback
- Spawn realization MUST be deterministic per seed + room index

---

### Biome 4 Allowed Enemy Pool

Supported non-boss enemy archetypes:

- Swarm
- Flanker
- Brute
- Heavy
- Ranged

The seed SHALL NOT introduce:
- any unsupported archetype outside this pool

---

### Biome 4 Room-Type Spawn Bounds

| Room Type   | Allowed Enemy Count | Allowed Enemy Types                     | Elite Allowed | Pattern   |
|------------|---------------------|-----------------------------------------|---------------|----------|
| COMBAT     | 3–4                 | All types                               | No            | Spread   |
| AMBUSH     | 3–4                 | All types                               | No            | Ambush   |
| ELITE      | 2–3                 | Brute, Heavy, Ranged, Swarm             | Yes           | Triangle |
| SAFE       | 0                   | None                                    | No            | None     |
| FINAL_BOSS | 1 + bounded adds    | FinalBoss + controlled adds (if defined) | No            | Fixed    |

---

### Current Implementation Reference

Current Biome 4 implementation shows:

- High-density COMBAT and AMBUSH encounters
- Strong ELITE combinations (Brute / Heavy / Ranged)
- SAFE room placed near end of biome
- FINAL_BOSS:
  - fixed multi-phase behavior
  - teleport, fireball, meteor, lava attacks
  - revive logic
  - boss logic is fully scripted and deterministic

👉 Boss behavior is **NOT seed-controlled**

---

### Seed Mapping for Biome 4 Spawn Composition

Supported seed variants:

- **Seed = 0**
- **Seed = 1**
- **Seed = 2**

Seed SHALL only vary composition within strict bounds.

---

### Seed = 0 (Balanced Final Preparation)

#### COMBAT
- Enemy count: **3**
- Composition examples:
  - **Swarm, Flanker, Ranged**
  - **Swarm, Brute, Heavy**
- Pattern: **Spread**
- Spawn delays: **0.0, 0.4, 0.8**

#### AMBUSH
- Enemy count: **3**
- Composition:
  - **Swarm, Flanker, Ranged**
- Pattern: **Ambush**

#### ELITE
- Enemy count: **2**
- Composition:
  - **Brute elite, Ranged elite**
- Pattern: **Triangle**

#### SAFE
- Enemy count: **0**

#### FINAL_BOSS
- Primary:
  - **FinalBoss**
- Adds:
  - **Only if defined in boss logic**
- Seed control:
  - NONE on boss behavior or phases

---

### Seed = 1 (Elite-Heavy Pressure Variant)

#### COMBAT
- Enemy count: **3–4**
- Composition examples:
  - **Flanker, Ranged, Heavy**
  - **Swarm, Brute, Heavy, Ranged**
- Pattern: **Spread**

#### AMBUSH
- Enemy count: **3–4**
- Composition:
  - **Swarm, Flanker, Ranged, Heavy**
- Pattern: **Ambush**

#### ELITE
- Enemy count: **3**
- Composition:
  - **Brute elite, Heavy elite, Ranged elite**
- Pattern: **Triangle**

#### SAFE
- Enemy count: **0**

#### FINAL_BOSS
- Primary:
  - **FinalBoss**
- Adds:
  - Only as defined in boss logic
- Seed SHALL NOT modify:
  - boss phases
  - revive logic
  - attack cycles

---

### Seed = 2 (Ambush + Chaos Pressure Variant)

#### COMBAT
- Enemy count: **3**
- Composition:
  - **Swarm, Ranged, Heavy**
- Pattern: **Spread**

#### AMBUSH
- Enemy count: **4**
- Composition:
  - **Swarm, Flanker, Ranged, Heavy**
- Pattern: **Ambush**
- Highest positional pressure

#### ELITE
- Enemy count: **2–3**
- Composition:
  - **Brute elite, Heavy elite**
  - or **Brute elite, Ranged elite, Swarm**
- Pattern: **Triangle**

#### SAFE
- Enemy count: **0**

#### FINAL_BOSS
- Primary:
  - **FinalBoss**
- Adds:
  - strictly controlled by boss system
- Seed control:
  - NONE beyond deterministic spawn validation

---

### Seed-Controlled Elements (Biome 4)

The seed MAY control:

- enemy composition within allowed pool
- enemy count within bounds
- spawn ordering
- formation realization
- encounter intensity within limits

---

### Non-Seed Elements (Biome 4)

The seed SHALL NOT control:

- FINAL_BOSS identity or behavior
- boss phase transitions
- boss revive mechanics
- boss attack patterns (fireball, meteor, lava)
- SAFE room enemy presence
- spawn safety rules
- allowed enemy pool

---

### Determinism Requirement

Given:

SEED + BIOME_INDEX (4) + ROOM_INDEX


The system MUST produce identical:

- enemy composition
- spawn count
- spawn ordering
- formation realization

across all runs.

---

### Difficulty Scaling Note

Compared to Biome 3:

- Highest encounter intensity
- Maximum elite density
- Strongest ambush pressure
- Final preparation before boss fight

---

### Summary

- COMBAT: **3–4 enemies**
- AMBUSH: **3–4 enemies**
- ELITE: **2–3 enemies**
- SAFE: **0 enemies**
- FINAL_BOSS: **fully scripted (no seed control)**
- Seed controls:
  - composition within bounds
  - count within bounds
  - ordering
- System is deterministic, bounded, and final-stage difficulty