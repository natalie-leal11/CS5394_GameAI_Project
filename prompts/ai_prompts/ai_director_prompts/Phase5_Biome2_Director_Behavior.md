# Phase 5 — Biome 2 Director Behavior

Apply AI Director behavior for Biome 2 only, preserving Biome 2-specific differences.

---

## Goal

Extend deterministic adaptation in Biome 2 with pressure-aware behavior beyond Biome 1.

---

## Biome 2 Scope and Constraints

Keep Biome 2 enemy scope to existing supported types:
- `Swarm`
- `Flanker`
- `Brute`
- `Heavy`

Eligible adaptation room types:
- `COMBAT`
- `AMBUSH`
- `ELITE`

Do not apply to:
- `SAFE`
- `MINI_BOSS`

---

## Biome 2 Directive Profile

Use existing documented Biome 2 emphasis:
- deterministic pressure level mapping from player state
- deterministic composition bias mapping (lighter/balanced/aggressive)
- bounded reinforcement scaling (still deterministic and capped)

Apply bounded adjustments to:
- enemy count offset
- pressure-based spawn spacing
- composition preference including Biome 2 `Heavy` constraints
- reinforcement behavior (bounded and seed-deterministic)
- hazard/recovery bias only within legal caps

---

## Biome 2 Safety Rules

Do not:
- affect Biome 1, 3, or 4 behavior here
- modify boss mechanics
- add new enemy classes
- introduce non-deterministic runtime logic

---

## Biome 2 Checklist

- [ ] Changes are Biome 2 only
- [ ] `Heavy` handling follows existing documented constraints
- [ ] Pressure/composition/reinforcement are bounded and deterministic
- [ ] No gameplay architecture redesign is introduced

Stop after Phase 5.
