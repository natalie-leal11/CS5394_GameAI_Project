PHASE 2 — Offline Logging and Dataset Export

Goal
Prepare logged run data for offline RL and analysis.

Create files:

src/game/rl/dataset_export.py
tools/rl/export_run_dataset.py

Requirements

1. Consume existing run logs only
2. Convert per-room and end-of-run summaries into an offline dataset format
3. Output CSV or JSONL suitable for later RL experiments
4. Keep this fully offline and separate from gameplay

Dataset should include fields such as:
- run_id
- seed
- biome_index
- room_index
- room_type
- enemy_count
- hp_start
- hp_end
- damage_taken
- clear_time
- director_state
- victory_or_defeat
- total_run_time
- rooms_cleared

Implementation constraints

- Do not change current room flow
- Do not change current combat logic
- Do not make gameplay read the exported dataset
- The exporter may read logs, transform them, and write a new artifact only

STOP AFTER IMPLEMENTATION
