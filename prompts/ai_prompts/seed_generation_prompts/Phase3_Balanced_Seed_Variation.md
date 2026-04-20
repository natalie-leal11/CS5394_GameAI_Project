# Phase 3 — Seed Variation 1: Balanced (Baseline / Implementation-Aligned)

Define the first implemented seed variant as the baseline profile.

---

## Goal

Capture the deterministic baseline variant used as balanced reference behavior.

---

## Variant Identity

This phase covers:
- `variant_id == 0`
- `Balanced` profile
- baseline ordering/composition closest to implementation defaults

---

## Room-Order Behavior (Bounded)

Variant 0 uses balanced flexible-slot ordering within each biome’s fixed constraints:
- fixed milestones remain unchanged
- SAFE remains exactly one per biome within allowed mid-biome positions
- flexible slots prioritize implementation-aligned balanced progression

---

## Encounter/Spawn Behavior (Bounded)

Variant 0 keeps baseline deterministic encounter composition tendencies:
- biome-legal enemy pools only
- count bounds respected by room type and biome
- deterministic spawn slot timing/order realization
- deterministic formation realization by room type (spread/ambush/triangle/single as legal)

---

## Safety Boundaries

Variant 0 must not:
- alter room counts/milestones
- add unsupported room or enemy types
- modify boss behavior or structure

---

## Phase 3 Checklist

- [ ] Variant 0 mapping is explicit and deterministic
- [ ] Baseline room-order behavior is bounded and implementation-aligned
- [ ] Baseline encounter/spawn behavior is bounded and deterministic
- [ ] Non-seed systems remain untouched

Stop after Phase 3.
