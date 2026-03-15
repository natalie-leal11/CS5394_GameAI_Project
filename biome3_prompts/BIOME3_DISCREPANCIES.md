# Biome 3 implementation — discrepancies and decisions

## Phase 1 (Ranged + projectile) — done

### Phase 1 approval (canonical decisions)

- **Use the existing projectile assets already present in the repo:**
  - `assets/entities/projectiles/enemy_projectile_16x16.png`
  - `assets/entities/projectiles/enemy_projectile_trail_16x16.png`
- **Trail:** The trail should be rendered if the projectile system supports it. (Current implementation uses the main projectile sprite only; trail rendering can be added when the projectile system supports it.)
- **Do not use boss projectile assets** for the Biome 3 ranged enemy.
- **Ranged movement speed = 100 px/s is acceptable for Phase 1.** Keep:
  - `ENEMY_RANGED_MOVE_SPEED = 100`
  - `RANGED_PROJECTILE_SPEED = 260` px/s
- **Phase 1 implementation is approved.**

### Asset discrepancies (resolved)

| Prompt | Repo / decision |
|--------|------------------|
| `fireball_16x16.png`, `fireball_trail_16x16.png` | Repo has `enemy_projectile_16x16.png`, `enemy_projectile_trail_16x16.png` under `assets/entities/projectiles/`. **Use existing** enemy projectile assets; trail to be rendered when projectile system supports it. |
| `attack_1.png → attack_4.png` under `biome3/ranged/` | Repo has **`shoot_1.png → shoot_4.png`** in same folder. **Loaded `shoot/` as the attack state** in code. |

### Implementation notes

- Ranged is **registered** in `ENEMY_TYPES`, `entities/__init__.py`, combat (skip melee + `apply_projectile_hits`), and game_scene (projectiles list, draw, `_enemy_stop_distance`). Biome 3 rooms use Ranged (Phase 2).
- Ranged movement speed **100 px/s** and projectile speed **260 px/s** kept as approved.
- Ranged **preferred range** = 180 px (`ENEMY_RANGED_STOP_DISTANCE`); backs off if closer, approaches if farther, shoots when in band.

### Response to phase 1 discrepencies:
Use the existing projectile assets already present in the repo:

- assets/entities/projectiles/enemy_projectile_16x16.png
- assets/entities/projectiles/enemy_projectile_trail_16x16.png

The trail should be rendered if the projectile system supports it.

Do not use boss projectile assets for the Biome 3 ranged enemy.

Ranged movement speed = 100 px/s is acceptable for Phase 1.
Keep:
- ENEMY_RANGED_MOVE_SPEED = 100
- RANGED_PROJECTILE_SPEED = 260 px/s

Phase 1 implementation is approved.

STOP and wait for my Phase 2 instructions.

---

## Phase 2 (Biome 3 room sequence 16–23) — done

### Phase 2 approval (canonical decisions)

- **HEAL_DROP_CHANCE** kept at **0.25** (approved).
- **AMBUSH_SPAWN_RADIUS_PX** kept at **200** (approved).
- **Triangle layout** kept as existing (approved).
- **Room 21 safe room** extended with **upgrade system** (see below); heal pickup remains separate.

### Discrepancies and decisions

| Prompt | Repo / decision |
|--------|------------------|
| **Combat clear heal drop chance = 35%** | Config has `HEAL_DROP_CHANCE = 0.25` (25%). **Approved** to keep at 0.25. |
| **Ambush ring radius = 160 px** | `spawn_helper` uses `AMBUSH_SPAWN_RADIUS_PX = 200`. **Approved** to keep 200. |
| **Triangle side length = 200 px** | Config has `TRIANGLE_OFFSET_PX = 80`. **Approved** to keep existing layout. |
| **Room 21 Safe: upgrade selection (3 options)** | **Implemented:** Room 21 safe room now has heal pickup + upgrade panel. Player sees 3 choices (Health +20% max HP, Speed +10%, Attack +12%), picks one with keys 1/2/3. Icons from `assets/ui/hud/icon_health_24x24.png`, `icon_speed_24x24.png`, `icon_attack_24x24.png`. Defense upgrade not implemented. |
| **Room 23 Mini Boss** | **Phase 3 implemented:** Room 23 now uses **Biome3MiniBoss**; spawn at room center, 2.0 s. |

### Implementation notes

- **Config:** `USE_BIOME3 = True`, `BIOME3_ROOM_COUNT = 8`, `BIOME3_START_INDEX = 16`.
- **room.py:** `total_campaign_rooms()` includes Biome 3 when `USE_BIOME3`; `generate_room()` branches on `BIOME3_START_INDEX` and uses `room_order_biome3(seed)`.
- **biome3_sequence.py:** Fixed order (16–23) when `BEGINNER_TEST_MODE`; otherwise shuffle 16–22, Room 23 always Mini Boss.
- **biome3_rooms.py:** Spawn specs per room (Ranged included); patterns: spread, ambush, triangle, single. Room 23 = single center spawn (2.0 s).
- **game_scene:** For `room_idx >= BIOME3_START_INDEX`, uses `get_biome3_spawn_specs` / `get_biome3_spawn_pattern`; Ranged passed in; Mini Boss single spawn at **room center** (playable bounds center).
- **Room 21 safe room upgrade system:** When `current_room_index == 21` and `room_type == SAFE`, a panel shows 3 upgrade choices (deterministic order: 1=Health, 2=Speed, 3=Attack). Player picks one with 1/2/3; effects: Health +20% base_max_hp/max_hp, Speed +10% move_speed_mult (movement system), Attack +12% attack_damage_mult (player.attack_multiplier). State resets on room transition. Additive with Biome 1/2.

