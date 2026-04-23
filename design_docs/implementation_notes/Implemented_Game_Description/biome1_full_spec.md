# BIOME 1 — FULL IMPLEMENTATION SPEC

**Source:** Extracted from current codebase only. No design docs or invented values.

---

## 1. Dungeon Structure

- **Total number of rooms:** 8 (campaign indices 0–7)
- **Room sequence (Room 0 → Room 7):**
  - **When `BEGINNER_TEST_MODE` is True (config):** Fixed order:
    - 0 → START  
    - 1 → COMBAT  
    - 2 → COMBAT  
    - 3 → SAFE  
    - 4 → COMBAT  
    - 5 → ELITE  
    - 6 → AMBUSH  
    - 7 → MINI_BOSS  
  - **When `BEGINNER_TEST_MODE` is False:** Deterministic shuffle of the middle 6 (rooms 1–6): `[COMBAT, COMBAT, COMBAT, SAFE, ELITE, AMBUSH]`; Room 0 = START, Room 7 = MINI_BOSS (fixed). Seed: `SEED` from config.
- **Types of rooms:** START, COMBAT, SAFE, ELITE, AMBUSH, MINI_BOSS (no CORRIDOR or FINAL_BOSS in Biome 1)
- **Entry room:** Room 0 (START). Player spawn at room spawn tile (center-prefer floor tile). Altar at center, training dummy bottom-left, exit trigger top-right.
- **Exit room:** Room 7 (MINI_BOSS). After mini boss death and door unlock delay, exit door leads to next campaign index (Biome 2 when `USE_BIOME2` is True).

---

## 2. Room-wise Breakdown

**Note:** All rooms use the same grid size: **30 cols × 20 rows** (from `LOGICAL_W // TILE_SIZE`, `LOGICAL_H // TILE_SIZE` = 960/32, 640/32). Config values `ROOM_SIZE_START`, `ROOM_SIZE_COMBAT`, etc. are **NOT IMPLEMENTED** in room generation.

### Room 0
- **Room type:** START  
- **Number of enemies:** 0 (hostile). 1 Training Dummy (non-hostile).  
- **Enemy types:** Training Dummy only.  
- **Enemy composition (from code):**
  - Hostile: none (`room_idx == 0` or `rtype == START` → no spawn_specs).
  - Non-hostile: 1 Training Dummy (added in `_setup_room0_props_and_dummy`, not from spawn system).
  - Counts: Swarm 0, Flanker 0, Brute 0, MiniBoss 0, Training Dummy 1.
  - Spawn distribution: N/A (dummy at fixed tile `(min_col, max_row)`).
- **Spawn positions:** Dummy at tile `(min_col, max_row)` with `min_col = wall_border() + 2`, `max_row = room.height - wall_border() - 3` (bottom-left, inside playable).  
- **Hazards present:** None (START has no lava/slow in tile grid).  
- **Hazards position:** N/A  
- **Special mechanics:** Altar at room center; exit trigger rect at top-right (3×3 tiles). Story panel (E/ESC to close). Dummy HP resets to `max_hp` after each player hit (same frame as player attacks).

### Room 1
- **Room type:** COMBAT (when `BEGINNER_TEST_MODE`); otherwise depends on shuffle.  
- **Number of enemies:** 1 (Beginner) or 3 (non-Beginner COMBAT).  
- **Enemy types:** Beginner: Swarm. Non-Beginner COMBAT: Swarm, Flanker, Brute (all non-elite).  
- **Enemy composition (from code):**
  - **When BEGINNER_TEST_MODE:** `spawn_specs = [(Swarm, False, 0.0, None)]`. Counts: Swarm 1, Flanker 0, Brute 0. All non-elite. Spawn distribution: **spread** (Biome 1 combat else branch). Spawn delays (s): 0.0. Telegraph: None → default 0.5 s.
  - **When not BEGINNER_TEST_MODE and room type COMBAT:** `spawn_specs = [(Swarm, False, 0.0, None), (Flanker, False, 0.4, None), (Brute, False, 0.8, None)]`. Counts: Swarm 1, Flanker 1, Brute 1. All non-elite. Spawn distribution: **spread**. Spawn delays (s): 0.0, 0.4, 0.8. Telegraph: 0.5 s default.
