# Phase 7 — Biome 4 Director Behavior

Apply AI Director behavior for Biome 4 only, including bounded final-boss pressure tuning.

---

## Goal

Deliver deterministic, fair, and intense Biome 4 adaptation while preserving final boss mechanics.

---

## Biome 4 Scope and Constraints

Keep Biome 4 enemy scope to existing supported types:
- `Swarm`
- `Flanker`
- `Brute`
- `Heavy`
- `Ranged`

Biome 4 room handling split:
- normal adaptation rooms: `COMBAT`, `AMBUSH`, `ELITE`
- special bounded handling: `FINAL_BOSS`
- safe-room adaptation remains bias-only and UI-preserving

---

## Biome 4 Directive Profile

Use existing documented Biome 4 emphasis:
- pressure/composition mapping from player state
- pacing bias (`relaxed`/`normal`/`intense`) within bounds
- boss pressure bias (`low`/`medium`/`high`) for small parameter nudges only

Apply deterministic bounded adjustments to:
- normal-room count/composition/pacing/reinforcement/hazard/recovery bias
- final-boss telegraph/frequency/recovery style tuning where already documented as legal
- revive-phase fairness pacing rules already documented

---

## Biome 4 Safety Rules

Do not:
- change final boss attack types
- change revive mechanics
- redesign boss phase structure
- introduce chaos spikes outside documented fairness bounds

---

## Biome 4 Checklist

- [ ] Changes are Biome 4 only
- [ ] Final-boss handling remains small, bounded, and deterministic
- [ ] Revive fairness constraints are preserved
- [ ] Core boss mechanics remain unchanged

Stop after Phase 7.
