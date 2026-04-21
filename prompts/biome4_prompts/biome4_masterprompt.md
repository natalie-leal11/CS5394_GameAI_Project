# Phase 1 — Incremental Coding Prompt
# Additive Biome 4 Room Composition + Metadata Support in `src/`

Implement **only** the following. Do not add final boss combat logic yet. Stop when this phase is complete.

---

## 1. Scope

- **Phase 1 deliverables:** additive Biome 4 room composition support for rooms **24–28** inside the existing `src/` codebase.
- **Architecture rule:** extend the current room / dungeon pipeline rather than replacing it.
- **Biome 4 rule:** reuse the same engine, room systems, spawn systems, and tile systems already used by Biomes 1–3.

---

## 2. Additive-only implementation rule

Preferred approach:
- create a dedicated Biome 4 room-definition module such as `src/dungeon/biome4_rooms.py`
- create a Biome 4 sequence helper such as `src/dungeon/biome4_sequence.py`
- add only narrow integration hooks if current room-loading code requires them

Do NOT:
- rewrite the current biome pipeline
- remove or renumber Biomes 1–3 rooms
- create a separate engine
- redesign combat or player systems

Any edits to existing files must be:
- minimal
- additive
- backwards-compatible
- clearly isolated to Biome 4 support

---

## 3. Environment rule

Biome 4 must use the **same floor tiles, wall tiles, door logic, and tile renderer** already used by earlier biomes.

Do NOT introduce a separate wall system.

Biome 4 atmosphere must come from overlays / props only, using these assets:

### Environment props
`src/assets/tiles/biome4/props/`

- `obsidian_pillar_32x32.png`
- `broken_statue_32x32.png`
- `spike_block_32x32.png`
- `lava_crack_overlay_32x32.png`
- `rock_cluster_64x64.png`

### Hazards
`src/assets/tiles/biome4/hazards/`

- `lava_bubble_1.png` → `lava_bubble_4.png`
- `lava_flow_1.png` → `lava_flow_6.png`
- `magma_pool_1.png` → `magma_pool_4.png`

### Room background reference
`src/assets/backgrounds/biome4_room_bg.png`

Important:
- these must be treated as visual overlays / hazard visuals on top of the existing tile system
- do not replace the current tile renderer
- do not introduce a separate room background pipeline unless the current engine already supports biome-specific backdrop overlays additively

---

## 4. Biome 4 room range

Biome 4 contains rooms:

- **24**
- **25**
- **26**
- **27**
- **28**
- **29**

For this phase, implement only **rooms 24–28** metadata and composition support.

Room **29** must be reserved as the **Final Boss room**, but full boss combat logic is out of scope for this phase.

---

## 5. Beginner test mode room order

If:

`BEGINNER_TEST_MODE = True`

Use the exact fixed order:

- **Room 24** → COMBAT
- **Room 25** → COMBAT
- **Room 26** → AMBUSH
- **Room 27** → ELITE
- **Room 28** → SAFE
- **Room 29** → FINAL_BOSS

---

## 6. Seed mode room order

If:

`BEGINNER_TEST_MODE = False`

Implement seed-based deterministic shuffled order for:

- COMBAT
- COMBAT
- AMBUSH
- ELITE
- SAFE

and then append:

- FINAL_BOSS as **Room 29**

Use deterministic seeded ordering only.

---

## 7. Wall thickness and door rules

Biome 4 room metadata must support:

### Wall thickness
- **Combat** = 2 tiles
- **Elite** = 2 tiles
- **Safe** = 2 tiles
- **Final Boss** = 2 tiles
- **Ambush** = 4 tiles

### Door rules
- Combat / Ambush / Elite doors start closed and open only after clear + unlock delay
- Safe room doors are open immediately
- Final Boss exit opens only after boss death + unlock delay

### Unlock delay
- `DOOR_UNLOCK_DELAY_SEC = 0.5`
- `FINAL_BOSS_DOOR_UNLOCK_DELAY_SEC = 0.5`

---

