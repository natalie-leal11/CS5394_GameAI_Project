# Phase 4 — Seed Variation 2: Combat-Heavy / Pressure

Define the second implemented seed variant with higher combat/pressure tendencies.

---

## Goal

Capture deterministic pressure-forward variation while staying within existing biome constraints.

---

## Variant Identity

This phase covers:
- `variant_id == 1`
- `Combat-heavy / Pressure` profile

---

## Room-Order Behavior (Bounded)

Variant 1 favors earlier or denser pressure in flexible slots where legal:
- room-type counts still respect biome rules
- SAFE placement constraints remain enforced
- fixed milestones remain unchanged
- pressure tendency appears through legal ordering, not structural changes

---

## Encounter/Spawn Behavior (Bounded)

Variant 1 favors stronger pressure composition tendencies already documented/implemented:
- higher-pressure mixes within legal enemy pools (for example earlier elite/heavy presence where biome permits)
- room-type count bounds still enforced
- deterministic spawn slot timing/order maintained
- deterministic pattern realization maintained

---

## Safety Boundaries

Variant 1 must not:
- exceed count caps
- introduce unsupported enemies (e.g., no `Ranged` before legal biome scope)
- alter boss logic or milestone structure

---

## Phase 4 Checklist

- [ ] Variant 1 mapping is explicit and deterministic
- [ ] Pressure-forward room ordering remains bounded
- [ ] Pressure-forward composition remains within legal pools/caps
- [ ] Structural/gameplay non-seed boundaries remain intact

Stop after Phase 4.
