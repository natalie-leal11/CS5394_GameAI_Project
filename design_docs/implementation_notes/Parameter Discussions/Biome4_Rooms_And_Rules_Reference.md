# Biome 4 - Rooms, Enemies, Spawn Rules & Healing (Complete Reference)

This document lists **every room**, what is implemented in each, enemy types, spawn rules, safe room behavior, and all healing values. Use it as the single refrence for Biome 4 content.

---

## Room order (Biome 4, rooms: 24-29)

When **BEGINNER_TEST_MODE = True** (fixed order):

| Room index | Room type   | Name / description         |
|-----------:|-------------|----------------------------|
| **24**      | COMBAT      | Combat 1                   |
| **25**      | ELITE      | Elite 1 2                   |
| **26**     | AMBUSH      | Ambush 1                   |
| **27**     | ELITE        | Elite 2 room                  |
| **28**     | SAFE      | Safe 3                   |                 |
| **29**     | MINI_BOSS   | Final Boss (end of biome)   |

---

## Wall border thickness (B)

- **B = 2 tiles:** COMBAT, SAFE, ELITE, MINI_BOSS.
- **B = 4 tiles:** AMBUSH only.

Playable tile bounds: rows `[B .. rows - B - 1]`, cols `[B .cols - B - 1]`.

---

## Room 24 - Combat 

- **Type:** COMBAT
- **Wall border:** B = 2
- **Hazards:** Lava/slow possible in playable area (center 3x3 safe, door zones excluded).
- **Doors:** Start **CLOSED**; open after all enemies dead
+ **door unlock delay** (see below).
- **Enemies(BEGINNER_TEST_MODE):**
    - Brute at 0.0s
    - Heavy at 0.4s
    - Brute at 0.8s
- **Spawn pattern:** Spread.
- **Heal drop on clear:** 15% chance, 20% base_max_hp (capped at 100%).
- **Transition:** Overlap exit -> room 25.

--- 
Room 25 - Elite 1 **EDIT**

- **Type:** ELITE
- **Wall border:** B = 2
- **Doors:** CLOSED until clear + delay.
- **Enemies (BEGINNER_TEST_MODE):**
    - 2x Heavy (elite) at 0.0 s
    - 2x Flanker (elite) at 0.4 s
- **Spawn pattern:** **Triangle**
(elite-appropriate spacing).
- **Spacing:** **MIN_DISTANCE_BETWEEN_ENEMIES_PX + ELITE_EXTRA_SPACING_PX** (90 + 60 = 150 px when elite).  
- **Heal drop on clear:** 15% chance, 40% base_max_hp (capped at 100%).  
- **Transition:** Overlap exit → room 26.

---

Room 26 - Ambush

-- **Type:** AMBUSH  
- **Wall border:** **B = 4** (thick walls).  
- **Doors:** CLOSED until clear + delay; **doorway carved 2 cols × B rows** at bottom (inner-face).  
- **Enemies (BEGINNER_TEST_MODE):**
  - 4x Flanker with 1.5 s telegraph 
- **Spawn pattern:** **Ambush** (ring / tight pattern).  
- **Heal drop on clear:** 15% chance, 30% base_max_hp (capped at 100%).  
- **Transition:** Overlap exit trigger (positioned at playable inner edge) → room 27.

---

Room 27 - Elite 2 **EDIT**

- **Type:** ELITE
- **Wall border:** B = 2
- **Doors:** CLOSED until clear + delay.
- **Enemies (BEGINNER_TEST_MODE):**
    - 2x Heavy (elite) at 0.0 s
    - 2x Flanker (elite) at 0.4 s
- **Spawn pattern:** **Triangle**
(elite-appropriate spacing).
- **Spacing:** **MIN_DISTANCE_BETWEEN_ENEMIES_PX + ELITE_EXTRA_SPACING_PX** (90 + 60 = 150 px when elite).  
- **Heal drop on clear:** 15% chance, 40% base_max_hp (capped at 100%).  
- **Transition:** Overlap exit → room 28.

---

Room 28 - Safe

- **Type:** SAFE  
- **Wall border:** B = 2  
- **Hazards:** No lava; optional minimal slow.  
- **Doors:** **OPEN** immediately (no combat lock).  
- **Enemies:** None.  
- **Contents:**
  - **Heal pickup** (one per visit):
    - Asset: `assets/tiles/powerups/heal_health_32x32.png` (displayed at 70×70).
    - Position: one corner of playable (e.g. top-left, ≥2 tiles from wall).
    - Prompt when close: **“Press [H] to gain Health Upgrade (+30%)”**  
