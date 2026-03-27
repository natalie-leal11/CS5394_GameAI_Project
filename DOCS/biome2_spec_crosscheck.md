# Biome 2 Full Spec — Cross-Check Report

Cross-check of `Implemented Game Description/biome2_full_spec.md` against the current codebase.

---

## 1. Mismatches

- **None** — spec matches `biome2_rooms.py`, `biome2_sequence.py`, `biome2_mini_boss_encounter.py`, `room.py`, `game_scene.py`, `mini_boss_2.py`, `config.py`, `heavy.py`, `combat.py` for Biome 2 behavior.

- **Code comment vs implementation (not a spec error):** `mini_boss_2.py` docstring references "96×96"; runtime uses `MINI_BOSS_SIZE` **(128, 128)** from `config.py`. Spec documents 128×128.

---

## 2. Missing values

- **Spec could add (optional):** Exact line references for `USE_BIOME3` / post–room-15 flow — implied in §1 as "when USE_BIOME3"; no numeric gap in gameplay spec.
- **No critical omissions** identified for the requested sections.

---

## 3. Verified items

- `BIOME2_ROOM_COUNT = 8`, `BIOME2_START_INDEX = 8`; campaign 8–15; `total_campaign_rooms()` includes Biome 2 when `USE_BIOME2`.
- `room_order_biome2(seed)`: Beginner fixed `[COMBAT,COMBAT,AMBUSH,SAFE,COMBAT,ELITE,AMBUSH]` + `MINI_BOSS`; else shuffle of 7 types + `MINI_BOSS` last.
- Beginner `get_biome2_spawn_specs`: rooms 0–7 match §5 table (including AMBUSH = Swarm + Flanker at 62–66 and 82–86).
- Non-Beginner: COMBAT four-slot (Heavy fourth), AMBUSH two-slot, ELITE three-slot, MINI_BOSS `_biome2_mini_boss_spawn_specs`.
- `get_biome2_spawn_pattern`: SAFE None, ELITE triangle, AMBUSH ambush, MINI_BOSS single, else spread.
- `game_scene`: `room_idx >= 8` → `get_biome2_spawn_specs(..., MiniBoss2)` and `get_biome2_spawn_pattern`.
- `generate_room`: `campaign_index` in 8–15 → `biome_index = 2`, `room_order_biome2(seed)[local_idx]`.
- Heavy: `enemy_base` / config HP 60, damage 12, speed 100 (Beginner 0.55× player), size (104,104), melee radius 42, offset 24, cooldown 1.7.
- MiniBoss2: same MINI_* stats as MiniBoss; adds at 8/12/16/20 s; boss at 2.0 s; `BIOME2_ADD_TELEGRAPH_SEC` 0.5.
- Grid 30×20; no biome-2-only visuals in draw path.
- Hazards: same `_make_tile_grid` rules by room type + `BEGINNER_TEST_MODE` caps.
- Safe room: same as Biome 1; heal tile `(b+2, b+2)` pattern per global safe logic.
- Rewards: heal drop on clear, mini-boss reward — same constants; `BIOME2_CLEAR_HEAL_*` unused in codebase search.
- `get_biome2_elite_spacing()` defined, never referenced outside definition file.
- Player: no biome_index branch for stats in Biome 2.

---

## 4. Summary counts

| Category        | Count |
|----------------|-------|
| Mismatches (spec vs code) | 0 |
| Code comment inconsistencies | 1 (mini_boss_2 96×96 vs 128) |
| Missing values (material) | 0 |
| Verified blocks   | 12+ |

**Conclusion:** `biome2_full_spec.md` is aligned with the implementation. Optional: fix the stale `mini_boss_2.py` docstring for consistency with `MINI_BOSS_SIZE`.
