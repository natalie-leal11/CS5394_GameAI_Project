# Phase 7 — Incremental Coding Prompt
# Dungeon + Doors + Hazards

Implement **only** the following. Do not add full 30-room run, final boss, biome transitions, or meta progression. Stop when this phase is complete.

---

## 1. Scope

- **Phase 7 deliverables:** Biome 1 dungeon structure (Rooms 0–7 only); room types START, CORRIDOR, COMBAT, AMBUSH, SAFE, ELITE, MINI_BOSS; each room has room_index, biome_index=1, room_type, hazard_percentage; doors (locked during combat, unlock 0.5 s after clear, safe door different color); hazards (lava 6 HP/sec, 3-frame 6 FPS; slow tile reduces speed); safe zone (at least one 3×3 safe tile region per room; spawn tile safe); safe room (30% missing HP restore, 2 upgrade options, player picks 1, deterministic under SEED); heal drop 25% after combat clear (seeded). Generate ONE room at a time; wait for confirmation before generating the next. Do not implement RL logging in this phase (Phase 8).
- **Source of truth:** Requirements_Analysis_Biome1.md and the master prompt (promptForpromptDungeon-v1.md). Use exact asset paths; do not invent paths.
- **Architecture:** Add under `src/dungeon/`: `room.py`, `corridor.py` (if needed), `hazard_system.py`, `door_system.py`. Room controller or equivalent to manage current room and transitions. Do not restructure `src/` beyond adding these.

---

## 2. Biome 1 structure (mandatory)

- **Rooms 0–7 only.** Do not generate rooms beyond index 7.
- **Mapping:** 0 = Start Room; 1–5 = Mixed (Combat/Ambush/Safe/Corridor); 6 = Elite Room; 7 = Mini Boss Room.
- **Room data:** Each room stores at least: `room_index`, `biome_index = 1`, `room_type`, `hazard_percentage`. Door unlocking depends on `room_type` (e.g. combat rooms lock until clear; safe room doors different color).

---

## 3. Door system

- **Path:** `assets/tiles/doors/` (use assets from Requirements).
- **Rules:** Doors are **locked during combat** (enemies alive). **Unlock delay: 0.5 sec after room clear.** **Safe room door:** different color (use specified asset or tint). Doors block passage until unlocked; when unlocked, player can transition to next room (e.g. trigger zone or door interaction).

---

## 4. Hazard system

- **Lava:** 3-frame animation, 6 FPS. **Damage: 6 HP/sec** (non-negotiable). No hardcoding outside config; put damage rate in config. Player and enemies (if applicable) take damage while overlapping lava tiles.
- **Slow tile:** Reduces movement speed (e.g. by a config factor). No damage. Apply only to normal movement (dash ignores slow per Requirements).
- **Placement:** Hazards are placed per room according to `hazard_percentage` and room layout. Use deterministic seed so layout is reproducible.

---

## 5. Safe zone enforcement (mandatory)

- **Every room** must contain **at least one 3×3 safe tile region** (no lava, no slow terrain).
- **Spawn tile** (player and optionally first enemy spawn) must be **safe**.

---

## 6. Safe room rules (Biome 1)

- **Safe room (room_type SAFE):** When player enters:
  - **Restore 30% of missing HP** (deterministic).
  - **Offer exactly 2 upgrade options.** Player selects **exactly 1.** Upgrades are deterministic under SEED (no permanent carryover beyond current run).
- No combat in safe room; doors may use “safe” color.

---

## 7. Heal drop rule (Biome 1)

- **After combat room clear:** Healing drop probability = **25%.**
- Use **centralized RNG (seeded).** Healing drop must NOT exceed biome caps (if defined). Log heal drop to RL logger in Phase 8; for Phase 7 just implement the drop and placement.

---

## 8. Room-by-room generation rule (mandatory)

- **Generate ONE room at a time.** Do not generate all 8 rooms in one go.
- **Wait for user confirmation** after each room before generating the next.
- Allow user to preview and test each room. Room generation must be **deterministic under SEED.**

---

## 9. Integration

- **Current room:** GameScene (or room controller) has a current room. Enemies, hazards, and doors belong to the current room. When all enemies are dead (and mini boss if applicable), start 0.5 s unlock timer; then unlock doors. Player entering a door trigger loads the next room (room_index + 1 or by link).
- **Spawn:** In each room, spawn enemies according to room_type (and AI Director in Phase 8). Use Phase 5 telegraph and portal. Elite room (index 6) allows elite; room 7 spawns mini boss. Start room (0) has no enemies.
- **Tiles/floor:** Draw room tiles (and hazards) before entities. Render order: background fill → tiles/floor → hazards → enemies → player → VFX → UI.

---

## 10. config.py additions

- Lava damage per second (6), slow factor, hazard_percentage bounds, safe room heal 30%, heal drop 25%, door unlock delay 0.5 s. No hardcoding in dungeon code.

---

## 11. Out of scope for Phase 7

- No full 30-room run. No final boss. No biome transitions. No meta progression.
- No RL logging implementation (Phase 8); only prepare for heal drop and room clear events.

---

## 12. Checklist (satisfy before considering Phase 7 done)

- [ ] Rooms 0–7 defined; each has room_index, biome_index=1, room_type, hazard_percentage.
- [ ] Doors: locked during combat; unlock 0.5 s after clear; safe door different color.
- [ ] Lava: 6 HP/sec, 3-frame 6 FPS; slow tile reduces speed; no hardcoding outside config.
- [ ] Every room has ≥1 safe 3×3 region; spawn tile is safe.
- [ ] Safe room: 30% HP restore, 2 upgrades, player picks 1, deterministic.
- [ ] Heal drop 25% after combat clear, seeded.
- [ ] One room at a time; deterministic; user confirmation between rooms.
- [ ] No Phase 8 RL logging implementation yet.

---

**Stop after Phase 7. Wait for user confirmation before proceeding to Phase 8.**
