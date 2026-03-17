# Phase 4 — Encounter + Safe-Room Wiring into Existing `src`

Implement ONLY the minimal wiring needed to make the existing game actually use the AI Director, Seed Variation, and Player Model.

---

## GOAL

Take the current repository’s existing encounter and safe-room flow and apply AI-side directives without redesigning the rest of the game.

This is the core integration phase.

---

## FILES TO EDIT

Create or update only where necessary:
- `src/game/scenes/game_scene.py`
- `src/systems/spawn_system.py`
- `src/dungeon/room_controller.py` (only if a helper query is needed)
- `src/game/ai/ai_director.py`
- `src/game/ai/metrics_tracker.py`
- `src/game/ai/player_model.py`

Avoid changes to unrelated files.

---

## ENCOUNTER WIRING RULES

### 1. Apply AI Director only at legal decision points
Use the Director only for things the docs allow, such as:
- bounded enemy count adjustment
- bounded archetype mix adjustment
- bounded elite bias
- bounded ambush/flexible-slot decision
- bounded spawn-delay variation
- bounded reinforcement enabling/disabling

Keep all decisions deterministic.

### 2. Preserve existing room/boss structure
Do not change:
- room 0 start
- room 29 final boss
- mini-boss milestone rooms
- room type support
- existing background assets
- room visuals
- start/settings/controls scenes

### 3. Safe rooms
Integrate AI-side influence into safe-room offerings/heal bias only.

Requirements:
- player still chooses exactly ONE upgrade
- preserve existing safe-room UI flow as much as possible
- bias the offered options, not the final forced selection
- health/defense favored when struggling
- balanced mix when stable
- offense/speed/cooldown favored when dominating
- keep bounded and parameter-driven

If the current code has special-case safe-room logic for specific room indices, preserve the UI flow and adapt the option generation layer underneath it rather than redesigning the screen.

### 4. Existing src-specific preservation
This repository already has:
- custom room progression
- existing spawn patterns
- existing safe-room and boss handling
- existing per-biome room helpers

Integrate with those systems rather than replacing them.

### 5. Bosses
AI Director must not rewrite boss phase logic or final boss structure.
Boss rooms may only consume allowed high-level recovery/pacing context before entry if that behavior is already legal and bounded.

---

## SUGGESTED APPROACH

- Compute a room directive when a room becomes active.
- Apply that directive when building enemy lists / spawn slots for eligible rooms.
- Preserve current hard-coded milestone/special-room behavior where AI authority does not apply.
- For safe rooms, modify the offered option pool/order/weights, not the UI shell.

---

## CHECKLIST

Before Phase 4 is complete:
- [ ] Eligible encounters now consume deterministic directives
- [ ] Safe-room offerings/heal bias now consume deterministic directives
- [ ] Boss logic and non-AI screens remain unchanged
- [ ] Current src repository still launches and plays
- [ ] Same seed + same input path gives same AI-side choices

STOP AFTER PHASE 4.
