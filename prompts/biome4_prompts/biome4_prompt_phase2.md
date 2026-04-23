# Phase 2 — Incremental Coding Prompt
# Additive Biome 4 Visual / Hazard / Spawn FX Integration in `src/`

Implement **only** the following. Do not add final boss combat logic yet. Stop when this phase is complete.

---

## 1. Scope

- **Phase 2 deliverables:** additive Biome 4 visual integration for room overlays, hazards, particles, elite effects, and reinforcement spawn effects inside the existing `src/` codebase.
- **Architecture rule:** reuse the existing tile renderer, hazard system, VFX system, spawn telegraph system, and asset loader.

---

## 2. Additive-only implementation rule

Preferred approach:
- create a dedicated Biome 4 visuals helper such as `src/dungeon/biome4_visuals.py`
- create a dedicated Biome 4 hazard / decoration helper if needed
- add only narrow integration hooks to current room rendering / spawn VFX logic

Do NOT:
- rewrite the current renderer
- replace current hazard logic
- invent a parallel VFX system
- hardcode direct image loading outside the centralized asset loader

---

## 3. Biome 4 environment assets

Integrate these Biome 4 props and hazards:

### Props
`src/assets/tiles/biome4/props/`

- `obsidian_pillar_32x32.png`
- `broken_statue_32x32.png`
- `spike_block_32x32.png`
- `lava_crack_overlay_32x32.png`
- `rock_cluster_64x64.png`

### Hazard visuals
`src/assets/tiles/biome4/hazards/`

- `lava_bubble_1.png` → `lava_bubble_4.png`
- `lava_flow_1.png` → `lava_flow_6.png`
- `magma_pool_1.png` → `magma_pool_4.png`

### Particle effects directory
`src/assets/effects/particles/`

This folder exists and must be supported by the asset pipeline for optional ash / ember particle usage if current effects system supports additive particles.

If the particle system expects concrete Biome 4 ambient particles, support these optional asset names if present and fall back safely if absent:
- `ash_particle_8x8.png`
- `ember_particle_8x8.png`
- `ember_glow_16x16.png`

Do not invent gameplay dependencies on these particles.

---

## 4. Hazard behavior rule

Biome 4 must reuse the existing hazard system.

Do NOT invent new gameplay hazard mechanics unless the current system already supports them generically.

Allowed Biome 4 visual hazard use:
- magma pools
- lava flow overlays
- lava bubbling tiles

These should visually represent stronger volcanic pressure while still using the current hazard rules already defined by the game.

---

## 5. Spawn / reinforcement FX assets

Integrate these effects through the existing spawn / telegraph / portal pipeline:

`src/assets/effects/spawn/`

- `spawn_portal_64x64.png`
- `spawn_portal_anim_64x64.png`
- `summon_circle_128x128.png`
- `summon_circle_anim_128x128.png`

Rules:
- use existing deterministic spawn timing
- do not create a separate spawn system
- these assets should work for Biome 4 ambushes, elite reinforcements, and boss add summoning later

---

## 6. Elite effect integration

Biome 4 elites must use:

`src/assets/effects/elites/`

- `elite_aura_red_64x64.png`
- `elite_aura_red_anim_64x64.png`
- `elite_spawn_flash_64x64.png`

Rules:
- preserve current elite stat modifiers
- only extend elite visuals for Biome 4 encounters
- use existing elite rendering conventions if already implemented
- do not redesign elite architecture

---

## 7. Room background assets

Support these background references:

`src/assets/backgrounds/`

- `biome4_room_bg.png`
- `final_boss_arena_bg.png`

Rules:
- if the current engine already supports biome-specific room backdrops, integrate them additively
- if the engine uses one shared tile background only, treat these as optional backdrop overlays
- do not replace the tile renderer

---

## 8. Boss telegraph support

Prepare the existing telegraph / VFX system to support these Biome 4 boss telegraph assets:

`src/assets/effects/telegraphs/`

- `boss_attack_circle_128x128.png`
- `boss_attack_circle_anim_128x128.png`
- `boss_wave_line_256x64.png`
- `boss_meteor_target_96x96.png`

In this phase, only add support so the final boss can use them later.
Do not implement the boss logic yet.

Also support deterministic telegraph timing metadata for later use:
- fireball cast telegraph = 0.5 s
- lava wave telegraph = 0.75 s
- meteor target telegraph = 1.0 s
- teleport strike warning = 0.6 s

Do not execute these attacks yet; only ensure the timing values can be consumed later.

---

## 9. Boss teleport / spawn / death FX support

Prepare effect loading support for:

`src/assets/effects/boss/`

- `boss_teleport_flash_64x64.png`
- `boss_teleport_smoke_64x64.png`
- `boss_teleport_anim_64x64.png`
- `boss_spawn_portal_256x256.png`
- `boss_spawn_portal_anim_256x256.png`
- `boss_spawn_explosion_128x128.png`
- `boss_death_explosion_256x256.png`
- `boss_death_energy_128x128.png`
- `boss_death_particles.png`

Important:
- do not implement the grab / claw mechanic
- do not load or use grab assets in this phase

---

## 10. Projectile asset support for later boss logic

Prepare projectile loading support for:

`src/assets/entities/projectiles/`

- `boss_fireball_24x24.png`
- `boss_fireball_anim_24x24.png`
- `boss_fireball_trail_24x24.png`
- `boss_wave_attack_64x64.png`
- `boss_meteor_64x64.png`
- `boss_meteor_anim_64x64.png`
- `boss_meteor_trail_32x32.png`
- `boss_meteor_impact_128x128.png`

This phase should only ensure these assets are loadable and compatible with the current projectile / VFX pipeline.

Do not implement final boss attacks yet.

---

## 11. Safe room / room rendering integration

Ensure Biome 4 safe room and combat rooms can render:

- biome props
- hazard overlays
- elite visual effects
- spawn circles / spawn portals

using the same scene update / draw order already used in earlier biomes.

Do not alter gameplay balance in this phase.

---

## 12. Final boss arena rendering preparation

Prepare Room 29 rendering support so the boss arena can later display:

- `src/assets/backgrounds/final_boss_arena_bg.png`
- Biome 4 hazard overlays
- boss spawn portal
- boss telegraphs
- boss death VFX
- boss UI anchor regions at the top of screen

This is preparation only. Do not implement boss combat yet.

---

## 13. Out of scope for this phase

Do **not** implement:
- final boss AI
- final boss state machine
- boss attacks
- boss HP system
- victory handling

This phase is only for additive Biome 4 visual / hazard / VFX integration.

---

## 14. Checklist

- [ ] Biome 4 props load through the current asset pipeline
- [ ] Biome 4 hazard visuals are integrated additively
- [ ] Spawn portal and summon circle assets work in current VFX pipeline
- [ ] Red elite aura assets are integrated for Biome 4 elite enemies
- [ ] Boss telegraph assets are loadable for later use
- [ ] Boss teleport / spawn / death effects are loadable for later use
- [ ] Boss projectile assets are supported for later use
- [ ] Particle assets fall back safely if absent
- [ ] Final boss arena rendering support is prepared
- [ ] No final boss combat logic is implemented yet

---
