# BIOME 4 — FULL IMPLEMENTATION SPEC

**Source:** Extracted from current codebase only. No invented values.

---

## 1. Dungeon Structure

- **Total number of rooms (Biome 4 segment):** `BIOME4_ROOM_COUNT` = 6 (`total_biome4_rooms()`).
- **Campaign room indices:** 24–29 inclusive (`BIOME4_START_INDEX` = 24). Last room index = `total_campaign_rooms() - 1` when `USE_BIOME4` is True.
- **Room sequence:**
  - **When `BEGINNER_TEST_MODE` is True:** Fixed order via `room_order_biome4`: index 24 → COMBAT, 25 → COMBAT, 26 → AMBUSH, 27 → ELITE, 28 → SAFE, 29 → FINAL_BOSS.
  - **When `BEGINNER_TEST_MODE` is False:** `random.Random(seed).shuffle(mid)` on `mid = [COMBAT, COMBAT, AMBUSH, ELITE, SAFE]`; then append `[FINAL_BOSS]`. Seed: `room_order_biome4(SEED)` from **`dungeon/room.py`** campaign room factory (same `SEED` as `_make_tile_grid`).
- **Types of rooms in Biome 4:** COMBAT, AMBUSH, ELITE, SAFE, FINAL_BOSS (no START, MINI_BOSS, CORRIDOR in this segment).
- **Entry room (first Biome 4):** Campaign index 24. Type from sequence above. Player spawn: `room.spawn_tile` via `_choose_spawn_tile`; position `world_pos_for_tile(spawn_tile)`.
- **Final room:** Campaign index 29, type FINAL_BOSS. Boss entity not from spawn system; spawned by `game_scene` after `BIOME4_FINAL_BOSS_SPAWN_DELAY_SEC` (2.0 s).
- **Transition from Biome 3:** Campaign index 23 is last Biome 3 room when `USE_BIOME3`; entering door to index 24 loads Biome 4 first room (`biome_index` = 4, `room_order_biome4`).

---

## 2. Room-wise Breakdown

**Grid:** Same as global campaign: `_room_grid_size()` → `LOGICAL_W // TILE_SIZE` × `LOGICAL_H // TILE_SIZE` (30 × 20 tiles, 960×640 px). Same as Biome 1/2/3.

**Local index** = `campaign_index - BIOME4_START_INDEX` (0–5). **`get_biome4_spawn_specs(room_idx, room_type, ...)`** uses **`room_idx` 0–4** (not Beginner-only): order of checks is **index-specific branches first**, then **fallback by `room_type`**.

**After shuffle:** campaign 24–28 are **not** tied to “Room 24 composition”; e.g. campaign 24 may be SAFE. Composition is always **`get_biome4_spawn_specs(local_idx, actual_room_type)`**.

### `room_idx == 0` + COMBAT
- **Enemies:** 4 — Swarm, Flanker, Ranged, Heavy (non-elite). Delays 0.0, 0.4, 0.8, 1.2 s. **spread**. Telegraph default 0.5 s.

### `room_idx == 1` + COMBAT
- **Enemies:** 3 — Brute, Ranged, Heavy (non-elite). Delays 0.0, 0.4, 0.8 s. **spread**. Telegraph 0.5 s.

### `room_idx == 2` + AMBUSH
- **Enemies:** 3 — Swarm, Flanker, Ranged. Telegraph **1.5 s** all slots. **ambush** r=160. Wall border 4.

### `room_idx == 3` + ELITE
- **Enemies:** Brute elite, Heavy elite, Ranged non-elite. **triangle** offset `BIOME4_TRIANGLE_OFFSET_PX` = 200/√2 (~141.42 px). Delays 0, 0.4, 0.8 s.

### Fallback by type (any local index if no branch above matched)
- **ELITE:** Same list as `room_idx == 3` + ELITE (Brute+, Heavy+, Ranged; triangle).
- **AMBUSH:** Same as `room_idx == 2` + AMBUSH (Swarm, Flanker, Ranged; 1.5 s; ambush 160 px).
- **COMBAT:** Swarm, Flanker, Ranged, Heavy; **spread**; delays 0, 0.4, 0.8, 1.2 s — applies when COMBAT at **local 2, 3, or 4** (locals 0–1 use the two COMBAT branches above instead).

