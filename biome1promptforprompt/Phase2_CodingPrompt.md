# Phase 2 — Incremental Coding Prompt  
# Player System (animations, movement, dash, attacks, parry, hit/death)

Implement **only** the following. Do not add enemies, combat damage resolution, dungeon, spawn system, or any later-phase features. Stop when this phase is complete.

---

## 1. Scope

- **Phase 2 deliverables:** Player entity with world_pos; animations (idle, walk, attack_short, attack_long, dash, block, parry, hit, death); movement system (WASD); dash (Space); short/long attack (mouse); block/parry (120ms window); hit and death states with animations. Camera in GameScene must follow player.
- **Source of truth:** Requirements_Analysis_Biome1.md and the master prompt (promptForpromptDungeon-v1.md). Use exact asset paths; do not invent paths.
- **Architecture:** Add under `src/` as in the master prompt: `entities/player.py`, `systems/movement.py`, `systems/animation.py`. No monolithic file. Do not restructure `src/` beyond adding these modules.

---

## 2. Player asset path and states (contract)

- **Base path:** `assets/entities/player/`
- **Required states (folder names):** idle, walk, attack_short, attack_long, dash, block, parry, hit, death.
- **Animation rules (from master prompt):**
  - attack_short: 4 frames, 10 FPS, non-loop
  - attack_long: 6 frames, 10 FPS, non-loop
  - dash: 2–3 frames, 12 FPS
  - Parry: 120 ms window (timing only in this phase; full combat in Phase 4)
  - Death: remove entity after death animation completes
- Load all player art via `asset_loader.load_animation()` with player size **64×64** (from config). Do not rename folders (e.g. keep `walk`, not `move`).

---

## 3. config.py additions

- Add player and movement constants (no hardcoding in entity/system code):
  - Movement speed (e.g. px/sec), dash speed multiplier, dash duration (sec), dash cooldown (sec)
  - Parry window (e.g. 0.12 sec)
  - Base player HP (e.g. 100) for display/state only; damage resolution in Phase 4
- Use values from Requirements_Analysis_Biome1.md or the project’s parameter docs where specified; otherwise define once in config.

---

## 4. Player entity (entities/player.py)

- **world_pos:** (float x, float y) in world space. All rendering uses `draw_pos = world_pos - camera_offset`.
- **State:** One of idle, walk, attack_short, attack_long, dash, block, parry, hit, death. State drives which animation is played and whether movement/input are allowed.
- **Animations:** Use `animation` system to advance frames by dt; respect FPS and loop/non-loop per state (attack_short, attack_long, dash, death = non-loop).
- **Movement:** Apply velocity from movement system (WASD). When not in a locking state (e.g. attack, dash, parry, hit, death), allow movement input.
- **Dash:** Triggered by Space. Fixed duration and cooldown (from config). During dash: use dash animation; apply dash velocity; no other input (e.g. no attack). Optionally i-frames per Requirements.
- **Attacks:** Short attack = Left mouse click; Long attack = Right mouse click. Play attack_short or attack_long animation (non-loop); lock movement until animation ends. Do not resolve damage to enemies yet (Phase 4).
- **Block/Parry:** Block (e.g. hold key/button) shows block animation; parry is a 120 ms window (e.g. at start of block or dedicated key). Parry success/fail and effects are Phase 4; here only timing and state (parry window active for 120 ms).
- **Hit:** When “hit” is triggered (stub for Phase 4), switch to hit state, play hit animation, brief invuln or flash if specified. No actual HP subtraction required for Phase 2 if no damage source exists.
- **Death:** When HP would be 0 or death is triggered, play death animation (non-loop), then remove entity or mark inactive so GameScene no longer draws/updates it. Per master prompt: “Death removes entity after animation completes.”
- **Bounds:** Player must stay within current room/screen bounds (use logical world bounds or a simple rectangle for Phase 2). No crossing doors yet.

---

