# Phase 5 — Seed Variation 3: Ambush-Heavy / Spike

Define the third implemented seed variant with ambush/spike tendencies.

---

## Goal

Capture deterministic ambush-oriented variation while preserving fairness bounds and fixed structure.

---

## Variant Identity

This phase covers:
- `variant_id == 2`
- `Ambush-heavy / Spike` profile

---

## Room-Order Behavior (Bounded)

Variant 2 emphasizes ambush/spike tendency in legal flexible slots:
- ambush-forward ordering where biome bounds allow
- SAFE still bounded to legal positions
- fixed milestones unchanged
- no room-count or room-type legality changes

---

## Encounter/Spawn Behavior (Bounded)

Variant 2 emphasizes deterministic ambush/spike encounter tendencies:
- ambush-weighted compositions/order where legal
- late-spike or heavier late-room pressure patterns where documented
- room-type count bounds and biome pools strictly enforced
- deterministic slot timing/order and formation realization preserved

---

## Safety Boundaries

Variant 2 must not:
- create unbounded difficulty spikes
- violate room-type or enemy-pool constraints
- alter boss behavior, milestone positions, or core systems

---

## Phase 5 Checklist

- [ ] Variant 2 mapping is explicit and deterministic
- [ ] Ambush/spike room ordering remains bounded
- [ ] Ambush/spike encounter behavior remains within legal limits
- [ ] Fairness and non-seed boundaries remain intact

Stop after Phase 5.
