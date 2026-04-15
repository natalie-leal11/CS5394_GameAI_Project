# Phase 6 — Gameplay Impact

Describe gameplay-facing effects of seed variation without expanding system scope.

---

## Goal

Document how each implemented seed variation changes run feel while preserving deterministic fairness constraints.

---

## Shared Gameplay Impact (All Variants)

All variants can change:
- pacing and encounter order within flexible slots
- encounter pressure profile via legal composition/count differences
- safe-room timing/location within bounded slots

All variants cannot change:
- campaign structure
- milestone rooms
- room size/layout algorithm
- boss identity/phase systems

---

## Variation-Specific Impact

`Balanced` (Variant 0):
- closest to baseline progression and composition
- smooth pacing profile, implementation-aligned

`Combat-heavy / Pressure` (Variant 1):
- stronger early/mid combat pressure where legal
- more pressure-forward encounter ordering/compositions within bounds

`Ambush-heavy / Spike` (Variant 2):
- more ambush/spike tendency in flexible slots where legal
- higher positional pressure moments while respecting caps/fairness

---

## Biome Scaling Context

Gameplay impact remains biome-aware:
- Biome 1 baseline pool constraints preserved
- Biome 2 adds `Heavy` pressure possibilities
- Biome 3 adds `Ranged` complexity
- Biome 4 keeps high-intensity pre-boss pressure but fixed final-boss structure

---

## Phase 6 Checklist

- [ ] Shared vs variation-specific impact is clear
- [ ] Impact descriptions stay inside implemented/documented scope
- [ ] Biome scaling differences are preserved
- [ ] No new gameplay systems are introduced

Stop after Phase 6.