## 8. Exact room contents

### Room 24 — Combat
- Swarm at 0.0 s
- Flanker at 0.4 s
- Ranged at 0.8 s
- Heavy at 1.2 s

### Room 25 — Combat
- Brute at 0.0 s
- Ranged at 0.4 s
- Heavy at 0.8 s

### Room 26 — Ambush
- Swarm
- Flanker
- Ranged

Ambush rules:
- spawn in a ring around the player
- radius = 160 px
- telegraph duration = 1.5 s

### Room 27 — Elite
- Brute (elite)
- Heavy (elite)
- Ranged

Spawn pattern:
- triangle formation
- side length = 200 px

### Room 28 — Safe
- no enemies
- heal pickup
- upgrade selection

### Room 29 — Final Boss
- reserve metadata only in this phase
- single center spawn
- spawn delay = 2.0 s
- full final boss logic will be added in Phase 3

---

## 9. Enemy roster rule

Biome 4 reuses existing enemies only:

- Swarm
- Flanker
- Brute
- Heavy
- Ranged

No new normal enemy type is added in this biome.

Enemy sizes remain:

- Swarm → 60×60
- Flanker → 48×48
- Brute → 80×80
- Heavy → 88×88
- Ranged → 64×64

Elite visual effects may use:

`src/assets/effects/elites/`

- `elite_aura_red_64x64.png`
- `elite_aura_red_anim_64x64.png`
- `elite_spawn_flash_64x64.png`

---

## 10. Spawn-rule metadata to encode

Add Biome 4 support for these global spawn rules:

- minimum distance from player = 150 px
- minimum distance between enemies = 90 px
- elite extra spacing = 60 px
- no spawns near walls
- no spawns near doors
- no spawns in corners
- ambush ring radius = 160 px
- spawn slot delay = 0.4 s

Do not rewrite the whole spawn system if metadata-driven extension is sufficient.

---

## 11. Healing rules to encode

Add Biome 4 metadata/support for:

- clear-heal drop chance = 30%
- clear-heal amount = 30% of base max HP
- clear-heal cap = 100% of base max HP
- safe room heal amount = 30% of base max HP
- safe room overheal cap = 130% of base max HP
- safe room pickup usable once per room visit
- final boss reward heal amount = 40% of base max HP
- final boss reward cap = 100% of base max HP

Do not redesign the healing system in this phase.

---

## 12. Safe room upgrade rules

Room 28 must reuse the existing safe-room interaction system, but Biome 4 safe room must show **4 upgrade options** and the player must choose **exactly 2 upgrades**.

Upgrade selection rules:
- options must be selected deterministically using seeded RNG
- no duplicate upgrade cards in the same safe room
- each upgrade can only be chosen once in that room interaction
- after the player selects 2 upgrades, the safe room interaction ends
- upgrades apply only for the current run

Upgrade pool:

### Health Upgrade
- `+20% max HP`
- Icon: `src/assets/ui/hud/icon_health_24x24.png`

### Speed Boost
- `+10% movement speed`
- Icon: `src/assets/ui/hud/icon_speed_24x24.png`

### Attack Boost
- `+12% attack damage`
- Icon: `src/assets/ui/hud/icon_attack_24x24.png`

### Defense Boost
- `-12% incoming damage`
- Icon: `src/assets/ui/hud/icon_defence_24x24.png`

### Cooldown Boost
- `-10% attack cooldown`
- Icon: `src/assets/ui/hud/icon_speed_24x24.png`

### Dash Boost
- `+15% dash distance or +10% dash speed depending on current dash system compatibility`
- Icon: `src/assets/ui/hud/icon_speed_24x24.png`

Important:
- if the current engine already has a fixed safe-room upgrade pool from earlier biomes, extend it minimally and add Biome 4-specific selection count support rather than replacing the system
- do not redesign the upgrade UI broadly in this phase

---

## 13. Final boss arena metadata to reserve now

Even though Room 29 combat is out of scope for this phase, reserve the following metadata now so later boss implementation does not guess:

