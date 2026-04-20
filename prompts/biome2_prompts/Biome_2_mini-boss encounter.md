# prompt_01 — Biome 2 mini-boss encounter: entry, phases, exit gating

**Target implementation:** `src/dungeon/biome2_mini_boss_encounter.py`, `src/entities/mini_boss.py` (or Biome 2 variant), `src/dungeon/room_controller.py`, `src/game/scenes/game_scene.py`.

---

## Objective

Isolate a **single prompt** for the **Biome 2 mini-boss room**: how the encounter is **entered**, phase transitions (if any), door lock rules, and **clear** conditions before the next room loads.

## Scope

- **Included:** Room type flags for mini-boss; spawn timing; interaction with `DoorSystem` (boss alive = locked).
- **Not included:** Biome 3 ranged enemies or final boss.

## Prompt body (for Cursor)

Document the **call graph** from room load → mini-boss spawn → HP-based events → `room_cleared` / boss death handlers. List **failure modes** (player death, reload checkpoint) and whether the mini-boss state resets on respawn.

## Constraints

- Reuse existing **Heavy** / mini-boss pipelines; no parallel boss framework.
- Deterministic spawn positions from room metadata + seed.

## Deliverables

- Checklist: 5–7 boolean questions (e.g. “Are doors locked until boss HP ≤ 0?”) answerable by reading code only.

## Sources

- `src/dungeon/biome2_mini_boss_encounter.py`, `src/dungeon/biome2_sequence.py`, `src/entities/mini_boss.py`
