# Biome 4 Phase 2 — Discrepancies, Issues & Clarifications

This document records issues, inconsistencies, and ambiguities in `biome4_prompt_phase2.md` for implementers and future edits.

---

## 1. Asset paths (Sections 3–12)

**Issue:** All paths are written as `src/assets/...`. In the repo, assets live under the project root as `assets/...` (no `src/`), consistent with Phase 1 discrepancies.

**Affected in Phase 2 prompt:**
- `src/assets/tiles/biome4/props/`
- `src/assets/tiles/biome4/hazards/`
- `src/assets/effects/particles/`
- `src/assets/effects/spawn/`
- `src/assets/effects/elites/`
- `src/assets/backgrounds/` (biome4_room_bg.png, final_boss_arena_bg.png)
- `src/assets/effects/telegraphs/`
- `src/assets/effects/boss/`
- `src/assets/entities/projectiles/` (boss_*)

**Recommendation:** Use `assets/...` (no `src/`) everywhere, or state the project convention (e.g. paths relative to project root).

---

## 2. Hazard visuals vs existing tile types (Sections 3–4)

**Issue:** The prompt lists three hazard visuals (lava_bubble, lava_flow, magma_pool) and says they should “visually represent stronger volcanic pressure while still using the current hazard rules.” The engine currently has only **two** hazard tile types: `TILE_LAVA` and `TILE_SLOW`. There is no “magma” gameplay type.

**Ambiguity:**
- Are “magma pool” visuals a **visual variant** for existing lava tiles in Biome 4 (same damage/behavior as lava)?
- Or should “magma” be a separate visual overlay set that maps 1:1 to lava tiles when in Biome 4?
- How are the three visuals (bubble, flow, magma) assigned? Per-tile RNG, per-room, or one dominant visual per room?

**Recommendation:** State explicitly: “Magma pool is a Biome 4 visual variant for lava tiles only; gameplay remains existing lava rules. Lava bubble and lava flow are optional overlay variants for lava tiles in Biome 4. Assignment may be deterministic (e.g. by tile index or room seed) or one visual set per room.”

---

## 3. Props placement (Section 3)

**Issue:** The prompt says “integrate” Biome 4 props (obsidian_pillar, broken_statue, spike_block, lava_crack_overlay, rock_cluster) but does not specify:
- How many props per room (or per room type).
- Placement rules (random, fixed positions, avoid spawn/door, etc.).
- Whether props block movement or are decorative only.
- Whether they are drawn on top of floor tiles only or can overlap hazards.

**Recommendation:** Add: “Props are decorative overlays only; they do not change collision or hazard logic. Placement: use seeded RNG per room; avoid player spawn and door tiles; specify max count per room type or a density cap.”

---

## 4. Particle system dependency (Section 3)

**Issue:** “This folder exists and must be supported” conflicts with “fall back safely if absent” and “optional ash / ember particle usage **if** current effects system supports additive particles.”

**Ambiguity:** Is the particle folder required to exist, or is support optional? The checklist says “Particle assets fall back safely if absent,” which implies optional.

**Recommendation:** Clarify: “The `assets/effects/particles/` folder and ash/ember assets are optional. If the current effects system does not support additive or ambient particles, skip particle integration. If assets are missing, do not fail load; omit or use placeholder.”

---

## 5. Spawn / reinforcement FX scope (Section 5)

**Issue:** “These assets should work for Biome 4 ambushes, elite reinforcements, and boss add summoning later.” It is unclear whether:
- Biome 4 **replaces** existing spawn/telegraph/portal visuals when in Biome 4 rooms, or
- These assets are **additional** options used only for specific Biome 4 spawn types (e.g. ambush vs normal).

**Recommendation:** Add: “Use Biome 4 spawn/portal/summon assets only when `room.biome_index == 4` (or when campaign room index is in Biome 4 range). Other biomes keep existing spawn visuals.”

---

## 6. Elite effect scope (Section 6)

**Issue:** “Only extend elite visuals for Biome 4 encounters” is clear, but the path is `src/assets/effects/elites/` and Phase 1 already references `assets/effects/elites/` (red aura, etc.). Phase 2 repeats the same assets.

**Recommendation:** Align path to `assets/effects/elites/`. State that Phase 2 ensures these are **used** for Biome 4 elite encounters (not just loadable); Phase 1 may have only reserved the path.

---

## 7. Room background integration (Section 7)

**Issue:** “If the engine uses one shared tile background only, treat these as optional backdrop overlays” — it is unclear how “backdrop overlay” is composited (behind tiles? behind everything? full-screen with room drawn on top?).

**Recommendation:** Define draw order: e.g. “Backdrop first (full screen or room-sized), then tile layer, then props/hazards/entities.” State whether biome4_room_bg applies to rooms 24–28 only and final_boss_arena_bg to room 29 only.