### SAFE (any local index 0–4)
- **Enemies:** 0. Hazards: no lava; slow 0–5% playable (`_make_tile_grid`). Heal tile + H same as other SAFE rooms.
- **Dual-upgrade (keys 1–4, two picks):** only if **`current_room_index == BIOME4_SAFE_ROOM_INDEX` (28)** **and** player presses H there (room must be SAFE). See §10. **Beginner** order puts SAFE at campaign 28; **if SAFE shuffles to 24–27, that flow never runs** for any room.

### Room 29 (local 5) — FINAL_BOSS
- **Room type:** FINAL_BOSS.
- **Spawn specs:** `[]` — no spawn-system enemies.
- **Boss:** `FinalBoss` at world center of room grid `(width//2, height//2)` after timer; see §7.
- **Hazards:** FINAL_BOSS tile caps in `_make_tile_grid`: lava ≤10% playable, slow ≤15%, combined hazard cap 65% playable (so ≥35% safe floor).
- **Door unlock:** After boss `inactive` and `MINI_BOSS_DOOR_UNLOCK_DELAY_SEC` (0.5 s) path sets `_doors_unlocked` and `on_room_clear` for FINAL_BOSS (see game_scene).

### Shuffled mode summary
- Locals **0–1** + COMBAT keep **distinct** lineups (4-enemy vs Brute/Ranged/Heavy). Locals **2–4** + COMBAT use **fallback** four-enemy spread.
- **ELITE** at local 3 matches fallback ELITE (same composition). **AMBUSH** at local 2 matches fallback AMBUSH (same composition).
- **SAFE** at any index: heal + H. **Dual-upgrade UI only at campaign index 28** when that room is SAFE and player heals there. **SAFE at 24–27:** after H, **`_safe_room_upgrade_pending`**; keys **1 or 2** clear pending **with no stat upgrades** (not Biome 3 Room 21 panel; not four-option panel).

---

## 3. Room Design & Environment

- **Room size:** 30×20 tiles; pixel width/height = `TILE_SIZE` × dimensions (32 px/tile → 960×640). Same as Biome 1/2/3.
- **Layout:** `tile_grid` floor / lava / slow; wall band via `wall_border_thickness(room_type)`.
- **Collision / playable bounds:** `room.playable_bounds_pixels()`; Final Boss uses `room_rect` from this for movement clamp and meteor bounds.
- **Camera:** Same as Biome 1 — room centered; `camera_offset` from room vs logical size.
- **Entry/exit:** Same door system as campaign (`_place_doors_for_room`, trigger overlap).
- **Biome 4 visuals:** `get_biome4_background(room_index)` — room 29 uses boss arena backdrop (`_bg_boss`); others `_bg_room` (`biome4_room_bg.png`). Props via `get_biome4_prop_placements`; blocking tiles merged into `_biome4_blocking_tiles` for movement/spawn (`_tile_blocks_movement`, `_ensure_biome4_blocking_tiles`).
- **FINAL_BOSS arena:** Same grid generation with stricter hazard caps; boss spawn at geometric room center in tile space converted to world.

---

## 4. Enemies (Detailed)

### Swarm, Flanker, Brute, Heavy, Ranged
- **Same as Biome 1/2/3** for base stats, melee/ranged behavior; elite uses **`ENEMY_ELITE_HP_MULT`** (1.4) and **`ENEMY_ELITE_DAMAGE_MULT`** (1.2) on base HP/damage where `elite=True`, contact damage intervals, etc.

### Final Boss (`FinalBoss`, `enemy_type` = `"final_boss"`)
- **New** to Biome 4 (class `entities.final_boss.FinalBoss`).
- **Role:** Final encounter only.
- **HP:** `FINAL_BOSS_HP` = 480 (phase 1→2 on same pool); after first death revive: `FINAL_BOSS_REVIVE_HP` = 50 (`max_hp` and `hp` set on revive).
- **Damage (melee teleport strike):** `enemy.damage` = `FINAL_BOSS_TELEPORT_STRIKE_DAMAGE` = 24 (used by `apply_enemy_attacks` on teleport strike frame).
- **Contact damage (overlap):** Handled only in `game_scene`: 128×128 rect centered on boss (`ex±64`), interval 0.5 s; `FINAL_BOSS_CONTACT_DAMAGE` = 18 unless `_revived` then `FINAL_BOSS_CONTACT_DAMAGE_REVIVE` = 15. States `revive_wait` skip contact.
- **Speed:** Phase 1 `FINAL_BOSS_MOVE_SPEED` = 135; phase 2 `FINAL_BOSS_MOVE_SPEED_PHASE2` = 175; post-revive `FINAL_BOSS_MOVE_SPEED_REVIVE` = 190. Rush speed `FINAL_BOSS_RUSH_SPEED` = 260 is **never applied** in code (`_rush_timer` only decrements, never set positive) — **NOT IMPLEMENTED** as behavior.
- **Size:** `FINAL_BOSS_SIZE` = (128, 128).
- **Attack types:** Fireball + lava wave (projectiles), meteor (scene-level impacts), teleport strike (melee frame), phase-change adds.
- **`FINAL_BOSS_ATTACK_RADIUS` (40) / `FINAL_BOSS_ATTACK_OFFSET` (50):** In `apply_enemy_attacks`, teleport strike hit requires **`state == attack2`**, **`_teleport_strike_damage_frame`**, and player within **40 px** of point **offset 50 px** from boss toward player (same melee pipeline as other enemies). Cooldown after hit uses **`FINAL_BOSS_ATTACK_COOLDOWN_SEC`** from `_enemy_attack_params`.
- **Boss** also sets its own **`attack_cooldown_timer`** when starting attacks (separate from that melee cooldown application).

