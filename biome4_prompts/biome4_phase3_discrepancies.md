# Biome 4 Phase 3 — Discrepancies, Issues & Clarifications

This document records issues, inconsistencies, and ambiguities in `biome4_prompt_phase3.md` for implementers and future edits.

**Implementers:** Use **`biome4_phase3_solution.md`** as the authoritative corrections and constants for Phase 3 (asset paths, attack priority, meteor count, phase change invulnerability, recovery, cooldown, spawn idle, telegraph asset, arena rules, victory flow).

---

## 1. Asset path convention (Sections 4–15)

**Issue:** The prompt uses `src/assets/...` for all asset paths. The project convention (per Phase 2 solution and existing codebase) is **assets under the project root**: `assets/...` (no `src/`). There is no `src/assets/` directory.

**Affected in Phase 3 prompt:**
- §4: `src/assets/entities/enemies/final_boss/` → **`assets/entities/enemies/final_boss/`** (or `assets/entities/final_boss/` if the repo groups boss separately)
- §6A, §10: `src/assets/entities/projectiles/` → **`assets/entities/projectiles/`**
- §6B, §6C, §11: `src/assets/effects/telegraphs/` → **`assets/effects/telegraphs/`**
- §6D, §12: `src/assets/effects/boss/` → **`assets/effects/boss/`**
- §10: `src/assets/effects/spawn/` → **`assets/effects/spawn/`**
- §13: `src/assets/backgrounds/final_boss_arena_bg.png` → **`assets/backgrounds/final_boss_arena_bg.png`**
- §14: `src/assets/ui/` (boss_health_bar_*, boss_name_banner) → **`assets/ui/`**
- §15: `src/assets/ui/` (victory_*) → **`assets/ui/`**

**Recommendation:** Use **`assets/...`** (relative to project root) everywhere. Do not create or reference `src/assets/`.

---

## 2. Boss spawn / death asset sizes (§12)

**Issue:** §12 lists:
- Spawn: `boss_spawn_portal_256x256.png`, `boss_spawn_portal_anim_256x256.png`, `boss_spawn_explosion_128x128.png`
- Death: `boss_death_explosion_256x256.png`, `boss_death_energy_128x128.png`, `boss_death_particles.png`

Phase 2’s `load_boss_fx_spawn()` and `load_boss_fx_death()` use **folder-based** loading (e.g. `boss/spawn`, `boss/death`) with sizes (128, 128). Phase 3 specifies **named files** and **256×256** for portal and death explosion.

**Recommendation:** Align Phase 3 implementation with the prompt’s filenames and sizes: spawn portal 256×256, death explosion 256×256, or document if the engine uses a single folder and scale at load time. Ensure Phase 2 loaders (or new ones) can provide 256×256 where specified.

---

## 3. Phase change invulnerability duration (§9)

**Issue:** “Invulnerability duration = animation duration or 2.0 s max, whichever the current boss framework supports more cleanly” is ambiguous. Animation duration may vary by frame count and FPS; “whichever supports more cleanly” leaves a choice to the implementer.

**Recommendation:** Pin to a single rule, e.g.: “Invulnerability duration = min(phase_change animation length, 2.0 s)” or “Invulnerability = 2.0 s, during which phase_change animation plays.” State whether the boss can be hit during the last frame of phase_change.

---

## 4. Meteor rain target count (§6C)

**Issue:** “Use 3 target zones per cast unless the active-enemy/projectile cap logic requires a lower bounded count” is vague. It is unclear what “active-enemy/projectile cap” refers to (total projectiles on screen? total meteors per cast? room enemy limit?) and how it should bound the count.

**Recommendation:** Define explicitly: e.g. “3 meteor impact zones per cast; if the projectile system has a per-source or global cap, use min(3, cap).” Or: “Always 3 zones; cap applies only to concurrent projectiles from other sources.”

---

## 5. Add summon placement (“ring around boss”) (§10)

**Issue:** “Adds spawn in ring around boss” and “deterministic placement” are under-specified: radius, angular spacing, and how to avoid walls/hazards are not defined.

**Recommendation:** Specify e.g.: “Ring radius = N tiles (e.g. 2–3); 3 adds placed at 0°, 120°, 240° (or similar); spawn tiles must be valid floor, not lava/slow, not in walls; use room seed + boss position for deterministic tile choice if multiple valid tiles per angle.”

