# BIOME 2 — FULL IMPLEMENTATION SPEC

**Source:** Extracted from current codebase only. No design docs or invented values.

---

## 1. Dungeon Structure

- **Total number of rooms in Biome 2:** 8 (`BIOME2_ROOM_COUNT = 8`)
- **Campaign indices / room numbers:** Campaign indices **8–15** (`BIOME2_START_INDEX = 8` through `BIOME2_START_INDEX + 7`). Local Biome 2 index `room_idx - 8` is **0–7** in `get_biome2_spawn_specs` / `room_order_biome2`.
- **Room sequence:**
  - **When `BEGINNER_TEST_MODE` is True:** Fixed order (campaign index → type):
    - 8 → COMBAT  
    - 9 → COMBAT  
    - 10 → AMBUSH  
    - 11 → SAFE  
    - 12 → COMBAT  
    - 13 → ELITE  
    - 14 → AMBUSH  
    - 15 → MINI_BOSS  
  - **When `BEGINNER_TEST_MODE` is False:** `random.Random(seed).shuffle(mid)` on `mid = [COMBAT, COMBAT, COMBAT, AMBUSH, AMBUSH, SAFE, ELITE]`; result **+** `[MINI_BOSS]` appended (last room always MINI_BOSS). Seed: argument to `room_order_biome2(seed)` from `generate_room(campaign_index, self._seed)` → same as `RoomController._seed` (default `SEED`).
- **Fixed vs shuffled:** Fixed when `BEGINNER_TEST_MODE`; otherwise shuffled middle 7 types, MINI_BOSS fixed last.
- **Types of rooms present:** COMBAT, AMBUSH, SAFE, ELITE, MINI_BOSS (no START in Biome 2 segment).
- **Entry room details:** First Biome 2 room is **campaign index 8**. Player enters via door transition from **campaign index 7** (Biome 1 mini boss room) when `USE_BIOME2` is True and total campaign includes Biome 2.
- **Exit room details:** Last Biome 2 room is **campaign index 15** (MINI_BOSS). After clear and transition, next room is **campaign index 16** (Biome 3 start) when `USE_BIOME3` is True; else run may end or continue per `total_campaign_rooms()`.
- **Biome 2 after Biome 1 mini-boss:** Yes, when `USE_BIOME2` is True: campaign order is 0–7 (Biome 1) then 8–15 (Biome 2). Room 7 → Room 8 is sequential door transition.

---

## 2. Room-wise Breakdown

**Shared (all Biome 2 rooms):** `generate_room` sets `biome_index = 2`, `width`/`height` from `_room_grid_size()` → **30×20** tiles (960×640 px). Hazard tile placement uses same `_make_tile_grid` as Biome 1 for non-START/SAFE types (lava/slow caps depend on `BEGINNER_TEST_MODE` and room type). `room.room_index` in `Room` dataclass is **global campaign index** (8–15). **Door locking/unlocking:** Same as Biome 1 — combat rooms load with `close_all()`; SAFE loads with `open_all()`; clear triggers `on_room_clear()` → `DOOR_UNLOCK_DELAY_SEC` (0.5 s) then `open_all()`. **Pattern vs Biome 1:** Different spawn tables (`get_biome2_spawn_specs`), **Heavy** enemy appears, **two AMBUSH** rooms in fixed order, **fourth combat slot** can have duplicate Brute + Heavy (Beginner room 12), **MiniBoss2** + timed adds on room 15.

### Campaign 8 (local 0)
- **Room type:** COMBAT (Beginner) or shuffled type (non-Beginner)
- **Enemies / composition / pattern:** See **§5** (Beginner: Swarm, Flanker, Brute — spread; non-Beginner COMBAT: Swarm, Flanker, Brute, Heavy — spread)
- **Hazards:** Lava/slow per `_make_tile_grid` (not START/SAFE)
- **Placement logic:** Same as Biome 1 hazard cell rules (`seed + room_index * 1000`)
- **Special mechanics:** None beyond spawn pattern

### Campaign 9 (local 1)
- **Room type:** COMBAT (Beginner) or shuffled
- **Enemies:** Beginner: Flanker, Brute, Heavy — spread. Non-Beginner: per type in §5
- **Hazards / doors:** Same as campaign 8 pattern for combat

