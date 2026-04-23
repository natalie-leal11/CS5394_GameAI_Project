# Phase 1 — Seed Overview

Define seed-system authority, boundaries, and variant model before implementation details.

---

## Goal

Establish a strict seed-only contract for deterministic procedural variation.

---

## What the Seed System Controls

The seed system controls bounded procedural variation for:
- room-order selection within legal flexible slots
- safe-room placement within legal mid-biome bounds
- encounter composition within biome/room-type constraints
- spawn ordering/slot timing realization
- deterministic spawn-position/hazard realization within fixed caps

---

## What the Seed System Does Not Control

The seed system must not control:
- total campaign room count
- fixed room milestones (`START`, `MINI_BOSS`, `FINAL_BOSS`)
- room size, grid dimensions, door algorithm, or core structure
- boss identity, boss phase mechanics, or revive logic
- core player/enemy combat mechanics
- menu/settings/victory/start scene flow

---

## Variant Model (Implemented)

Use the existing finite variant model:
- `TOTAL_SEED_VARIANTS = 3`
- `variant_id = run_seed % 3`

Variant names used by existing docs/implementation context:
- Variant 0: `Balanced` (baseline / implementation-aligned)
- Variant 1: `Combat-heavy / Pressure`
- Variant 2: `Ambush-heavy / Spike`

---

## Phase 1 Checklist

- [ ] Seed authority is explicit and bounded
- [ ] Non-seed responsibilities are explicit
- [ ] Three-variant model is explicit and unchanged
- [ ] No new gameplay systems are introduced

Stop after Phase 1.
