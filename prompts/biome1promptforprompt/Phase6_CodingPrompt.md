# Phase 6 — Incremental Coding Prompt
# Mini Boss

Implement **only** the following. Do not add full dungeon generation, biome transitions, or final boss. Stop when this phase is complete.

---

## 1. Scope

- **Phase 6 deliverables:** Mini boss entity (96×96); states idle, move, attack_01, attack_02, dash, windup, phase_change, hit, death; health bar (frame + fill assets); on death spawn reward and unlock doors after delay. Mini boss confined to room; combat and contact rules apply.
- **Source of truth:** Requirements_Analysis_Biome1.md and the master prompt (promptForpromptDungeon-v1.md). Use exact asset paths; do not invent paths.
- **Architecture:** Add `entities/mini_boss.py` (or under existing entities). Health bar is UI (screen-space or fixed to boss). Door unlock is a signal to the room/door system (Phase 7); for Phase 6, implement the delay and a callback or flag that Phase 7 can use.

---

## 2. Mini boss asset path and states

- **Path:** `assets/entities/enemies/mini_boss/`
- **States (folder names):** idle, move, attack_01, attack_02, dash, windup, phase_change, hit, death.
- **Sprite size:** **96×96** (master prompt). Load via `asset_loader.load_animation()` with natural sort.
- **Health bar assets:**
  - `assets/ui/hud/mini_boss_health_frame_400x40.png`
  - `assets/ui/hud/mini_boss_health_fill_396x24.png`
- **On death (mandatory):** Spawn reward (e.g. pickup or placeholder); unlock doors after a short delay (e.g. 0.5 s). Door unlock: set a “doors unlocked” flag or call into door system so Phase 7 can implement actual door state.

---

## 3. Mini boss behavior

- **world_pos, state, animations:** Same pattern as other entities. State machine drives move, attack_01, attack_02, dash, windup, phase_change, hit, death. Death is non-loop; when animation completes, remove entity, spawn reward, and trigger “unlock doors after delay.”
- **Room confinement:** Mini boss must stay within room bounds (same as Phase 3); no crossing doors.
- **Combat:** Mini boss can deal damage (contact and/or attack hitboxes); player can damage mini boss. Use config for HP and damage. Phase 4 combat resolution applies.
- **Health bar:** Draw in UI layer (screen-space). Position fixed (e.g. top-center) or follow boss on screen. Fill width based on current HP / max HP. Use frame and fill assets above.

---

## 4. Spawn and room

- **When:** Mini boss spawns in the “mini boss room” (e.g. room index 7 in Biome 1). Until Phase 7, use a single test arena or a flag “is mini boss room” so the spawn system (Phase 5) or scene logic spawns one mini boss. No need for full dungeon yet.
- **Telegraph/portal:** Optionally use Phase 5 telegraph and portal for mini boss spawn; otherwise spawn at a fixed position in the room.

---

## 5. Reward spawn

- On death, spawn a reward (e.g. heal pickup or placeholder sprite) at or near mini boss position. Reward logic (what it does when collected) may be minimal in Phase 6 (e.g. heal 30% or placeholder); full safe-room upgrades are Phase 7.

---

## 6. Door unlock delay

- After mini boss death animation and reward spawn, wait a configured delay (e.g. 0.5 s), then set “doors unlocked” for the current room. Phase 7 will use this to change door state and allow transition.

---

## 7. config.py additions

- Mini boss HP, damage, speeds (move, dash), and door-unlock delay. No hardcoding in mini_boss.py.

---

## 8. Out of scope for Phase 6

- No full dungeon or multiple room types (Phase 7); one mini boss room or test arena is enough.
- No RL training; logging can be Phase 8.

---

## 9. Checklist (satisfy before considering Phase 6 done)

- [ ] Mini boss loads and plays all states from `assets/entities/enemies/mini_boss/` at 96×96.
- [ ] Health bar displays with frame and fill assets; fill reflects current HP.
- [ ] On death: reward spawns; after delay, doors marked unlocked (for Phase 7).
- [ ] Mini boss confined to room; combat and contact damage work.
- [ ] No Phase 7 dungeon generation or Phase 8 RL beyond any stub.

---

**Stop after Phase 6. Wait for user confirmation before proceeding to Phase 7.**
