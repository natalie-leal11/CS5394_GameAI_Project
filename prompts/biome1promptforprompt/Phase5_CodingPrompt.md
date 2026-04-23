# Phase 5 — Incremental Coding Prompt
# Spawn + Telegraph + Spawn Portal

Implement **only** the following. Do not add mini boss logic, dungeon room generation, or RL logging. Stop when this phase is complete.

---

## 1. Scope

- **Phase 5 deliverables:** Spawn system that places enemies using telegraphs and a spawn portal; telegraph duration 0.5 s, 3 pulses; spawn at final frame; telegraph and portal have no collision. Enemies still confined to room and subject to Phase 3/4 rules.
- **Source of truth:** Requirements_Analysis_Biome1.md and the master prompt (promptForpromptDungeon-v1.md). Use exact asset paths; do not invent paths.
- **Architecture:** Add or extend `src/systems/spawn_system.py` (or equivalent). Telegraph and portal are visual only (no collision). Do not restructure `src/` beyond adding/editing this module and any small VFX/entity hooks.

---

## 2. Telegraph assets and rules

- **Path:** `assets/effects/telegraphs/` (use assets listed in Requirements, e.g. telegraph tile, AOE ring, etc.).
- **Rules (mandatory):**
  - **Duration:** 0.5 seconds.
  - **Pulses:** 3 (visual pulse count).
  - **Spawn at final frame:** The actual enemy spawn occurs when the telegraph finishes (at the end of the 0.5 s duration).
  - **No collision:** Telegraph does not block movement or attacks; it is visual only.

---

## 3. Spawn portal assets and rules

- **Path:** `assets/effects/spawn_portal/` (use frames listed in Requirements).
- **Rules:** Play portal animation at the spawn position when an enemy is about to spawn (e.g. during or at end of telegraph). Spawn the enemy at the designated position when the telegraph’s final frame/instant is reached. Portal has **no collision**.

---

## 4. Spawn system behavior

- **Trigger:** When a room (or test arena) requires enemy spawns, the spawn system places one or more spawn “slots” (positions). For each slot:
  1. Show telegraph at that position for 0.5 s (3 pulses).
  2. At the end of the telegraph, show spawn portal and spawn the enemy at that position.
  3. Enemy appears on the tile grid (`world_x = tile_x * TILE_SIZE`, `world_y = tile_y * TILE_SIZE`), at least 3 tiles from player if possible, and no overlap with player (shift by +3 tiles if needed).
- **Timing:** All timers frame-based (deterministic). Spawn delay between successive spawns may come from config or AI Director later; for Phase 5 use a fixed delay (e.g. from config) so multiple enemies do not spawn on the same frame unless designed.
- **Enemy type:** Spawn system receives or chooses enemy type (swarm/flanker/brute) and elite flag per room/design; no AI Director yet. Use deterministic logic (e.g. slot index + SEED) so runs are reproducible.

---

## 5. Integration with GameScene / room

- **Room/arena:** Use the same “room” bounds as Phase 3 (single rectangle or test arena). Spawn positions must be inside room bounds and on the grid. Enemies remain confined after spawn (Phase 3).
- **Render order:** Draw telegraphs and spawn portal in the VFX layer (after entities, before UI). Use camera_offset for world-to-screen. Remove telegraph and portal when their animation/time is done.

---

## 6. config.py additions

- Add spawn timing constants: telegraph duration (0.5 s), pulses (3), spawn delay between slots (optional). No hardcoding in spawn system.

---

## 7. Out of scope for Phase 5

- No mini boss (Phase 6).
- No dungeon layout or room types (Phase 7); use single test room/arena if needed.
- No RL logging (Phase 8).

---

## 8. Checklist (satisfy before considering Phase 5 done)

- [ ] Telegraph shows for 0.5 s with 3 pulses at spawn position; no collision.
- [ ] Spawn portal plays at spawn position; enemy spawns at telegraph end; no collision.
- [ ] Enemies spawn on grid, within room bounds, with 3-tile/overlap rules respected.
- [ ] Spawn timing is deterministic (frame-based).
- [ ] No Phase 6/7/8 features.

---

**Stop after Phase 5. Wait for user confirmation before proceeding to Phase 6.**
