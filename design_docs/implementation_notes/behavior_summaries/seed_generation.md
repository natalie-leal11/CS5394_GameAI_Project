---
# Seed Generation — Behavior Implementation Summary

## Overview

Every random decision in a dungeon run is controlled by a single integer seed
(default `SEED = 42` in `config.py`). The seed is hashed into a family of
independent, named random streams — one per room, per channel, per biome. Any
two runs started with the same seed produce identical room layouts, enemy
compositions, spawn orderings, and encounter timings on any machine.

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
independent values for different input combinations. Passing different
`(room_index, channel, biome_index)` tuples always yields different seeds.

---

## Per-Room RNG — make_room_rng

`make_room_rng(room_index, channel, biome_index) -> random.Random`

Creates a fully isolated `random.Random` instance seeded by
`derive_seed(run_seed, room_index, channel_hash, biome_index)`. Every
combination of run seed, biome, room position, and named channel (e.g.
`"enemy_type"`, `"spawn_order"`, `"hazard_layout"`) gets its own stream.
Drawing values from one room's stream never affects any other room's stream.

---

## Variant System

The run seed is divided into three variants via `seed % 3`:

- **Variant 0** — heaviest composition (Swarm + Flanker + Brute).
- **Variant 1** — lighter composition (Swarm + Flanker).
- **Variant 2** — parity-based rule tied to the campaign room index.

`seeded_encounter_specs.py` maps `(seed_variant, room_type, campaign_index)`
to a specific enemy composition list. The same seed always produces the same
variant and therefore the same enemy lists across the entire run.

---

## Global AI Streams

`get_stream(name, offset) -> random.Random` provides named RNG streams for
systems outside the room structure (e.g. reinforcement timing, director
variation). These are seeded from the run seed plus a stable name-derived
offset so they are independent from room-level streams.

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

## RL Integration

`DungeonEnv.reset(seed=N)` passes `N` to `initialize_run_seed()` via the
`run_seed_override` parameter on `SceneManager.switch_to_game()`. This ensures
every training episode and every evaluation episode with a given seed produces
an identical dungeon. The `BestProgressionEvalCallback` uses a fixed set of
seeds during evaluation to make checkpoint comparisons fair.

---

## Primary File Locations

| File | Contents |
|---|---|
| `src/game/rng.py` | `derive_seed()`, `make_room_rng()`, `get_stream()`, `initialize_run_seed()`, `_run_seed` global |
| `src/game/config.py` | `SEED = 42` master seed constant |
| `src/dungeon/seeded_encounter_specs.py` | Variant logic, per-room composition lookup tables |
| `src/dungeon/biomeN_rooms.py` | Room layout randomisation using `make_room_rng()` per biome |
| `src/game/phase1_seed_debug.py` | Smoke test; writes `logs/seed_run_<timestamp>.txt` |
