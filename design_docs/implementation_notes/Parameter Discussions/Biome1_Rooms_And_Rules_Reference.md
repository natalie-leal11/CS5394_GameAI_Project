# Biome 1 — Rooms, Enemies, Spawn Rules & Healing (Complete Reference)

This document lists **every room**, what is implemented in each, enemy types, spawn rules, safe room behavior, and all healing values. Use it as the single reference for Biome 1 content.

---

## Room order (Biome 1, 8 rooms: 0–7)

When **BEGINNER_TEST_MODE = True** (fixed order):

| Room index | Room type   | Name / description        |
|-----------:|-------------|----------------------------|
| **0**      | START       | Training room              |
| **1**      | COMBAT      | Combat 1                    |
| **2**      | COMBAT      | Combat 2                    |
| **3**      | SAFE        | Safe room                  |
| **4**      | COMBAT      | Combat 3                    |
| **5**      | ELITE       | Elite room                 |
| **6**      | AMBUSH      | Ambush room                |
| **7**      | MINI_BOSS   | Mini Boss (end of biome)   |

When **BEGINNER_TEST_MODE = False**: order is **START** + shuffled **[COMBAT, COMBAT, COMBAT, SAFE, ELITE, AMBUSH]** + **MINI_BOSS** (seed-based).

---

## Wall border thickness (B)

- **B = 2 tiles:** START, COMBAT, SAFE, ELITE, MINI_BOSS  
- **B = 4 tiles:** AMBUSH only  

Playable tile bounds: rows `[B .. rows - B - 1]`, cols `[B .. cols - B - 1]`.

---

## Room 0 — Training / Start

- **Type:** START  
- **Wall border:** B = 2  
- **Hazards:** None (no lava, minimal/no slow)  
- **Doors:** Exit door **OPEN** by default (no combat lock).  
- **Contents:**
  - **Training dummy** (damageable, bottom-left of playable area, ≥2 tiles from wall).
  - **Altar / book pedestal** (center). Press **[E]** to read story; “Press [E] to Read” when near.  
- **Enemies:** None (no spawns).  
- **Spawn pattern:** N/A.  
- **Heal drop on clear:** No (START excluded).  
- **Transition:** Player overlaps exit door trigger → load room 1.

---

## Room 1 — Combat 1

- **Type:** COMBAT  
- **Wall border:** B = 2  
- **Hazards:** Lava/slow possible in playable area (center 3×3 safe, door zones excluded).  
- **Doors:** Start **CLOSED**; open after all enemies dead + **door unlock delay** (see below).  
- **Enemies (BEGINNER_TEST_MODE):**
  - 1× **Swarm** (Melee Grunt), non-elite, spawn at 0.0 s.  
- **Spawn pattern:** Spread (single enemy).  
- **Heal drop on clear:** 25% chance (HEAL_DROP_CHANCE); if rolled, **30% of base_max_hp** (capped at base_max_hp, no overheal).  
- **Transition:** After door open, overlap exit trigger → load room 2.

---

## Room 2 — Combat 2

- **Type:** COMBAT  
- **Wall border:** B = 2  
- **Doors:** CLOSED until clear + delay.  
- **Enemies (BEGINNER_TEST_MODE):**
  - Swarm at 0.0 s  
  - Swarm at 0.4 s (SPAWN_SLOT_DELAY_SEC)  
  - Flanker at 0.8 s  
- **Spawn pattern:** Spread.  
- **Heal drop on clear:** 25% chance, 30% base_max_hp (cap at 100%).  
- **Transition:** Overlap exit → room 3.

---

## Room 3 — Safe room

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
- **Transition:** Overlap exit → room 4.

---

## Room 4 — Combat 3

- **Type:** COMBAT  
- **Wall border:** B = 2  
- **Doors:** CLOSED until clear + delay.  
- **Enemies (BEGINNER_TEST_MODE):**
  - Swarm at 0.0 s  
  - Swarm at 0.4 s  
  - Flanker at 0.8 s  
- **Spawn pattern:** Spread.  
- **Heal drop on clear:** 25% chance, 30% base_max_hp (capped at 100%).  
- **Transition:** Overlap exit → room 5.

---

## Room 5 — Elite

- **Type:** ELITE  
- **Wall border:** B = 2  
- **Doors:** CLOSED until clear + delay.  
- **Enemies (BEGINNER_TEST_MODE):**
  - 1× **Brute** (elite) at 0.0 s  
  - 1× **Swarm** (non-elite) at 0.4 s  
- **Spawn pattern:** **Triangle** (elite-appropriate spacing).  
- **Spacing:** **MIN_DISTANCE_BETWEEN_ENEMIES_PX + ELITE_EXTRA_SPACING_PX** (90 + 60 = 150 px when elite).  
- **Heal drop on clear:** 25% chance, 30% base_max_hp (capped at 100%).  
- **Transition:** Overlap exit → room 6.

---

## Room 6 — Ambush

- **Type:** AMBUSH  
- **Wall border:** **B = 4** (thick walls).  
- **Doors:** CLOSED until clear + delay; **doorway carved 2 cols × B rows** at bottom (inner-face).  
- **Enemies (BEGINNER_TEST_MODE):**
  - 2× **Swarm**, both with 1.5 s telegraph.  
- **Spawn pattern:** **Ambush** (ring / tight pattern).  
- **Heal drop on clear:** 25% chance, 30% base_max_hp (capped at 100%).  
- **Transition:** Overlap exit trigger (positioned at playable inner edge) → room 7.

---

## Room 7 — Mini Boss

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
- **Mini Boss:** `MINI_BOSS_DOOR_UNLOCK_DELAY_SEC = 0.5` (after death, 0.5 s then exit opens).  
- **Room 0:** Doors open immediately (no timer).  
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

## Enemy types (Biome 1)

| Type       | Class     | Base HP | Base damage | Size (px) | Notes                    |
|-----------|-----------|---------|-------------|-----------|---------------------------|
| Swarm     | Swarm     | 30      | 10          | 60×60     | Melee Grunt               |
| Flanker   | Flanker   | 22      | 8           | 48×48     | Fast Flanker              |
| Brute     | Brute     | 50      | 14          | 80×80     | Heavy Brute               |
| Mini Boss | MiniBoss  | (config)| (config)    | 96×96     | Single per room 7         |
| Dummy     | TrainingDummy | (high) | 0           | —         | Room 0 only, damageable   |

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
| START / SAFE| —         | No enemies                      |
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
