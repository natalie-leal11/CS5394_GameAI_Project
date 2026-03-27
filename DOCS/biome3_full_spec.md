# BIOME 3 — FULL IMPLEMENTATION SPEC

**Source:** Extracted from current codebase only. No design docs or invented values.

---

## 1. Dungeon Structure

- **Total number of rooms in Biome 3:** 8 (`BIOME3_ROOM_COUNT = 8`)
- **Campaign indices / room numbers:** Campaign indices **16–23** (`BIOME3_START_INDEX = 16` through `BIOME3_START_INDEX + 7`). Local Biome 3 index `room_idx - 16` is **0–7** in `get_biome3_spawn_specs` / `room_order_biome3`.
- **Room sequence:**
  - **When `BEGINNER_TEST_MODE` is True:** Fixed order (campaign index → type):
    - 16 → COMBAT
    - 17 → COMBAT
    - 18 → AMBUSH
    - 19 → COMBAT
    - 20 → ELITE
    - 21 → SAFE
    - 22 → COMBAT
    - 23 → MINI_BOSS
  - **When `BEGINNER_TEST_MODE` is False:** `random.Random(seed).shuffle(mid)` on `mid = [COMBAT, COMBAT, COMBAT, AMBUSH, ELITE, SAFE, COMBAT]` (7 types); result **+** `[MINI_BOSS]` appended (last room always MINI_BOSS). Seed: argument to `room_order_biome3(seed)` from `generate_room(campaign_index, self._seed)` → same as `RoomController._seed` (default `SEED`).
- **Fixed vs shuffled:** Fixed when `BEGINNER_TEST_MODE`; otherwise shuffled middle 7 types, MINI_BOSS fixed last.
- **Types of rooms present:** COMBAT, AMBUSH, SAFE, ELITE, MINI_BOSS (no START in Biome 3 segment).
- **Entry room details:** First Biome 3 room is **campaign index 16**. Player enters via door transition from **campaign index 15** (Biome 2 mini boss room) when `USE_BIOME3` is True and total campaign includes Biome 3.
- **Exit room details:** Last Biome 3 room is **campaign index 23** (MINI_BOSS). After clear and transition, next room is **campaign index 24** (Biome 4 start) when `USE_BIOME4` is True; else run may end or continue per `total_campaign_rooms()`.
- **Transition from Biome 2:** Yes, when `USE_BIOME3` is True: campaign order is 0–7 (Biome 1), 8–15 (Biome 2), then 16–23 (Biome 3). Room 15 → Room 16 is sequential door transition.

---

## 2. Room-wise Breakdown

**Shared (all Biome 3 rooms):** `generate_room` sets `biome_index = 3`, `width`/`height` from `_room_grid_size()` → **30×20** tiles (960×640 px). Hazard tile placement uses same `_make_tile_grid` as Biome 1 for non-START/SAFE types (lava/slow caps depend on `BEGINNER_TEST_MODE` and room type). `room.room_index` in `Room` dataclass is **global campaign index** (16–23). **Door locking/unlocking:** Combat/elite/ambush: close on load; after full clear, `on_room_clear()` → `DOOR_UNLOCK_DELAY_SEC` (0.5 s) then `open_all()`. SAFE loads with `open_all()`. **MINI_BOSS (campaign 23):** door-unlock timer starts when the boss dies (`MINI_BOSS_DOOR_UNLOCK_DELAY_SEC` 0.5 s), not only on full room clear (adds may still be alive). **Pattern vs Biome 2:** Different spawn tables (`get_biome3_spawn_specs`); **Ranged** enemy appears; **Biome3MiniBoss** on room 23 with Phase 2 adds (2 Swarm + 1 Flanker in ring); no Heavy in non-Beginner COMBAT (Biome 3 COMBAT uses Swarm, Flanker, Ranged, Brute).

