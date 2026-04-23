---
# AI Director — Behavior Implementation Summary

## Overview

The AI Director is the adaptive difficulty engine. It observes the player's
performance across the last three rooms and adjusts the parameters of the next
encounter — never the current one. All adjustments are frozen into an immutable
snapshot before room transition so that mid-room events cannot retroactively
change what was already decided.

The system is built in three cleanly separated layers: raw metric accumulation,
player state classification, and difficulty output generation.

---

## Layer 1 — MetricsTracker

Runs every frame during play. Accumulates raw per-room data into `RoomMetrics`
objects stored in `run.room_history` (last three rooms retained):

- HP at room entry and exit
- Damage taken per room
- Kill counts and room clear times
- Deaths and near-death events (HP below critical threshold mid-room)
- Healing received and healing wasted
- Dash usage count
- Time spent on hazard tiles

A `summarize()` call produces a `MetricsSummary` snapshot that the next layer
reads.

---

## Layer 2 — PlayerModel

Called once after each room ends. Reads the metrics summary and classifies the
player into one of three states using a deterministic priority chain:

**STRUGGLING** is assigned if any of the following is true:
- Current HP is below the critical threshold (~20% of max HP).
- The player died in the last room.
- At least two of these three weak signals are simultaneously present:
  HP is below the weak threshold (~40%), two of the last three rooms ended in
  near-death or death, and average HP loss over the last three rooms exceeds a
  configured percentage.

**DOMINATING** is assigned (if not Struggling) if HP is above the dominating
threshold and two or more of the following are true: a clean-clear streak exists,
average HP loss is low, and room clear times are fast.

**STABLE** is the fallback when neither condition above is met.

**Life-phase override:** a player on their last life is always classified as
STRUGGLING regardless of metrics. A player who just lost a life remains
STRUGGLING for at least one room before normal classification resumes.

**Trial phase override:** Biome 1 rooms 1–4 are treated as onboarding. During
this window `effective_enemy_adjustment()` always returns 0, preventing the
director from penalising new players who are still learning the controls.

---

## Layer 3 — AIDirector

Translates the classification from PlayerModel into a set of difficulty outputs:

| Output | STRUGGLING | STABLE | DOMINATING |
|---|---|---|---|
| `difficulty_modifier` | 0.85 | 1.0 | 1.15 |
| `enemy_adjustment` | −1 | 0 | +1 |
| `reinforcement_chance` | ~0.05 | ~0.10 | ~0.25 |
| `composition_bias` | lighter | normal | harder |
| `hazard_bias` | lower | normal | higher |
| `reward_bias` | more_help | normal | lower_help |

Biomes 2–4 extend this with additional outputs: pressure level, ranged bias,
hazard tune factor, boss pressure (Biome 4), and pacing bias (Biome 4). All
biome-specific values are derived from the same three-state classification.

`capture_encounter_snapshot()` freezes all current outputs into an immutable
`EncounterDirectorSnapshot` dataclass. Biome-specific spawn modules receive
this snapshot when building the next room's enemy list.

Every room transition writes a JSON log to `logs/AI_Director_Logs/` recording
the classification and full output set for that room.

---

## Primary File Locations

| File | Contents |
|---|---|
| `src/game/ai/ai_director.py` | `AIDirector.update()`, `capture_encounter_snapshot()`, `EncounterDirectorSnapshot` dataclass |
| `src/game/ai/player_model.py` | `PlayerModel.classify()`, all classification thresholds and priority logic |
| `src/game/ai/metrics_tracker.py` | `MetricsTracker`, `RunMetrics`, `RoomMetrics`, per-frame accumulation |
| `src/game/ai/difficulty_params.py` | All numeric thresholds: critical HP, weak HP, dominating HP, streak counts |
| `src/game/ai/ai_logger.py` | JSON log writer, outputs to `logs/AI_Director_Logs/` |
| `src/game/ai/biome1_director_spawn.py` | Consumes snapshot to build Biome 1 enemy composition |
| `src/game/ai/biome2_director_spawn.py` | Biome 2 spawn (adds ranged bias) |
| `src/game/ai/biome3_director_spawn.py` | Biome 3 spawn |
| `src/game/ai/biome4_director_spawn.py` | Biome 4 spawn (adds boss pressure, pacing bias) |
