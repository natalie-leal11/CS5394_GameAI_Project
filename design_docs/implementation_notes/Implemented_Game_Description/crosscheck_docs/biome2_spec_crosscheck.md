# Biome 2 Full Spec — Cross-Check Report

Cross-check of `biome2_full_spec.md` against the current codebase. Only differences, missing details, and ambiguities are reported; the spec file is not modified.

---

## Mismatches (spec is wrong)

1. **§9 Safe Room — "optional Safe Room upgrade paths (same global logic, not biome-tagged)"**
   - **Spec says:** Upgrade paths are "same global logic, not biome-tagged."
   - **Code:** The upgrade choice panel (1/2/3 or 1–4 keys) is gated by `current_room_index == BIOME3_SAFE_ROOM_INDEX` (21) or `current_room_index == BIOME4_SAFE_ROOM_INDEX` (28) only (`game_scene.py` 2369, 2409). Biome 2 safe room (e.g. campaign index 11) never shows an upgrade panel; only the H-key heal is available.
   - **Exact fix:** Replace with: "In Biome 2 safe room, no upgrade choice panel is shown; only the H-key heal. The upgrade panel (Health/Speed/Attack/Defence) appears only in Biome 3 safe room (campaign index 21) and Biome 4 safe room (campaign index 28)."

---

## Missing Values (implemented but not documented)

2. **§6 Mini Boss / §10 Rewards — Reward orb heal cap**
   - **Code:** Collecting any reward orb (mini-boss or room-clear) sets `self._player.hp = min(base_max_hp, self._player.hp + base_max_hp * heal_pct)` (`game_scene.py` 1243). Heal from orbs cannot exceed `base_max_hp` (no overheal from orbs).
   - **Add:** In §6 and §10, state explicitly: "Collecting the reward orb heals 30% of `base_max_hp`, capped at `base_max_hp` (no overheal from orbs)."

3. **§5 Table — "default 0.5" for telegraph**
   - **Code:** When `telegraph_sec` in spawn_specs is `None`, `SpawnSystem` uses `SPAWN_TELEGRAPH_DURATION_SEC` (`config.py` 167) = 0.5 s (`spawn_system.py` 95).
   - **Add:** Either keep "default 0.5" and add: "(None → `SPAWN_TELEGRAPH_DURATION_SEC` = 0.5)", or cite the constant name.

4. **§2 Shared — Door unlock trigger for MINI_BOSS room**
   - **Code:** For mini-boss rooms, door unlock uses a separate path: when a mini-boss (including MiniBoss2) dies, `_mini_boss_death_pos` is set; next frame a reward is appended and `_door_unlock_timer = MINI_BOSS_DOOR_UNLOCK_DELAY_SEC` is set (`game_scene.py` 1136–1139). `on_room_clear()` is still called only when all enemies (boss + adds) are dead (`game_scene.py` 1074–1078). So the door-unlock timer for the mini-boss room starts on boss death, not on room clear.
   - **Add:** In §2 Campaign 15 or shared text, note: "Mini-boss room: door-unlock timer starts when the boss dies (`MINI_BOSS_DOOR_UNLOCK_DELAY_SEC`), not when the room is fully cleared (adds may still be alive)."

5. **§10 — Room-clear heal drop: no guaranteed heal**
   - **Code:** Room clear only adds a center orb when `rng.random() < HEAL_DROP_CHANCE` (0.25) (`game_scene.py` 1082). No automatic HP change; player must collect the orb.
   - **Spec** already says "seeded roll; reward at room center tile if success" — optionally add: "No heal applied on clear; player must overlap the orb to receive the 30% heal (capped at `base_max_hp`)."

---

## Ambiguities

6. **§9 — "optional Safe Room upgrade paths"**
   - "Optional" is vague: it is not that upgrades are optional in Biome 2, but that the upgrade panel does not exist there. See Mismatch 1; clarifying that Biome 2 safe has no upgrade panel removes the ambiguity.

7. **§5 Table row 8 — "default 0.5"**
   - "Default" is not tied to a constant. Clarify: "Telegraph: None in spawn_specs → `SPAWN_TELEGRAPH_DURATION_SEC` (0.5 s) used by SpawnSystem."

