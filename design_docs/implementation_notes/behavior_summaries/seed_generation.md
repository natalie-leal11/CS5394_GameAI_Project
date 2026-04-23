---
# Seed Generation — Behavior Implementation Summary

## Overview

Every random decision in a dungeon **run** is ultimately keyed off one integer
`run_seed` (initialized from `SEED` in `config.py` for non-RL, or from
`initialize_run_seed` / CLI / `DungeonEnv.reset`). The `run_seed` is hashed into
a family of named streams — one per room, per channel, per biome. Any two runs
with the same `run_seed` agree on room-type order, layouts driven by
`make_room_rng`, encounter composition, and heal-drop room picks. (One
documented exception: some **hazard placement** scatter in `room.py` still mixes
`config.SEED` into `derive_seed` — see “Run seed – additional coupled outputs”.)

This determinism is what makes RL training scientifically valid: the agent can
be evaluated across multiple seeds fairly, and any training run can be
reproduced exactly from its seed value.

---

## Core Hashing — derive_seed

`derive_seed(*parts: int) -> int` is the foundation of the entire system. It
mixes a variable number of integer parts using an FNV-style multiply-and-XOR
hash and returns a stable 32-bit integer:

```python
def derive_seed(*parts: int) -> int:
    x = 0x9E3779B9
    for p in parts:
        x ^= int(p) & 0xFFFFFFFF
        x = (x * 0x01000193) & 0xFFFFFFFF
    x ^= (len(parts) * 0x85EBCA6B) & 0xFFFFFFFF
    return x if x != 0 else 0x1A2B3C4D
```

The output is deterministic for any given tuple of inputs and produces
independent values for different input combinations. (Collisions in 32 bits are
theoretically possible but are not relied on; `make_room_rng` uses a **fixed**
part order listed in the next section.)

---

## Per-Room RNG — make_room_rng

`make_room_rng(room_index, channel, biome_index) -> random.Random`

Creates a fully isolated `random.Random` instance seeded by
`derive_seed(_run_seed, biome_index, room_index, channel_key(channel))` (see
`src/game/rng.py`: `biome_index` and `room_index` are masked to 16 bits before
mixing; `channel` is a string hashed via `channel_key`, not a precomputed int).
Every combination of run seed, biome, campaign room index, and named channel
(e.g. `"enemy_type"`, `"spawn_order"`, layout passes in `biomeN_rooms.py`) gets
its own stream. Drawing values from one room’s stream does not affect another’s.

Helper entry points (`sample_seeded_choice`, `sample_seeded_shuffle`,
`sample_seeded_uniform`, `sample_seeded_int`) all build on `make_room_rng` with
the same parameters.

---

## Variant System

The run seed is divided into three variants via `run_seed % 3` (see also
`get_variant_id()` and `TOTAL_SEED_VARIANTS` in `rng.py`, matching
`_variant(seed)` in `seeded_encounter_specs.py`):

- **Variant 0** — heaviest composition (e.g. Swarm + Flanker + Brute) where that template applies.
- **Variant 1** — lighter composition (e.g. Swarm + Flanker).
- **Variant 2** — mixed rules tied to the **campaign index** and extra hashing:
  - For **COMBAT** / **AMBUSH**: composition alternates on `campaign_index % 2`.
  - For **ELITE** (Biome 1): `derive_seed(seed, campaign_index, 0xE1) & 1` picks
    between two elite loadouts when variant is 2.

`seeded_encounter_specs.py` maps `(seed_variant, room_type, campaign_index, …)` 
to concrete spawn specs. The same `run_seed` always yields the same variant and, 
for a given room type and index, the same spec list.

---

## Global AI Streams

`get_stream(name, offset) -> random.Random` seeds
`random.Random(derive_seed(_run_seed, channel_key(name), int(offset)))` — a
named stream independent of any single room’s `make_room_rng`. (Call sites may
be sparse; the API is the supported way to add **non–room-scoped** randomness
without cross-talk to `make_room_rng`.)

---

## Run Seed Initialisation

`initialize_run_seed(raw=None)` is called at the start of every run:
- If `raw` is provided (e.g. from CLI or RL `reset(seed=N)`), it is used directly.
- If `raw` is `None`, the seed is derived from the current millisecond timestamp,
  producing a different run each time while remaining fully reproducible if the
  value is logged and replayed.