- **Spawn positions:** Spread pattern: `generate_valid_spawn_position` per enemy (valid floor/lava/slow tiles, min distance from player, doors, walls; spacing between enemies).  
- **Hazards present:** Lava and/or slow tiles (see Section 6). Not START/SAFE.  
- **Hazards position:** Deterministic from `seed + room_index * 1000`; center 3×3 and door-adjacent zones excluded; then shuffled cells for lava/slow.  
- **Special mechanics:** Spawn slot delays: 0.0, 0.4, 0.8 s for 2nd/3rd enemy when 3 enemies. Telegraph 0.5 s (SPAWN_TELEGRAPH_DURATION_SEC).

### Room 2
- **Room type:** COMBAT (when `BEGINNER_TEST_MODE`); otherwise depends on shuffle.  
- **Number of enemies:** 3.  
- **Enemy types:** Beginner: Swarm, Swarm, Flanker. Non-Beginner COMBAT: Swarm, Flanker, Brute (all non-elite).  
- **Enemy composition (from code):**
  - **When BEGINNER_TEST_MODE:** `spawn_specs = [(Swarm, False, 0.0, None), (Swarm, False, 0.4, None), (Flanker, False, 0.8, None)]`. Counts: Swarm 2, Flanker 1, Brute 0. All non-elite. Spawn distribution: **spread**. Spawn delays (s): 0.0, 0.4, 0.8 (SPAWN_SLOT_DELAY_SEC = 0.4). Telegraph: 0.5 s default.
  - **When not BEGINNER_TEST_MODE and room type COMBAT:** Same as Room 1 non-Beginner: Swarm 1, Flanker 1, Brute 1; all non-elite; **spread**; delays 0.0, 0.4, 0.8.
- **Spawn positions:** Spread pattern (same as Room 1).  
- **Hazards present:** Yes (same logic as Room 1).  
- **Hazards position:** Same as Room 1.  
- **Special mechanics:** Spawn delays 0.0, SPAWN_SLOT_DELAY_SEC (0.4), SPAWN_SLOT_DELAY_SEC * 2 (0.8) s.

### Room 3
- **Room type:** SAFE (when `BEGINNER_TEST_MODE`); otherwise depends on shuffle.  
- **Number of enemies:** 0.  
- **Enemy types:** None.  
- **Enemy composition (from code):**
  - `rtype in (RoomType.START, RoomType.SAFE)` → no spawn_specs. Counts: Swarm 0, Flanker 0, Brute 0, MiniBoss 0. Spawn distribution: N/A.
- **Spawn positions:** N/A  
- **Hazards present:** No lava. Slow: 0–5% of playable cells (uniform random in [0, min(0.05, HAZARD_SLOW_MAX_FRACTION)]).  
- **Hazards position:** Shuffled playable cells; no center 3×3 reserved for SAFE.  
- **Special mechanics:** Heal object at top-left of playable area, tile (wall_border()+2, wall_border()+2). Player near heal (distance ≤ 70 px) can press H to gain SAFE_ROOM_HEAL_PERCENT (30%) of base_max_hp, once per Safe Room; HP capped by SAFE_ROOM_OVERHEAL_CAP_RATIO (130% of base). Door opens immediately (no clear condition).

### Room 4
- **Room type:** COMBAT (when `BEGINNER_TEST_MODE`); otherwise depends on shuffle.  
- **Number of enemies:** 3.  
- **Enemy types:** Beginner: Swarm, Swarm, Flanker. Non-Beginner COMBAT: Swarm, Flanker, Brute (all non-elite).  
- **Enemy composition (from code):**
  - **When BEGINNER_TEST_MODE:** `spawn_specs` identical to Room 2: Swarm 2, Flanker 1, Brute 0; all non-elite; **spread**; delays 0.0, 0.4, 0.8 s; telegraph 0.5 s default.
  - **When not BEGINNER_TEST_MODE and room type COMBAT:** Swarm 1, Flanker 1, Brute 1; all non-elite; **spread**; delays 0.0, 0.4, 0.8 s.
- **Spawn positions:** Spread pattern.  
- **Hazards present:** Yes.  
- **Hazards position:** Same as Room 1.  
- **Special mechanics:** Same spawn delays as Room 2.