### Campaign 10 (local 2)
- **Room type:** AMBUSH (Beginner) or shuffled
- **Enemies:** Beginner: Swarm + Flanker, telegraph **1.5** s each — ambush radius `AMBUSH_SPAWN_RADIUS_PX` (200). Non-Beginner AMBUSH: Swarm, Flanker — ambush
- **Wall border:** 4 tiles (`wall_border_thickness(AMBUSH)`)

### Campaign 11 (local 3)
- **Room type:** SAFE (Beginner) or shuffled
- **Enemies:** None
- **Hazards:** No lava; slow 0–5% playable (same as Biome 1 SAFE)
- **Special:** `open_all()` on load; heal object — same as Biome 1 Safe Room behavior in `game_scene`

### Campaign 12 (local 4)
- **Room type:** COMBAT (Beginner) or shuffled
- **Enemies:** Beginner: Swarm, Brute, Brute, Heavy — spread, delays 0, 0.4, 0.8, 1.2 s

### Campaign 13 (local 5)
- **Room type:** ELITE (Beginner) or shuffled
- **Enemies:** Beginner: Brute elite, Swarm elite, Swarm non-elite — triangle `TRIANGLE_OFFSET_PX` (80). Non-Beginner ELITE: same trio pattern as Beginner ELITE branch in `get_biome2_spawn_specs`

### Campaign 14 (local 6)
- **Room type:** AMBUSH (Beginner) or shuffled
- **Same as campaign 10** for Beginner ambush layout

### Campaign 15 (local 7)
- **Room type:** MINI_BOSS
- **Enemies:** MiniBoss2 at 2.0 s; adds Swarm 8.0 s, Flanker 12.0 s, Brute 16.0 s, Heavy 20.0 s — each add `BIOME2_ADD_TELEGRAPH_SEC` = 0.5 s. Positions: one per slot via `generate_valid_spawn_position` loop (`pattern == "single"` and len > 1)
- **Hazards:** Same combat-room hazard rules
- **Special:** Reward at boss death pos; `MINI_BOSS_DOOR_UNLOCK_DELAY_SEC`. Mini-boss room: door-unlock timer starts when the boss dies (`MINI_BOSS_DOOR_UNLOCK_DELAY_SEC`), not when the room is fully cleared (adds may still be alive). `MiniBoss2` in `isinstance(..., (MiniBoss, MiniBoss2, ...))` for death handling

---

## 3. Room Design & Environment Details

- **General room size:** **30 cols × 20 rows** (960×640 px). Same as Biome 1 (`_room_grid_size()`).
- **All rooms same size:** Yes for Biome 2; `ROOM_SIZE_*` config **NOT IMPLEMENTED** in generation.
- **Layout structure:** Same as Biome 1: `tile_grid` floor/lava/slow; wall band 2 (COMBAT/SAFE/ELITE/MINI_BOSS) or 4 (AMBUSH).
- **Collision boundaries:** Same as Biome 1 (`playable_bounds_pixels`, `_resolve_entity_wall_collision`).
- **Camera behavior:** Same as Biome 1 (`camera_offset` centers room in logical screen).
- **Entry/exit logic:** Same as Biome 1 (`_place_doors_for_room`, door trigger transition, spawn on `room.spawn_tile`).
- **Combat / Safe / Elite / Ambush / Mini-boss look/feel:** **Same tile/wall/door drawing as Biome 1** (`_draw_room_tiles_and_doors`). No `biome_index == 2` branch in `game_scene.draw` for alternate backgrounds or overlays.
- **Visual or environmental differences from Biome 1:** **NOT IMPLEMENTED** in code (same rendering path).

---

## 4. Enemies (Detailed)

- **Swarm, Flanker, Brute:** Same stats, sizes, melee params, elite multipliers as Biome 1 (`enemy_base`, config). Used in Biome 2 with same `BEGINNER_TEST_MODE` speed overrides when True.
- **Heavy (class in `entities/heavy.py`, type `"heavy"`):**
  - **New vs Biome 1:** Biome 1 combat spawn lists do not include Heavy; Heavy is Biome 2+ in implemented spawns.
  - **Role:** melee (slow armored)
  - **HP:** 60 base; elite: 60 × 1.4 = 84
  - **Damage:** 12 base; elite: 14.4
  - **Speed:** `ENEMY_HEAVY_MOVE_SPEED` = 100 px/s (or `int(PLAYER_MOVE_SPEED * 0.55)` when `BEGINNER_TEST_MODE`)
  - **Size:** `ENEMY_HEAVY_SIZE` = (104, 104)
  - **Attack:** melee; radius 42.0, offset 24.0, cooldown 1.7 s
  - **Movement:** chase, stop 64 px, contact damage interval 0.5 s, unstuck/heavy clearance logic in `enemy_base`
  - **Special:** `for_heavy=True` in spawn validation (`MIN_TILES_FROM_WALL_HEAVY`, corner exclusion, etc.) when `game_scene` spawns Heavy
