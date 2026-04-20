# Phase 3 — Incremental Coding Prompt
# Enemy System (swarm / flanker / brute + elite overlay)

Implement **only** the following. Do not add combat VFX (slash, hit sparks, damage numbers), telegraphs, spawn portal, dungeon rooms, or mini boss. Stop when this phase is complete.

---

## 1. Scope

- **Phase 3 deliverables:** Three enemy types (Swarm, Flanker, Brute) with animations; elite modifier (overlay + stat bonus); enemy base class; enemies spawn at least 3 tiles from player (scaffolding); enemies stay within room/play bounds; contact damage to player every 0.5 s when in contact (frame-based, deterministic). No spawn telegraph or portal yet.
- **Source of truth:** Requirements_Analysis_Biome1.md and the master prompt (promptForpromptDungeon-v1.md). Use exact asset paths; do not invent paths.
- **Architecture:** Add under `src/` as in the master prompt: `entities/enemy_base.py`, `entities/swarm.py`, `entities/flanker.py`, `entities/brute.py`. Reuse or extend `systems/animation.py` and `systems/movement.py` as needed. Do not restructure `src/` beyond adding these modules.

---

## 2. Enemy asset paths and states (contract)

- **Base path:** `assets/entities/enemies/<type>/` with `<type>` one of: `swarm`, `flanker`, `brute`.
- **Folder names (per master prompt):** Use **walk** (NOT move), **idle**, **attack**, **death**, **hit** (if defined). Do not rename to `move`.
- **Sprite sizes:** Swarm and Flanker use default enemy size (e.g. 32×32 or as in Requirements). **Brute:** optional **80×80** per master prompt. Load all via `asset_loader.load_animation()`.
- **Elite assets (exact paths):**
  - `assets/entities/enemies/elite/elite_glow_overlay.png`
  - `assets/entities/enemies/elite/elite_aura_01.png`
  - `assets/entities/enemies/elite/elite_aura_02.png`
- **Elite rules:** +40% HP, +20% damage (store on entity; damage application in this phase is contact-only). Aura loop at **6 FPS**. Render overlay **after** the base sprite.

---

## 3. config.py additions

- Add enemy-related constants (no hardcoding in entity code): e.g. base HP and damage per type (or one base with type multiplier), contact damage interval (0.5 s), elite HP multiplier (1.4), elite damage multiplier (1.2). Use Requirements or parameter docs where specified.

---

## 4. Enemy base (entities/enemy_base.py)

- **world_pos:** (float x, float y) in world space. Drawing uses `draw_pos = world_pos - camera_offset`.
- **State:** idle, walk, attack, hit, death (or per-type subset). State drives animation; death is non-loop and leads to removal when finished.
- **Animations:** Use the same animation system as player (FPS, loop/non-loop). Load from `assets/entities/enemies/<type>/<state>/` with natural-sorted frames.
- **Elite flag:** If True, apply +40% HP and +20% damage, and draw elite overlay + aura after base sprite (aura at 6 FPS).
- **Room confinement (mandatory):** Enemies must stay within room/play bounds: do not cross doors, do not move into invalid tiles, do not leave the active room area. For Phase 3, “room” may be a single rectangle (e.g. current play area or a fixed box). Clamp or constrain position each frame so the enemy never leaves this region.
- **Contact damage (mandatory):** When the enemy’s collision rect overlaps the player’s:
  - Apply damage to the player at a **fixed interval of 0.5 seconds**.
  - Use a **frame-based or time-based timer** (deterministic; no randomness).
  - **Reset the timer when the enemy is no longer in contact** with the player.
  - Damage amount comes from config (base × elite multiplier if elite). Do not add randomness to the interval or the amount for this rule.
- **Death:** When HP ≤ 0, play death animation (non-loop). When the animation completes, remove the entity or mark inactive so it is no longer updated or drawn. No reward drop or door logic yet (Phase 6/7).

---

## 5. Swarm, Flanker, Brute (entities/swarm.py, flanker.py, brute.py)