### Room 5
- **Room type:** ELITE (when `BEGINNER_TEST_MODE`); otherwise depends on shuffle.  
- **Number of enemies:** 2 (Beginner) or 3 (non-Beginner).  
- **Enemy types:** Beginner: Brute (elite), Swarm. Non-Beginner ELITE: Swarm (elite), Flanker (elite), Brute (elite).  
- **Enemy composition (from code):**
  - **When BEGINNER_TEST_MODE:** `spawn_specs = [(Brute, True, 0.0, None), (Swarm, False, SPAWN_SLOT_DELAY_SEC, None)]`. Counts: Swarm 1, Flanker 0, Brute 1. Brute elite, Swarm non-elite. Spawn distribution: **triangle** (`rtype == RoomType.ELITE` → spawn_triangle). Spawn delays (s): 0.0, 0.4. Telegraph: 0.5 s default.
  - **When not BEGINNER_TEST_MODE and room type ELITE:** `spawn_specs = [(Swarm, True, 0.0, None), (Flanker, True, 0.4, None), (Brute, True, 0.8, None)]`. Counts: Swarm 1, Flanker 1, Brute 1. All elite. Spawn distribution: **triangle** (TRIANGLE_OFFSET_PX = 80). Spawn delays (s): 0.0, 0.4, 0.8.
- **Spawn positions:** Triangle for both Beginner and non-Beginner when room type ELITE (TRIANGLE_OFFSET_PX = 80; one base position then three at base + (0,0), (-80, 80), (80, 80) clamped to playable).  
- **Hazards present:** Yes.  
- **Hazards position:** Same as Room 1.  
- **Special mechanics:** Elite modifiers: HP ×1.4, damage ×1.2. Spawn delays 0.0, 0.4, 0.8 s for non-Beginner.

### Room 6
- **Room type:** AMBUSH (when `BEGINNER_TEST_MODE`); otherwise depends on shuffle.  
- **Number of enemies:** 2 (Beginner) or 3 (non-Beginner).  
- **Enemy types:** Beginner: Swarm, Swarm (both with telegraph 1.5 s). Non-Beginner AMBUSH: Swarm, Flanker, Brute (all non-elite).  
- **Enemy composition (from code):**
  - **When BEGINNER_TEST_MODE:** `spawn_specs = [(Swarm, False, 0.0, 1.5), (Swarm, False, SPAWN_SLOT_DELAY_SEC, 1.5)]`. Counts: Swarm 2, Flanker 0, Brute 0. All non-elite. Spawn distribution: **ambush** (`rtype == RoomType.AMBUSH` → spawn_ambush; radius AMBUSH_SPAWN_RADIUS_PX = 200 px, evenly spaced by angle). Spawn delays (s): 0.0, 0.4. Telegraph: 1.5 s for both slots.
  - **When not BEGINNER_TEST_MODE and room type AMBUSH:** `spawn_specs = [(Swarm, False, 0.0, None), (Flanker, False, 0.4, None), (Brute, False, 0.8, None)]`. Counts: Swarm 1, Flanker 1, Brute 1. All non-elite. Spawn distribution: **ambush**. Spawn delays (s): 0.0, 0.4, 0.8. Telegraph: 0.5 s default.
- **Spawn positions:** Ambush pattern: around player at radius AMBUSH_SPAWN_RADIUS_PX (200 px), evenly spaced by angle; clamped to playable; ensure_valid_spawn_position applied.  
- **Hazards present:** Yes. Wall border thickness 4 (AMBUSH); other rooms 2.  
- **Hazards position:** Same logic; playable area smaller due to border 4.  
- **Special mechanics:** Beginner: telegraph_sec = 1.5 for both slots. Non-Beginner: no telegraph override (0.5 s default).

### Room 7
- **Room type:** MINI_BOSS  
- **Number of enemies:** 1  
- **Enemy types:** MiniBoss (Biome 1 mini boss class).  
- **Enemy composition (from code):**
  - `spawn_specs = [(MiniBoss, False, 2.0, None)]` (same for BEGINNER_TEST_MODE and non-Beginner; `rtype == RoomType.MINI_BOSS`). Counts: Swarm 0, Flanker 0, Brute 0, MiniBoss 1. Spawn distribution: **single** (`len(spawn_specs) == 1 and spawn_specs[0][0] == MiniBoss` → one position from `generate_valid_spawn_position(room, player_center, [], is_elite=False, rng=rng)`). Spawn delay (s): 2.0. Telegraph: 0.5 s default.
