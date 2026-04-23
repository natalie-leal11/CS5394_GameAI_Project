# prompt_01 — Biome 3 ranged enemy + miniboss: projectiles, LoS, phase sync

**Target implementation:** `src/entities/ranged.py`, `src/entities/projectile.py`, `src/entities/biome3_miniboss.py`, `src/systems/combat.py`, `src/dungeon/biome3_sequence.py`.

---

## Objective

Provide a **feature-scoped prompt** for **Biome 3 combat**: ranged attacks, projectile lifetime/collision, and **mini-boss** multi-phase behavior without duplicating Final Boss logic.

## Scope

- **Included:** Projectile spawn points, wall collision, damage application interval; miniboss phase thresholds and telegraphs.
- **Not included:** Biome 4 lava arena or RL reward rebalancing.

## Prompt body (for Cursor)

Enumerate **all** projectile-creating enemy types in Biome 3; for each, list max simultaneous projectiles, friendly-fire rules, and cleanup on room transition. For **miniboss**, map HP % → phase index → animation/attack set.

## Constraints

- Must use existing **collision** helpers; no second physics world.
- On `load_room`, **all** projectiles and enemy-owned entities must be cleared.

## Deliverables

- Bullet list of **edge cases** (room transition mid-flight, player death mid-cast) with expected behavior per code path.

## Sources

- `src/entities/ranged.py`, `src/entities/projectile.py`, `src/entities/biome3_miniboss.py`, `src/dungeon/biome3_rooms.py`
