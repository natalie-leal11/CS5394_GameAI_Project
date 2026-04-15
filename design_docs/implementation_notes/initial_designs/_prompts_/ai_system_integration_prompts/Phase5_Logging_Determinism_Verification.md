# Phase 5 — Logging + Determinism Verification for Existing `src`

Implement ONLY deterministic logging and verification helpers needed for offline analysis and confidence in the integrated systems.

---

## GOAL

Add logging that supports:
- offline RL parameter tuning later
- determinism verification now

Logging must never influence runtime gameplay decisions.

---

## FILES TO EDIT

Create or update:
- `src/game/logger.py`
- `src/game/ai/metrics_tracker.py`
- `src/game/ai/ai_director.py`
- `src/game/scenes/game_scene.py`

Avoid unrelated changes.

---

## REQUIRED LOG CONTENT

Log enough to verify:
- run seed
- room index
- biome index
- room type
- player state
- selected AI directive values
- safe-room offering bias / chosen options
- clear time
- damage taken
- win/loss summary

Use file-based local logs only.

Suggested outputs:
- per-room JSONL or JSON entries
- end-of-run summary JSON

Do not read these logs back during gameplay.

---

## DETERMINISM VERIFICATION

Add lightweight verification support so the repo can confirm:
- same seed + same inputs -> same AI-side directives
- same seed -> same safe-room offering set/order
- same seed -> same encounter adjustment decisions

Do not build a giant test framework unless the repo already has one.
Small helper assertions or simple repeatable checks are enough.

---

## PRESERVATION RULES

Do NOT use this phase to:
- redesign scene flow
- redesign menus
- redesign room rendering
- redesign enemy AI
- redesign bosses
- redesign assets

This is logging/verification only.

---

## FINAL CHECKLIST

Before Phase 5 is complete:
- [ ] logs are written locally
- [ ] logs do not influence gameplay
- [ ] AI-side decisions are inspectable per room
- [ ] end-of-run summary exists
- [ ] existing game still launches
- [ ] non-AI gameplay systems remain intact

STOP AFTER PHASE 5.