### Campaign 16 (local 0)
- **Room type:** COMBAT (Beginner) or shuffled type (non-Beginner)
- **Number of enemies:** 3 (Beginner) or 4 (non-Beginner COMBAT)
- **Enemy types:** Beginner: Swarm, Flanker, Ranged (all non-elite). Non-Beginner COMBAT: Swarm, Flanker, Ranged, Brute (all non-elite)
- **Elite/non-elite:** All non-elite
- **Spawn delays (s):** 0, 0.4, 0.8 (Beginner); 0, 0.4, 0.8, 1.2 (non-Beginner COMBAT)
- **Telegraph:** None → `SPAWN_TELEGRAPH_DURATION_SEC` (0.5 s)
- **Spawn formation:** spread
- **Spawn positions logic:** `spawn_spread(room, player_center, len(spawn_specs), is_elite=False, rng, door_positions)`; RNG `random.Random(SEED + room.room_index * 10000)`
- **Hazards present:** Lava/slow per `_make_tile_grid` (not START/SAFE)
- **Hazard placement logic:** Same as Biome 1 (`seed + campaign_index * 1000`)
- **Special mechanics:** None beyond spawn pattern
- **Door locking/unlocking:** Same as Biome 1 (close on load; open after clear + 0.5 s delay)
- **Heavy spawn (when Heavy appears):** `game_scene` runs `ensure_valid_spawn_position(..., for_heavy=True)` for Heavy slots. `blocked_tiles` for spawn validation is passed only when `current_room_index >= BIOME4_START_INDEX`; in Biome 3, `blocked_tiles` is **None**.

### Campaign 17 (local 1)
- **Room type:** COMBAT (Beginner) or shuffled
- **Number of enemies:** 3
- **Enemy types:** Beginner: Flanker, Ranged, Brute (non-elite). Non-Beginner: per COMBAT type in §5
- **Spawn delays:** 0, 0.4, 0.8 s
- **Telegraph:** default 0.5
- **Spawn formation:** spread
- **Hazards / doors:** Same as campaign 16 for combat

### Campaign 18 (local 2)
- **Room type:** AMBUSH (Beginner) or shuffled
- **Number of enemies:** 3
- **Enemy types:** Beginner: Swarm, Flanker, Ranged (non-elite). Non-Beginner AMBUSH: Swarm, Flanker, Ranged (non-elite)
- **Spawn delays:** 0, 0.4, 0.8 s
- **Telegraph:** **1.5** s each (explicit in spawn_specs)
- **Spawn formation:** ambush (`spawn_ambush`; default `AMBUSH_SPAWN_RADIUS_PX` 200)
- **Wall border:** 4 tiles (`wall_border_thickness(AMBUSH)`)

### Campaign 19 (local 3)
- **Room type:** COMBAT (Beginner) or shuffled
- **Number of enemies:** 3
- **Enemy types:** Beginner: Brute, Ranged, Heavy (non-elite)
- **Spawn delays:** 0, 0.4, 0.8 s
- **Telegraph:** default 0.5
- **Spawn formation:** spread
- **Hazards / doors:** Same as campaign 16

### Campaign 20 (local 4)
- **Room type:** ELITE (Beginner) or shuffled
- **Number of enemies:** 3
- **Enemy types:** Beginner: Brute elite, Ranged elite, Swarm non-elite. Non-Beginner ELITE: same
- **Spawn delays:** 0, 0.4, 0.8 s
- **Telegraph:** default 0.5
- **Spawn formation:** triangle (`spawn_triangle`, `TRIANGLE_OFFSET_PX` 80, is_elite=True)

### Campaign 21 (local 5)
- **Room type:** SAFE (Beginner) or shuffled
- **Number of enemies:** 0
- **Enemy types:** None
- **Hazards:** No lava; slow 0–5% playable (same as Biome 1 SAFE)
- **Special:** `open_all()` on load; heal object — same as Biome 1 Safe Room. **Upgrade panel (1/2/3)** appears only when **`current_room_index == BIOME3_SAFE_ROOM_INDEX` (21)** and room type is SAFE. In `BEGINNER_TEST_MODE`, SAFE is always at 21. When `BEGINNER_TEST_MODE` is False, SAFE may land at any campaign index 16–22; **only if SAFE is at index 21** does the upgrade panel apply—other Biome 3 SAFE indices get H-heal only, no 1/2/3 upgrade.

### Campaign 22 (local 6)
- **Room type:** COMBAT (Beginner) or shuffled
- **Number of enemies:** 4 (Beginner)
- **Enemy types:** Beginner: Swarm, Flanker, Ranged, Heavy (non-elite)
- **Spawn delays:** 0, 0.4, 0.8, 1.2 s
- **Telegraph:** default 0.5
- **Spawn formation:** spread