---

## 8. Boss telegraph timing metadata (Section 8)

**Issue:** Telegraph durations (fireball 0.5 s, lava wave 0.75 s, meteor 1.0 s, teleport 0.6 s) should be “consumed later.” Where should they live?

**Recommendation:** Specify: “Store in config (e.g. `BIOME4_BOSS_TELEGRAPH_*_SEC`) or in a Biome 4 boss metadata module. Phase 2 only defines the constants; Phase 3 reads them when implementing attacks.”

---

## 9. Boss FX and grab assets (Section 9)

**Issue:** “Do not load or use grab assets in this phase” implies grab assets exist or will exist elsewhere. The prompt does not list them.

**Recommendation:** Add: “Grab/claw assets (if any) are explicitly out of scope for Phase 2; do not add paths or loaders for them.”

---

## 10. Projectile asset “support” (Section 10)

**Issue:** “Ensure these assets are loadable and compatible with the current projectile / VFX pipeline.” The current pipeline supports optional `image_path` and `size` on projectiles. “Compatible” could mean: (a) load_image(path, size) succeeds, or (b) a projectile instance can be constructed with these as custom image/size.

**Recommendation:** Clarify: “Phase 2 adds no new projectile types or behavior. Only ensure that load_image (or equivalent) can load these paths and sizes without error; no gameplay use until Phase 3.”

---

## 11. “Final boss arena rendering preparation” (Section 12)

**Issue:** “Boss UI anchor regions at the top of screen” is vague. Is this a reserved rectangle (e.g. for boss HP bar), or a comment in code, or an empty component?

**Recommendation:** Add: “Preparation means: document or reserve screen regions (e.g. top center) for future boss HP/name UI; no actual boss UI widgets in Phase 2.”

---

## 12. Overlap with Phase 1 (environment assets)

**Issue:** Phase 1 already lists Biome 4 props and hazards (with corrected `assets/` paths in the Phase 1 discrepancies solution). Phase 2 again lists the same props and hazard visuals.

**Recommendation:** Add a cross-reference: “Phase 1 defined which assets exist; Phase 2 implements their loading and rendering. Use the same path convention as Phase 1 solution (assets/..., no src/).”

---

## 13. Hazard system “reuse” (Section 4)

**Issue:** “Do NOT invent new gameplay hazard mechanics” — the current hazard system uses `TILE_LAVA` and `TILE_SLOW` and likely a single visual per type. Biome 4 wants “lava bubbling,” “lava flow,” “magma pool” as visuals.

**Recommendation:** State: “Hazard **gameplay** (damage, slow, tile checks) is unchanged. Only the **visual** drawn for a lava or slow tile may be Biome 4–specific (e.g. choose among lava_bubble, lava_flow, magma_pool for lava tiles when in Biome 4).”

---

## 14. Checklist vs scope

**Issue:** Checklist item “Final boss arena rendering support is prepared” is broad. Section 12 lists backdrop, hazard overlays, boss spawn portal, telegraphs, death VFX, UI anchor regions.

**Recommendation:** Ensure “prepared” is interpreted as: assets loadable, draw order/extensions identified, no boss logic. Optionally split into “Room 29 can show final_boss_arena_bg and Biome 4 hazard overlays” and “Boss FX/telegraph assets are loadable for Phase 3.”

---

## Summary table

| #  | Section   | Type       | Summary |
|----|-----------|------------|---------|
| 1  | 3–12      | Paths      | Use `assets/...` not `src/assets/...` |
| 2  | 3–4       | Hazards    | Map lava_bubble/lava_flow/magma_pool to existing TILE_LAVA (visual only) |
| 3  | 3         | Props      | Define placement rules and non-blocking behavior |
| 4  | 3         | Particles  | Clarify optional vs required; fallback when absent |
| 5  | 5         | Spawn FX   | Use Biome 4 spawn assets only when in Biome 4 |
| 6  | 6         | Elite      | Path alignment; ensure use in Biome 4 encounters |
| 7  | 7         | Background | Draw order and per-room (24–28 vs 29) assignment |
| 8  | 8         | Telegraph  | Where to store timing constants for Phase 3 |
| 9  | 9         | Boss FX    | Grab assets explicitly out of scope |
| 10 | 10        | Projectiles| ‘Compatible’ = loadable only, no behavior |
| 11 | 12        | Arena      | ‘UI anchor regions’ = reserved areas, no widgets |
| 12 | 3         | Phase 1    | Phase 2 implements loading/rendering of Phase 1 assets |
| 13 | 4         | Hazards    | Gameplay unchanged; only visuals Biome 4–specific |
| 14 | 14        | Checklist  | ‘Prepared’ = loadable + draw hooks, no boss logic |