---

## 6. Teleport strike “slam” animation (§6D)

**Issue:** “Perform slam / strike attack using existing damage system” and “teleport effect + `attack2` or nearest compatible slam frame flow” leave animation choice open. “Nearest compatible slam frame flow” is unclear.

**Recommendation:** State explicitly: “After teleport, play `attack2` animation and apply contact/melee damage when the strike frame hits. Do not invent a new animation; use `attack2` (or a single documented fallback if the engine requires it).”

---

## 7. Attack-to-animation mapping and “do not guess” (§6)

**Issue:** §6 says “Do not guess alternate animation bindings unless the current engine requires a narrowly documented compatibility fallback.” The prompt already maps attacks to animations (e.g. fireball → attack1, lava wave → attack2). If a file is missing (e.g. attack2_3.png), behavior is undefined.

**Recommendation:** Add: “If a listed animation file is missing, log or document the fallback (e.g. reuse idle or another attack) and do not silently substitute unrelated animations. Prefer single, documented fallbacks.”

---

## 8. Boss spawn “base spawn time” and “initial spawn” (§3, §7)

**Issue:** §3 says “base boss spawn time = 2.0 s”; §7 says “boss spawn idle delay = 0.75 s”. It is unclear whether “spawn time” is (a) delay before the boss entity appears, (b) duration of the spawn portal VFX, or (c) time until first attack. “Boss spawn idle delay” suggests the boss is already present and idles 0.75 s before acting.

**Recommendation:** Clarify: e.g. “Spawn time 2.0 s = delay from room entry until boss entity spawns (portal VFX can run during this). After spawn, boss idles 0.75 s before entering the attack loop.”

---

## 9. Phase 2 timing constants (§6, §11)

**Issue:** Phase 2 already defines telegraph durations in config: `BIOME4_BOSS_TELEGRAPH_FIREBALL_SEC`, `BIOME4_BOSS_TELEGRAPH_LAVA_WAVE_SEC`, `BIOME4_BOSS_TELEGRAPH_METEOR_SEC`, `BIOME4_BOSS_TELEGRAPH_TELEPORT_SEC` (0.5, 0.75, 1.0, 0.6). Phase 3 repeats these values in §6.

**Recommendation:** Phase 3 should **read** these constants from config (or the same metadata module) and not redefine them. Single source of truth avoids drift.

---

## 10. “Arena hazard caps must respect Phase 1 reserved metadata” (§3)

**Issue:** Phase 1 may define hazard limits for the final boss room. Current `room.py` (or equivalent) already uses rules for `RoomType.FINAL_BOSS` (e.g. lava ≤10%, slow ≤15%, safe ≥35%). “Phase 1 reserved metadata” is not clearly referenced.

**Recommendation:** Explicitly point to the existing FINAL_BOSS room generation rules (e.g. in `room.py` or dungeon config) and state that Phase 3 does not change those caps; Room 29 is generated with the same rules.

---

## 11. Victory flow and “end-of-run / scene transition” (§15)

**Issue:** “Victory flow must reuse current end-of-run / scene transition system if available” assumes such a system exists. If the game has no “run complete” or “return to menu” flow, behavior is undefined.

**Recommendation:** Specify: “If no end-of-run scene exists, implement a minimal victory state (e.g. show victory screen, then transition to main menu or defined next scene). Do not add a new top-level engine; plug into existing scene stack or main loop.”

---

## 12. Boss UI assets and layout (§14)

**Issue:** §14 lists `boss_health_bar_frame.png`, `boss_health_bar_fill.png`, `boss_name_banner.png` but not size, position, or how fill reflects HP (e.g. fill width = HP ratio, or segment-based). Phase 2 reserved a “boss UI anchor” (e.g. top center); Phase 3 does not reference it.

**Recommendation:** State that boss UI is drawn in the Phase 2–reserved anchor region (e.g. config: `BIOME4_BOSS_UI_ANCHOR_*`). Define fill rule: e.g. “Health fill width = (current HP / max HP) × bar width.” Specify whether the banner shows a fixed name or a configurable string.

---

## 13. Determinism and seeded RNG (§16)

