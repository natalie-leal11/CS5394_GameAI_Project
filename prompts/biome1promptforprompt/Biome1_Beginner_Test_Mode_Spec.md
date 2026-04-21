# BIOME 1 — BEGINNER TEST MODE SPEC

*(Deterministic + Reduced Difficulty for First-Time Playtesting)*

---

## 1. Purpose

This mode is designed for:

- First-time playtesting  
- Debugging combat feel  
- Observing AI behavior clearly  
- Verifying room flow  
- Reducing overwhelm  

This is **NOT final balance**.  
This is a **temporary beginner-friendly configuration**.

---

## 2. Disable Systems (Testing Mode Only)

The following must be disabled:

- Seed-based room shuffling  
- Seed-based composition selection  
- RL tuning  
- Procedural hazard randomness  
- Composition swapping  
- Reinforcement waves  
- Boss adds  

Biome 1 must run **deterministically**.

---

## 3. Tile System (Locked)

- Tile size = **32 × 32 px**  
- All rooms use tile grid  
- Coordinates format: `(row, col)`  
- Rows increase **top → bottom**  
- Columns increase **left → right**  
- All objects align strictly to tile grid  

---

## 4. Fixed Biome 1 Room Order (Total = 8 Rooms)

| Room Index | Room Type         |
|-----------|------------------|
| 0         | Start Room        |
| 1         | Combat Room 1     |
| 2         | Combat Room 2     |
| 3         | Safe Room         |
| 4         | Combat Room 3     |
| 5         | Elite Room        |
| 6         | Ambush Room       |
| 7         | Mini Boss Room    |

**No variation allowed.**

---

## 5. Room Dimensions

| Room Type  | Size (Tiles) |
|------------|--------------|
| Start      | 16×16        |
| Combat     | 12×12        |
| Ambush     | 8×8          |
| Safe       | 12×12        |
| Elite      | 16×16        |
| Mini Boss  | 16×16        |

---

## 6. Global Enemy Spawn Rules

Enemies must:

- Spawn ≥ 4 tiles from player spawn  
- Spawn ≥ 2 tiles from other enemies  
- Spawn only on predefined anchor tiles  
- Not spawn inside safe zones  
- Not spawn on hazards  
- Not spawn on walls  
- Not block door tiles  
- Not block exit path  

---

## 7. Biome 1 Enemy Roster

Allowed enemies:

- Melee Grunt  
- Fast Flanker  
- Ranged Caster  
- Elite Guardian  
- Mini Boss: Biome 1 Guardian  

Restrictions:

- No summoning behavior  
- No reinforcement waves  
- No mini boss adds  

---

## 8. Beginner Enemy Composition Per Room

### Room 0 — Start Room
- No enemies  
- Optional Training Dummy only  

---

### Room 1 — Combat 1 (Very Easy)
- 2 × Melee Grunt  

**Purpose:**  
Introduce basic movement + spacing.

---

### Room 2 — Combat 2 (Light Mixed)
- 2 × Melee Grunt  
- 1 × Ranged Caster  

**Total:** 3 enemies  
No flanker yet.

---

### Room 3 — Safe Room
- No enemies  
- Fountain  
- Upgrade tiles  
- No enemy anchors active  

---

### Room 4 — Combat 3 (Introduce Speed Variation)
- 2 × Melee Grunt  
- 1 × Fast Flanker  

**Total:** 3 enemies  
First appearance of flanker.

---

### Room 5 — Elite Room (Simplified)
- 1 × Elite Guardian  
- 1 × Melee Grunt  

**Total:** 2 enemies  
No ranged support.

---

### Room 6 — Ambush Room (Gentle)
- Single-wave spawn after telegraph  
- 2 × Melee Grunt  

**Telegraph delay:** 1.5 seconds  

---

### Room 7 — Mini Boss
- 1 × Mini Boss  
- No adds  
- No reinforcements  

---

## 9. Anchor-Based Spawn System

Enemies spawn only at predefined anchor coordinates per room template.

### Example — Ambush Room (8×8)

**Anchors:**

(1,1), (1,6), (2,1), (2,6),
(5,1), (5,6), (6,2), (6,5)


**Player spawn:**

(6,3), (6,4)


**Safe zone:**
- Rows: 3–5  
- Cols: 2–4  

Enemies must **never spawn inside safe zone**.

---

## 10. Beginner Enemy Speed Adjustments

Assume **Player Base Speed = 100%**

| Enemy Type       | Speed            |
|-----------------|------------------|
| Melee Grunt     | 70% of player    |
| Fast Flanker    | 85% of player    |
| Ranged Caster   | 60% of player    |
| Elite Guardian  | 65% of player    |
| Mini Boss       | 75% of player    |

### Additional AI Timing Adjustments

- Melee reaction delay before chase = 0.4 sec  
- Ambush telegraph = 1.5 sec  
- Elite heavy wind-up = +0.2 sec  
- Mini boss heavy wind-up = +0.3 sec  

---

## 11. Behavior Radii (Reduced Pressure)

| Parameter                | Beginner Value |
|------------------------|----------------|
| Wake Radius            | 7 tiles        |
| Chase Radius           | 6 tiles        |
| Disengage Radius       | 8 tiles        |
| Min spawn from player  | 4 tiles        |
| Min spawn from enemy   | 2 tiles        |

Enemies disengage earlier to reduce pressure.

---

## 12. Hazard Rules (Beginner Friendly)

### Room caps:

| Hazard         | Allowed  |
|----------------|----------|
| Lava           | 0–3%     |
| Slow Terrain   | 5–8%     |
| Walls          | 10–15%   |
| Safe Area      | ≥ 75%    |

---

### Lava
- 6 HP per second  
- Dash prevents damage  
- Never blocks spawn tile  
- Never blocks exit tile  

---

### Slow Terrain
- -25% movement speed  
- Affects player and enemies  
- Dash not affected  

---

## 13. Summary

This configuration ensures:

- Low enemy count  
- Slower enemies  
- Longer reaction windows  
- Clear spacing  
- Stable deterministic behavior  
- Ideal debugging environment  