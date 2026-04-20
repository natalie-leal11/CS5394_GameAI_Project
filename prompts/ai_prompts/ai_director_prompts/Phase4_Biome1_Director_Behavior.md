# Phase 4 — Biome 1 Director Behavior

Apply AI Director behavior for Biome 1 only, using existing documented constraints.

---

## Goal

Add small deterministic Biome 1 adaptation with bounded Director influence.

---

## Biome 1 Scope and Constraints

Keep Biome 1 enemy scope limited to:
- `Swarm`
- `Flanker`
- `Brute`

Eligible adaptation room types:
- `COMBAT`
- `AMBUSH`
- `ELITE`

Do not apply Director adaptation to:
- `START`
- `SAFE`
- `MINI_BOSS`

---

## Biome 1 Directive Profile

Use deterministic state-driven mapping already documented for Biome 1:
- `STRUGGLING` -> lower pressure, reduced count, no/low reinforcement, relief-oriented bias
- `STABLE` -> baseline pressure and count
- `DOMINATING` -> higher pressure, +1 bounded count option, challenge-oriented bias

Apply only bounded changes to:
- enemy count
- composition bias (within Biome 1 enemy set)
- spawn pacing
- reinforcement policy
- light hazard/recovery bias where architecture safely supports it

---

## Biome 1 Safety Rules

Do not:
- introduce new enemy types/archetypes
- alter mini-boss logic
- alter room order/milestones
- redesign spawn system architecture

Use deterministic seed-driven evaluation where probabilistic decisions are allowed.

---

## Biome 1 Checklist

- [ ] Changes are Biome 1 only
- [ ] Enemy set remains `Swarm`/`Flanker`/`Brute`
- [ ] Directives are bounded and deterministic
- [ ] Mini-boss and non-AI systems remain unchanged

Stop after Phase 4.