---

## 5. Enemy Composition by Room

| Campaign index (Beginner order) | Type | Matches `get_biome4_spawn_specs` branch |
|----------------------------------|------|----------------------------------------|
| 24 (local 0) | COMBAT | `room_idx 0` + COMBAT |
| 25 (local 1) | COMBAT | `room_idx 1` + COMBAT |
| 26 (local 2) | AMBUSH | `room_idx 2` + AMBUSH (= fallback AMBUSH) |
| 27 (local 3) | ELITE | `room_idx 3` + ELITE (= fallback ELITE) |
| 28 (local 4) | SAFE | — |
| 29 (local 5) | FINAL_BOSS | FinalBoss (timer spawn) |

**Shuffled:** Types permute across 24–28; composition = **`get_biome4_spawn_specs(local_idx, type)`** as §2 (locals 0–1 COMBAT differ from locals 2–4 COMBAT).

**Differences from earlier biomes:** Heavy + Ranged appear in Biome 4 combat lineups; ambush uses `BIOME4_AMBUSH_RADIUS_PX` 160 (Biome 1 ambush uses `AMBUSH_SPAWN_RADIUS_PX` 200 where applicable). Elite triangle uses `BIOME4_TRIANGLE_OFFSET_PX` vs Biome 1 `TRIANGLE_OFFSET_PX` 80.

---

## 6. Mini Boss (if present)

- **NOT IMPLEMENTED** as a dedicated MINI_BOSS room type in Biome 4 sequence. Final encounter is FINAL_BOSS only.

---

## 7. FINAL BOSS

### Core Stats
- **HP:** 480 until first death; revive segment 50 HP (`FINAL_BOSS_REVIVE_HP`). Second death → `inactive`.
- **Speed:** 135 → 175 at 50% HP threshold; 190 after revive.
- **Stop distance:** `FINAL_BOSS_STOP_DISTANCE` = 160 px (movement stops closer; fireball chosen when `dist >=` this).
- **Phase transition:** When `not _revived and not _phase2 and hp <= max_hp * 0.5`: `_phase2 = True`, `move_speed = FINAL_BOSS_MOVE_SPEED_PHASE2`, state `phase_change`, `_phase_change_invuln_timer = BOSS_PHASE_CHANGE_INVULN_SEC` (2.0 s), `_pending_adds = True`, `_adds_spawned = True` (**`_adds_spawned` is never read** elsewhere — unused flag), `_cycle_index = 0`.

### Movement
- **Chase:** When in idle/walk chase logic, moves if `dist > FINAL_BOSS_STOP_DISTANCE` and `_attack_recovery_timer <= 0`. **`attack_cooldown_timer` does not block** this movement (only gates starting a new attack from the cycle).
- **Phase 2 fireball:** During `attack1` after telegraph elapses (`_pending_fireball_dir is None`), boss moves toward player while `dist > FINAL_BOSS_STOP_DISTANCE` with clamp **64 px inset** from `room_rect` left/right/top/bottom.
- **Teleport:** Repositions via `_start_teleport_strike` (see below).

### Attack Patterns (deterministic cycle)

**Cycles (tuples in `final_boss.py`):**
- **Phase 1:** `PHASE1_CYCLE` = (`fireball`, `lava_wave`, `fireball`, `teleport_strike`, `fireball`).
- **Phase 2:** `PHASE2_CYCLE` = (`teleport_strike`, `fireball`, `meteor_rain`, `lava_wave`, `fireball`).
- **After revive:** `REVIVE_CYCLE` = (`teleport_strike`, `fireball`, `meteor_rain`) — no lava_wave.

