# Phase 3 — AI Director Foundation Integrated with Existing `src`

Implement ONLY the deterministic AI Director decision layer and connect it to the existing game state at a high level.

---

## GOAL

Use:
- deterministic metrics
- deterministic player state
- deterministic seed variation
- fixed runtime parameters

to produce bounded encounter/safe-room directives for the existing game.

The AI Director must remain a meta-layer.
It must not directly drive per-enemy logic.

---

## FILES TO EDIT

Create or update:
- `src/game/ai/ai_director.py`
- `src/game/ai/difficulty_params.py`
- `src/game/scenes/game_scene.py`

Optionally update `src/dungeon/room_controller.py` only if a tiny query/helper is necessary.
Do not redesign room generation.

---

## AI DIRECTOR REQUIREMENTS

### Inputs
The Director may read:
- room index / biome index
- current room type
- current metrics summary
- current player state
- fixed difficulty params
- seed-derived variation helpers

### Outputs
The Director may output bounded high-level directives such as:
- enemy_count_offset
- archetype_mix_profile
- elite_bias
- ambush_intensity / flexible-slot choice where legal
- reinforcement enable/disable
- spawn_delay profile
- safe-room heal bias
- upgrade offering bias profile

### Forbidden
The Director may NOT:
- modify dungeon structure
- modify milestone positions
- modify hazard caps
- modify room art or UI flow
- modify base player stats
- directly control enemy AI behavior
- perform online learning
- use direct random calls

### Runtime purity
Decision methods should be close to pure functions of:
- metrics + player state + params + room context + seed-derived helpers

---

## IMPLEMENTATION DETAILS

### 1. In ai_director.py
Add:
- `AIDirector` class
- deterministic planning methods, e.g.
  - `plan_room(...)`
  - `plan_safe_room(...)`
  - `plan_flexible_slot(...)`

Use clear dataclasses for outputs.
Clamp all outputs to configured bounds.

### 2. In game_scene.py
Instantiate and update the AI Director using the current run state.
Store the most recent directive for the current room.

Do NOT yet deeply rewrite existing enemy spawn code.
Only make the directive available and prepare for phase 4 wiring.

### 3. Preserve current game feel outside AI influence
If a room/boss/safe-room is outside AI authority, keep current behavior exactly as-is.

---

## CHECKLIST

Before Phase 3 is complete:
- [ ] AI Director exists and computes deterministic bounded directives
- [ ] AI Director uses metrics/player state/params
- [ ] AI Director does not use direct random calls
- [ ] Existing room generation and UI still work
- [ ] No broad encounter rewrite yet

STOP AFTER PHASE 3.
