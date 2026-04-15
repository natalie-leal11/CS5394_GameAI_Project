# Phase 1 — AI Director Overview and Boundaries

Define the AI Director role clearly before implementation-level wiring.

---

## Goal

Establish a strict Director-only contract for what the AI Director controls and what it never controls.

---

## What the AI Director Controls

The Director controls high-level, bounded adaptation directives such as:
- enemy count offset (bounded)
- archetype/composition bias profile (bounded)
- elite bias (bounded)
- reinforcement enable/chance (bounded)
- spawn pacing/delay profile (bounded)
- safe-room heal and upgrade offering bias (bounded)

All outputs are advisory/planning directives for existing systems.

---

## What the AI Director Reads

The Director may read:
- room and biome context (room index, biome index, room type)
- metrics summary from `MetricsTracker`
- current player state from `PlayerModel` (`STRUGGLING`, `STABLE`, `DOMINATING`)
- fixed runtime parameters from `difficulty_params.py`
- seed-driven context/variation helpers where already supported

---

## What the AI Director Does Not Control

The Director must not:
- rewrite dungeon generation or room ordering
- change milestone positions or boss room placement
- redesign room types, scene flow, menus, controls, or art
- directly control per-enemy behavior trees/attack logic
- mutate base player/enemy stats outside existing bounded systems
- perform online training or runtime RL

---

## Determinism Baseline

Director planning must be deterministic:
- no direct unseeded random calls
- same seed + same input path -> same directive sequence
- all values clamped to configured bounds

---

## Phase 1 Checklist

- [ ] Director responsibility boundary is explicit and narrow
- [ ] Inputs are defined and limited
- [ ] Outputs are high-level and bounded
- [ ] Forbidden responsibilities are explicit
- [ ] Determinism expectations are explicit

Stop after Phase 1.