**Issue:** “Seeded behavior only where the current project already allows seeded randomness” implies the boss should use the same global SEED (or a derived seed) for any RNG (e.g. add placement, attack choice if weighted random). The prompt also says “deterministic weighted rotation or scripted priority loop.”

**Recommendation:** Use the project’s existing SEED (e.g. from config). For “weighted rotation,” define either (a) a fixed scripted order with no randomness, or (b) seeded random with SEED + room_index + encounter_phase so the same run reproduces the same choices. Document which option is used.

---

## 14. Checklist: code path `src/entities/final_boss.py` (§18)

**Issue:** The checklist says “`src/entities/final_boss.py` exists.” In the repo, source files live under `src/` (e.g. `src/entities/...`). So **code** paths like `src/entities/final_boss.py` are correct. Only **asset** paths must not use `src/assets/`.

**Recommendation:** No change for code paths. Keep checklist as-is; ensure implementers do not confuse asset root (`assets/`) with source root (`src/`).

---

## 15. Grab / claw explicit exclusion (§8, §17)

**Issue:** Phase 2 already excluded grab/claw. Phase 3 repeats “Do NOT implement the grab / claw mechanic” and “No player immobilization logic.” Alignment is good; worth cross-referencing.

**Recommendation:** Add a short note: “Consistent with Phase 2: no grab assets, no immobilization, no hold-for-2-seconds logic. Ignore any grab-related content elsewhere in the repo.”

---

## 16. Fireball “trail” asset (§6A)

**Issue:** §6A lists `boss_fireball_trail_24x24.png` but does not specify whether it is a separate projectile sprite, a trailing VFX, or an extra frame in the fireball animation.

**Recommendation:** Clarify usage: e.g. “Trail asset is an optional visual trail or secondary frame for the fireball projectile; it does not add collision or damage. If the engine has no trail system, the fireball may be drawn without it.”

---

## 17. Lava wave “straight line” and telegraph asset (§6B)

**Issue:** “Boss launches wave in straight line” and “telegraph = 0.75 s using boss_wave_line_256x64.png” do not specify direction (e.g. toward player, fixed axis, or facing-based). Wave width/length and how the 256×64 texture maps to world space are also unspecified.

**Recommendation:** Define: e.g. “Wave direction = boss facing direction (or toward player at cast time). Telegraph shows a 256×64 line in that direction for 0.75 s; then the damaging wave projectile spawns. Reuse existing projectile/collision logic for the wave hitbox.”

---

## Summary table

| #  | Section | Type        | Summary |
|----|---------|-------------|---------|
| 1  | 4–15    | Paths       | Use `assets/...` not `src/assets/...` |
| 2  | 12      | Asset size  | Spawn portal / death explosion 256×256; align with Phase 2 loaders |
| 3  | 9       | Phase change| Pin invulnerability rule (e.g. min(anim, 2.0 s) or fixed 2.0 s) |
| 4  | 6C      | Meteor      | Define “3 target zones” vs projectile/enemy cap clearly |
| 5  | 10      | Add summon  | Define ring radius, angles, and deterministic tile choice |
| 6  | 6D      | Teleport    | Use `attack2` for post-teleport strike; document fallback if any |
| 7  | 6       | Animations  | Document fallback when an animation file is missing |
| 8  | 3, 7    | Spawn timing| Separate “spawn time 2.0 s” from “idle delay 0.75 s” |
| 9  | 6, 11   | Timing      | Phase 3 should use Phase 2 telegraph constants from config |
| 10 | 3       | Hazards     | Room 29 hazard caps = existing FINAL_BOSS rules (Phase 1) |
| 11 | 15     | Victory     | Define behavior when no existing end-of-run system exists |
| 12 | 14     | Boss UI     | Use Phase 2 UI anchor; define fill rule and banner content |
| 13 | 16     | Determinism | Use project SEED; document scripted vs seeded-weighted loop |
| 14 | 18     | Checklist   | Code path `src/entities/` is correct; assets use `assets/` |
| 15 | 8, 17  | Grab        | Align with Phase 2; no grab, no immobilization |
| 16 | 6A     | Fireball    | Clarify trail asset role (visual only, no extra damage) |
| 17 | 6B     | Lava wave   | Define wave direction and telegraph/wave geometry |