**Cycle advancement:** `_advance_cycle()` on attack anim finish (or skip). If `teleport_strike` chosen but `_teleport_cooldown_timer > 0`, skip to next attack index.

#### Fireball
- **Targeting at release:** Direction = normalize(`player.world_pos - boss.world_pos`) at frame telegraph ends (not initial telegraph aim).
- **Telegraph:** `BOSS_TELEGRAPH_FIREBALL_PHASE1` = 0.45 s or `BOSS_TELEGRAPH_FIREBALL_PHASE2` = 0.35 s.
- **On cast:** `Projectile` 24×24, `FINAL_BOSS_FIREBALL_SPEED` = 300, `FINAL_BOSS_FIREBALL_LIFETIME_SEC` = 3.0, `FINAL_BOSS_FIREBALL_DAMAGE` = 20, `ignore_obstacles=True`.
- **Frequency:** On fireball start, `attack_cooldown_timer = FINAL_BOSS_FIREBALL_CAST_COOLDOWN` (**config value `2`**, integer). Recovery after anim: `BOSS_ATTACK_RECOVERY_FIREBALL_PHASE1` 0.2 / Phase2 0.12 / revive `FINAL_BOSS_ATTACK_RECOVERY_FIREBALL_REVIVE` 0.1.
- **Range gate:** Only starts if `dist >= FINAL_BOSS_STOP_DISTANCE` (160). **`FINAL_BOSS_FIREBALL_RANGE_MIN` / `FINAL_BOSS_FIREBALL_RANGE_MAX`** exist in config but **not used** in boss logic.

#### Lava wave
- **Range:** `FINAL_BOSS_WAVE_RANGE_MIN` = 80 ≤ dist ≤ `FINAL_BOSS_WAVE_RANGE_MAX` = 350.
- **Telegraph:** `BOSS_TELEGRAPH_LAVA_PHASE1` = 0.5 s or Phase2 = 0.4 s.
- **Projectile:** 64×64, damage 22, speed **280**, lifetime **2.0**. **`ignore_obstacles` not set** (False). **`Projectile.update`** moves in a straight line with **no wall/prop checks** (same as lava; **fireball** alone sets **`ignore_obstacles=True`** for any code path that respects it).

#### Meteor rain
- **State:** `special` animation.
- **Telegraph until impact:** `BOSS_TELEGRAPH_METEOR_PHASE1` = 0.85 s; Phase2 and revive use `BOSS_TELEGRAPH_METEOR_PHASE2` = 0.7 s.
- **Targets:** 3 positions; offsets from player at cast time: (0,0), (80,0), (-48,64) then rotated by angle `(step % 7) * 0.45` rad; `step = int(_time * 10) % 100`; clamped to room_rect ±48 px; snapped to valid tiles (`TILE_FLOOR`, `TILE_LAVA`, `TILE_SLOW`, not wall band).
- **Impact:** `game_scene` queues `_meteor_impacts` with `trigger_at = _room_time + telegraph_sec`, radius **64**, damage `FINAL_BOSS_METEOR_DAMAGE` = 18. Display ring 0.4 s after trigger.
- **Phase 2 / revived:** During meteor telegraph, at **0.35 s** into state, one extra fireball toward current player (same projectile stats as main fireball).

#### Teleport strike
- **Range gate:** `FINAL_BOSS_TELEPORT_RANGE_MIN` = 100 ≤ dist ≤ `FINAL_BOSS_TELEPORT_RANGE_MAX` = 340.
- **Telegraph:** `BOSS_TELEGRAPH_TELEPORT_PHASE1` = 0.5 s / Phase2 = 0.4 s in `teleport_telegraph` state.
- **Destination:** Each attempt uses **`random.Random(SEED + room_index * 1000 + int(self._time * 10))`** (new RNG per `_start_teleport_strike` call with that seed). 60% “behind” player (π ± 0.55 from player facing), else uniform angle; radius uniform **96–176** or **96–216** px; clamp room_rect ±80; up to 12 tries with `block_check`; `FINAL_BOSS_TELEPORT_COOLDOWN_SEC` = 2.5 after start.
- **Strike:** Warp → `attack2` + `_teleport_strike_damage_frame`; damage via **`apply_enemy_attacks`** as in §4 (**radius 40, offset 50**, 24 dmg).