### Response to phase 2 discrepencies:
Phase 2 is acceptable overall.

Approve these decisions for now:
- keep HEAL_DROP_CHANCE at 0.25 for now
- keep AMBUSH_SPAWN_RADIUS_PX at 200
- keep the existing triangle layout

However, Room 21 safe room is still incomplete and must now be extended to support upgrades in addition to the heal pickup.

The upgrade icons are already present in the repo under:
- assets/ui/hud/icon_health_24x24.png
- assets/ui/hud/icon_speed_24x24.png
- assets/ui/hud/icon_attack_24x24.png
- assets/ui/hud/icon_defence_24x24.png

Please implement the Biome 3 safe room upgrade system using these existing assets.

Requirements:
1. Room 21 safe room must contain:
   - the existing heal pickup
   - upgrade choices

2. Upgrade selection rules:
   - show 3 upgrade choices to the player
   - player can choose only 1 upgrade
   - selection must be deterministic using the seeded RNG
   - heal pickup remains separate from upgrades

3. For now, implement these 3 upgrade types:
   - Health Upgrade
   - Speed Boost
   - Attack Boost

4. Upgrade details and gameplay impact:
   - Health Upgrade
     - icon: assets/ui/hud/icon_health_24x24.png
     - effect: +20% max HP
     - impact: increases survivability for the rest of the run

   - Speed Boost
     - icon: assets/ui/hud/icon_speed_24x24.png
     - effect: +10% movement speed
     - impact: improves repositioning, dodging, and spacing against ambush/ranged pressure

   - Attack Boost
     - icon: assets/ui/hud/icon_attack_24x24.png
     - effect: +12% attack damage
     - impact: improves room clear speed and overall combat efficiency

5. Do not implement Defense Upgrade right now.
6. Reuse the existing HUD / UI / interaction systems wherever possible.
7. Keep the implementation additive and compatible with Biome 1 and Biome 2.
8. Do not change anything else unless required for this safe room upgrade feature.

After implementing this safe room upgrade addition, STOP and wait for my next instruction.

---

## Phase 3 (Biome 3 mini boss) — done

### Phase 3 approval (canonical decisions)

- **Approved:** Use the flat `biome3_miniboss` asset path and prefix-based animation loading; keep spawn at **2.0 s**; keep the fixed adds composition (**2 Swarm, 1 Flanker**).
- **Accepted for now:** Keep Biome 3 mini boss reward heal aligned with the existing shared mini boss reward flow (25%) unless later balancing requires a separate Biome 3 override; keep door unlock using the shared global mini boss unlock delay config.
- **Phase 3 is approved.** No further changes at this time.

### Asset discrepancies

| Prompt | Repo / decision |
|--------|------------------|
| **Path:** `assets/entities/enemies/biome3/miniboss/` with subfolders `idle/`, `move/`, `attack1/`, `attack2/`, `summon/`, `phase_change/`, `hit/`, `death/` (frame_01.png style) | Repo has **flat folder** `assets/entities/enemies/biome3_miniboss/` with files `idle_1.png`, `move_1.png`, `attack1_1.png`, `attack2_1.png`, `summon_1.png`, `phase_change_1.png`, `hit_1.png`, `death_1.png`, etc. **Used flat path** and added `load_animation_by_prefix()` in asset_loader to load by prefix (e.g. `idle_*`, `attack1_*`). |
| **Spawn 2.0 s** | Implemented (same as other mini bosses). |
| **On death: heal pickup 30% base HP, cap 100%** | Existing config uses `MINI_BOSS_REWARD_HEAL_PERCENT` (25%) and same reward/door-unlock flow. **No separate 30% for Biome 3**; discrepancy noted. |
| **Door unlock 0.5 s** | Config has `MINI_BOSS_DOOR_UNLOCK_DELAY_SEC` (shared). If prompt intended 0.5 s for Biome 3 only, that would be a config override; **not added** — use global value. |

### Implementation notes

- **`src/entities/biome3_miniboss.py`:** `Biome3MiniBoss` (96×96), states: idle, move, attack_01, attack_02, summon, phase_change, hit, death. Phase 1: melee like MiniBoss. At 50% HP: plays `phase_change` once, then sets `_pending_adds = True`.
- **game_scene:** When any enemy has `_pending_adds`, spawns **2 Swarm + 1 Flanker** in a ring (radius 120 px, 3 positions 120° apart) around that enemy and appends to `_enemies`; then clears `_pending_adds`.
- **Combat:** `mini_boss_3` uses same melee params as mini_boss / mini_boss_2; included in “attacking” state check for attack_01/attack_02.
- **Room 23:** `get_biome3_spawn_specs` is called with `Biome3MiniBoss` as the Mini Boss class for Biome 3; Room 23 single spawn uses it. Death reward and door unlock use existing Phase 6 logic (all mini bosses).

### Response to Phase 3 discrepencies:
Phase 3 looks acceptable overall.

Approved:
- use the flat biome3_miniboss asset path and prefix-based animation loading
- keep spawn at 2.0 s
- keep the fixed adds composition:
  2 Swarm
  1 Flanker

Accepted for now:
- keep Biome 3 mini boss reward heal aligned with the existing shared mini boss reward flow (25%) unless later balancing requires a separate Biome 3 override
- keep door unlock using the shared global mini boss unlock delay config

Do not change anything further right now.
Phase 3 is approved.
STOP and wait for my next instruction.