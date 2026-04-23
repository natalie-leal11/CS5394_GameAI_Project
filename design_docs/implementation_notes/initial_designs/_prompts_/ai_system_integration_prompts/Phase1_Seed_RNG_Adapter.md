# Phase 1 — Seed/RNG Adapter for Existing `src` Code

Implement ONLY deterministic seed-controlled variation infrastructure that can plug into the existing codebase.
Do not yet rewrite the encounter loop.

---

## GOAL

Add seed-derived variation streams that integrate with the existing `src` game without changing non-AI systems.

This phase must respect:
- the existing current room sequence
- the existing room controller
- the existing spawn system
- the existing asset/UI pipeline

---

## FILES TO EDIT

Create or update:
- `src/game/rng.py`
- `src/game/ai/ai_director.py`
- `src/game/scenes/game_scene.py` (minimal initialization only)
- `src/game/config.py` (only if a small constant toggle is needed)

---

## IMPLEMENTATION REQUIREMENTS

### 1. In `src/game/rng.py`
Extend the RNG adapter with deterministic helper functions for AI-side variation.
Suggested concepts:
- one global run seed
- named deterministic streams
- stable per-room derivation

Suggested helper API:
- `make_room_rng(room_index: int, channel: str) -> random.Random`
- `sample_seeded_choice(seq, room_index: int, channel: str)`
- `sample_seeded_shuffle(seq, room_index: int, channel: str)`
- `sample_seeded_uniform(a, b, room_index: int, channel: str)`
- `sample_seeded_int(a, b, room_index: int, channel: str)`

All AI-side randomness must route through this module.

### 2. In `src/game/ai/ai_director.py`
Add dataclasses for deterministic outputs, for example:
- `EncounterDirective`
- `SafeRoomDirective`
- `VariationDirective`

Include only fields that the Director is allowed to influence, such as:
- enemy_count_offset
- spawn_delay_profile
- reinforcement_enabled
- elite_bias
- ambush_bias
- safe_room_heal_bias
- upgrade_bias_profile

Do NOT directly control enemy behavior or room generation.

### 3. In `src/game/scenes/game_scene.py`
Initialize the run seed for new AI systems when a run starts or resets.
Use the same existing seed source already used by the game for deterministic runs.

Requirements:
- do not change the game’s existing room skeleton
- do not change screen flow
- do not change existing room loading semantics
- do not break existing reset/start behavior
seed variation is limited to:
- flexible room-type selection within fixed biome bounds
- enemy spawn-pattern variation
- seed must NOT change:
- room size
- room geometry/layout
- milestone rooms
- boss structure
- safe-room count per biome

### 4. Boundaries

Seed-controlled variation SHALL be limited to the following:

- Room type selection within predefined biome-specific bounds  
  (e.g., selecting positions of COMBAT, AMBUSH, ELITE within allowed slots)
- Enemy encounter composition within allowed biome + room-type limits  
- Enemy spawn positions and formation realization (spread, triangle, ambush)
- Enemy spawn ordering and slot-based timing (within defined delays)
- Hazard placement (lava / slow tiles) within predefined caps

---

Seed-controlled variation MUST NOT alter:

- Total number of rooms per biome  
- Fixed milestone room positions:
  - START room (first)
  - MINI_BOSS / FINAL_BOSS room (last)
- Safe room count (exactly 1 per biome)
- Room size, grid dimensions, or layout structure
- Door placement and connectivity
- Supported room types per biome
- Boss identity, phases, or attack logic
- Core gameplay systems (movement, combat mechanics)
- UI screens (start/menu/victory)

---

### Determinism Requirement

Given the same:


SEED + BIOME_INDEX + ROOM_INDEX


The system MUST produce identical:

- Room type selection (within bounds)
- Enemy composition
- Spawn positions
- Spawn ordering
- Hazard placement

---

## CHECKLIST

Before Phase 1 is complete:
- [ ] AI-side seed helper exists
- [ ] Derived room-level variation is deterministic
- [ ] Existing run start/reset still works
- [ ] No non-AI systems were redesigned
- [ ] AI Director now has deterministic directive dataclasses but not full logic yet

STOP AFTER PHASE 1.