- **Heal behavior (Safe Room pickup):**
  - **Amount:** `heal_amount = base_max_hp * 0.30` (30%).  
  - **Overheal:** Allowed; **cap = base_max_hp * 1.30** (150%).  
  - **Formula:** `current_hp = min(current_hp + heal_amount, cap)` (cap = 130% of base).  
  - **Limit:** Usable **once per room visit**; then object dims / becomes inactive.  
- **Heal drop on clear:** No (SAFE excluded).  
- **Transition:** Overlap exit → room 29.

---

Room 29 - Final Boss **EDIT**

---

## Door unlock delay (combat rooms)

- **Config:** `DOOR_UNLOCK_DELAY_SEC = 0.5` (room clear → doors open after 0.5 s).
- **Mini Boss:** `FINAL_BOSS_DOOR_UNLOCK_DELAY_SEC = 0.5` (after dealth, 0.5s then exit opens).
- **Safe room:** Doors open immediately.

---

## Spawn rules (global)

- **Min distance from player:** **90 px** (MIN_DISTANCE_FROM_PLAYER_PX).  
- **Min tiles from wall:** **3** (MIN_TILES_FROM_WALL).  
- **Min tiles from door:** **3** (MIN_TILES_FROM_DOOR).  
- **Min distance between enemies:** **90 px** (MIN_DISTANCE_BETWEEN_ENEMIES_PX).  
- **Elite extra spacing:** **+60 px** (ELITE_EXTRA_SPACING_PX).  
- **No spawn in corners;** no spawn in door tiles or within 3 tiles of doors.  
- **Spawn slot delay:** **0.4 s** (SPAWN_SLOT_DELAY_SEC) between slots (except Final Boss 2.5 s).

--- 

Enemy types (Biome 4) **EDIT**

| Type       | Class     | Base HP | Base damage | Size (px) | Notes                    |
|-----------|-----------|---------|-------------|-----------|---------------------------|
| Swarm     | Swarm     | 30      | 10          | 60×60     | Melee Grunt               |
| Flanker   | Flanker   | 22      | 8           | 48×48     | Fast Flanker              |
| Brute     | Brute     | 50      | 14          | 80×80     | Heavy Brute               |
| Heavy     | Heavy     | 60      | 16          | 88x88     | Heavy Armored
| Mini Boss | MiniBoss  | (config)| (config)    | 96×96     | Single per room 7         |

Elite modifier: HP ×1.8, damage ×1.5.

---

# Healing summary

| Source              | When / where                    | Amount              | Cap / overheal              |
|---------------------|----------------------------------|---------------------|-----------------------------|
| **Safe Room [H]**   | Press H near heal object (room 28)| +50% base_max_hp    | 150% base (overheal allowed)|
| **Heal drop**       | 15% on combat/elite/ambush clear | +20% base_max_hp on combat, +30% base_max_hp on ambush, +40% base_max_hp on elite  | 100% base (no overheal)      |

- **Safe Room:** `SAFE_ROOM_HEAL_PERCENT = 0.30`, `SAFE_ROOM_OVERHEAL_CAP_RATIO = 1.50`; once per visit.  
- **Heal drop:** `HEAL_DROP_CHANCE = 0.15`; not in START or SAFE.  

---

## Spawn pattern summary

| Room type   | Pattern   | Notes                          |
|-------------|-----------|---------------------------------|
| SAFE        | —        | No enemies                      |
| COMBAT      | Spread    | Default spread positions        |
| ELITE       | Triangle  | Elite spacing (+60 px)          |
| AMBUSH      | Ambush    | Ring / tight, telegraph optional|
| FINAL_BOSS   | Single    | One central spawn               |

---

## Quick reference constants

- **TILE_SIZE:** 32 px  
- **Room grid:** cols = screen_width // 32, rows = screen_height // 32  
- **PLAYER_SIZE:** 96×96  
- **Door sprite:** 96×96; trigger = door_rect.inflate(-20, -20)  
- **Door unlock (normal):** DOOR_UNLOCK_DELAY_SEC = 0.5 s  
- **Mini Boss door unlock:** MINI_BOSS_DOOR_UNLOCK_DELAY_SEC = 0.5 s  
- **SPAWN_SLOT_DELAY_SEC:** 0.4 s  
- **HEAL_DROP_CHANCE:** 0.15  
- **SAFE_ROOM_HEAL_PERCENT:** 0.30  
- **SAFE_ROOM_OVERHEAL_CAP_RATIO:** 1.50   

This is the full list of what each room is, what is implemented in it, which enemies appear, spawn rules, safe room behavior, and all healing values for Biome 4.