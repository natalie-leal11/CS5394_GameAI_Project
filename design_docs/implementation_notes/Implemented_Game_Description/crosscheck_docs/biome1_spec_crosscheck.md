# Biome 1 Full Spec — Cross-Check Report

Cross-check of `biome1_full_spec.md` against the current codebase. Only mismatches and missing values are listed.

---

## Mismatches (spec is wrong or incomplete)

1. **Section 9 — Safe Room “Health Upgrade”**
   - **Spec says:** "+30% max HP"
   - **Code:** `SAFE_ROOM_UPGRADE_HEALTH_MULT = 1.20` (game_scene.py line 58) → **+20% max HP**, not 30%.
   - **Fix:** Change to "+20% max HP" and cite `SAFE_ROOM_UPGRADE_HEALTH_MULT = 1.20`.

2. **Section 2 — Room 3 (Safe Room) / Section 6 — Heal object position**
   - **Spec says:** "Heal object placed in one corner (world position from valid tile)"
   - **Code:** Heal position is fixed at tile `(b + 2, b + 2)` (game_scene.py 1089–1091), i.e. **top-left** of playable area (2 tiles from wall border), not a generic “one corner.”
   - **Fix:** State explicitly: "Heal object at top-left of playable area, tile (wall_border()+2, wall_border()+2)."

---

## Missing values (spec omits implemented details)

3. **Section 4 — Mini Boss**
   - **Missing:** Sprite/size. Code: `MINI_BOSS_SIZE = (128, 128)` (config.py line 29).
   - **Add:** e.g. "Size (sprite): (128, 128) — MINI_BOSS_SIZE."

4. **Section 3 — Enemies (Swarm, Flanker, Brute)**
   - **Missing:** Melee attack radius and offset (used for hit detection).
   - **Code:** Swarm: radius 20.0, offset 20.0. Flanker: 16.0, 18.0. Brute: 26.0, 22.0 (config.py 57–67).
   - **Add (optional):** One line per enemy with attack radius and offset for completeness.

5. **Section 6 — Hazards**
   - **Missing:** When `BEGINNER_TEST_MODE` is True, **non–START/SAFE** rooms (combat, elite, ambush, mini_boss) use **slow 5–8%** (slow_min = 5%, slow_max = 8%), not the generic 5–10%.
   - **Code:** room.py 143–145: `slow_min = int(total * 0.05)`, `slow_max = int(total * 0.08)` in BEGINNER_TEST_MODE.
   - **Add:** e.g. "When BEGINNER_TEST_MODE: combat/elite/ambush/mini_boss rooms use slow 5–8% (slow_min 5%, slow_max 8%)."

6. **Section 8 — RNG**
   - **Clarification:** Spawn position RNG uses `SEED + room.room_index * 10000` (game_scene.py 451) with the **config constant** `SEED`. Room order and tile grid use the seed passed to `generate_room()` (RoomController’s `_seed`). In current code, RoomController is constructed with `SEED` (game_scene.py 367), so both paths use the same value. If in the future a run-specific seed is passed to RoomController, room order and hazards would use that seed, while spawn positions would still use the global config `SEED` — a potential inconsistency. Not a current bug; worth a one-line note in the spec.

---

## Verified (no change needed)

- Room count 8, room order (fixed vs shuffle), room types.
- Grid size 30×20; ROOM_SIZE_* not used in generation.
- Room 0: dummy position (min_col, max_row), exit rect top-right 3×3, altar center, dummy HP reset.
- Room 1–7 spawn specs (Beginner vs non-Beginner), enemy counts, spread/triangle/ambush/single patterns.
- Enemy base stats, elite multipliers, speeds (including BEGINNER_TEST_MODE 0.85/0.65/0.75).
- Mini Boss: HP 200, damage 18, speed 100/165, attack cooldown 2.0 s, stop 70 px, no dash in update, assets `mini_boss_1`.
- Player: HP 1000, speed 220, dash params, short/long damage and timings, block/parry.
- Lava 6 dps, 3 frames @ 6 FPS; slow factor 0.75; door margin 3; center 3×3 safe zone; BEGINNER lava 0–3%.
- SAFE: no lava; slow 0–5%; heal 30% base_max_hp, overheal cap 130%, H key, once per Safe Room.
- Seed usage: room order shuffle, tile grid (seed + room_index*1000), spawn RNG (SEED + room_index*10000).
- MINI_BOSS_DOOR_UNLOCK_DELAY_SEC 0.5, MINI_BOSS_REWARD_HEAL_PERCENT 0.30, SPAWN_SLOT_DELAY_SEC 0.4, TRIANGLE_OFFSET_PX 80, AMBUSH_SPAWN_RADIUS_PX 200.

---

## Summary

| Type           | Count |
|----------------|-------|
| Mismatches     | 2     |
| Missing values | 4     |
| Note (RNG)     | 1     |

Apply the fixes above to `biome1_full_spec.md` so the doc matches the codebase.