#### Summon animation state
- **`summon` state** exists in anim map; **no cycle step selects summon** — phase change uses `_pending_adds` only. **NOT IMPLEMENTED** as named “summon” attack state transition.

### Attack Cycle Order
- Strict tuple order per phase; index wraps; teleport skipped if on cooldown.

### Phase System
- **Phase 1:** First cycle tuple; speed 135.
- **Phase 2:** Second tuple; speed 175; on entry adds 2 Swarm + 1 Flanker (see below); 2 s invuln anim.
- **Post-revive:** Third tuple; speed 190; cooldowns `FINAL_BOSS_ATTACK_COOLDOWN_REVIVE` = 0.6, recovery `FINAL_BOSS_ATTACK_RECOVERY_REVIVE` = 0.15.

### Revive Mechanic
- **When:** First time HP reaches 0: `death` anim to end → `revive_wait` (not inactive). Second death (`_revived` True): `inactive` after death anim.
- **Timer:** `FINAL_BOSS_REVIVE_DELAY_SEC` = 2.0 s in `revive_wait`; then position = center of `room_rect`, HP 50, `_revived = True`, `_revive_invuln_timer = FINAL_BOSS_REVIVE_INVULN_SEC` (1.5 s).
- **Once:** `_revive_used` guard; only one revive segment.

### AI Behavior
- **Attacks while moving:** Phase 2 during fireball cast (after telegraph) moves while closing.
- **Chase:** Yes when not in special states and recovery allows.
- **Pause:** Attack animations and telegraphs block new attacks; recovery timers between actions.

### Ally/Enemy Spawn
- **On phase 2 entry:** `game_scene` loop: when any enemy has `_pending_adds`, spawns **2× Swarm + 1× Flanker** at radius **120** px angles 0, 2π/3, 4π/3 around boss; `ensure_valid_spawn_position`; non-elite. Same code path comment as Biome 3 miniboss adds.

### UI / Feedback
- **Health bar:** `BIOME4_BOSS_UI_ANCHOR_*` (x centered−200, y 10, w 400, h 60); fill scaled by `hp/max_hp`. Shown while boss not `inactive` (includes teleport/revive_wait for bar visibility rule: boss hidden in `revive_wait` draw but bar logic uses `not inactive` — during revive_wait boss `draw` returns early; health bar still shows if `final_boss` in list and not inactive).
- **Name banner:** Above bar when assets loaded.
- **Revive text:** `"THE BOSS RISES AGAIN"` when `state == revive_wait` first frame sets `_boss_revive_message_until = _room_time + FINAL_BOSS_REVIVE_MESSAGE_DURATION_SEC` (1.5 s).
- **Telegraphs / meteor targets:** `_draw_boss_telegraphs_and_meteor_targets` for FINAL_BOSS room.
- **Spawn VFX:** `_boss_spawn_fx_timer` = 1.2 s at spawn; death FX 2.0 s at death positions.

### Death Behavior
- **Final death:** Boss removed from `_enemies` when `inactive`; reward at death world pos; `_door_unlock_timer = MINI_BOSS_DOOR_UNLOCK_DELAY_SEC` (0.5 s); when timer expires `_doors_unlocked` and `on_room_clear` if FINAL_BOSS.
- **Player attacks:** No damage during `_revive_invuln_timer > 0` or `state == revive_wait`.

### Rewards
- **Heal pickup:** Same reward orb as mini boss path; on FINAL_BOSS room `FINAL_BOSS_REWARD_HEAL_PERCENT` = **0.40** of `base_max_hp` (capped to `base_max_hp` in heal line: `min(base_max_hp, hp + base_max_hp * heal_pct)`).

### Victory Flow
- **Trigger:** Player overlaps exit door with `target_room_index > cur_idx` and `current_room_index == total_campaign_rooms() - 1` → `_victory_phase = True`, `_victory_timer = 0`.
- **Timeline (`_victory_timer`):** **0–2 s:** centered **`victory_banner`** only (no full-screen bg in that phase). **2–5 s:** black fill + **`victory_screen_bg`** centered. **≥5 s:** `switch_to_start()`.
- **Input:** Ignored during `_victory_phase`.

---

## 8. Player Configuration

- **Same as Biome 1** for base movement, dash, attacks, config-driven stats unless modified by prior biomes or **dual-upgrade picks at campaign room 28** (`move_speed_mult`, `attack_damage_mult`, `damage_taken_mult`, `base_max_hp`).

---

## 9. Hazards