- **Spawn positions:** Single position from `generate_valid_spawn_position(room, player_center, [], is_elite=False, rng=rng)` (min distance from player, valid tile).  
- **Hazards present:** Yes (same hazard logic as combat rooms).  
- **Hazards position:** Same as Room 1.  
- **Special mechanics:** Spawn delay 2.0 s. On death: reward heal drop (MINI_BOSS_REWARD_HEAL_PERCENT = 30% of player base_max_hp); after MINI_BOSS_DOOR_UNLOCK_DELAY_SEC (0.5 s) doors unlock.

---

## Room Design & Environment Details

### General Room Layout (Biome 1)
- **Room size (tile/grid dimensions):** All Biome 1 rooms use the same grid from `_room_grid_size()`: width = `LOGICAL_W // TILE_SIZE` (30), height = `LOGICAL_H // TILE_SIZE` (20). So 30 cols × 20 rows. Pixel size: `room.pixel_width` = 960, `room.pixel_height` = 640. Config values `ROOM_SIZE_START`, `ROOM_SIZE_COMBAT`, etc. are NOT IMPLEMENTED in generation.
- **Layout structure:** Single `tile_grid` (list of list of str) per room. Tile types: `TILE_FLOOR`, `TILE_LAVA`, `TILE_SLOW`. Wall band is implicit: `wall_border_thickness(room_type)` tiles from each edge (2 for most types, 4 for AMBUSH). No separate obstacle layer or prop tiles in grid; Room 0 and Safe Room use world-positioned props (altar, dummy, heal object) drawn on top.
- **Collision boundaries:** Playable area from `room.playable_bounds_pixels()` → (min_x, min_y, max_x, max_y) in world pixels. Walls block via `room.is_tile_in_wall_band(tx, ty)`; tiles in wall band block movement in `_resolve_entity_wall_collision`. Lava and slow tiles do NOT block movement; player and enemies clamped to room bounds. Door tiles in wall band are passable when door state is OPEN.
- **Camera behavior:** `camera_offset` (game_scene property): when room is loaded, `ox = (LOGICAL_W - room.pixel_width) / 2.0`, `oy = (LOGICAL_H - room.pixel_height) / 2.0`, return `(-ox, -oy)`. Room is centered on the logical screen; no player-follow camera. `set_camera_target` exists but offset does not use it when room is present.
- **Entry/exit logic:** Doors placed by `_place_doors_for_room(room)`. Exit door: tiles (w-2, w-1) × rows (h-B .. h-1), B = wall_border(); state OPEN for START, else LOCKED; `target_room_index = room.room_index + 1`. Entrance door (room_index > 0): tiles (0, 1) × same rows; state OPEN; `target_room_index = room.room_index - 1`. Transition: player hitbox overlapping open door trigger rect (3×TILE_SIZE door rect inflated by -20 px) triggers `load_room(next_idx)` and player reposition to new room spawn tile.

### Combat Rooms
- **Actual room size:** Same as general: 30×20 tiles (960×640 px). No per-type size in code.
- **Layout pattern:** Open: no obstacle tiles. Tile grid is floor + lava + slow only; walls are the border band. No interior walls or obstacle props in Biome 1 combat rooms.
- **Enemy spawn behavior:** Spawn specs and positions set once when room loads (`_ensure_spawn_system`). Pattern by room type: COMBAT/ELITE → spread or triangle (ELITE); AMBUSH → ambush (radius 200 px, even angle spacing). Positions from `spawn_spread`, `spawn_triangle`, or `spawn_ambush`; each validated with `generate_valid_spawn_position` / `ensure_valid_spawn_position` (playable, floor/lava/slow, min distance from player/doors/walls).
- **Hazard presence:** Yes. Lava and slow placed in playable area (see Section 6). Center 3×3 and door-adjacent zones (DOOR_HAZARD_MARGIN = 3) excluded from hazard placement.
- **Room clear conditions:** `room_type in (RoomType.COMBAT, RoomType.AMBUSH, RoomType.ELITE, RoomType.MINI_BOSS)`. Clear when `(self._spawn_system is None or self._spawn_system.all_spawns_completed()) and len(self._enemies) == 0`. Inactive enemies are removed from `_enemies` each frame (`self._enemies = [e for e in self._enemies if not getattr(e, "inactive", False)]`), so when last enemy goes inactive, next frame count is 0 and clear triggers.
- **Door locking/unlocking logic:** On load, combat rooms get `door_system.close_all()` (exit LOCKED). When room clear condition is met, `room_controller.on_room_clear()` → `door_system.start_unlock_timer()` with `DOOR_UNLOCK_DELAY_SEC` (0.5 s). DoorSystem.update(dt) counts down; at 0 calls `open_all()`. Exit door then OPEN and player can trigger transition.

