# Phase 0 — Repository Contract + Non-AI Preservation Lock

Implement ONLY the contract and scaffolding required to safely integrate the AI systems into the existing `src` codebase.
Do not implement full AI logic yet.

---

## PURPOSE

Lock the integration scope so the existing repository remains intact while making room for:
- Seed-Controlled Variation
- Metrics Tracking
- Player Model
- AI Director
- deterministic logging

---

## EXISTING FILES YOU MUST INTEGRATE WITH

Read and preserve the existing behavior of:
- `src/game/scenes/game_scene.py`
- `src/game/scene_manager.py`
- `src/dungeon/room_controller.py`
- `src/systems/spawn_system.py`
- `src/game/logger.py`
- `src/game/config.py`

Do not redesign these files.
Only make additive or narrowly targeted edits.

---

## FILES TO CREATE

Create these new files only if they do not already exist:

- `src/game/ai/__init__.py`
- `src/game/ai/difficulty_params.py`
- `src/game/ai/metrics_tracker.py`
- `src/game/ai/player_model.py`
- `src/game/ai/ai_director.py`
- `src/game/rng.py`

If a folder is missing, create it minimally.

---

## IMPLEMENTATION REQUIREMENTS

### 1. difficulty_params.py
Add externally configurable constants / dictionaries for:
- player-state thresholds
- per-biome AI Director bounds
- safe-room offering bias weights
- enemy-count adjustment bounds
- reinforcement / ambush / elite bias bounds
- healing bias bounds

These values must be read-only during gameplay.

### 2. rng.py
Add a small centralized seeded RNG adapter for NEW AI-related variation only.
Requirements:
- one run seed in
- deterministic derived streams out
- no direct random calls inside Player Model or AI Director
- avoid changing unrelated non-AI generation behavior in this phase

Suggested API:
- `set_run_seed(seed: int) -> None`
- `get_run_seed() -> int`
- `get_stream(name: str, offset: int = 0)`
- `derive_seed(*parts) -> int`

Use Python `random.Random` internally in this file only.

### 3. metrics_tracker.py / player_model.py / ai_director.py
Create stubs and dataclasses only.
No heavy game wiring yet.
Each module should import cleanly.

Suggested responsibilities:
- `MetricsTracker`: room-level and run-level deterministic metrics accumulation
- `PlayerModel`: classify Struggling / Stable / Dominating from metrics + params
- `AIDirector`: output high-level bounded encounter directives from room index + metrics + params + seed-derived variation

### 4. game_scene.py
Add minimal import-safe placeholders only if needed.
Do not change gameplay flow yet.

---

## NON-AI PRESERVATION RULES

Do NOT change:
- current scene flow
- start menu behavior
- controls screen
- settings screen
- victory screen timing or art
- room rendering assets
- boss art/boss rules
- upgrade visuals
- room milestone indices
- room type definitions

---

## CHECKLIST

Before Phase 0 is complete:
- [ ] New modules exist and import without crashing
- [ ] Existing game still runs
- [ ] No menu/start/asset behavior changed
- [ ] No gameplay behavior changed yet
- [ ] No direct random calls were added outside `src/game/rng.py`

STOP AFTER PHASE 0.
