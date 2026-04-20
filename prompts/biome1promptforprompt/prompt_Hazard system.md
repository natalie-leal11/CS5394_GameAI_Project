# prompt_03 — Hazard system: tile damage, cooldowns, dash immunity, RL counters

**Target implementation:** `src/dungeon/hazard_system.py`, player damage hooks, `RewardSnapshot.damage_from_hazards` / `time_in_hazard_tiles` in `src/rl/reward.py` if wired.

---

## Objective

Add or document **hazard behavior** as implemented: periodic damage on lava (or similar), interaction with **dash i-frames** if any, and **metrics/RL** exposure so reward shaping and debugging stay consistent.

## Scope

- **Included:** Which tile layers trigger hazards; per-frame vs per-interval damage; safe zones in beginner spec vs runtime.
- **Not included:** Replacing the tile renderer or adding new physics.

## Prompt body (for Cursor)

Trace **one frame** of `HazardSystem.update` (or equivalent): inputs (player rect, room), outputs (damage event list, time-in-hazard accumulator). Verify **no damage** on invalid states (invuln, death). If RL reads hazard totals, ensure the same numbers feed **MetricsTracker** and **RewardSnapshot** without double counting.

## Constraints

- Hazard intensity must respect director/config **caps** documented for each biome.
- Fail gracefully in rooms with no hazard layer.

## Deliverables

- Sequence diagram or numbered list (≤12 steps) from tile query → HP delta → optional RL reward term.

## Sources

- `src/dungeon/hazard_system.py`, `src/entities/player.py`, `src/rl/reward.py`
