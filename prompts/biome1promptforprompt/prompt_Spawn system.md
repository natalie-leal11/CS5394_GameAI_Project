# prompt_02 — Spawn system: telegraphs, staggered slots, clear gating, reinforcement

**Target implementation:** `src/systems/spawn_system.py`, `src/systems/spawn_helper.py`, hooks from `src/game/scenes/game_scene.py`.

---

## Objective

Provide a **focused prompt** for the **spawn pipeline**: telegraph timing, multiple spawn slots, **no new combat spawns after room clear**, and reinforcement waves only when the director/spec allows—matching current `SpawnSystem` behavior.

## Scope

- **Included:** `_spawned_enemies` / clear interaction; distance-to-player rules; elite vs normal paths; interaction with `BEGINNER_TEST_MODE` if present.
- **Not included:** New enemy types, Biome 4 boss adds, or RL auto-resolve.

## Prompt body (for Cursor)

Map the **state machine** of spawn: initial delay, per-slot offsets, and what resets on `load_room`. Explicitly call out **dummies** vs combat enemies if the codebase distinguishes `is_training_dummy`. Require assertions: after `room_cleared_flag` is true, no additional **combat** enemy factories run until the next room load.

## Constraints

- Deterministic under fixed `SEED` for a given room index.
- Do not increase spawn caps beyond `game.config` / director params.

## Deliverables

- A table (in the agent response) of **timers** and **flags** read/written each frame by `SpawnSystem`.

## Sources

- `src/systems/spawn_system.py`, `src/systems/spawn_helper.py`, `src/game/config.py`
