# Biome 4 Phase 2 — Corrections & Clarifications

This section resolves discrepancies in **Phase 2 — Visual / Hazard / VFX Integration**.

---

## 1. Asset Path Convention

All asset paths must follow the project asset convention.

Correct root path:

`assets/...`

Paths are relative to the **project root** (or as defined in the existing asset loader).

Do NOT use:

`src/assets/...`

All Phase 2 paths must therefore follow the format:

Examples:

- `assets/tiles/biome4/props/`
- `assets/tiles/biome4/hazards/`
- `assets/effects/spawn/`
- `assets/effects/elites/`
- `assets/effects/telegraphs/`
- `assets/effects/boss/`
- `assets/entities/projectiles/`
- `assets/backgrounds/`

Implementers must **not create a new `src/assets/` directory**.

---

## 2. Particle System Clarification

Phase 2 references the folder:

`assets/effects/particles/`

Particle effects in Biome 4 are **optional ambient visuals**.

If the engine already supports particle effects, it may optionally load **only** these filenames (do not invent or depend on others):

- `ash_particle_8x8.png`
- `ember_particle_8x8.png`
- `ember_glow_16x16.png`

Important rules:

- Do **not invent additional particle filenames**
- Do **not require these particles for gameplay**
- If the files are missing, the engine must **fail gracefully and continue rendering**

Particles are only visual enhancements.

---

## 3. Background Rendering Rule

Biome 4 introduces background references:

- `assets/backgrounds/biome4_room_bg.png`
- `assets/backgrounds/final_boss_arena_bg.png`

These backgrounds must be treated as:

**optional backdrop overlays**

They must **NOT replace the existing tile-grid renderer**.

Rendering order must remain:

1. **Background** (when supported): treat as a single layer drawn **before** the tile grid (step 0).
2. Tile grid floor
3. Wall tiles
4. Biome hazard overlays
5. Biome props
6. Entities
7. VFX
8. UI

Background images should only render **behind the tile grid if supported**.

If the engine does not support this cleanly, the backgrounds may be ignored **without changing gameplay or room logic**.

---

## 4. Boss Telegraph Timing Metadata

Phase 2 prepares telegraph assets for Phase 3 boss combat.

Add metadata support for the following telegraph timings:

| Attack | Telegraph Duration |
|--------|---------------------|
| Fireball cast | 0.5 s |
| Lava wave | 0.75 s |
| Meteor target | 1.0 s |
| Teleport strike warning | 0.6 s |

Rules:

- Telegraph timing must be deterministic
- Timing must be configurable through **constants or a dedicated Biome 4 boss metadata module** so Phase 3 can read them (e.g. `BIOME4_BOSS_TELEGRAPH_*_SEC` in config)
- Do not execute the attacks yet
- Only ensure the telegraph system can consume these values later

---

## 5. Final Boss Arena Rendering Preparation

Even though Phase 2 does not implement boss combat, the rendering pipeline must support **Room 29 boss arena visuals**.

Room 29 must be able to render:

- `assets/backgrounds/final_boss_arena_bg.png`
- Biome hazard overlays
- Boss spawn portal
- Boss telegraph indicators
- Boss death visual effects
- **Boss UI anchor region:** a reserved screen area (e.g. top center) for future boss HP/name UI; **no UI widgets are implemented in Phase 2**

This preparation ensures Phase 3 can plug in boss logic without changing the renderer.

---

## 6. Grab / Claw Mechanic Exclusion

Biome 4 **does not include the grab / claw mechanic**.

Phase 2 must therefore:

- not load grab assets
- not reference grab animations
- not implement grab VFX
- not introduce immobilization effects

Any grab-related content must be ignored entirely.

---

## 7. Spawn FX Integration Rule

Spawn FX assets:

`assets/effects/spawn/`

- `spawn_portal_64x64.png`
- `spawn_portal_anim_64x64.png`
- `summon_circle_128x128.png`
- `summon_circle_anim_128x128.png`

**Scope:** Use these spawn/portal/summon assets **only for Biome 4 rooms** (e.g. when room is in Biome 4 range, such as `biome_index == 4` or campaign room index 24–29). Other biomes keep existing spawn visuals.

Integration rule:

Prefer extending:

- the current **spawn VFX registry**
- the current **room rendering helper**
- or the current **spawn telegraph system**

Avoid modifying core spawn logic unless absolutely necessary.

Spawn VFX must remain **deterministic and metadata-driven**.

---

## 8. Hazard Visuals Rule

Biome 4 hazard visuals (lava_bubble, lava_flow, magma_pool) are **visual variants only** for existing hazard tiles.

- **Gameplay:** Do not add new hazard tile types or new damage/slow mechanics. Reuse existing `TILE_LAVA` and `TILE_SLOW` logic.
- **Visuals:** When in Biome 4, the **visual** drawn for a lava (or optionally slow) tile may be Biome 4–specific (e.g. choose among lava_bubble, lava_flow, magma_pool for lava tiles).
- Magma pool is a **visual variant for lava tiles only**; it does not introduce a new gameplay hazard.

---

## 9. Updated Phase 2 Checklist

Add the following validation checks to the Phase 2 checklist:

- [ ] Biome 4 props load through the current asset pipeline (using `assets/` path convention, no `src/`)
- [ ] Biome 4 hazard visuals integrate as **overlays** without modifying the tile renderer
- [ ] Spawn portal and summon circle assets render correctly for Biome 4 rooms
- [ ] Red elite aura effects work for Biome 4 elites
- [ ] Boss telegraph assets load successfully
- [ ] Boss teleport / spawn / death VFX load successfully
- [ ] Boss projectile assets are loadable for Phase 3
- [ ] Particle effects fall back safely if assets are absent
- [ ] Room 29 arena rendering support is prepared
- [ ] No final boss combat logic exists yet
