# Biome 3 Full Spec — Cross-Check Report

Cross-check of `biome3_full_spec.md` against the current codebase. The spec file is not modified.

---

## Mismatches

1. **§4 Enemies — BEGINNER speed overrides**
   - **Spec says:** "`BEGINNER_TEST_MODE` speed overrides when True (config overrides Flanker, Brute, MiniBoss only; Ranged has no Beginner speed override)."
   - **Code:** When `BEGINNER_TEST_MODE` is True (`config.py` 341–347), `ENEMY_HEAVY_MOVE_SPEED` is also set to `int(_player_speed * 0.55)` (same block as Flanker/Brute/MiniBoss). Heavy is **not** excluded from Beginner overrides.
   - **Fix:** State that Heavy also uses a Beginner speed override (0.55 × `PLAYER_MOVE_SPEED`), or remove “only” and list Flanker, Brute, Heavy, MiniBoss.

2. **§6 Mini Boss — move speed**
   - **Spec says:** "`MINI_BOSS_MOVE_SPEED` 100" for Biome3MiniBoss.
   - **Code:** When `BEGINNER_TEST_MODE` is True, `MINI_BOSS_MOVE_SPEED = int(_player_speed * 0.75)` → **165** px/s (with default `PLAYER_MOVE_SPEED` 220). Biome3MiniBoss reads `MINI_BOSS_MOVE_SPEED` at init.
   - **Fix:** Add: when `BEGINNER_TEST_MODE`, mini-boss move speed is 165 px/s (0.75 × player speed), not 100.

3. **§9 / §10 — Biome 3 upgrade panel vs SAFE room index**
   - **Spec implies:** Biome 3 “safe room” has the upgrade panel (often tied to “campaign index 21”).
   - **Code:** Upgrade UI and key handler require **`current_room_index == BIOME3_SAFE_ROOM_INDEX` (21)** **and** `room_type == SAFE` (`game_scene.py` 2366–2372, 2640–2644). Room **type** SAFE in Biome 3 can appear at **any** campaign index 16–22 when shuffled (`room_order_biome3`). Only when that SAFE room is **exactly** index **21** does the 1/2/3 upgrade appear. If SAFE is e.g. campaign 18, player gets H-heal only—**no** upgrade panel.
   - **Fix:** State explicitly: upgrade (Health/Speed/Attack) is available **only** when the SAFE room occurs at **campaign index 21**; in non-`BEGINNER_TEST_MODE`, that is **not** guaranteed.

---

## Missing Values

4. **Heavy spawn in Biome 3:** For `Heavy`, `game_scene` still calls `ensure_valid_spawn_position(..., for_heavy=True)`. `blocked_tiles` is passed only when `current_room_index >= BIOME4_START_INDEX`; in Biome 3, `blocked` is **None**. Spec does not mention this Biome 4–only prop blocking for Heavy.

5. **Biome 3 room 21 upgrade vs H:** Keys 1/2/3 apply upgrades without requiring `_safe_room_heal_done` or `_safe_room_upgrade_pending`. Player can take an upgrade **without** pressing H first. Spec lists “H for heal; 1/2/3 for upgrade” but does not state that H is **not** a prerequisite for 1/2/3 in code.

6. **Projectile default asset:** Ranged `Projectile` without custom `image_path` uses `PROJECTILE_IMAGE_PATH` / `PROJECTILE_SIZE` (16×16) from `projectile.py`; Biome3MiniBoss fireball uses separate path/size. Spec covers fireball; optional note: default ranged projectile asset path/size in code.

7. **`biome3_rooms.py` line 59 comment:** Still says “placeholder until Phase 3”; runtime uses `Biome3MiniBoss` from `game_scene`—behavior matches spec; comment is stale only (not a spec error).

---

## Ambiguities

8. **§9 “Overheal cap” / H heal:** Safe room H applies `hp += base_max_hp * SAFE_ROOM_HEAL_PERCENT` with **no** immediate clamp to `base_max_hp * SAFE_ROOM_OVERHEAL_CAP_RATIO` in that handler. HUD uses `SAFE_ROOM_OVERHEAL_CAP_RATIO` (1.30) for bar display. Whether gameplay **hard-caps** HP at 130% elsewhere is not spelled out in spec vs single-line heal code.

9. **§2 shared “clear triggers on_room_clear() → DOOR_UNLOCK_DELAY_SEC”:** For MINI_BOSS room, door unlock timer is also started on boss death (`MINI_BOSS_DOOR_UNLOCK_DELAY_SEC`), same pattern as Biome 2 spec—Biome 3 spec mentions door on boss death in §2 Campaign 23; §2 opening paragraph still reads like generic clear-only flow for all combat types.

10. **“Biome 3 safe room” vs “room 21”:** Wording can be read as “any Biome 3 SAFE” having upgrades; code ties upgrades to **index 21**, not to SAFE type alone.

---

## Verified

- **§1:** `BIOME3_ROOM_COUNT` 8, `BIOME3_START_INDEX` 16, fixed order when `BEGINNER_TEST_MODE`, shuffle list + MINI_BOSS last when False (`biome3_sequence.py`).
- **§2 / §5:** All `get_biome3_spawn_specs` Beginner branches (room_idx 0–7) and non-Beginner branches (COMBAT, AMBUSH, ELITE, MINI_BOSS, SAFE) match spec counts, types, elite flags, delays, telegraph 1.5 on ambush.
- **§2 Campaign 18:** `spawn_ambush` without extra radius arg → `AMBUSH_SPAWN_RADIUS_PX` 200.
- **§2 Campaign 23:** Adds 2 Swarm + 1 Flanker, radius 120, angles `i * 2π/3` (`game_scene.py` 956–971).
- **§3:** 30×20 grid, `ROOM_SIZE_*` not used, no `biome_index == 3` draw branch.
- **§4 Ranged:** Stats, kiting thresholds 140/220, projectile speed/lifetime, `ENEMY_RANGED_STOP_DISTANCE` 180, combat melee params for `"ranged"`.
- **§6 Biome3MiniBoss:** `enemy_type` `mini_boss_3`, `MINI_BOSS_SIZE` (128,128), HP 200, damage 18, stop 70, phase at 50% HP, fireball constants 16/280/3.0/2.2, reward heal cap, door delay 0.5 s.
- **§7:** No `biome_index == 3` player stat branch.
- **§8 Hazards:** `_make_tile_grid` with `seed + campaign_index * 1000`; SAFE / BEGINNER caps as Biome 1.
- **§10:** Heal drop 25%, reward orb cap at `base_max_hp`.
- **§11:** No Biome 3 AI director.
- **§12:** `room_order_biome3(seed)`, spawn RNG `SEED + room_index * 10000`, heal drop `SEED + current_room_index * 100`.
- **§13:** No B3-only visuals; docstring 96×96 vs `MINI_BOSS_SIZE`; Ranged no Beginner override (correct).

---

## Summary

| Type        | Count |
|------------|-------|
| Mismatches | 3     |
| Missing    | 4     |
| Ambiguities| 3     |
| Verified   | 12+   |

**Conclusion:** Update `biome3_full_spec.md` for (1) Heavy + Biome3MiniBoss Beginner speeds, (2) upgrade panel only at campaign index 21 (not every Biome 3 SAFE when shuffled), and (3) optional clarity on H vs 1/2/3 ordering and Heavy `blocked_tiles` in Biome 3.
