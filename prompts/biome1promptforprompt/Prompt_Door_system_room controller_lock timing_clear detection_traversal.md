# prompt_01 — Door system + room controller: lock timing, clear detection, traversal

**Target implementation:** `src/dungeon/door_system.py`, `src/dungeon/room_controller.py`, integration in `src/game/scenes/game_scene.py`.

---

## Objective

Capture a **single-feature** coding prompt for **doors**: combat-locked while enemies remain, **unlock delay** after clear, and **room index advance** on exit—aligned with how the engine already wires `RoomController` and `DoorSystem`.

## Scope

- **Included:** Door lock state vs `_room_cleared_flag` (or equivalent); delay constants from `game.config`; edge case: player dies during delay; no double-advance on repeated collision.
- **Not included:** New tile art, RL reward changes, or biome-specific boss logic beyond what existing hooks already do.

## Prompt body (for Cursor)

Implement or verify **additive tests/docs only** unless the repo already satisfies behavior: document the exact order of `DoorSystem.update`, room-clear detection, and `load_room` / index increment. List config keys (`DOOR_UNLOCK_DELAY_SEC`, boss variants) and invariants: doors must not open mid-combat; must open after delay once clear is true; traversing an exit must increment **current_room_index** exactly once per transition.

## Constraints

- Prefer **read-only** discovery first: grep `door`, `unlock`, `room_cleared` in `game_scene` and `room_controller`.
- Changes must remain **backwards-compatible** with manual play.

## Deliverables

- Short verification checklist (3–5 bullets) an agent can run in-game or via a minimal integration test plan.

## Sources

- `src/dungeon/door_system.py`, `src/dungeon/room_controller.py`, `src/game/scenes/game_scene.py`