### Arena layout rules
- room type = `FINAL_BOSS`
- boss spawn at room center
- player entry spawn must be safe
- exit door remains locked until boss death
- arena should be larger/open enough to support projectile dodging

### Arena hazard caps
- lava coverage ≤ 10%
- slow terrain coverage ≤ 15%
- wall coverage ≤ 25%
- minimum safe area ≥ 35%

### Arena fairness rules
- do not place lava on player spawn
- do not place lava on boss spawn
- do not block the path between player entry and arena center
- do not place hazards directly on exit door tiles
- preserve at least one broad dodge lane across the arena

---

## 14. Out of scope for this phase

Do **not** implement:
- final boss combat
- boss projectiles
- boss phase change
- boss UI
- victory screen flow

This phase is only for additive Biome 4 room composition / metadata support.

---

## 15. Checklist

- [ ] Biome 4 room definition module exists
- [ ] Rooms 24–28 are defined additively
- [ ] Room 29 is reserved as FINAL_BOSS metadata
- [ ] Beginner mode uses exact fixed room order
- [ ] Seed mode uses deterministic shuffled order for 24–28 + fixed 29
- [ ] Room composition data is encoded exactly
- [ ] Safe room shows 4 upgrade options and player chooses exactly 2
- [ ] Final boss arena metadata and hazard caps are reserved now
- [ ] Existing Biomes 1–3 behavior is preserved
- [ ] No final boss combat logic is added yet

---

**Stop after Phase 1. Wait for user confirmation before proceeding to Phase 2.**

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

**Stop after Phase 2. Wait for user confirmation before proceeding to Phase 3.**

# Phase 3 — Incremental Coding Prompt
# Additive Final Boss Support in `src/` for Biome 4

Implement **only** the following. Stop when this phase is complete.

---

## 1. Scope

- **Phase 3 deliverables:** additive Final Boss support inside `src/` for Room 29, including boss state machine, boss attacks, boss phase change, boss add summoning, boss UI, arena flow, death flow, and victory handling.
- **Architecture rule:** extend the existing boss / spawn / room-clear / projectile / UI pipeline rather than replacing it.

---

## 2. Additive-only implementation rule

Preferred approach:
- add a dedicated boss module such as `src/entities/final_boss.py`
- add a dedicated boss encounter helper if needed
- add only small, backwards-compatible hooks into existing room-clear, projectile, and HUD logic

Do NOT:
- rewrite the current mini boss system broadly
- redesign the combat engine
- redesign player systems
- modify unrelated biome logic

Any existing-file edits must be:
- minimal
- additive
- isolated to Final Boss support

---

## 3. Final Boss room contract

Biome 4 final boss encounter is for **Room 29**.

Room 29 rules:
- room type = FINAL_BOSS
- wall border thickness = 2 tiles
- doors remain closed until boss is dead
- after boss death, wait **0.5 s** before exit opens
- base boss spawn pattern = single central spawn
- base boss spawn time = **2.0 s**
- after death, trigger victory flow
- final boss reward heal = 40% of base max HP, capped at base max HP
- arena hazard caps must respect Phase 1 reserved metadata

Use these exact values.

---

## 4. Final Boss assets

Boss animation folder:

`src/assets/entities/enemies/final_boss/`

Animations:

- `idle_1.png` → `idle_4.png`
- `walk_1.png` → `walk_6.png`
- `attack1_1.png` → `attack1_6.png`
- `attack2_1.png` → `attack2_6.png`
- `special_1.png` → `special_6.png`
- `summon_1.png` → `summon_6.png`
- `phase_change_1.png` → `phase_change_8.png`
- `hit_1.png` → `hit_3.png`
- `death_1.png` → `death_10.png`

Boss size:
- **128×128**

---

## 5. Final Boss stats

Implement Final Boss with:

- HP = 480
- contact damage = 18
- fireball damage = 20
- lava wave damage = 22
- meteor damage = 18
- teleport strike damage = 24
- attack cooldown = 1.4 s
- movement speed = 85 px/s
- stop distance from player = 170 px
- preferred fireball range = 220–420 px
- preferred wave range = 140–260 px
- preferred teleport trigger range = 120–320 px