Every run writes the seed value and per-room RNG draws to
`logs/seed_run_<timestamp>.txt` via `phase1_seed_debug.py`.

---

## Run seed – additional coupled outputs

These are **not** a second RNG source: they are deterministic functions of the
same `run_seed` (and sometimes `campaign_index` / biome) once `initialize_run_seed` has run.

| Output | Role |
|--------|------|
| **Campaign room type order** | For each biome, `room_order_biome1_srs(seed)` … `room_order_biome4_srs(seed)` in `srs_biome_order.py` define which `RoomType` appears at each campaign index (`generate_room` in `room.py`). |
| **`RoomController(seed)`** | Constructed with `get_run_seed()`; passes `seed` into `generate_room(campaign_index, seed)` so tile/layout and room type at index *i* are fixed for that run. |
| **Heal-drop evaluation room (per biome)** | `compute_selected_heal_drop_room_by_biome(run_seed)` in `game_scene.py` picks, per biome, which **eligible** campaign room index is used for the post-clear heal roll (its own `derive_seed(rs, channel_key("heal_drop_biome_room_pick"), biome)`). |
| **First Biome 1 safe room (SRS / UI)** | `_first_safe_room_index_biome1(seed)` / `room_order_biome1_srs(seed)` — first `SAFE` in the Biome 1 order for this `run_seed`. |
| **Metrics + AI log metadata** | `MetricsTracker.start_run(run_seed)` and `AILogger(run_seed=…)` store the same integer for run-level logging (`run_id` may be separate; **RNG shape** is from `run_seed`). |
| **Exception: hazard *placement* scatter** | `_placement_rng` in `room.py` mixes `config.SEED` (engine default), not the dynamic `run_seed`, so a specific hazard scatter phase stays tied to the **config** constant unless refactored — see docstring in `room.py`. |

---

## RL Integration

`DungeonEnv.reset(seed=N)` sets `numpy.random.seed(seed)` (Gymnasium `reset`)
**and** passes `N` as `run_seed_override` into `GameScene.reset(...)` via
`SceneManager.switch_to_game(run_seed_override=N, …)`. That value feeds
`initialize_run_seed`, so a given `N` matches the same dungeon as a manual
run with that seed. Optional `rl_curriculum_scenario` comes from
`reset(options={"curriculum_scenario": "interact" | "safe_heal"})` (see
`DungeonEnv` / `rl/wrappers`); it is **not** an RNG input but **does** change
which room is prepared on the first tick for RL curriculum micro-episodes.

The `BestProgressionEvalCallback` (dungeon PPO) can use a fixed set of
evaluation seeds so checkpoint comparisons are fair.

---

## Primary File Locations

| File | Contents |
|---|---|
| `src/game/rng.py` | `derive_seed`, `channel_key`, `make_room_rng`, `get_stream`, `initialize_run_seed`, `set_run_seed`, `get_run_seed`, `get_variant_id`, `sample_seeded_*` helpers, `_run_seed` / `_variant_id` globals |
| `src/game/config.py` | `SEED = 42` master seed constant |
| `src/dungeon/seeded_encounter_specs.py` | Variant logic, per-room composition lookup tables |
| `src/dungeon/srs_biome_order.py` | `room_order_biome1_srs`–`room_order_biome4_srs` — SRS **room-type order** per biome from `derive_seed` |
| `src/dungeon/room.py` | `generate_room`, `_placement_rng` (placement uses `config.SEED`); per-biome order delegates to SRS / sequence modules |
| `src/dungeon/biomeN_rooms.py` | Procedural room layout; uses `make_room_rng()` / `derive_seed` per biome and channel |
| `src/dungeon/room_controller.py` | `RoomController(seed=…)`; `load_room` → `generate_room(campaign_index, seed)` |
| `src/game/scenes/game_scene.py` | `initialize_run_seed`, `compute_selected_heal_drop_room_by_biome`, `reset(..., run_seed_override, rl_curriculum_scenario)` |
| `src/game/phase1_seed_debug.py` | Smoke test; writes `logs/seed_run_<timestamp>.txt` |