- **Lava / slow tiles:** Same tile damage as global (`LAVA_DAMAGE_PER_SECOND`, etc.). FINAL_BOSS room: caps in §2.
- **Biome 4 hazard overlays:** Optional lava/slow overlays from `biome4_visuals` when drawing.
- **Otherwise:** Same as earlier biomes for non–FINAL_BOSS rooms (standard `_make_tile_grid` fractions).

---

## 10. Safe Room

- **Exists:** One SAFE among Biome 4 rooms 24–28 (fixed at campaign **28** in Beginner order).
- **Dual-upgrade (four options, pick 2 with keys 1–4):** Runs **only** when **`current_room_index == 28`** **and** room type is **SAFE** **and** player uses **H** at heal spot. Then `_safe_room_biome4_picks_remaining = 2`; upgrades use **`SAFE_ROOM_UPGRADE_*`** in `game_scene` (1.20, 1.10, 1.12, 0.88). **If SAFE shuffles to 24–27, this entire dual-upgrade feature never appears** in that run (no other index enables the four-option panel).
- **SAFE at campaign 24–27:** H heal (`SAFE_ROOM_HEAL_PERCENT` 0.30, `"+30% Health"` VFX). **`_safe_room_upgrade_pending = True`** but **no** Biome 3 Room 21 UI (index 21 only). **No** four-option panel. **Keys 1 or 2** clear `_safe_room_upgrade_pending` **without** stat upgrades.

---

## 11. Rewards / Recovery System

- **Combat room clear:** Same as Biome 1 — `HEAL_DROP_CHANCE` roll `SEED + current_room_index * 100`; not in START/SAFE; **FINAL_BOSS not in** `is_combat_room` tuple — no room-clear heal drop from that path in boss room.
- **Mini boss:** N/A in Biome 4.
- **Final boss:** 40% max HP heal orb; 0.5 s door unlock then clear.

---

## 12. AI Director / Scaling

- **Biome 4-specific director:** NOT IMPLEMENTED. Enemy counts fixed by room type + local index rules.

---

## 13. RNG / Seed Behavior

- **`room_order_biome4(SEED)`:** Shuffles middle five room types (non-Beginner).
- **Room tiles:** `_make_tile_grid(..., campaign_index, seed)` with `seed = SEED`.
- **Spawn positions:** `random.Random(SEED + room_index * 10000)` for Biome 4 spawn patterns.
- **Final boss teleport:** `random.Random(SEED + room_index * 1000 + int(_time * 10))` inside `_start_teleport_strike`.
- **Meteor target rotation:** `step = int(_time * 10) % 100`; angle **`(step % 7) * 0.45`** rad (deterministic). Code assigns **`rng = _make_rng(room_index, step)`** in `_start_meteor_rain` but **does not use `rng`** for placement.
- **Prop placements:** `get_biome4_prop_placements(..., SEED)`.

---

## 14. Missing / Incomplete Features

- **`FINAL_BOSS_FINAL_DEATH_DELAY_SEC` (0.5):** Defined in config; **not referenced** in codebase.
- **`FINAL_BOSS_RUSH_SPEED` / `FINAL_BOSS_RUSH_DURATION_SEC`:** `_rush_timer` never set > 0 — rush **not active**.
- **`FINAL_BOSS_FIREBALL_RANGE_MIN` / `FINAL_BOSS_FIREBALL_RANGE_MAX`:** Imported in `final_boss.py`, **unused**.
- **`FINAL_BOSS_METEOR_TARGETS` / `FINAL_BOSS_METEOR_SPACING_PX`:** Imported; placement uses hardcoded 3 impacts and module constant `METEOR_TARGET_SPACING_PX` = 80 — config spacing/target count **unused** for layout.
- **`BOSS_SPAWN_IDLE_DELAY` (0.6 s):** In **`spawn_idle`**, **`_set_state("idle")`** runs immediately, so **`state` leaves `spawn_idle` on the first update** and **`_spawn_idle_timer` is no longer decremented**. **Observed behavior:** post-spawn delay is **not enforced**; class docstring “0.75 s” also does not match config.
- **`summon` animation state:** No attack cycle entry — unused as gameplay state.
- **`BIOME4_BOSS_TELEGRAPH_FIREBALL_SEC`:** Legacy comment in config; phase telegraphs use `BOSS_TELEGRAPH_*`.
- **Meteor `_start_meteor_rain`:** **`rng = _make_rng(...)`** is **dead** (unused variable).

---

*End of Biome 4 full implementation spec.*