### Safe Room
- **Does safe room exist?** Yes. Room type SAFE; appears once in Biome 1 (room index 3 when BEGINNER_TEST_MODE, else in shuffled 1–6).
- **Room size:** Same as general: 30×20 tiles.
- **Enemies present:** None. `rtype in (RoomType.START, RoomType.SAFE)` → no spawn_specs.
- **Hazards present:** No lava. Slow: 0–5% of playable cells (`rng.uniform(0, min(0.05, HAZARD_SLOW_MAX_FRACTION))`, n_slow = int(total * slow_pct)).
- **Healing / player recovery:** Heal object at top-left of playable area, tile (wall_border()+2, wall_border()+2). Player within 70 px and pressing H: `hp += base_max_hp * SAFE_ROOM_HEAL_PERCENT` (0.30), capped at `base_max_hp * SAFE_ROOM_OVERHEAL_CAP_RATIO` (1.30). Once per Safe Room (`_safe_room_heal_done`). Health upgrade (when applied): +20% max HP — `SAFE_ROOM_UPGRADE_HEALTH_MULT = 1.20` (game_scene); exact upgrade trigger not fully verified here.
- **Objects present:** One heal object (position only; no separate asset for “heal pad” in code—proximity prompt and H key logic).
- **Visual differences (tiles, lighting, assets):** NOT IMPLEMENTED. Same tile drawing as other rooms (floor/lava/slow from `_draw_room_tiles_and_doors`; no biome_index check for Safe). No dedicated Safe Room background or lighting in code.
- **Special mechanics:** On load, `room_controller.load_room` calls `door_system.open_all()` for SAFE room type, so exit is open immediately (no clear condition).

