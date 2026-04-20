# Biome 4 Phase 1 — Discrepancies, Issues & Clarifications

This document records issues, inconsistencies, and ambiguities in `biome4_prompt_phase1.md` for implementers and future edits.

---

## 1. Asset paths (Section 3)

**Issue:** Paths are written as `src/assets/...`. In the repo, assets live under the project root as `assets/...` (no `src/`).

**Current in prompt:**
- `src/assets/tiles/biome4/props/`
- `src/assets/tiles/biome4/hazards/`
- `src/assets/backgrounds/biome4_room_bg.png`
- `src/assets/effects/elites/` (Section 9)
- `src/assets/ui/hud/icon_*.png` (Section 12)

**Recommendation:** Use `assets/...` (no `src/`) everywhere, or state the actual project convention so implementers do not create or expect `src/assets/`.

---

## 2. Room 29 scope (Section 4 vs. Sections 5–6)

**Issue:** “Implement only rooms 24–28” plus “Room 29 must be reserved” can be read as “do not implement Room 29 at all.”

**Clarification needed:** Phase 1 should:
- Define Room 29 in metadata as FINAL_BOSS (spawn delay 2.0 s, center spawn, etc.).
- Not implement boss combat, projectiles, or boss UI.

**Recommendation:** Add one sentence: “Room 29 is defined in metadata only (type FINAL_BOSS, spawn delay, center spawn); no combat or boss logic in this phase.”

---

## 3. Enemy sizes (Section 9)

**Issue:** Document specifies:
- Swarm → 60×60
- Flanker → 48×48
- Brute → 80×80
- Heavy → 88×88
- Ranged → 64×64

Existing config (e.g. `config.py`) uses different sizes (e.g. Swarm 64×64, Flanker 56×56, etc.).

**Risk:** Implementers may add Biome 4–specific size overrides or duplicate logic.

**Recommendation:** Either (a) align the document with current engine sizes, or (b) state explicitly: “Biome 4 uses these sizes” and that config/engine will be extended for Biome 4 only (and where).

---

## 4. Safe room: 4 options from 6-card pool (Section 12)

**Issue:** “4 upgrade options” and “choose exactly 2” are clear, but the pool has 6 upgrades. It is not explicit that “4 options” means “4 cards drawn from the pool (no duplicates), player picks 2.”

**Recommendation:** Add: “Each safe room offers 4 options drawn from the pool without duplication; the player selects exactly two.”

---

## 5. Duplicate icon (Section 12)

**Issue:** Speed Boost, Cooldown Boost, and Dash Boost all reference `icon_speed_24x24.png`.

**Recommendation:** If intentional, add a note: “Speed-related upgrades may share the same icon.” If not, assign distinct icon paths for Cooldown and Dash.

---

## 6. Wall thickness (Section 7)

**Issue:** “Combat / Elite / Safe / Final Boss = 2 tiles”, “Ambush = 4 tiles”. If the engine currently has a single global wall thickness, it is unclear whether to add a new parameter or only override for Ambush.

**Recommendation:** Add: “Where the engine has a single wall thickness, use it for Combat, Elite, Safe, and Final Boss; only Ambush uses 4 tiles.”

---

## 7. Final boss door unlock constant (Section 7)

**Issue:** Document introduces `FINAL_BOSS_DOOR_UNLOCK_DELAY_SEC = 0.5`. The codebase may only have `DOOR_UNLOCK_DELAY_SEC`.

**Recommendation:** State whether to add a new constant for the final boss exit or reuse `DOOR_UNLOCK_DELAY_SEC`.

---

## 8. “Base max HP” definition (Section 11)

**Issue:** Healing rules refer to “base max HP” (clear-heal cap, safe room overheal cap, final boss reward cap). Term is not defined.

**Recommendation:** Define once, e.g. “Base max HP = player’s max HP at run start (before any upgrades).”

---

## 9. Spawn slot delay (Section 10)

**Issue:** “Spawn slot delay = 0.4 s” for Biome 4. Biomes 1–3 may use a different value (e.g. 0.5 s).

**Recommendation:** State explicitly: “For Biome 4, spawn slot delay = 0.4 s” (and whether this overrides a global or is Biome 4–specific in config/metadata).

---

## 10. Final boss arena size (Section 13)

**Issue:** “Arena should be larger/open enough to support projectile dodging” is vague for implementation.

**Recommendation:** Optionally add a concrete constraint, e.g. “Keep at least one clear lane of width ≥ N tiles across the arena.”

---

## 11. Spawn system extension (Section 10)

**Issue:** “Do not rewrite the whole spawn system if metadata-driven extension is sufficient” is good but does not point to where to extend.

**Recommendation:** Add: “Prefer adding Biome 4–specific min distance, spacing, and slot delay in config or room metadata rather than changing core spawn logic.”

---

## Summary table

| # | Section | Type        | Summary                                              |
|---|---------|------------|------------------------------------------------------|
| 1 | 3, 9, 12| Paths      | Use `assets/...` not `src/assets/...`               |
| 2 | 4       | Scope      | Clarify Room 29 = metadata only, no combat          |
| 3 | 9       | Data       | Enemy sizes vs current config                        |
| 4 | 12      | Clarity    | 4 options from pool, choose 2                        |
| 5 | 12      | Assets     | Same icon for 3 upgrades                            |
| 6 | 7       | Logic      | Wall thickness: when to override                     |
| 7 | 7       | Config     | New constant vs reuse for boss door delay            |
| 8 | 11      | Definition | Define “base max HP”                                 |
| 9 | 10      | Config     | Biome 4 spawn slot delay 0.4 s vs global             |
| 10| 13      | Clarity    | Arena “open enough” → concrete constraint            |
| 11| 10      | Guidance   | Where to add Biome 4 spawn metadata                  |

# Biome 4 discrepencies solution:
## 3. Environment rule

Biome 4 must use the **same floor tiles, wall tiles, door logic, and tile renderer** already used by earlier biomes.

Do NOT introduce a separate wall system.

Biome 4 atmosphere must come from overlays / props only, using these assets:

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
Use the existing `DOOR_UNLOCK_DELAY_SEC = 0.5` if the engine already supports one shared unlock delay cleanly.

If the current codebase supports per-room or per-boss unlock delays cleanly, you may add:
- `FINAL_BOSS_DOOR_UNLOCK_DELAY_SEC = 0.5`

Do not refactor the door system broadly just to introduce a second constant if reuse is sufficient.

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
- for **Biome 4**, spawn slot delay is **0.4 s**
- prefer encoding this as **Biome 4 room metadata or biome-specific config**
- do not rewrite the core spawn system if metadata-driven extension is sufficient
- prefer adding Biome 4-specific min distance, spacing, and slot delay in config or room metadata rather than changing core spawn logic

## 11. Healing rules to encode

Define:

- **base max HP** = the player’s max HP at run start, before any safe-room or combat upgrades are applied

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

## 12. Safe room upgrade rules

Room 28 must reuse the existing safe-room interaction system, but Biome 4 safe room must show **4 upgrade options drawn from the upgrade pool without duplication**, and the player must choose **exactly 2 upgrades**.

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

`DOOR_UNLOCK_DELAY_SEC = 0.5`

Do **not** introduce a new constant such as `FINAL_BOSS_DOOR_UNLOCK_DELAY_SEC` unless the current door system already supports per-room unlock timing cleanly.

For Phase 1:
- all room exits, including the Final Boss exit, use the same unlock delay constant
- avoid refactoring the door system only to support a second constant
