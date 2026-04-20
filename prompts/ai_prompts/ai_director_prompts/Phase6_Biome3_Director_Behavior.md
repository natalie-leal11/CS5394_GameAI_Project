# Phase 6 — Biome 3 Director Behavior

Apply AI Director behavior for Biome 3 only, preserving Biome 3-specific ranged and hazard differences.

---

## Goal

Add deterministic Biome 3 adaptation with ranged-pressure and hazard-aware tuning, within existing scope.

---

## Biome 3 Scope and Constraints

Keep Biome 3 enemy scope to existing supported types:
- `Swarm`
- `Flanker`
- `Brute`
- `Ranged`

Eligible adaptation room types:
- `COMBAT`
- `AMBUSH`
- `ELITE`

Do not apply full encounter adaptation to:
- `SAFE`
- `MINI_BOSS` (except small legal parameter nudges already documented)

---

## Biome 3 Directive Profile

Use existing documented Biome 3 emphasis:
- pressure-level mapping
- composition bias with ranged awareness
- hazard bias (low/normal/high style)
- bounded reinforcement scaling

Apply deterministic bounded adjustments to:
- count/composition/pacing
- ranged-pressure profile
- hazard intensity bias within current caps
- limited mini-boss tuning where explicitly legal and bounded

---

## Biome 3 Safety Rules

Do not:
- redesign mini-boss phase mechanics
- add new enemy classes
- alter non-Biome-3 systems in this phase
- use unseeded random behavior

---

## Biome 3 Checklist

- [ ] Changes are Biome 3 only
- [ ] Ranged/hazard behavior follows existing documented boundaries
- [ ] Mini-boss changes remain limited and legal
- [ ] Deterministic bounded behavior is preserved

Stop after Phase 6.