### Campaign 23 (local 7)
- **Room type:** MINI_BOSS
- **Number of enemies:** 1 (Biome3MiniBoss) + 3 adds when boss reaches Phase 2 (50% HP): 2 Swarm, 1 Flanker (non-elite), spawned in ring at radius 120 px around boss
- **Enemy types:** Biome3MiniBoss at 2.0 s; adds spawned by `game_scene` when boss sets `_pending_adds = True` (after phase_change animation)
- **Spawn formation:** single (boss at one `generate_valid_spawn_position`; adds at angles 0, 2π/3, 4π/3, radius 120)
- **Hazards:** Same combat-room hazard rules
- **Special:** Reward at boss death pos; `MINI_BOSS_DOOR_UNLOCK_DELAY_SEC`; Biome3MiniBoss in `isinstance(..., (MiniBoss, MiniBoss2, Biome3MiniBoss, ...))` for death handling. Mini-boss room: door-unlock timer starts when the boss dies, not when room is fully cleared (adds may still be alive).

---

## 3. Room Design & Environment Details

- **General room size:** **30 cols × 20 rows** (960×640 px). Same as Biome 1 (`_room_grid_size()`).
- **All rooms same size:** Yes for Biome 3; `ROOM_SIZE_*` config **NOT IMPLEMENTED** in generation.
- **Layout structure:** Same as Biome 1: `tile_grid` floor/lava/slow; wall band 2 (COMBAT/SAFE/ELITE/MINI_BOSS) or 4 (AMBUSH).
- **Collision boundaries:** Same as Biome 1 (`playable_bounds_pixels`, `_resolve_entity_wall_collision`).
- **Camera behavior:** Same as Biome 1 (`camera_offset` centers room in logical screen).
- **Entry/exit logic:** Same as Biome 1 (`_place_doors_for_room`, door trigger transition, spawn on `room.spawn_tile`).
- **Combat / Safe / Elite / Ambush / Mini-boss look/feel:** **Same tile/wall/door drawing as Biome 1** (`_draw_room_tiles_and_doors`). No `biome_index == 3` branch in `game_scene.draw` for alternate backgrounds or overlays.
- **Visual or environmental differences from Biome 1/2:** **NOT IMPLEMENTED** in code (same rendering path).

---

## 4. Enemies (Detailed)

- **Swarm, Flanker, Brute, Heavy:** Same stats, sizes, melee params, elite multipliers as Biome 1/2 (`enemy_base`, config). When `BEGINNER_TEST_MODE` is True (`config.py`): `ENEMY_FLANKER_MOVE_SPEED` = `int(PLAYER_MOVE_SPEED * 0.85)`, `ENEMY_BRUTE_MOVE_SPEED` = `int(PLAYER_MOVE_SPEED * 0.65)`, `ENEMY_HEAVY_MOVE_SPEED` = `int(PLAYER_MOVE_SPEED * 0.55)`, `ENEMY_SWARM_MOVE_SPEED` = 100; **Ranged** has **no** Beginner speed override (`ENEMY_RANGED_MOVE_SPEED` stays 100).
- **Ranged (class in `entities/ranged.py`, type `"ranged"`):**
  - **New vs Biome 1/2:** Biome 1 and 2 combat spawn lists do not include Ranged; Ranged is Biome 3+ in implemented spawns.
  - **Role:** Ranged (projectile attacker; no melee). Kiting: back away if closer than `RANGED_KITE_CLOSE_THRESHOLD`, approach if farther than `RANGED_KITE_FAR_THRESHOLD`, strafe in ideal band.
  - **HP:** `ENEMY_RANGED_BASE_HP` = 28; elite: 28 × 1.4 = 39.2
  - **Damage:** `ENEMY_RANGED_BASE_DAMAGE` = 8 (projectile uses `self.damage` from entity); elite: 8 × 1.2 = 9.6
  - **Speed:** `ENEMY_RANGED_MOVE_SPEED` = 100 px/s
  - **Size:** `ENEMY_RANGED_SIZE` = (72, 72)
  - **Attack type:** Projectile; no melee. Combat uses radius 0, offset 0, cooldown 999.0 for `"ranged"` (`combat.py`).
  - **Projectile:** `Projectile` with `RANGED_PROJECTILE_SPEED` 260, `RANGED_PROJECTILE_LIFETIME_SEC` 3.0; damage = entity damage (base or elite). Default sprite: `PROJECTILE_IMAGE_PATH` = `assets/entities/projectiles/enemy_projectile_16x16.png`, `PROJECTILE_SIZE` = (16, 16) (`projectile.py`).
  - **Attack cooldown:** `ENEMY_RANGED_ATTACK_COOLDOWN_SEC` = 1.4 s
  - **Movement:** Kite: close threshold 140 px, far threshold 220 px; strafe speed factor 0.7, attack strafe 0.5; stop distance `ENEMY_RANGED_STOP_DISTANCE` = 180 px (no melee); when overlapping player and not dashing, push enemy to `stop_dist` from player
  - **Special:** `_pending_projectile` set on attack; `game_scene` collects and adds to `_projectiles`; `apply_projectile_hits` resolves damage