### Entry Room (Room 0 / Start)
- **Structure:** Room type START. Same 30×20 grid. No lava; no slow in tile grid. Wall border 2. Spawn tile from `_choose_spawn_tile` (center-prefer floor).
- **Enemies or hazards:** 0 hostile enemies. 1 Training Dummy (non-hostile) at fixed tile (min_col, max_row). No lava/slow tiles.
- **Player initialization:** On room load, player position set to `room.world_pos_for_tile(room.spawn_tile[0], room.spawn_tile[1])`. HP set to base_max_hp (1000) when room is START. Altar at room center (world_pos_for_tile(cx, cy), cx = width//2, cy = height//2). Exit trigger rect: (room.pixel_width - 3*TILE_SIZE, 0, 3*TILE_SIZE, 3*TILE_SIZE). Story panel (E/ESC to close). Dummy HP reset to max_hp after each player hit in same frame.

### Mini Boss Room (Biome 1)
- **Room size:** Same as general: 30×20 tiles (960×640 px).
- **Layout:** Same as combat: open tile grid (floor + lava + slow), wall band 2. No special arena geometry.
- **Boss spawn logic:** Single spawn spec `(MiniBoss, False, 2.0, None)`. One world position from `generate_valid_spawn_position(room, player_center, [], is_elite=False, rng=rng)`. Spawn system runs with start_time_sec 2.0 and default telegraph 0.5 s. MiniBoss instantiated and added to _enemies when spawn slot fires.
- **Special mechanics:** Room clear when MiniBoss goes inactive and is removed from list (len(_enemies)==0) and spawns complete → on_room_clear() → door unlock timer 0.5 s. On MiniBoss death (inactive set), game_scene also sets `_mini_boss_death_pos` and adds reward at that position; `_door_unlock_timer = MINI_BOSS_DOOR_UNLOCK_DELAY_SEC` (0.5 s) — when it expires `_doors_unlocked = True` (used for Final Boss; for Mini Boss the actual door open is via on_room_clear → DoorSystem.start_unlock_timer → open_all). Reward collect: overlap with reward pos gives heal MINI_BOSS_REWARD_HEAL_PERCENT (30%) of base_max_hp.

### Boss Room (Biome 1)
- **Boss Room (final boss arena):** NOT IMPLEMENTED in Biome 1. Biome 1 ends with Mini Boss room (Room 7). Final Boss is Biome 4 Room 29 only.

---

## 3. Enemies (Detailed)

### Swarm
- **Role:** melee  
- **HP:** 30 (base). Elite: 30 × 1.4 = 42  
- **Damage:** 10 (base). Elite: 10 × 1.2 = 12  
- **Speed:** 100 px/s (when BEGINNER_TEST_MODE); otherwise 100 px/s (config ENEMY_SWARM_MOVE_SPEED)  
- **Size (sprite size):** (64, 64) — ENEMY_SWARM_SIZE  
- **Attack type:** Melee (hitbox overlap with player in attack state)  
- **Attack radius/offset:** 20.0 px / 20.0 px — ENEMY_SWARM_ATTACK_RADIUS, ENEMY_SWARM_ATTACK_OFFSET  
- **Attack cooldown:** 1.2 s — ENEMY_SWARM_ATTACK_COOLDOWN_SEC  
- **Movement behavior:** Chase player; stop at ENEMY_SWARM_STOP_DISTANCE (40 px). Clamped to room playable bounds. Contact damage every ENEMY_CONTACT_DAMAGE_INTERVAL_SEC (0.5 s) while overlapping.  
- **Special abilities:** None. Anti-stuck: after STUCK_FRAME_COUNT (20) frames with movement < STUCK_MOVEMENT_THRESHOLD_PX (3 px), velocity rotated by random ±70°.

### Flanker
- **Role:** melee (fast)  
- **HP:** 22 (base). Elite: 30.8  
- **Damage:** 8 (base). Elite: 9.6  
- **Speed:** When BEGINNER_TEST_MODE: int(PLAYER_MOVE_SPEED * 0.85) = 187 px/s; otherwise 260 px/s  
- **Size:** (56, 56) — ENEMY_FLANKER_SIZE  
- **Attack type:** Melee  
- **Attack radius/offset:** 16.0 px / 18.0 px — ENEMY_FLANKER_ATTACK_RADIUS, ENEMY_FLANKER_ATTACK_OFFSET  
- **Attack cooldown:** 1.0 s  
- **Movement behavior:** Same as Swarm (chase, stop at 50 px, contact damage, bounds clamp, anti-stuck).  
- **Special abilities:** None.

### Brute
- **Role:** melee (slow, high HP/damage)  
- **HP:** 50 (base). Elite: 70  
- **Damage:** 10 (base). Elite: 12  
- **Speed:** When BEGINNER_TEST_MODE: int(PLAYER_MOVE_SPEED * 0.65) = 143 px/s; otherwise 120 px/s  
- **Size:** (96, 96) — ENEMY_BRUTE_SIZE  
- **Attack type:** Melee (slam animation folder)  
- **Attack radius/offset:** 26.0 px / 22.0 px — ENEMY_BRUTE_ATTACK_RADIUS, ENEMY_BRUTE_ATTACK_OFFSET  
- **Attack cooldown:** 1.5 s  
- **Movement behavior:** Chase, stop at 60 px; same contact damage and bounds; anti-stuck.  
- **Special abilities:** None.

### Training Dummy (Room 0 only)
- **Role:** non-hostile (practice target)  
- **HP:** 9999 (display); reset to max_hp after each player hit (same update frame).  
- **Damage:** 0  
- **Speed:** 0 (does not move)  
- **Size:** (96, 128) — DUMMY_SIZE  
- **Attack type:** None  
- **Attack cooldown:** N/A  
- **Movement behavior:** None  
- **Special abilities:** None. Hitbox used for player short/long attack and dash practice.

---

## 4. Mini Boss (Biome 1)

- **Name:** MiniBoss (class MiniBoss; assets prefix `mini_boss_1`)  
- **Size (sprite):** (128, 128) — MINI_BOSS_SIZE  
- **HP:** 200 — MINI_BOSS_BASE_HP  
- **Phases:** Single phase in code (no phase_change state used in update logic; dash/windup/phase_change exist in animation states but are not triggered by AI).  
- **Attack patterns:** Melee only. States attack_01 and attack_02 alternate when in range; attack when attack_cooldown_timer <= 0. Combat system sets attack_cooldown_timer = MINI_BOSS_ATTACK_COOLDOWN_SEC (2.0 s) when hit connects. No dash or windup in update.  
- **Movement:** Chase player at MINI_BOSS_MOVE_SPEED (100 px/s normally; when BEGINNER_TEST_MODE: int(PLAYER_MOVE_SPEED * 0.75) = 165 px/s). Stop at MINI_BOSS_STOP_DISTANCE (70 px). Confined to room_rect. Facing: left/right by player position.  
- **Special mechanics:** No contact damage (combat via attack_01/attack_02 only). No summons. On death: inactive = True; door unlock after MINI_BOSS_DOOR_UNLOCK_DELAY_SEC (0.5 s); reward heal 30% base_max_hp.  
- **Speed:** 100 px/s (or 165 when BEGINNER_TEST_MODE). MINI_BOSS_DASH_SPEED (180) is in config but **NOT IMPLEMENTED** in MiniBoss update (no dash state transition).

---

## 5. Player Configuration

- **Player HP:** 1000 — PLAYER_BASE_HP. base_max_hp and max_hp set to this on init and on Room 0 spawn.  
- **Movement speed:** 220 px/s — PLAYER_MOVE_SPEED  
- **Dash mechanics:** PLAYER_DASH_SPEED_MULT = 2.2, PLAYER_DASH_DURATION_SEC = 0.18, PLAYER_DASH_COOLDOWN_SEC = 0.90  
- **Attack types:** Short (LMB), Long (RMB). Block = J, Parry = K.  
- **Damage values:** PLAYER_SHORT_ATTACK_DAMAGE = 10, PLAYER_LONG_ATTACK_DAMAGE = 8  
- **Cooldowns:** Short: windup 0.12 s, active 0.10 s, recovery 0.18 s. Long: windup 0.20 s, cooldown 0.60 s.  
- **Ranges:** Short melee 48 px; long (projectile) 192 px  
- **Scaling logic:** PLAYER_ATTACK_LEVEL_STEP = 0.10 (+10% damage per level); exact level application not extracted in this spec. Block: PLAYER_BLOCK_DAMAGE_FACTOR = 0.5. Parry window: PLAYER_PARRY_WINDOW_SEC = 0.12  

---

## 6. Hazards

### Lava
- **Name:** Lava (tile type TILE_LAVA)  
- **Damage:** 6 per second — LAVA_DAMAGE_PER_SECOND. Applied per frame via hazard system (damage_per_second_for_lava()).  
- **Trigger condition:** Player standing on lava tile (tile_at_world checked each frame).  
- **Placement logic:** Deterministic. Room type START/SAFE: no lava. Other rooms: n_lava cells chosen from shuffled playable cells (excluding center 3×3 and door-adjacent zones). When BEGINNER_TEST_MODE: lava_cap = total * 0.03 (0–3%). Otherwise: lava_cap = total * HAZARD_LAVA_MAX_FRACTION (0.05). n_lava = randint(0, lava_cap).  
- **Tile interaction:** Grid value TILE_LAVA. Animation: 3 frames at 6 FPS — LAVA_ANIM_FRAMES, LAVA_ANIM_FPS.

### Slow
- **Name:** Slow (tile type TILE_SLOW)  
- **Damage:** 0  
- **Trigger condition:** Player movement over slow tile; speed multiplied by SLOW_TILE_SPEED_FACTOR (0.75). Dash ignores slow.  
- **Placement logic:** Same shuffle/cell exclusion as lava. START: no slow. SAFE: slow_pct in [0, min(0.05, HAZARD_SLOW_MAX_FRACTION)], n_slow = int(total * slow_pct). When BEGINNER_TEST_MODE, non-START/non-SAFE rooms: slow tiles are 5–8% of playable cells (slow_min = int(total * 0.05), slow_max = int(total * 0.08)). Other rooms (non-Beginner): slow_min = total * 0.05, slow_max = total * 0.10; n_slow = randint(slow_min, min(slow_max, total - n_lava)).  
- **Tile interaction:** Grid value TILE_SLOW. No animation in config for slow tile.

### Door / safe zones
- **DOOR_HAZARD_MARGIN:** 3 tiles. No lava/slow placed in exit zone (right/bottom) or entrance zone (left/bottom) within margin.  
- **Center safe zone:** 3×3 around playable center excluded from lava/slow (except SAFE which has no lava and minimal slow).

---

## 7. AI Director / Scaling (if present)

- **Difficulty scaling rules:** NOT IMPLEMENTED. No per-room intensity or difficulty curve in code.  
- **Enemy adjustment logic:** Elite flag only (HP ×1.4, damage ×1.2) when spawn_specs set elite=True. No per-room stat scaling.  
- **Reinforcement logic:** NOT IMPLEMENTED for Biome 1 (no mid-room spawns).  
- **Player state mapping (struggling/stable/etc.):** NOT IMPLEMENTED.

---

## 8. RNG / Seed Behavior

- **Is seed used?** Yes. SEED = 42 (config).  
- **What does it control?**  
  - Room order (Biome 1): when BEGINNER_TEST_MODE is False, shuffle of [COMBAT, COMBAT, COMBAT, SAFE, ELITE, AMBUSH] via `random.Random(seed)`.  
  - Tile grid (lava/slow): `random.Random(seed + room_index * 1000)` for cell shuffle and n_lava/n_slow.  
  - Spawn positions: `random.Random(SEED + room.room_index * 10000)` in game_scene.  
  - **RNG clarification (config SEED vs RoomController._seed):** Spawn RNG uses the config constant `SEED`. Room order and tile grid use the seed passed to `generate_room` (`RoomController._seed`). `RoomController(SEED)` in game_scene matches today; if a run-specific seed were passed to RoomController, room order and hazards would use `_seed` while spawn positions would still use config `SEED`.  
  - Player spawn tile: _choose_spawn_tile uses deterministic order (center-first then row/col scan); no extra seed.  
  - Heal drop chance: HEAL_DROP_CHANCE (0.25) used elsewhere; seed not re-checked in this extraction for heal drops.

---

## 9. Missing / Incomplete Features

- **Room dimensions:** Config defines ROOM_SIZE_START, ROOM_SIZE_COMBAT, etc. These are **NOT IMPLEMENTED**. All rooms use _room_grid_size() = (30, 20) (viewport-based).  
- **Mini Boss dash/phase_change:** MINI_BOSS_DASH_SPEED and animation states dash, windup, phase_change exist; **dash and phase change are not used** in MiniBoss update (no state transitions to them).  
- **Biome 1–specific spawn table:** When BEGINNER_TEST_MODE is False, COMBAT and AMBUSH both use the same spawn list (Swarm, Flanker, Brute) with elite=False for COMBAT/AMBUSH and elite=True only for ELITE. Room 6 (AMBUSH) does not use a different enemy set than COMBAT, only a different spawn pattern (ambush) and wall border 4.  
- **Per-room enemy count variation:** Non-Beginner Biome 1 always uses 3 enemies for COMBAT/AMBUSH and 3 for ELITE. No room-index–specific counts.  
- **Visual identity / palette:** No code reference to Biome 1–specific palette (e.g. Ash Dungeon, torchlight). Background and visuals are generic or shared.  
- **Ambient particles (ember/ash):** NOT IMPLEMENTED in Biome 1 (no particle count/speed in code for Biome 1).  
- **Safe Room health upgrade (+20% max HP, not +30%):** `SAFE_ROOM_UPGRADE_HEALTH_MULT = 1.20` (game_scene). Logic applies in Safe Room in some branches (e.g. upgrade picks). Exact trigger (H key vs interact) and single-use behavior are in game_scene; not all Safe Room upgrade paths re-verified for this spec.
