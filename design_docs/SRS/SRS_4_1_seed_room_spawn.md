# SRS §4.1.3–§4.1.6 — Implementation verification

This document **verifies** the codebase against **SRS/AI_Dungeon_ProjSRS.md** §4.1.3–§4.1.6.

**Scope:** Behavior when **`BEGINNER_TEST_MODE` is `False`** (full SRS seed path). When **`True`**, fixed orders and scripted spawns are preserved for tests/specs (`srs_biome_order.py`, `biome*_rooms.py` beginner branches).

---

## §4.1.3 Seed-controlled variation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Seed controls **flexible encounter slots** (room-type ordering within fixed multiset) | **PASS** | `dungeon/srs_biome_order.py` — shuffle / elite&ambush counts (B2) from seeded `Random(derive_seed(...))`. |
| Seed controls **enemy spawn patterns** (spread / ambush / triangle / single via `game_scene` + `spawn_helper`) | **PASS** | Pattern chosen by **room type**; **positions** use `random.Random(SEED + room_index * 10000)` in `game_scene._ensure_spawn_system` — deterministic per seed + campaign index. |
| Seed controls **deterministic encounter composition** within biome bounds | **PASS** | `dungeon/seeded_encounter_specs.py` — `build_biome1..4_*`; RNG = `derive_seed(seed, campaign_index, salt, channel_key(room_type))`. |
| Seed does **not** control **total room count** | **PASS** | `config` `BIOME*_ROOM_COUNT`, `total_campaign_rooms()`; sequences fixed length. |
| Seed does **not** control **milestone positions** (boss at end of each biome segment) | **PASS** | `MINI_BOSS` / `FINAL_BOSS` appended after shuffle in `srs_biome_order.py`. |
| Seed does **not** control **room sizes** / **grid dimensions** | **PASS** | `dungeon/room.py` `_room_grid_size()` from `LOGICAL_W` / `LOGICAL_H` / `TILE_SIZE` only. |
| Seed does **not** control **core room geometry** (walls, doors algorithm) | **PASS** | `room_controller._place_doors_for_room`, `wall_border_thickness` — not keyed to encounter RNG. |
| Seed does **not** **override hazard caps** | **PASS** | `_make_tile_grid` uses **config fractions** and fixed caps (e.g. FINAL_BOSS 10%/15%/65%); RNG only picks counts **within** caps (`seed + room_index * 1000`). |

---

## §4.1.4 Room distribution — overview

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Seed influences **room type assignment** within predefined bounds | **PASS** | `srs_biome_order.py` per biome. |
| Seed influences **enemy spawn patterns and compositions** | **PASS** | `seeded_encounter_specs.py` + `game_scene` spawn layout RNG. |
| Seed does **not** influence room **size**, **grid dimensions**, **core layout structure** | **PASS** | Same as §4.1.3. |

### Fixed global constraints

| Requirement | Status | Notes |
|-------------|--------|-------|
| Fixed **rooms per biome** | **PASS** | 8 / 8 / 8 / 6 (+ flags). |
| **First room = START** (global dungeon) | **PASS** | Biome 1 index 0 = `START`. |
| **Last room = MINI_BOSS** (biomes 1–3) / **FINAL_BOSS** (biome 4) | **PASS** | Appended after flex segment in `srs_biome_order.py`. |
| SRS tables list **START ×1** per biome | **PARTIAL** | **Campaign model:** only **campaign room 0** is `START`. Biomes 2–4 segments start with combat-type rooms, not a second `START`. This matches a **continuous 30-room run**, not a literal repeat of `START` every 8 rooms. |
| Exactly **1 SAFE** per biome | **PASS** | Multisets + single `SAFE` in flex. |
| SAFE **not** first / **not** last (before boss) | **PASS** | `_repair_safe_not_ends_of_segment`. |
| **30%–60%** placement for SAFE | **PARTIAL** | **Not enforced as a hard band.** Only **“not first / not penultimate-before-boss”** (interior of flex segment). SRS text uses “Recommended” for 30–60%; implementation satisfies **SHALL** mid-biome wording via end constraints. |
| Boss rooms **fixed** / not seed-chosen type | **PASS** | Terminal type fixed; seed does not swap boss enum. |

### Per-biome multiset (non-beginner)

| Biome | SRS | Status |
|-------|-----|--------|
| **1** | 3×COMBAT, 1 SAFE, 1 ELITE, 1 AMBUSH in rooms 1–6; START + MINI_BOSS fixed | **PASS** |
| **2** | 1 SAFE, ELITE 1–2, AMBUSH 1–2, remainder COMBAT (7 flex) | **PASS** | `elite_n`, `ambush_n` ∈ [1,2], `combat_n` = remainder. |
| **3** | 1 SAFE, 2 ELITE, 2 AMBUSH, 2 COMBAT | **PASS** |
| **4** | 1 SAFE, ELITE 2–3, AMBUSH 2–3, COMBAT remainder, FINAL_BOSS last | **PASS (constrained)** | With **5** flex slots, only **1 SAFE + 2 ELITE + 2 AMBUSH** satisfies 2–3 bands → **0 COMBAT** in flex. Seed varies **order** only. Documented trade-off. |