- **Biome3MiniBoss:** See **§6**.

---

## 5. Enemy Composition by Room

**`SPAWN_SLOT_DELAY_SEC` = 0.4** unless noted. **RNG for positions:** `random.Random(SEED + room.room_index * 10000)` in `game_scene` (config `SEED`).

### BEGINNER_TEST_MODE (fixed types per campaign index)

| Campaign | Type   | Count | Types (elite) | Delays (s) | Telegraph | Formation |
|---------|--------|-------|----------------|------------|-----------|-----------|
| 16 | COMBAT | 3 | Swarm, Flanker, Ranged (non-elite) | 0, 0.4, 0.8 | default 0.5 | spread |
| 17 | COMBAT | 3 | Flanker, Ranged, Brute (non-elite) | 0, 0.4, 0.8 | 0.5 | spread |
| 18 | AMBUSH | 3 | Swarm, Flanker, Ranged (non-elite) | 0, 0.4, 0.8 | **1.5** all | ambush |
| 19 | COMBAT | 3 | Brute, Ranged, Heavy (non-elite) | 0, 0.4, 0.8 | 0.5 | spread |
| 20 | ELITE  | 3 | Brute elite, Ranged elite, Swarm non-elite | 0, 0.4, 0.8 | 0.5 | triangle |
| 21 | SAFE   | 0 | — | — | — | — |
| 22 | COMBAT | 4 | Swarm, Flanker, Ranged, Heavy (non-elite) | 0, 0.4, 0.8, 1.2 | 0.5 | spread |
| 23 | MINI_BOSS | 1 + 3 adds | Biome3MiniBoss @2.0; Phase 2: 2 Swarm, 1 Flanker (ring radius 120) | 2.0 boss | — | single (adds via _pending_adds) |

**Differs from Biome 2:** Ranged in all combat/ambush/elite; no Heavy in non-Beginner COMBAT (Swarm, Flanker, Ranged, Brute); AMBUSH has 3 enemies (Swarm, Flanker, Ranged); ELITE has Brute elite, Ranged elite, Swarm non-elite; Mini boss is Biome3MiniBoss with Phase 2 adds (2 Swarm + 1 Flanker in ring), not timed schedule.

### Non-Beginner (by `room_type` from shuffle)

- **COMBAT:** Swarm, Flanker, Ranged, Brute (non-elite), delays 0, 0.4, 0.8, **1.2**, spread — **4 enemies** (no Heavy in Biome 3 COMBAT).
- **AMBUSH:** Swarm, Flanker, Ranged (non-elite), telegraph 1.5, ambush — **3 enemies**.
- **ELITE:** Brute elite, Ranged elite, Swarm non-elite — triangle.
- **SAFE:** empty.
- **MINI_BOSS:** Biome3MiniBoss at 2.0 s; Phase 2 adds 2 Swarm + 1 Flanker in ring (radius 120).

---

## 6. Mini Boss (Biome 3)

