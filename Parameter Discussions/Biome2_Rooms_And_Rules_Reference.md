# Biome 2 - Rooms, Enemies, Spawn Rules & Healing (Complete Reference)

This document lists **every room**, what is implemented in each, enemy types, spawn rules, safe room behaviorr, and all healing values. Use it as the single reference for Biome 2 content.

---

## Room order (Biome 2, 8 rooms: 8-15)

When **BEGINNER_TEST_MODE = True** (fixed order):

| Room index | Room type   | Name / description         |
|-----------:|-------------|----------------------------|
| **8**      | COMBAT      | Combat 1                   |
| **9**      | COMBAT      | Combat 2                   |
| **10**     | AMBUSH      | Ambush 1                   |
| **11**     | SAFE        | Safe room                  |
| **12**     | COMBAT      | Combat 3                   |
| **13**     | ELITE       | Elite room                 |
| **14**     | AMBUSH      | Ambush 2                   |
| **15**     | MINI_BOSS   | Mini Boss (end of biome)   |

When **BEGINNER_TEST_MODE = False**: order is shuffled **[COMBAT, COMBAT, COMBAT, AMBUSH, AMBUSH, SAFE, ELITE]** + **MINI_BOSS** (seed-based).

---

## Wall border thickness (B)

- **B = 2 tiles:** COMBAT, SAFE, ELITE, MINI_BOSS.
- **B = 4 tiles:** AMBUSH only.

Playable tile bounds: rows `[B .. rows - B - 1]`, cols `[B .cols - B - 1]`.

---

## Room 8 - Combat 1

- **Type:** COMBAT
- **Wall border:** B = 2
- **Hazards:** Lava/slow possible in playable area (center 3x3 safe, door zones excluded).
- **Doors:** Start **CLOSED**; open after all enemies dead
+ **door unlock delay** (see below).
- **Enemies(BEGINNER_TEST_MODE):**
    - Swarm at 0.0s
    - Flanker at 0.4s
    - Brute at 0.8s
- **Spawn pattern:** Spread.
- **Heal drop on clear:** 25% chance, 30% base_max_hp (capped at 100%).
- **Transition:** Overlap exit -> room 9.

---

## Room 9 - Combat 2

- **Type:** COMBAT
- **Wall border:** B = 2
- **Doors:** CLOSED until clear + delay.
- **Enemies(BEGINNER_TEST_MODE):**
    - Flanker at 0.0s
    - Brute at 0.4s
    - Heavy at 0.8s
- **Spawn pattern:** Spread.
- **Heal drop on clear:** 25% chance, 30% base_max_hp (capped at 100%).
- **Transition:** Overlap exit -> room 10.

---

## Room 10 - Ambush 1

- **Type:** AMBUSH  
- **Wall border:** **B = 4** (thick walls).  
- **Doors:** CLOSED until clear + delay; **doorway carved 2 cols × B rows** at bottom (inner-face).  
- **Enemies (BEGINNER_TEST_MODE):**
  - 1× **Swarm** + 1x **Flanker**, both with 1.5 s telegraph.  
- **Spawn pattern:** **Ambush** (ring / tight pattern).  
- **Heal drop on clear:** 25% chance, 30% base_max_hp (capped at 100%).  
- **Transition:** Overlap exit trigger (positioned at playable inner edge) → room 11.

---

## Room 11 - Safe Room

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
  - **Overheal:** Allowed; **cap = base_max_hp * 1.30** (130%).  
  - **Formula:** `current_hp = min(current_hp + heal_amount, cap)` (cap = 130% of base).  
  - **Limit:** Usable **once per room visit**; then object dims / becomes inactive.  
- **Heal drop on clear:** No (SAFE excluded).  
- **Transition:** Overlap exit → room 12.

---

## Room 12 - Combat 3

- **Type:** COMBAT  
- **Wall border:** B = 2  
- **Doors:** CLOSED until clear + delay.  
- **Enemies (BEGINNER_TEST_MODE):**
  - Swarm at 0.0 s  
  - Brute at 0.4 s  
  - Brute at 0.8 s  
  - Heavy at 1.2 s
- **Spawn pattern:** Spread.  
- **Heal drop on clear:** 25% chance, 30% base_max_hp (capped at 100%).  
- **Transition:** Overlap exit → room 13.

---

## Room 13 - Elite Room

- **Type:** ELITE  
- **Wall border:** B = 2  
- **Doors:** CLOSED until clear + delay.  
- **Enemies (BEGINNER_TEST_MODE):**
  - 1× **Brute** (elite) at 0.0 s  
  - 1× **Swarm** (elite) at 0.4 s 
  - 1x **Swarm** (non-elite) at 0.8 s 
- **Spawn pattern:** **Triangle** (elite-appropriate spacing).  
- **Spacing:** **MIN_DISTANCE_BETWEEN_ENEMIES_PX + ELITE_EXTRA_SPACING_PX** (90 + 60 = 150 px when elite).  
- **Heal drop on clear:** 25% chance, 30% base_max_hp (capped at 100%).  
- **Transition:** Overlap exit → room 14.

---

# Room 14 - Ambush 2

-- **Type:** AMBUSH  
- **Wall border:** **B = 4** (thick walls).  
- **Doors:** CLOSED until clear + delay; **doorway carved 2 cols × B rows** at bottom (inner-face).  
- **Enemies (BEGINNER_TEST_MODE):**
  - 1× **Swarm** + 1x **Flanker**, both with 1.5 s telegraph.  