- **MiniBoss2:** See **§6**.

---

## 5. Enemy Composition by Room

**`SPAWN_SLOT_DELAY_SEC` = 0.4** unless noted. **RNG for positions:** `random.Random(SEED + room.room_index * 10000)` in `game_scene` (config `SEED`).

### BEGINNER_TEST_MODE (fixed types per campaign index)

| Campaign | Type   | Count | Types (elite) | Delays (s) | Telegraph | Formation |
|---------|--------|-------|----------------|------------|-----------|-----------|
| 8  | COMBAT | 3 | Swarm, Flanker, Brute (all non-elite) | 0, 0.4, 0.8 | default 0.5 | spread |
| 9  | COMBAT | 3 | Flanker, Brute, Heavy (non-elite) | 0, 0.4, 0.8 | 0.5 | spread |
| 10 | AMBUSH | 2 | Swarm, Flanker (non-elite) | 0, 0.4 | **1.5** both | ambush |
| 11 | SAFE   | 0 | — | — | — | — |
| 12 | COMBAT | 4 | Swarm, Brute, Brute, Heavy | 0, 0.4, 0.8, 1.2 | 0.5 | spread |
| 13 | ELITE  | 3 | Brute elite, Swarm elite, Swarm non-elite | 0, 0.4, 0.8 | 0.5 | triangle |
| 14 | AMBUSH | 2 | Swarm, Flanker (non-elite) | 0, 0.4 | **1.5** both | ambush |
| 15 | MINI_BOSS | 5 spawns | MiniBoss2 @2.0; Swarm@8, Flanker@12, Brute@16, Heavy@20 (non-elite) | see times | **0.5** on adds | single (multi `generate_valid_spawn_position`) |

**Differs from Biome 1:** Heavy; duplicate Brute on room 12; two AMBUSH rooms with **Swarm + Flanker** (2 enemies each; Biome 1 non-Beginner AMBUSH uses 3 enemies); Elite trio Brute+Swarm+Swarm; MiniBoss2 + 4 timed adds.

### Non-Beginner (by `room_type` from shuffle)

- **COMBAT:** Swarm, Flanker, Brute, Heavy (non-elite), delays 0, 0.4, 0.8, **1.2**, spread — **4 enemies** (Biome 1 COMBAT has 3).
- **AMBUSH:** Swarm, Flanker, telegraph 1.5, ambush — **2 enemies** (Biome 1 non-Beginner AMBUSH has 3).
- **ELITE:** Brute elite, Swarm elite, Swarm non-elite — same structure as Beginner ELITE, triangle.
- **SAFE:** empty.
- **MINI_BOSS:** Same 5-slot schedule as Beginner room 15.

---

## 6. Mini Boss (Biome 2)

- **Name/class:** `MiniBoss2` (`entities/mini_boss_2.py`); `enemy_type` = `"mini_boss_2"`
- **Sprite size:** `MINI_BOSS_SIZE` = **(128, 128)** (comment in file says 96×96; code uses `MINI_BOSS_SIZE` from config)
- **HP / damage / speed / stop / attack cooldown:** Same config as Biome 1 MiniBoss: `MINI_BOSS_BASE_HP` 200, `MINI_BOSS_BASE_DAMAGE` 18, `MINI_BOSS_MOVE_SPEED` (and Beginner override), stop 70 px, `MINI_BOSS_ATTACK_COOLDOWN_SEC` 2.0 after hit
- **Phases:** Same as MiniBoss — single-phase AI (attack_01/attack_02 alternate); dash/phase_change assets not used in update
- **Attack patterns / movement / special (base boss):** Same as Biome 1 Mini Boss
- **Biome 2 encounter-specific:** Adds from `get_biome2_mini_boss_adds_schedule`: **8.0 s** Swarm, **12.0 s** Flanker, **16.0 s** Brute, **20.0 s** Heavy; `BIOME2_ADD_TELEGRAPH_SEC` = **0.5**; `BIOME2_MINI_BOSS_SPAWN_TIME` = **2.0** for boss spawn slot
- **Reward on death:** Same as Biome 1 — reward at death pos, collect heal `MINI_BOSS_REWARD_HEAL_PERCENT` (0.30) of `base_max_hp`, capped at `base_max_hp` (no overheal from orbs)
- **Door unlock:** Same flow — inactive boss removed from list → room clear → `on_room_clear()`; also `_mini_boss_death_pos` / `_door_unlock_timer` path shared with boss types
- **Same as Biome 1 mini-boss or different:** **Different** class/assets (`mini_boss_2` folder), **same** numeric combat stats; **adds** are Biome-2-only

