# Phase 4 — Incremental Coding Prompt
# Combat + VFX (slash / hit sparks / damage numbers)

Implement **only** the following. Do not add telegraphs, spawn portal, mini boss, dungeon rooms, or RL logging. Stop when this phase is complete.

---

## 1. Scope

- **Phase 4 deliverables:** Full combat resolution (player attacks damage enemies; enemy attacks and contact damage reduce player HP; parry/block effects); slash VFX; hit sparks; damage numbers (font_damage.ttf, float 0.6 s, fade out). Block reduces contact damage; perfect parry negates contact damage (per Requirements). No new enemies or rooms beyond what Phases 2–3 provide.
- **Source of truth:** Requirements_Analysis_Biome1.md and the master prompt (promptForpromptDungeon-v1.md). Use exact asset paths; do not invent paths.
- **Architecture:** Add or extend under `src/systems/combat.py` (or equivalent). VFX may live in `systems/` or a small `vfx` helper. Do not restructure `src/` beyond adding/editing these.

---

## 2. Combat resolution

- **Player → Enemy damage:** When player short or long attack connects (hitbox/hurtbox overlap during attack active frames), apply damage to the enemy. Use attack damage values from config (short vs long; type modifiers if any). Enemy HP decreases; at 0, enemy enters death state and is removed when animation completes (already in Phase 3).
- **Enemy → Player damage:** Contact damage (0.5 s interval) and any enemy attack hitboxes (melee/projectile) apply damage to the player. Player HP from config; at 0, player enters death state and is removed after death animation (Phase 2).
- **Block:** When player is blocking, reduce incoming contact/attack damage by a defined factor (from config or Requirements). Block does NOT reduce lava damage (Phase 7).
- **Parry:** During the 120 ms parry window, if the player parries an incoming attack, negate that hit (no damage). Optionally reflect or stun per Requirements. Perfect parry negates contact damage for that contact instance.
- **Determinism:** All damage and hit detection must be deterministic (frame-based or seeded); no randomness unless explicitly specified (e.g. crits) in Requirements.

---

## 3. Slash VFX

- **When:** Play slash VFX when player short or long attack hits an enemy (or at attack release). Use assets from Requirements (e.g. slash sprites under `assets/effects/` if specified). Position at hit location or weapon arc; respect camera_offset (world to screen).
- **Duration:** One-shot or short animation; remove when finished. No collision.

---

## 4. Hit sparks

- **When:** Play hit sparks when any attack (player or enemy) connects. Position at impact; use assets from Requirements (e.g. under `assets/effects/`). Draw in world-space then convert to screen with camera_offset.
- **Duration:** Short; remove when finished. No collision.

---

## 5. Damage numbers

- **Font:** Use `assets/fonts/font_damage.ttf` (or path from Requirements). Fallback to placeholder font if missing so the game does not crash.
- **When:** On any damage dealt (player taking damage or enemy taking damage), spawn a floating number at the damaged entity’s position.
- **Behavior:** Float for **0.6 seconds**; then **fade out**. Display the numeric value (e.g. damage amount). Draw in screen-space (world position minus camera_offset) so it follows the entity on screen.
- **Render order:** After entities (player/enemies), before or with other VFX; per master prompt: “VFX (slash/hit sparks/telegraphs/portal)” then “UI (HUD, damage numbers, prompts)”. So damage numbers are part of VFX/UI layer.

---

## 6. Integration with Phase 2 and 3

- Ensure player attack hitboxes (short/long) are defined and checked against enemy hurtboxes each frame during attack active frames.
- Ensure enemy attack hitboxes (and contact) are checked against player hurtbox; apply block/parry before applying damage.
- Ensure all damage events can trigger: enemy death, player death, damage numbers, hit sparks, and slash VFX as above.

---

## 7. config.py additions

- Add combat constants: player short/long attack damage, block damage reduction factor, parry window (already 0.12 s if present). No hardcoding in combat code.

---

## 8. Out of scope for Phase 4

- No telegraphs or spawn portal (Phase 5).
- No mini boss (Phase 6).
- No dungeon, doors, or hazards (Phase 7).
- No RL logging (Phase 8).

---

## 9. Checklist (satisfy before considering Phase 4 done)

- [ ] Player attacks deal damage to enemies; enemies can die from player attacks.
- [ ] Enemies and contact damage deal damage to player; block reduces damage; parry negates damage when in window.
- [ ] Slash VFX plays on player hit; hit sparks on impact; both use correct assets and camera.
- [ ] Damage numbers appear for 0.6 s and fade out; use font_damage.ttf (or fallback).
- [ ] Player and enemy death handled; no Phase 5/6/7/8 features.

---

**Stop after Phase 4. Wait for user confirmation before proceeding to Phase 5.**
