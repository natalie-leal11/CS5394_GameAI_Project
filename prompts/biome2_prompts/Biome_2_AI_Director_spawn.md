# prompt_02 — Biome 2 AI Director spawn: weights, caps, encounter specs

**Target implementation:** `src/game/ai/biome2_director_spawn.py`, `src/game/ai/ai_director.py`, `src/dungeon/seeded_encounter_specs.py` (if referenced).

---

## Objective

Capture **director-driven spawn** rules specific to **Biome 2**: how encounter tables differ from Biome 1, where **Heavy** enters the weight vector, and how metrics (struggling/stable/dominating) adjust spawn pressure.

## Scope

- **Included:** Read-only mapping from `DifficultyParams` / `PlayerModel` to spawn directives; biome index guards.
- **Not included:** Retuning global PPO or editing `difficulty_params.json` defaults without user request.

## Prompt body (for Cursor)

Produce a **compact matrix**: player state × (elite enabled, max enemies, spawn delay) for Biome 2 rooms. Note **idempotence**: same seed + room index → same directive. Point to unit/integration tests if they exist.

## Constraints

- Director must never violate **max enemy** and **spawn delay** bounds from config/schema.
- Clear separation: Biome 2 logic must not accidentally run in Biome 1 rooms.

## Deliverables

- One paragraph “integration contract” for `GameScene` calling into director before `SpawnSystem` tick.

## Sources

- `src/game/ai/biome2_director_spawn.py`, `src/game/ai/ai_director.py`, `src/game/ai/player_model.py`
