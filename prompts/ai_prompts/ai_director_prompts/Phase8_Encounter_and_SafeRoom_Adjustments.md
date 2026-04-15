# Phase 8 — Encounter and Safe-Room Adjustments

Wire Director outputs into existing encounter and safe-room flows after biome phases are defined.

---

## Goal

Apply deterministic Director directives at legal integration points without gameplay redesign.

---

## Encounter Integration Rules

Integrate Director directives for eligible rooms only:
- bounded enemy count adjustments
- bounded composition/archetype bias
- bounded elite and reinforcement policies
- bounded spawn pacing profile

Preserve:
- room progression and milestone structure
- boss room handling
- existing non-AI architecture

---

## Safe-Room Integration Rules

Director influence remains bounded bias only:
- heal bias
- upgrade offering bias/profile/order/weights where existing code supports it

Must preserve:
- existing safe-room UI flow
- exactly one player-selected upgrade
- no forced final choice by Director

---

## Cross-Phase Safety Rules

Do not:
- merge biome logic into a single non-biome-aware pathway that removes documented differences
- alter core combat/boss/menu systems
- add new gameplay systems

---

## Phase 8 Checklist

- [ ] Eligible encounters consume deterministic bounded directives
- [ ] Safe-room offerings/heal consume deterministic bounded bias
- [ ] Player one-choice safe-room rule remains intact
- [ ] Biome-specific differences remain preserved

Stop after Phase 8.
