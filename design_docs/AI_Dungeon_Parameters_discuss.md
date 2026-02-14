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

---

## 8) Key Guarantees

- Same seed ⇒ same dungeon plan and room layouts (pre-game generation)
- AI Director decisions are deterministic (pure rule-based)
- Difficulty adjustments always remain within predefined bounds
- No unwinnable runs due to hazard placement or blocked progression
