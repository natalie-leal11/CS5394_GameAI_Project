# prompt_02 — Biome 4 visuals & hazards: overlays, lava caps, elite VFX

**Target implementation:** `src/dungeon/biome4_visuals.py`, `src/dungeon/hazard_system.py`, `src/systems/vfx.py`, asset paths under `assets/tiles/biome4/`.

---

## Objective

Capture **rendering and hazard** integration for **Biome 4**: prop overlays, lava/magma visuals, **elite** spawn flashes, and **reinforcement** telegraphs—without bypassing the shared tile renderer.

## Scope

- **Included:** Draw order (tiles → hazards → props → entities); hazard damage caps tied to room metadata; performance (batching, no per-frame surface alloc).
- **Not included:** Replacing Biome 1–3 art.

## Prompt body (for Cursor)

List **each** visual helper in `biome4_visuals` and when it is called from `GameScene` or room draw. Relate **hazard** tile layers to `HazardSystem` queries for the player footprint.

## Constraints

- Asset paths must follow repo root `assets/...` (not `src/assets/`).
- Visual-only changes must not affect hitboxes unless spec explicitly ties them.

## Deliverables

- Layer diagram (text) of draw passes for a Biome 4 combat room.

## Sources

- `src/dungeon/biome4_visuals.py`, `src/dungeon/hazard_system.py`, `src/dungeon/biome4_rooms.py`