---

## 7. Player Configuration in Biome 2

- **Same as Biome 1** for HP, dash, attacks, block/parry, cooldowns (`Player`, `config`). No `biome_index == 2` branch altering player stats in code.

---

## 8. Hazards

- **Lava / slow / door margins / center safe zone:** **Same as Biome 1** (`_make_tile_grid`, `HazardSystem`). Campaign indices 8–15 use `room_index` in RNG `seed + room_index * 1000`.
- **SAFE (e.g. room 11 in Beginner):** Same as Biome 1 Safe (no lava, optional slow 0–5%).
- **Combat / elite / ambush / mini-boss rooms:** Same hazard generation rules as Biome 1 for those room types (including BEGINNER lava 0–3% and slow 5–8% in non-START/non-SAFE when `BEGINNER_TEST_MODE`).

---

## 9. Safe Room

- **Exists:** Yes (one per Biome 2 order; campaign index depends on shuffle — **11** when `BEGINNER_TEST_MODE`).
- **Room size / enemies / hazards / heal / overheal / H key / door open on load:** **Same as Biome 1** Safe Room implementation in `game_scene` + `room_controller`.
- **Objects:** Heal object at `(wall_border()+2, wall_border()+2)`; in Biome 2 safe room, no upgrade choice panel is shown; only the H-key heal. The upgrade panel (Health/Speed/Attack/Defence) appears only in Biome 3 safe room (campaign index 21) and Biome 4 safe room (campaign index 28).
- **Visual differences:** **NOT IMPLEMENTED** (same as Biome 1).

---

## 10. Rewards / Upgrades / Recovery

- **Enemy kills:** No automatic heal on kill in code.
- **Room clear:** **Same as Biome 1** — `HEAL_DROP_CHANCE` (0.25) seeded roll; reward at room center tile if success; not START/SAFE. No heal applied on clear; player must overlap the orb to receive the 30% heal (capped at `base_max_hp`).
- **Mini-boss death:** **Same as Biome 1** — collectible reward, `MINI_BOSS_REWARD_HEAL_PERCENT`. Collecting the reward orb heals 30% of `base_max_hp`, capped at `base_max_hp` (no overheal from orbs).
- **`BIOME2_CLEAR_HEAL_PERCENT` / `BIOME2_CLEAR_HEAL_CAP` in `biome2_rooms.py`:** Defined but **NOT IMPLEMENTED** in `game_scene` (no reference).
- **Progression bonus / free max-HP tied to Biome 2 only:** **NOT IMPLEMENTED** (Safe upgrade logic is global).

---

## 11. AI Director / Scaling (if present)

- **Same as Biome 1:** **NOT IMPLEMENTED** — no Biome-2-specific director, reinforcement, or player-state scaling.

---

## 12. RNG / Seed Behavior

- **Seed used:** Yes — `room_order_biome2(seed)` for order (non-Beginner); `_make_tile_grid(..., campaign_index, seed)` for hazards; spawn positions `SEED + room.room_index * 10000` in game_scene.
- **Room order:** Non-Beginner: shuffled with `RoomController._seed`. Beginner: fixed.
- **Rewards:** Heal drop uses `SEED + current_room_index * 100` (same as Biome 1).
- **Global SEED vs RoomController:** **Same clarification as Biome 1** — spawn RNG uses config `SEED`; `generate_room` uses `_seed` (typically equal).

---

## 13. Missing / Incomplete Features

- **`get_biome2_elite_spacing()`:** Returns `True` but **never called** — dead code.
- **`BIOME2_CLEAR_HEAL_PERCENT` / `BIOME2_CLEAR_HEAL_CAP`:** Not wired to gameplay.
- **Biome 2 visual identity:** No separate background/tile set for `biome_index == 2`.
- **Comment mismatch:** `mini_boss_2.py` docstring says 96×96; actual render size is `MINI_BOSS_SIZE` (128×128).
