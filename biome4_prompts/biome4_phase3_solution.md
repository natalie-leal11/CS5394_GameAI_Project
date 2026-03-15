# Biome 4 Phase 3 — Corrections & Clarifications

This document resolves discrepancies in **Phase 3 — Additive Final Boss Support** and gives implementers a single source of truth.

---

## 1. Asset Path Convention

Phase 3 must **not** use `src/assets/...`. The repo convention is assets under the **project root**:

**Correct root path:** `assets/...`

**Replace all Phase 3 asset paths as follows:**

| Prompt / doc says | Use instead |
|-------------------|-------------|
| `src/assets/entities/enemies/final_boss/` | `assets/entities/enemies/final_boss/` |
| `src/assets/entities/projectiles/` | `assets/entities/projectiles/` |
| `src/assets/effects/boss/` | `assets/effects/boss/` |
| `src/assets/effects/telegraphs/` | `assets/effects/telegraphs/` |
| `src/assets/effects/spawn/` | `assets/effects/spawn/` |
| `src/assets/backgrounds/` | `assets/backgrounds/` |
| `src/assets/ui/` | `assets/ui/` |

Implementers must **not** create or reference a `src/assets/` directory.

---

## 2. Teleport Strike Animation Mapping

The prompt’s “attack2 or nearest compatible slam frame flow” is ambiguous. Use this **explicit** sequence:

**Teleport strike animation sequence:**

1. Play **boss teleport effect** (e.g. `boss_teleport_anim`, or teleport VFX from `assets/effects/boss/`).
2. Boss appears at destination; play **attack2** animation.
3. **Damage event** is applied on the appropriate frame of attack2 (slam/strike frame), using the existing damage system.

Do not introduce a separate “slam” animation unless the engine already has one; **attack2** is the post-teleport strike animation.

---

## 3. Boss Attack Loop — Deterministic Priority

High-level “prefer fireball if far, prefer lava wave mid-range” can lead to random or underspecified behavior. Use a **deterministic priority order**:

**Attack selection priority (evaluate in order):**

1. If **teleport cooldown is ready** AND **player distance &lt; 200 px** → **Teleport Strike**
2. If **player distance &gt; 260 px** → **Fireball**
3. If **player distance 140–260 px** → **Lava Wave**
4. Every **N seconds** (e.g. 8–10 s, fixed or seeded) → **Meteor Rain**

After Phase 2 (50% HP), you may increase Meteor and Teleport usage deterministically (e.g. shorter N for Meteor, or slightly larger teleport trigger range), but the **priority order** and **no randomness** rule remain.

---

## 4. Meteor Rain — Fixed Target Count

Do **not** leave meteor count as “3 unless system requires lower.” Fix it:

**Meteor Rain:**

- **3 meteor targets** per cast.
- **Deterministic placement** (e.g. from room/boss seed).
- **Minimum spacing ≥ 120 px** between target centers.

If the projectile system has a hard cap on concurrent projectiles, document that cap and ensure 3 meteors do not exceed it; otherwise always use 3 targets.

---

## 5. Phase Change Invulnerability Duration

Use a **single rule**, not “animation duration or 2 s max”:

**Phase change invulnerability = 2.0 seconds**

The boss is invulnerable for exactly 2.0 s during the phase transition (while `phase_change` animation plays). If the animation is shorter, invulnerability still lasts 2.0 s; if longer, cap display as needed but keep invulnerability at 2.0 s.

---

## 6. Boss Recovery Window

“Short recovery window” must be a constant:

**BOSS_ATTACK_RECOVERY = 0.6 s**

This is the minimum delay **after** an attack animation completes before the next attack can start. Store in config or a boss constants module.

---

## 7. Attack Cooldown vs Recovery — Clarification

Phase 3 defines both “attack cooldown = 1.4 s” and “recovery window,” which can be confused.

**Correct logic:**

- **Attack cooldown** = time between **attack starts** (e.g. 1.4 s in Phase 1, 1.2 s after phase change). The next attack may **begin** only after this cooldown has elapsed since the **start** of the previous attack.
- **Recovery window** = delay **after** the attack animation (and damage) **completes** before the boss can start another action. Use **BOSS_ATTACK_RECOVERY = 0.6 s**.

So: cooldown governs “time between starting attacks”; recovery governs “minimum idle time after an attack finishes.” Both can be enforced (e.g. next attack starts only when both “cooldown since last attack start” and “recovery since last attack end” are satisfied).

---

## 8. Boss Spawn Idle Delay — Constant

The prompt mentions “boss spawn idle delay = 0.75 s” but does not define it as a constant.

**Fix:** Define explicitly:

**BOSS_SPAWN_IDLE_DELAY = 0.75 s**

This is the delay after the boss entity spawns (and spawn VFX) before the boss enters the normal attack loop. Store in config or boss constants.

---

## 9. Meteor Telegraph Asset — Explicit Path

Phase 3 references the telegraph folder but not the specific file in the rule. Add an explicit reference:

**Meteor Rain telegraph asset:**

`assets/effects/telegraphs/boss_meteor_target_96x96.png`

Use this asset for the visible telegraph before each meteor impact. Telegraph duration = 1.0 s (use existing Phase 2 constant `BIOME4_BOSS_TELEGRAPH_METEOR_SEC`).

---

## 10. Arena Rules — Phase 1 Only

Phase 3 must **not** regenerate or modify Room 29 layout or hazard rules.

**Rule:** Arena hazard and layout rules are defined in **Phase 1** metadata (e.g. FINAL_BOSS room type, lava/slow caps, safe area). Phase 3 must **reuse** that layout. Do not reimplement or change arena generation.

---

## 11. Victory Flow — Reuse Existing System

“Reuse existing end-of-run / scene transition system” must be explicit so implementers do not add a new menu framework.

**Rule:** Victory flow must trigger the **existing** run-completion or scene transition system already used by earlier game endings (e.g. post–mini boss, or campaign complete). Do **not** introduce a new menu or engine architecture. If no such system exists, implement a minimal victory state that transitions to the same destination (e.g. main menu or next scene) used elsewhere.

---

## Summary Table

| Issue | Fix |
|-------|-----|
| Asset paths | Use `assets/...` only; no `src/assets/` |
| Teleport strike animation | Sequence: teleport effect → attack2 → damage on strike frame |
| Attack logic | Deterministic priority: teleport (close) → fireball (far) → lava wave (mid) → meteor (every N s) |
| Meteor count | Fixed **3** targets; ≥120 px spacing; deterministic placement |
| Phase change invulnerability | **2.0 s** constant |
| Recovery window | **BOSS_ATTACK_RECOVERY = 0.6 s** |
| Cooldown vs recovery | Cooldown = time between attack **starts**; recovery = delay after attack **ends** |
| Spawn idle delay | **BOSS_SPAWN_IDLE_DELAY = 0.75 s** constant |
| Meteor telegraph asset | Explicit path: `assets/effects/telegraphs/boss_meteor_target_96x96.png` |
| Arena rules | Reuse Phase 1 metadata; do not regenerate or modify arena layout |
| Victory flow | Reuse existing run-completion / scene transition; no new menu framework |