- **Name/class:** `Biome3MiniBoss` (`entities/biome3_miniboss.py`); `enemy_type` = `"mini_boss_3"`
- **Sprite size:** `MINI_BOSS_SIZE` = **(128, 128)** (from config; docstring says 96×96)
- **HP / damage / move speed:** `MINI_BOSS_BASE_HP` 200, `MINI_BOSS_BASE_DAMAGE` 18. When `BEGINNER_TEST_MODE` is False: `MINI_BOSS_MOVE_SPEED` = **100** px/s. When `BEGINNER_TEST_MODE` is True: `MINI_BOSS_MOVE_SPEED` = **`int(PLAYER_MOVE_SPEED * 0.75)`** = **165** px/s (default `PLAYER_MOVE_SPEED` 220). Melee attack uses `MINI_BOSS_ATTACK_RADIUS` 32.0, `MINI_BOSS_ATTACK_OFFSET` 28.0, `MINI_BOSS_ATTACK_COOLDOWN_SEC` 2.0 (set by combat when damage applied).
- **Stop distance:** `BIOME3_MINIBOSS_STOP_DISTANCE` = 70.0 px
- **Phases:** Two phases. Phase 1: melee (attack_01/attack_02) and fireball at range. Phase 2 at **50% HP** (`BIOME3_MINIBOSS_PHASE2_HP_RATIO` = 0.5): plays `phase_change` animation once, then sets `_pending_adds = True`; `game_scene` spawns 2 Swarm + 1 Flanker in ring (radius 120 px, angles 0, 2π/3, 4π/3).
- **Attack patterns:** At distance > 70 px: if fireball cooldown ready, cast fireball (state `fireball`); else move toward player. At distance ≤ 70 px: alternate `attack_01` / `attack_02` (melee); combat applies damage when state in (`attack_01`, `attack_02`).
- **Ranged (fireball):** When `fireball_cooldown_timer <= 0`, spawns `Projectile` with `BIOME3_MINIBOSS_FIREBALL_DAMAGE` 16, `BIOME3_MINIBOSS_FIREBALL_SPEED` 280.0, `BIOME3_MINIBOSS_FIREBALL_LIFETIME_SEC` 3.0; image `BIOME3_MINIBOSS_FIREBALL_IMAGE_PATH`, size (24, 24). Cooldown `BIOME3_MINIBOSS_FIREBALL_COOLDOWN_SEC` = 2.2 s.
- **Movement behavior:** Chase player; clamp to room rect or `ENEMY_MIN_X/Y`, `ENEMY_MAX_X/Y`; anti-stuck and stuck tracking from `enemy_base`.
- **Special abilities:** Phase 2 add spawn (2 Swarm + 1 Flanker in ring); fireball projectile (handled in `game_scene` projectiles list and `apply_projectile_hits`).
- **Reward on death:** Same as Biome 1/2 — reward at death pos, collect heal `MINI_BOSS_REWARD_HEAL_PERCENT` (0.30) of `base_max_hp`, capped at `base_max_hp` (no overheal from orbs).
- **Door unlock:** Same flow — `_mini_boss_death_pos` / `_door_unlock_timer` = `MINI_BOSS_DOOR_UNLOCK_DELAY_SEC` (0.5 s); door unlocks on timer expiry.
- **Improved vs Biome 1/2:** **Different** class/assets; **same** base HP/damage; move speed same as other mini bosses (100 or 165 px/s per `BEGINNER_TEST_MODE`); **adds** Phase 2 (2 Swarm + 1 Flanker in ring); **ranged** fireball (damage 16, speed 280, cooldown 2.2 s); two-phase AI.

---

## 7. Player Configuration

- **Same as Biome 1** for HP, dash, attacks, block/parry, cooldowns (`Player`, `config`). No `biome_index == 3` branch altering player stats in code.

---

## 8. Hazards

- **Lava / slow / door margins / center safe zone:** **Same as Biome 1** (`_make_tile_grid`, `HazardSystem`). Campaign indices 16–23 use `room_index` (campaign_index) in RNG `seed + room_index * 1000`.
- **SAFE (campaign 21 in Beginner):** Same as Biome 1 Safe (no lava, optional slow 0–5%).
- **Combat / elite / ambush / mini-boss rooms:** Same hazard generation rules as Biome 1 for those room types (including BEGINNER lava 0–3% and slow 5–8% in non-START/non-SAFE when `BEGINNER_TEST_MODE`).

---

## 9. Safe Room

