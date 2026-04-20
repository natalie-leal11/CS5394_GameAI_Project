# prompt_01 — Final boss (Room 29): phases, adds, victory, door delays

**Target implementation:** `src/entities/final_boss.py`, `src/dungeon/biome4_rooms.py`, `src/dungeon/biome4_sequence.py`, `src/game/scenes/game_scene.py` (victory / game over).

---

## Objective

Single prompt for **Final Boss** endgame: arena boundaries, **phase** transitions, **add** summons, player **death** vs **victory**, and **exit door** timing (`FINAL_BOSS_DOOR_UNLOCK_DELAY_SEC` or equivalent).

## Scope

- **Included:** Boss state machine, invulnerability windows, projectile/teleport attacks; interaction with `DoorSystem` until boss death.
- **Not included:** Biome 3 miniboss or unrelated biomes.

## Prompt body (for Cursor)

Build a **timeline** from room load → boss spawn delay → each phase → death → victory scene → return to menu. Note **RL** branches: `_rl_controlled` auto-actions must not skip mandatory waits unless already implemented.

## Constraints

- Boss must respect **metadata** from Biome 4 room composition (spawn point, delays).
- No duplicate victory triggers on the same frame.

## Deliverables

- Finite-state style list: states, transitions, and which timers reset on player respawn (if applicable).

## Sources

- `src/entities/final_boss.py`, `src/dungeon/biome4_rooms.py`, `src/game/scenes/game_scene.py`