8. **§2 — "clear triggers on_room_clear() → DOOR_UNLOCK_DELAY_SEC"**
   - This applies to normal combat/elite/ambush rooms. For MINI_BOSS, the door unlock is driven by boss death and `MINI_BOSS_DOOR_UNLOCK_DELAY_SEC`; `on_room_clear()` is still invoked when the room is fully clear (for consistency), but the door has already been unlocked by the mini-boss death timer. Stating that mini-boss door unlock is tied to boss death (see Missing #4) resolves this.

---

## Verified

- **§1 Dungeon structure:** `BIOME2_ROOM_COUNT` = 8, `BIOME2_START_INDEX` = 8; campaign 8–15; fixed order when `BEGINNER_TEST_MODE` (`biome2_sequence.py` 14–23); non-Beginner shuffle of 7 types + MINI_BOSS (`biome2_sequence.py` 24–32); entry from room 7, exit room 15; room 16 when `USE_BIOME3` (`room.py` 305–316, `config.py` 252–253).
- **§2 Room-wise:** Grid 30×20; hazards via `_make_tile_grid(..., campaign_index, seed)` with `seed + room_index * 1000` (`room.py` 96–98, 332–333); door locking/unlocking and room types per campaign match `biome2_rooms.py` and `game_scene.py` (room_idx ≥ 8).
- **§3 Room design:** `_room_grid_size()` 30×20; wall_border 2 or 4 by room type (`room.py` 62–66, 69–72); no `biome_index == 2` draw branch.
- **§4 Enemies:** Swarm/Flanker/Brute/Heavy stats and Heavy spawn validation (`config.py`, `heavy.py`, `game_scene` Heavy branch); MiniBoss2 uses same MINI_* config as MiniBoss.
- **§5 Composition:** All Beginner and non-Beginner spawn_specs and patterns match `get_biome2_spawn_specs` and `get_biome2_spawn_pattern`; delays 0, 0.4, 0.8, 1.2; telegraph 1.5 for ambush; RNG `SEED + room.room_index * 10000` (`game_scene.py` 450).
- **§6 Mini Boss:** MiniBoss2, MINI_BOSS_SIZE (128,128); add times 8/12/16/20 s; boss at 2.0 s; BIOME2_ADD_TELEGRAPH_SEC 0.5; reward at death pos; `MINI_BOSS_REWARD_HEAL_PERCENT`; death handling via `isinstance(..., MiniBoss2)`.
- **§7 Player:** No biome_index == 2 branch; same as Biome 1.
- **§8 Hazards:** `_make_tile_grid` with campaign_index; BEGINNER caps (lava 0–3%, slow 5–8%) in `room.py` 141–146; SAFE no lava, slow 0–5%.
- **§10 Rewards:** No heal on kill; HEAL_DROP_CHANCE 0.25, center tile; mini-boss reward same constant; BIOME2_CLEAR_HEAL_* not used in game_scene.
- **§11 AI Director:** Not implemented.
- **§12 RNG:** room_order_biome2(seed); hazards seed + campaign_index*1000; spawn SEED + room_index*10000; heal drop SEED + current_room_index*100 (`game_scene.py` 1081).
- **§13 Missing features:** `get_biome2_elite_spacing()` unused; BIOME2_CLEAR_* unused; no biome 2 visuals; mini_boss_2.py comment 96×96 vs MINI_BOSS_SIZE 128.

---

## Notes (optional)

- **Seed consistency:** Spawn positions use config `SEED`; `generate_room` uses `RoomController._seed` (typically the same). If a run-specific seed were passed to the controller later, room order and hazards would use it while spawn RNG would still use global `SEED` — same note as Biome 1.
- **Mini-boss room clear:** Room is considered clear (and heal-drop roll happens) only when all enemies including adds are dead; the mini-boss reward orb appears at boss death and can be collected before adds are dead.

---

## Summary Table

| Type            | Count |
|-----------------|-------|
| Mismatches      | 1     |
| Missing values  | 4     |
| Ambiguities     | 3     |
| Verified blocks | 12    |

---

**Goal:** Use this report to update `biome2_full_spec.md` so it is 100% aligned with the implementation (without changing the spec in this task).
