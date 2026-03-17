# Phase 2 — Metrics Tracking + Player Model Integration into Existing `src`

Implement ONLY deterministic player metrics tracking and player-state classification, wired into the current repository.

---

## GOAL

Use the existing gameplay loop to measure player performance without changing non-AI systems.
Then classify the player as:
- STRUGGLING
- STABLE
- DOMINATING

This classification must be deterministic and parameter-driven.

---

## FILES TO EDIT

Create or update:
- `src/game/ai/metrics_tracker.py`
- `src/game/ai/player_model.py`
- `src/game/scenes/game_scene.py`
- `src/game/logger.py` (only if tiny helper stubs are needed)

Do not redesign unrelated files.

---

## METRICS TO TRACK

Track only metrics supported by the SRS/project docs, such as:
- player HP percent
- health trend
- damage taken in room
- room clear time
- recent clean clear / heavy-damage outcomes
- death count in run
- rooms cleared
- run elapsed time

Keep it lightweight and deterministic.

---

## IMPLEMENTATION REQUIREMENTS

### 1. metrics_tracker.py
Add a `MetricsTracker` class that supports:
- run start
- room start
- room end
- damage taken
- enemy room clear result
- player death
- run end snapshot
- read-only current summary access

Use dataclasses where helpful.

### 2. player_model.py
Add:
- `PlayerState` enum or constants
- `PlayerModel` class
- parameter-driven thresholds loaded from `difficulty_params.py`

`PlayerModel.classify(...)` must be a pure deterministic function of:
- current metrics summary
- fixed thresholds/params

No randomness.

### 3. game_scene.py
Integrate metrics hooks into the existing run loop.
Use narrow changes only.

Examples of legitimate hook points:
- when a run/reset begins
- when a room loads
- when room combat starts
- when player takes damage
- when room clears
- when player dies
- when final win/loss resolves

Do NOT alter:
- attack mechanics
- animation systems
- enemy AI
- asset bindings
- menu/start/settings logic

### 4. Preserve existing safe-room/player flow
Do not redesign current safe-room UI here.
Just make sure the Player Model can later influence safe-room offerings.

---

## CHECKLIST

Before Phase 2 is complete:
- [ ] Metrics tracker exists and is wired into current run flow
- [ ] Player model exists and classifies deterministically
- [ ] Thresholds come from `difficulty_params.py`
- [ ] Existing game still plays normally
- [ ] No AI Director decisions applied yet beyond internal state computation

STOP AFTER PHASE 2.