- Each module defines one enemy type that extends the enemy base (or uses a common base).
- Differences are: asset path (`enemies/swarm/`, `enemies/flanker/`, `enemies/brute/`), base HP/damage/speed (from config or Requirements), and any type-specific behavior (e.g. Flanker dash, Brute windup). Per master prompt, “As soon as combat/AI is implemented, enemy engagement distance, dash distance, melee range, and telegraph radius MUST follow the Requirement Analysis values.” Use those values for movement speed, engagement range, and any dash/windup timing; do not override with the 3-tile spawn rule (that rule is for spawn position only).
- **Sprites:** Brute uses 80×80 if specified; Swarm and Flanker use the size defined in Requirements or config.

---

## 6. Spawn (scaffolding for Phase 3)

- **No telegraph or spawn portal in Phase 3** (Phase 5).
- When GameScene has a “test” or default room, spawn a small, deterministic set of enemies (e.g. 1 of each type, or a mix) so that:
  - Spawn positions are on the **tile grid:** `world_x = tile_x * TILE_SIZE`, `world_y = tile_y * TILE_SIZE`.
  - Every enemy is **at least 3 tiles (≥ 96 px) away** from the player at spawn.
  - If an enemy’s rect would overlap the player’s rect at spawn, shift that enemy by +3 tiles in x or y (deterministic).
- Optionally support an “elite” variant for one or more spawns (e.g. one elite per test room) so the overlay and stat modifiers can be verified. Do not implement AI Director or procedural composition yet; that comes with Phase 7/8.

---

## 7. GameScene integration

- **Update order:** After player update, update all active enemies (movement/AI, contact damage timer, state, animation). Then draw: background, then enemies, then player, then UI (per master render order: tiles → hazards → enemies → player → VFX → UI). So draw enemies **before** the player.
- **Camera:** Unchanged; still centered on player. Enemies are drawn at `world_pos - camera_offset`.
- **Bounds:** Pass the current “room” bounds (rectangle) into the movement or enemy system so all enemies are constrained. For Phase 3 this can be the same rectangle as the play area (e.g. logical world size or a padded region).

---

## 8. Contact damage rule (mandatory)

- Enemies that deal contact damage:
  - Apply damage to the player **every 0.5 seconds** while in contact.
  - Timer is **frame-based (deterministic)**; no randomness.
  - Timer **resets on exit from collision** (when player and enemy no longer overlap).
- Implement this in the enemy base or a small helper used by the base; ensure all three types that use contact damage follow this rule.

---

## 9. Elite overlay rendering

- For each elite enemy, after drawing the base sprite:
  - Draw the elite overlay (e.g. `elite_glow_overlay.png`) and/or aura frames (`elite_aura_01.png`, `elite_aura_02.png`) at 6 FPS.
  - Overlay and aura use the same world_pos and camera_offset as the base sprite (no extra offset unless specified in Requirements).

---

## 10. Out of scope for Phase 3

- No slash VFX, hit sparks, or damage numbers (Phase 4).
- No telegraphs or spawn portal (Phase 5).
- No mini boss (Phase 6).
- No dungeon rooms, doors, or hazards (Phase 7).
- No RL logging of enemy_spawn/enemy_death (Phase 8).
- No AI Director or params_biome1.json (Phase 8); use fixed test spawns only.

---

## 11. Checklist (satisfy before considering Phase 3 done)

- [ ] Swarm, Flanker, and Brute exist and load animations from `assets/entities/enemies/<type>/` (walk, idle, attack, death, hit if defined).
- [ ] Elite variant: +40% HP, +20% damage; overlay and aura drawn after base sprite; aura at 6 FPS.
- [ ] Enemies spawn at least 3 tiles from player; on grid; no overlap with player at spawn (shift by +3 tiles if needed).
- [ ] Enemies stay within room/play bounds; no crossing doors or leaving the active area.
- [ ] Contact damage to player every 0.5 s while in contact; timer frame-based; timer resets on exit from collision.
- [ ] Enemy death: death animation plays; entity removed or inactive when animation completes.
- [ ] Render order: enemies drawn before player; camera still follows player.
- [ ] No Phase 4/5/6/7/8 features (no VFX, telegraph, portal, mini boss, dungeon, RL logging).

---

**Stop after Phase 3. Wait for user confirmation before proceeding to Phase 4.**
