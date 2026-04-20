# Phase 3 — Director Core Decision Logic

Define deterministic AI Director planning methods and bounded directive outputs.

---

## Goal

Produce high-level directives as deterministic functions of:
- metrics summary
- player state
- room/biome context
- fixed parameters
- seed-driven variation context (where already supported)

---

## Required Director Inputs

The Director reads:
- room index, biome index, room type
- metrics summary snapshot from existing tracker
- `PlayerState` classification (`STRUGGLING`, `STABLE`, `DOMINATING`)
- fixed parameters from `difficulty_params.py`
- seed-derived helpers used by current architecture

Do not consume untracked or undocumented inputs.

---

## Required Director Outputs

Output bounded high-level directives only, such as:
- enemy count offset
- composition/archetype bias
- elite bias
- reinforcement policy
- spawn delay/pacing profile
- safe-room heal bias
- safe-room upgrade offering bias

Clamp all outputs to configured bounds.

---

## Deterministic Planning Methods

Implement clear planning methods (naming can vary), for example:
- room directive planner
- safe-room directive planner
- optional flexible-slot planner where legal

Methods should be pure or near-pure:
- no unseeded randomness
- no hidden stateful drift
- no direct mutation of unrelated gameplay systems

---

## Forbidden Core Behavior

Director logic must not:
- directly run per-enemy combat AI
- redesign spawn architecture
- alter room progression structure
- alter UI/menu/scene flow
- implement runtime online learning

---

## Phase 3 Checklist

- [ ] Core inputs/outputs are explicit and bounded
- [ ] Decision logic is deterministic and inspectable
- [ ] Director remains meta-layer only
- [ ] No non-Director gameplay responsibilities are added

Stop after Phase 3.
