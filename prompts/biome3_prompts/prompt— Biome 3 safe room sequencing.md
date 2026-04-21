# prompt_02 — Biome 3 safe room sequencing & SRS order (`srs_biome_order`)

**Target implementation:** `src/dungeon/srs_biome_order.py`, safe-room upgrade hooks in `src/game/scenes/game_scene.py`, `src/entities/player.py` (upgrade apply).

---

## Objective

Document **safe room** placement and **upgrade choice** flow for Biome 3 campaigns: how SRS (safe room system) order interacts with room indices, **one-pick** or **multi-pick** rules, and persistence across checkpoint respawn.

## Scope

- **Included:** Functions that decide which upgrade cards appear; Biome 3–specific safe room rules vs global; `_safe_room_health_mult` style stats.
- **Not included:** New UI assets.

## Prompt body (for Cursor)

Trace **one full safe-room visit**: door entry → heal eligibility → upgrade UI state machine → exit. Cross-reference `biome3_sequence` and `srs_biome_order` for **which** room indices are safe vs combat.

## Constraints

- **Additive** documentation only unless a bug is found; do not rewrite upgrade balance.
- Respawn must not duplicate upgrades already committed to the run.

## Deliverables

- Short table: room index → room type → safe-room actions available.

## Sources

- `src/dungeon/srs_biome_order.py`, `src/dungeon/biome3_sequence.py`, `src/game/scenes/game_scene.py`
