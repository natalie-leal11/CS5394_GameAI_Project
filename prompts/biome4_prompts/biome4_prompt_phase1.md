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

# Biome 4 discrepancies solution

The following sections **replace or amend** the same-numbered sections in the Phase 1 prompt above. Use these versions when resolving the issues listed in `biome4_phase1_discrepencies.md`.

---

## 3. Environment rule

Biome 4 must use the **same floor tiles, wall tiles, door logic, and tile renderer** already used by earlier biomes.

Do NOT introduce a separate wall system.

Biome 4 atmosphere must come from overlays / props only, using these assets (paths relative to project root):

### Environment props
`assets/tiles/biome4/props/`

- `obsidian_pillar_32x32.png`
- `broken_statue_32x32.png`
- `spike_block_32x32.png`
- `lava_crack_overlay_32x32.png`
- `rock_cluster_64x64.png`

### Hazards
`assets/tiles/biome4/hazards/`

- `lava_bubble_1.png` → `lava_bubble_4.png`
- `lava_flow_1.png` → `lava_flow_6.png`
- `magma_pool_1.png` → `magma_pool_4.png`

### Room background reference
`assets/backgrounds/biome4_room_bg.png`

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

Room **29** must still be **defined in metadata** in this phase as the **Final Boss room**:
- room type = `FINAL_BOSS`
- single center spawn
- spawn delay = `2.0 s`
- final boss arena metadata reserved
- no boss combat, boss projectiles, boss UI, or victory logic in this phase

Room 29 is included in the room list and sequence (e.g. Beginner/seed order) but has no combat logic in this phase.

---

## 7. Wall thickness and door rules

Biome 4 room metadata must support:

### Wall thickness
- **Combat** = 2 tiles
- **Elite** = 2 tiles
- **Safe** = 2 tiles
- **Final Boss** = 2 tiles
- **Ambush** = 4 tiles

If the current engine uses a single default wall thickness, keep that behavior for:
- Combat
- Elite
- Safe
- Final Boss

Only Ambush rooms require the thicker **4-tile** border override.

### Door rules
- Combat / Ambush / Elite doors start closed and open only after clear + unlock delay
- Safe room doors are open immediately
- Final Boss exit opens only after boss death + unlock delay

### Unlock delay
Use the existing `DOOR_UNLOCK_DELAY_SEC` (e.g. 0.5) if the engine already supports one shared unlock delay cleanly.

If the current codebase supports per-room or per-boss unlock delays cleanly, you may add:
- `FINAL_BOSS_DOOR_UNLOCK_DELAY_SEC = 0.5`

Do not refactor the door system broadly just to introduce a second constant if reuse is sufficient.

---

## 9. Enemy roster rule

Biome 4 reuses existing enemies only:

- Swarm
- Flanker
- Brute
- Heavy
- Ranged

No new normal enemy type is added in this biome.

Use the **current engine-configured enemy sizes** unless the project owner explicitly chooses to standardize Biome 4 to different sizes.

If the engine already has authoritative enemy sizes in config or entity definitions, do **not** create Biome 4-only duplicate size logic in this phase.

Elite visual effects may use:

`assets/effects/elites/`

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

Important:
- for **Biome 4**, spawn slot delay is **0.4 s** (Biomes 1–3 may keep their existing slot delay if different)
- prefer encoding this as **Biome 4 room metadata or biome-specific config**
- do not rewrite the core spawn system if metadata-driven extension is sufficient
- prefer adding Biome 4-specific min distance, spacing, and slot delay in config or room metadata rather than changing core spawn logic

---

## 11. Healing rules to encode

Define:

- **base max HP** = the player's max HP at run start, before any safe-room or combat upgrades are applied. This definition is authoritative for this document.

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

Room 28 must reuse the existing safe-room interaction system, but Biome 4 safe room must show **4 upgrade options drawn from the upgrade pool without duplication**, and the player must choose **exactly 2 upgrades**. Four options are offered per safe room; the player selects exactly two.

Upgrade selection rules:
- options must be selected deterministically using seeded RNG
- no duplicate upgrade cards in the same safe room
- each upgrade can only be chosen once in that room interaction
- after the player selects 2 upgrades, the safe room interaction ends
- upgrades apply only for the current run

Upgrade pool:

### Health Upgrade
- `+20% max HP`
- Icon: `assets/ui/hud/icon_health_24x24.png`

### Speed Boost
- `+10% movement speed`
- Icon: `assets/ui/hud/icon_speed_24x24.png`

### Attack Boost
- `+12% attack damage`
- Icon: `assets/ui/hud/icon_attack_24x24.png`

### Defense Boost
- `-12% incoming damage`
- Icon: `assets/ui/hud/icon_defence_24x24.png`

### Cooldown Boost
- `-10% attack cooldown`
- Icon: `assets/ui/hud/icon_speed_24x24.png`

### Dash Boost
- `+15% dash distance or +10% dash speed depending on current dash system compatibility`
- Icon: `assets/ui/hud/icon_speed_24x24.png`

Note:
- speed-related upgrades may intentionally share the same icon if distinct icon assets do not already exist
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
- arena should support projectile dodging with at least one clear dodge lane

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
- preserve at least one clear dodge lane of width **≥ 4 tiles** across the arena

---

## Enemy Size Rule

Biome 4 must **reuse the existing enemy sizes defined by the engine configuration**.

Do **not** introduce Biome-4-specific size overrides or duplicate size logic.

If the project already defines enemy sizes in a central configuration (for example `config.py`, entity definitions, or enemy classes), those values remain authoritative for all biomes including Biome 4.

Implementers must:
- use the current engine-defined sizes
- avoid redefining enemy sizes in Biome 4 metadata
- avoid creating biome-specific size branches

This keeps enemy collision, rendering, and combat behavior consistent across Biomes 1–4.

---

## Upgrade Icon Rule

Some upgrades intentionally reuse the same icon asset.

The following upgrades may share:

`assets/ui/hud/icon_speed_24x24.png`

Shared icon upgrades:
- Speed Boost
- Cooldown Boost
- Dash Boost

Reason:
- these upgrades all represent **speed or timing improvements**

If distinct icons are added in the future, the upgrade system can reference them without requiring system redesign.

For Phase 1 implementation, **shared icons are intentional and valid**.

---

## Door Unlock Delay Rule

Biome 4 should **reuse the existing door unlock delay constant** already present in the engine.

Use:

`DOOR_UNLOCK_DELAY_SEC` (e.g. 0.5)

Do **not** introduce a new constant such as `FINAL_BOSS_DOOR_UNLOCK_DELAY_SEC` unless the current door system already supports per-room unlock timing cleanly.

For Phase 1:
- all room exits, including the Final Boss exit, use the same unlock delay constant
- avoid refactoring the door system only to support a second constant

---