### Seed responsibilities called out in SRS

| Item | Status | Evidence |
|------|--------|----------|
| (1) Room ordering within distribution | **PASS** | `srs_biome_order.py`. |
| (2) Enemy composition | **PASS** | `seeded_encounter_specs.py`. |
| (3) Enemy spawn positions | **PASS** | `SEED + room_index * 10000` + pattern functions. |
| (4) Hazard placement (lava/slow) | **PASS** | `_make_tile_grid`: `random.Random(seed + room_index * 1000)` **within** caps. |

### Non-seed (deterministic) items

| Item | Status |
|------|--------|
| Room size, layout structure, door positions | **PASS** |
| Boss **placement** (always terminal in segment) | **PASS** |
| Safe room **mechanics** (heal %, upgrades) | **PASS** | `config` + `game_scene` logic, not encounter RNG. |

---

## §4.1.5–§4.1.6 Spawn bounds and global rules

| Requirement | Status | Evidence |
|-------------|--------|----------|
| SAFE **0** enemies; START **0** hostile spawns | **PASS** | Empty specs + `game_scene` branches. |
| MINI_BOSS **1** primary mini boss | **PASS** | `build_*` + `MiniBoss` / `MiniBoss2` / `Biome3MiniBoss`; Biome 2 **adds** from **fixed schedule** (`biome2_mini_boss_encounter`), not random composition. |
| FINAL_BOSS primary **fixed**; Phase 1 empty spawn list | **PASS** | `get_biome4_spawn_specs` returns `[]` for `FINAL_BOSS` (metadata / future boss). |
| No unsupported archetypes; counts within table min–max | **PASS** | Pools and `randint` ranges in `seeded_encounter_specs.py`. |
| Boss **identity** / **phase logic** not replaced by seed | **PASS** | Boss classes and schedules fixed. |
| **Elite multiplier** values not seed-driven | **PASS** | `config` `ENEMY_ELITE_*`. |
| Spawn **safety** (playable, separation) | **PASS** | `systems/spawn_helper.py` + `game_scene` (unchanged fairness path). |
| **Determinism:** same seed + **campaign room index** + **room type** → same composition | **PASS** | `derive_seed(seed, campaign_index, …)` (global index uniquely identifies biome+slot). |
| Same → same **spawn positions** | **PASS** | Layout RNG `SEED + room_index * 10000` (same as campaign index in `Room.room_index`). |

### Biome-specific tables (non-beginner builds)

| Biome | COMBAT / AMBUSH / ELITE counts & pools | Status |
|-------|----------------------------------------|--------|
| **1** | COMBAT 1–3; AMBUSH 2–3; ELITE 2–3; Swarm/Flanker/Brute only; no Heavy/Ranged | **PASS** |
| **2** | COMBAT 3–4; AMBUSH 2–3; ELITE 2–3; Heavy in pool; ELITE pool Swarm/Brute/Heavy (no Flanker on ELITE row) | **PASS** |
| **3** | COMBAT/AMBUSH 3–4; ELITE 2–3; Ranged + Heavy in pools | **PASS** |
| **4** | Same pattern when room type occurs; ELITE pool includes Swarm (§4.1.5); §4.1.6 table omits Swarm — implementation follows **§4.1.5** | **PASS** (intentional alignment with wider pool in §4.1.5) |

### Known **PARTIAL** / follow-ups

| Topic | Detail |
|-------|--------|
| **Biome 3 mini-boss adds** | SRS: **0–3 phase-triggered** adds. Current `build_biome3_spawn_specs` returns **single** boss entry; **phase adds** may live in **boss AI** (`Biome3MiniBoss`), not in initial `spawn_specs`. Verify boss script matches SRS “not freely randomized.” |
| **Biome 4 COMBAT rooms** | In non-beginner flex multiset there are **no** COMBAT tiles; COMBAT spawn table is **ready** if design later adds COMBAT to flex. |
| **`run_seed` vs `config.SEED`** | Procedural generation uses **`config.SEED`** (and `RoomController` seed). If `set_run_seed` diverged from `SEED`, AI streams could differ; **game** aligns them on reset — keep them equal for SRS “one run seed.” |

---

## Summary

- **§4.1.3** and **§4.1.4** core **SHALL**s are implemented for non-beginner runs, with **documented** caveats: **campaign START** only on room 0; **Biome 4** flex multiset forces **no COMBAT**; **30–60% SAFE** is **not** a hard filter.
- **§4.1.5–§4.1.6** encounter bounds and determinism are implemented in **`seeded_encounter_specs.py`** with explicit pools and count ranges; boss/add **scripts** should be reviewed separately for full **phase-trigger** wording.

**Primary files:** `dungeon/srs_biome_order.py`, `dungeon/seeded_encounter_specs.py`, `dungeon/room.py` (`_make_tile_grid`), `dungeon/biome1_rooms.py`, `dungeon/biome2_rooms.py`, `dungeon/biome3_rooms.py`, `dungeon/biome4_rooms.py`, `game/scenes/game_scene.py` (`_ensure_spawn_system`), `game/rng.py`.