Use config/constants where appropriate.
Do not hardcode everywhere.

---

## 6. Final Boss abilities

Implement these boss attacks only:

### Attack-to-animation mapping
- **Fireball attack** uses `attack1`
- **Lava wave attack** uses `attack2`
- **Meteor rain attack** uses `special`
- **Teleport strike** uses teleport effect + `attack2` or nearest compatible slam frame flow
- **Summon adds** uses `summon`
- **Phase transition** uses `phase_change`
- **Hit reaction** uses `hit`
- **Death flow** uses `death`

Do not guess alternate animation bindings unless the current engine requires a narrowly documented compatibility fallback.

### A. Fireball attack
Use:

`src/assets/entities/projectiles/`

- `boss_fireball_24x24.png`
- `boss_fireball_anim_24x24.png`
- `boss_fireball_trail_24x24.png`

Rules:
- deterministic projectile speed
- projectile speed = 280 px/s
- projectile lifetime = 3.0 s
- projectile damage = 20
- cast telegraph = 0.5 s
- reuse existing projectile collision system

### B. Lava wave attack
Use:

- `src/assets/entities/projectiles/boss_wave_attack_64x64.png`

Rules:
- boss launches wave in straight line
- damage = 22
- telegraph = 0.75 s using `boss_wave_line_256x64.png`
- reuse existing projectile / collision / telegraph logic where possible

### C. Meteor rain attack
Use:

- `boss_meteor_64x64.png`
- `boss_meteor_anim_64x64.png`
- `boss_meteor_trail_32x32.png`
- `boss_meteor_impact_128x128.png`

Telegraph with:

`src/assets/effects/telegraphs/`

- `boss_meteor_target_96x96.png`

Rules:
- deterministic impact positions
- use visible telegraph before impact
- damage = 18
- meteor telegraph duration = 1.0 s
- meteor timing must be deterministic
- use 3 target zones per cast unless the active-enemy/projectile cap logic requires a lower bounded count

### D. Teleport strike
Use:

`src/assets/effects/boss/`

- `boss_teleport_flash_64x64.png`
- `boss_teleport_smoke_64x64.png`
- `boss_teleport_anim_64x64.png`

Rules:
- teleport to a nearby valid position
- do not teleport into walls / doors / invalid tiles
- maintain fair distance from player
- warning delay = 0.6 s before strike lands
- after teleport, perform slam / strike attack using existing damage system
- damage = 24

---

## 7. Boss attack loop / behavior rules

Final Boss must not choose attacks randomly without control. Use a deterministic weighted rotation or scripted priority loop.

Recommended behavior:
- if player is far away, prefer **Fireball**
- if player is mid-range and in front arc, prefer **Lava Wave**
- if player has stayed mobile and distant for extended time, use **Meteor Rain**
- if player is close or flanking repeatedly, use **Teleport Strike**
- after Phase 2 starts, increase Meteor / Teleport usage modestly but deterministically

Boss fairness rules:
- no attack should fire with zero warning
- boss must idle briefly after initial spawn
- boss AI must not chain more than 2 high-pressure attacks back-to-back without a short recovery window

Timing rules:
- boss spawn idle delay = 0.75 s
- minimum recovery between completed attacks = 0.6 s
- do not overlap teleport strike with meteor cast
- phase change must interrupt the normal attack loop cleanly

---

## 8. Explicit exclusion rule

Do **NOT** implement the **grab / claw mechanic** in this version.

Ignore all grab behavior and grab assets even if present elsewhere.

No player immobilization logic.
No hold-for-2-seconds logic.

---

## 9. Phase change rule

At **50% HP**, the Final Boss must:

- trigger `phase_change` animation
- become briefly invulnerable during transition
- summon adds
- then resume attack pattern with increased pressure

Use:

- `phase_change_1.png` → `phase_change_8.png`