## 5. Movement system (systems/movement.py)

- **Input:** WASD (or configurable keys). Output a velocity vector (px/sec) from config movement speed.
- **Delta-time:** Multiply velocity by `dt` so movement is frame-rate independent.
- **Dash:** When dash is active, override normal velocity with dash direction and dash speed (from config). Enforce dash duration and cooldown with timers (frame-based or time-based; deterministic).
- **Collision/bounds:** Clamp or constrain player position so the player does not leave the allowed area (e.g. room or current view bounds). No tile/wall collision required in Phase 2 unless already specified in Requirements.
- Movement system updates player `world_pos`; it does not load assets or draw.

---

## 6. Animation system (systems/animation.py)

- **Role:** Given current state, dt, and per-state spec (FPS, loop/non-loop), advance frame index and return current frame surface (or index). Player (and later entities) use this to choose which sprite to draw.
- **Specs:** Store or receive for each state: frame count, FPS, loop (yes/no). Example: attack_short → 4 frames, 10 FPS, non-loop; when animation ends, transition back to idle or next state.
- **Natural sort:** Frame lists must be loaded with natural sort (already required in asset_loader). Animation system only advances index and handles end-of-animation transitions.

---

## 7. GameScene integration

- **Spawn:** When GameScene becomes active, create the player at a fixed world position (e.g. center: `(LOGICAL_W/2, LOGICAL_H/2)` or a spawn point). Use one player instance; no respawn logic yet.
- **Camera:** Set camera target to player: `set_camera_target(player.world_pos[0], player.world_pos[1])` each frame (or equivalent). So `camera_offset = player.world_pos - (LOGICAL_W/2, LOGICAL_H/2)`.
- **Update order:** Each frame: handle input → movement system updates player world_pos → animation system advances → then draw. Player draws at `draw_pos = world_pos - camera_offset`; UI (e.g. HUD) in screen-space only.
- **Render order:** Per master prompt: background fill, then tiles (if any), then hazards (if any), then enemies (none yet), then **player**, then VFX, then UI. So draw player after any floor/tiles and before UI.
- **Input:** In GameScene, handle keydown/keyup and mouse for WASD, Space (dash), Left click (short attack), Right click (long attack), and block/parry key. Do not handle Esc for quit in GameScene if that is global; or forward Esc to pause/quit per Requirements.

---

## 8. Main loop

- Ensure main still clears screen every frame, then updates and draws current scene. GameScene’s update/draw use the player and camera as above. Pass `camera_offset` from GameScene (derived from player) into draw so all world-space draws are consistent.

---

## 9. Out of scope for Phase 2

- No enemy entities or AI.
- No combat damage resolution (no HP change from attacks; parry/block can be state-only).
- No slash VFX, hit sparks, or damage numbers (Phase 4).
- No dungeon rooms, doors, or hazards (Phase 7).
- No RL logging of combat events (Phase 8).
- Lava damage “6 HP/sec” and safe rooms are later phases.

---

## 10. Checklist (satisfy before considering Phase 2 done)

- [ ] Player has world_pos and is drawn at world_pos - camera_offset.
- [ ] Camera centers on player in GameScene.
- [ ] WASD moves player at configured speed; movement is delta-time scaled.
- [ ] Dash (Space): correct duration, cooldown, and speed; dash animation plays; no movement/attack during dash.
- [ ] Short attack (Left click): 4 frames, 10 FPS, non-loop; long attack (Right click): 6 frames, 10 FPS, non-loop.
- [ ] Block and parry states exist; parry has a 120 ms window (no combat effect yet).
- [ ] Hit state and death state: animations play; on death, entity is removed or inactive after animation completes.
- [ ] All player art loaded from `assets/entities/player/<state>/` via asset_loader; player sprite 64×64.
- [ ] Player stays within bounds; no Phase 3+ features.

---

**Stop after Phase 2. Wait for user confirmation before proceeding to Phase 3.**
