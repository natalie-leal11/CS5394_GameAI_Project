# rl_prompt_15 — Phase 2: offline logging and dataset export

**Sequence:** 15 of 18 — *Offline datasets from existing logs.*

**Implementation (repo):** `src/game/rl/dataset_export.py`, `tools/rl/export_run_dataset.py`; `ai_prompts/rl_integration_prompts/Phase2_Offline_Logging_and_Dataset_Export.md`.

---

## Objective

Convert **existing** run logs into CSV/JSONL datasets for offline analysis and parameter evaluation—without gameplay consuming those files.

## Scope

- **Included:** Fields such as `run_id`, `seed`, `biome_index`, `room_index`, `room_type`, `enemy_count`, HP start/end, damage, clear time, director state, outcome, timings, `rooms_cleared`.
- **Not included:** Changing room flow or combat; gameplay reading the export.

## Changes required

- Read logs only; transform; write new artifact.

## Constraints

- Do not alter current room flow or combat logic; exporter is one-way out of runtime.

## Implementation steps

1. Implement log ingestion and schema mapping.
2. Emit CSV or JSONL.
3. Keep pipeline offline.

## Deliverables

- Export utilities and reproducible dataset files.

## Sources

- `ai_prompts/rl_integration_prompts/Phase2_Offline_Logging_and_Dataset_Export.md`