- **Spawn pattern:** **Ambush** (ring / tight pattern).  
- **Heal drop on clear:** 25% chance, 30% base_max_hp (capped at 100%).  
- **Transition:** Overlap exit trigger (positioned at playable inner edge) → room 15.

---

# Room 15 - Mini Boss

- **Type:** MINI_BOSS  
- **Wall border:** B = 2  
- **Doors:** CLOSED until mini boss dead; then **MINI_BOSS_DOOR_UNLOCK_DELAY_SEC** (0.5 s) before exit opens.  
- **Enemies:**
  - 1× **Mini Boss** only, spawn at 2.0 s.  
- **Spawn pattern:** Single central position (no cluster).  
- **On Mini Boss death:**
  - **Reward drop** (heal pickup) at death position: collect by overlap.  
  - **Reward heal:** **30% of base_max_hp**, **capped at base_max_hp** (no overheal): `player.hp = min(base_max_hp, player.hp + base_max_hp * MINI_BOSS_REWARD_HEAL_PERCENT)`.  
- **No room 8:** Using exit returns to **main menu** (run complete).  
- **Transition:** Overlap exit → switch to start scene.

---

## Door unlock delay (combat rooms)

- **Config:** `DOOR_UNLOCK_DELAY_SEC = 0.5` (room clear → doors open after 0.5 s).
- **Mini Boss:** `MINI_BOSS_DOOR_UNLOCK_DELAY_SEC = 0.5` (after dealth, 0.5s then exit opens).
- **Safe room:** Doors open immediately.

---

## Spawn rules (global)

- **Min distance from player:** **150 px** (MIN_DISTANCE_FROM_PLAYER_PX).  
- **Min tiles from wall:** **3** (MIN_TILES_FROM_WALL).  
- **Min tiles from door:** **3** (MIN_TILES_FROM_DOOR).  
- **Min distance between enemies:** **90 px** (MIN_DISTANCE_BETWEEN_ENEMIES_PX).  
- **Elite extra spacing:** **+60 px** (ELITE_EXTRA_SPACING_PX).  
- **No spawn in corners;** no spawn in door tiles or within 3 tiles of doors.  
- **Spawn slot delay:** **0.4 s** (SPAWN_SLOT_DELAY_SEC) between slots (except Mini Boss 2.0 s).

--- 

Enemy types (Biome 2)

| Type       | Class     | Base HP | Base damage | Size (px) | Notes                    |
|-----------|-----------|---------|-------------|-----------|---------------------------|
| Swarm     | Swarm     | 30      | 10          | 60×60     | Melee Grunt               |
| Flanker   | Flanker   | 22      | 8           | 48×48     | Fast Flanker              |
| Brute     | Brute     | 50      | 14          | 80×80     | Heavy Brute               |
| Heavy     | Heavy     | 60      | 16          | 88x88     | Heavy Armored
| Mini Boss | MiniBoss  | (config)| (config)    | 96×96     | Single per room 7         |

Elite modifier: HP ×1.4, damage ×1.2.

---

## Healing summary

| Source              | When / where                    | Amount              | Cap / overheal              |
|---------------------|----------------------------------|---------------------|-----------------------------|
| **Safe Room [H]**   | Press H near heal object (room 3)| +30% base_max_hp    | 130% base (overheal allowed)|
| **Heal drop**       | 25% on combat/elite/ambush clear | +30% base_max_hp    | 100% base (no overheal)      |
| **Mini Boss reward**| Collect orb after killing boss   | +30% base_max_hp    | 100% base (no overheal)      |

- **Safe Room:** `SAFE_ROOM_HEAL_PERCENT = 0.30`, `SAFE_ROOM_OVERHEAL_CAP_RATIO = 1.30`; once per visit.  
- **Heal drop:** `HEAL_DROP_CHANCE = 0.25`; not in START or SAFE.  
- **Mini Boss reward:** `MINI_BOSS_REWARD_HEAL_PERCENT = 0.30`; capped at base_max_hp.

---

## Spawn pattern summary

| Room type   | Pattern   | Notes                          |
|-------------|-----------|---------------------------------|
| SAFE        | —        | No enemies                      |
| COMBAT      | Spread    | Default spread positions        |
| ELITE       | Triangle  | Elite spacing (+60 px)          |
| AMBUSH      | Ambush    | Ring / tight, telegraph optional|
| MINI_BOSS   | Single    | One central spawn               |

---

## Quick reference constants

- **TILE_SIZE:** 32 px  
- **Room grid:** cols = screen_width // 32, rows = screen_height // 32  
- **PLAYER_SIZE:** 96×96  
- **Door sprite:** 96×96; trigger = door_rect.inflate(-20, -20)  
- **Door unlock (normal):** DOOR_UNLOCK_DELAY_SEC = 0.5 s  
- **Mini Boss door unlock:** MINI_BOSS_DOOR_UNLOCK_DELAY_SEC = 0.5 s  
- **SPAWN_SLOT_DELAY_SEC:** 0.4 s  
- **HEAL_DROP_CHANCE:** 0.25  
- **SAFE_ROOM_HEAL_PERCENT:** 0.30  
- **SAFE_ROOM_OVERHEAL_CAP_RATIO:** 1.30  
- **MINI_BOSS_REWARD_HEAL_PERCENT:** 0.30  

This is the full list of what each room is, what is implemented in it, which enemies appear, spawn rules, safe room behavior, and all healing values for Biome 1.