Phase transition rules:
- invulnerability duration = animation duration or 2.0 s max, whichever the current boss framework supports more cleanly
- HP does not reset
- after phase change, reduce attack cooldown slightly to `1.2 s`
- after phase change, meteor and teleport can appear more often, but still deterministically

This phase change must be deterministic.

---

## 10. Add summoning rule

At phase change, summon:

- 2 Swarm
- 1 Flanker

Use:

`src/assets/effects/spawn/`

- `spawn_portal_64x64.png`
- `spawn_portal_anim_64x64.png`
- `summon_circle_128x128.png`
- `summon_circle_anim_128x128.png`

Rules:
- adds spawn in ring around boss
- deterministic placement
- adds count toward current active enemy system
- add spawning must not affect earlier biome rooms

---

## 11. Boss telegraphs

Use:

`src/assets/effects/telegraphs/`

- `boss_attack_circle_128x128.png`
- `boss_attack_circle_anim_128x128.png`
- `boss_wave_line_256x64.png`
- `boss_meteor_target_96x96.png`

Rules:
- attacks must be visibly telegraphed
- telegraph timing must be deterministic
- reuse existing telegraph rendering pipeline wherever possible

Recommended mapping:
- `boss_attack_circle_*` for general cast warning or teleport strike area
- `boss_wave_line_*` for Lava Wave
- `boss_meteor_target_*` for Meteor Rain

---

## 12. Boss spawn / death effects

Use:

`src/assets/effects/boss/`

### Spawn
- `boss_spawn_portal_256x256.png`
- `boss_spawn_portal_anim_256x256.png`
- `boss_spawn_explosion_128x128.png`

### Death
- `boss_death_explosion_256x256.png`
- `boss_death_energy_128x128.png`
- `boss_death_particles.png`

Rules:
- boss spawn uses dramatic portal effect at room start
- boss death uses explosion / energy effect
- after boss death animation + death effect, unlock exit after 0.5 s

---

## 13. Arena background

Use:

`src/assets/backgrounds/final_boss_arena_bg.png`

Rules:
- integrate additively if the engine supports boss-arena backdrop overlays
- do not replace the tile renderer

---

## 14. Boss UI

Use:

`src/assets/ui/`

- `boss_health_bar_frame.png`
- `boss_health_bar_fill.png`
- `boss_name_banner.png`

Rules:
- show boss UI only during Room 29 encounter
- health fill reflects current boss HP
- reuse existing HUD rendering conventions where possible

---

## 15. Victory handling

Use:

`src/assets/ui/`

- `victory_screen_bg.png`
- `victory_banner.png`

Rules:
- after final boss death and room clear, trigger victory flow
- victory flow must reuse current end-of-run / scene transition system if available
- do not create a separate engine or menu architecture

---

## 16. Determinism rules

Final Boss encounter must be deterministic:
- fixed event ordering
- fixed cooldowns
- fixed projectile speeds
- deterministic summon positions
- no uncontrolled randomness
- seeded behavior only where the current project already allows seeded randomness

---

## 17. Out of scope for this phase

Do **not** add:
- new player skills
- grab mechanic
- online learning
- new biome systems
- post-game meta progression

This phase is only for additive Final Boss support in Biome 4.

---

## 18. Checklist

- [ ] `src/entities/final_boss.py` exists
- [ ] Room 29 can run a Final Boss encounter
- [ ] Fireball attack works
- [ ] Lava wave attack works
- [ ] Meteor rain attack works
- [ ] Teleport strike works
- [ ] Grab / claw mechanic is not implemented
- [ ] Boss uses explicit attack-to-animation mapping
- [ ] Boss attack loop and recovery windows are deterministic
- [ ] Phase change at 50% HP works
- [ ] Adds spawn deterministically at phase change
- [ ] Boss health bar UI works
- [ ] Boss death flow + victory flow work
- [ ] Existing Biomes 1–3 and earlier boss behavior are preserved

---

**Stop after Phase 3. Wait for user confirmation before proceeding further.**