- **Exists:** Yes (one SAFE per Biome 3 order). In `BEGINNER_TEST_MODE`, SAFE is always campaign **21**. When shuffled, SAFE may be any campaign index **16–22** (never 23).
- **Room size / enemies / hazards / heal / H key / door open on load:** **Same as Biome 1** Safe Room implementation in `game_scene` + `room_controller`.
- **Healing available:** Yes — H key near heal object: `hp += base_max_hp * SAFE_ROOM_HEAL_PERCENT` (0.30), once per safe room visit; **no clamp** to `base_max_hp` or `SAFE_ROOM_OVERHEAL_CAP_RATIO` on that line. HUD health bar uses `SAFE_ROOM_OVERHEAL_CAP_RATIO` (1.30) for the overheal segment display.
- **Health / Speed / Attack upgrade:** **Only when `current_room_index == 21` (`BIOME3_SAFE_ROOM_INDEX`) and room type is SAFE.** Pick **one** of 1=Health +20% max HP (`SAFE_ROOM_UPGRADE_HEALTH_MULT` 1.20), 2=Speed +10% (`SAFE_ROOM_UPGRADE_SPEED_MULT` 1.10), 3=Attack +12% (`SAFE_ROOM_UPGRADE_ATTACK_MULT` 1.12). Keys 1, 2, or 3 do **not** require pressing H first in code (upgrade can be taken without prior H heal). Panel drawn when index 21, SAFE, and `_safe_room_upgrade_chosen_this_room` is False.
- **Overheal cap (display):** HUD uses `SAFE_ROOM_OVERHEAL_CAP_RATIO` 1.30 for overheal bar segment.
- **Interaction key:** H for heal (any SAFE); 1/2/3 for upgrade **only in campaign room 21 when it is SAFE**.
- **Objects present:** Heal object at `(wall_border()+2, wall_border()+2)`; upgrade panel UI only when campaign index 21 and SAFE.
- **Door behavior:** Open on load (`open_all()`).
- **Visual design:** Same as Biome 1 (no `biome_index == 3` draw branch).

---

## 10. Rewards / Recovery

- **Enemy kills:** No automatic heal on kill in code.
- **Room clear:** **Same as Biome 1** — `HEAL_DROP_CHANCE` (0.25) seeded roll; reward at room center tile if success; not START/SAFE. No heal applied on clear; player must overlap the orb to receive the 30% heal (capped at `base_max_hp`).
- **Mini-boss death:** **Same as Biome 1** — collectible reward, `MINI_BOSS_REWARD_HEAL_PERCENT`. Collecting the reward orb heals 30% of `base_max_hp`, capped at `base_max_hp` (no overheal from orbs).
- **Max HP upgrade:** Available only when the player is in **campaign index 21** and that room is SAFE (`BIOME3_SAFE_ROOM_INDEX`), via upgrade panel choice 1 (Health +20%). If SAFE is shuffled to another index, no upgrade panel—only heal.
- **Progression bonus:** Same global Safe Room heal at any SAFE; one-of-three upgrade (Health/Speed/Attack) **only** at campaign index 21 when that room is SAFE.

---

## 11. AI Director / Scaling

- **Same as Biome 1:** **NOT IMPLEMENTED** — no Biome-3-specific director, reinforcement, or player-state scaling.

---

## 12. RNG / Seed Behavior

- **Seed used:** Yes — `room_order_biome3(seed)` for order (non-Beginner); `_make_tile_grid(..., campaign_index, seed)` for hazards; spawn positions `SEED + room.room_index * 10000` in `game_scene`.
- **Room order:** Non-Beginner: shuffled with `RoomController._seed`. Beginner: fixed.
- **Rewards:** Heal drop uses `SEED + current_room_index * 100` (same as Biome 1).
- **Global SEED vs RoomController:** Same clarification as Biome 1 — spawn RNG uses config `SEED`; `generate_room` uses `_seed` (typically equal).

---

## 13. Missing / Incomplete Features

- **Biome 3 visual identity:** No separate background/tile set for `biome_index == 3` in draw path.
- **Biome3MiniBoss docstring:** Says "96×96"; code uses `MINI_BOSS_SIZE` (128, 128) from config.
- **Ranged BEGINNER speed override:** Ranged has no Beginner speed override; Flanker, Brute, Heavy, MiniBoss do (per `config.py` when `BEGINNER_TEST_MODE`).
- **`biome3_rooms.py` room 23 comment:** Still says "placeholder until Phase 3"; runtime passes `Biome3MiniBoss` from `game_scene`.
