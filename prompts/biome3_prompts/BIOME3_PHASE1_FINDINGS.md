# Biome 3 Phase 1 — Findings (Missing Assets & Ambiguities)

## Resolved / Using existing assets

1. **Projectile images**
   - Prompt: `fireball_16x16.png`, `fireball_trail_16x16.png`
   - Repo: `enemy_projectile_16x16.png`, `enemy_projectile_trail_16x16.png`
   - **Decision:** Use `enemy_projectile_16x16.png` and `enemy_projectile_trail_16x16.png` for ranged enemy projectiles. No new assets added.

2. **Ranged animation state**
   - Prompt: `attack_1.png → attack_4.png`
   - Repo: `shoot_1.png → shoot_4.png` under `assets/entities/enemies/biome3/ranged/`
   - **Decision:** Load the `shoot` folder as the attack/shoot state (state name `"attack"` in code, folder `shoot` on disk).

## Implementation location

- **Prompt:** All Biome 3 in `src_biome3/`, no edits to `src/`.
- **Decision:** Phase 1 is implemented **only in `src_biome3/`**. No files in `src/` are modified. Integration with the main engine will happen in a separate merge step after verification. (Previously considered additively in `src/`: new files (`entities/ranged.py`, `entities/projectile.py`) plus minimal, additive edits to register ranged (config, enemy_base, combat, entities `__init__`). This keeps the game playable and matches the “additive architecture” goal. A separate `src_biome3/` copy can be created later for a clean merge reference if needed.

## No blocking issues

- Ranged specs in the prompt are explicit: attack cooldown 1.2 s, projectile speed 260 px/s, damage 8, lifetime 3.0 s.
- Enemy asset paths and projectile rules are clear; we use existing projectile assets and the `shoot` animation folder as above.

---

Phase 1 implementation is in `src_biome3/` (ranged, projectile, config_biome3). The main game in `src/` does not load Biome 3 until merge.
