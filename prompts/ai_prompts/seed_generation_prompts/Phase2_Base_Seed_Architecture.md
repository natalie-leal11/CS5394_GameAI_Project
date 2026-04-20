# Phase 2 — Base Seed Architecture

Define the deterministic architecture used by all seed-driven variation.

---

## Goal

Lock the run-seed lifecycle and deterministic derivation interfaces used by room order, encounter composition, and spawn realization.

---

## Run Seed Lifecycle

Use existing run lifecycle behavior:
- initialize run seed once at run start/reset
- store run seed globally for shared deterministic access
- derive `variant_id` from `run_seed % 3`
- keep run seed aligned with existing procedural generation seed usage

---

## Deterministic RNG Architecture

Use centralized deterministic helpers (existing `rng.py` style):
- deterministic `derive_seed(...)`
- named channel keys for stable stream separation
- per-room deterministic stream derivation (`make_room_rng(...)`)
- deterministic helper samplers (choice/shuffle/uniform/int)

All seed-side randomness routes through deterministic derivation patterns.

---

## Channel/Context Separation

Maintain deterministic separation by context:
- room-order channels
- encounter-composition channels
- spawn-realization channels
- optional safe-room/heal-room pick channels

Do not introduce unseeded randomness into seed-controlled systems.

---

## Structural Boundaries

Architecture must preserve:
- room-count constants per biome
- milestone positions
- supported room types/enemy pools per biome
- hazard cap boundaries

---

## Phase 2 Checklist

- [ ] Run-seed initialization/storage is deterministic
- [ ] Variant mapping remains `run_seed % 3`
- [ ] Derived streams/channels are deterministic and stable
- [ ] No structural constraints are loosened

Stop after Phase 2.
