# rl_prompt_24 — Training callbacks and experiment layout (`best_progress_callback`, `experiment_layout`)

**Sequence:** 24 — *Checkpoint selection by domain progress and reproducible experiment folders.*

**Implementation (repo):** `src/rl/best_progress_callback.py`, `src/rl/experiment_layout.py`, `src/rl/train_ppo.py` / `train_curriculum_ppo.py` integration points.

---

## Objective

Document and, if needed, extend **SB3 callbacks** and **directory layout** so long runs save **best** policies by a game-relevant statistic (e.g. max room reached, rooms cleared), not only by raw episodic return—while keeping experiment roots **namespaced** (timestamp, tag) to avoid overwriting prior work.

## Scope

- **Included:** Callback contract (which infos/episode buffers are read); where `experiment_layout` writes `models/`, `logs/`; interaction with VecEnv vs single env.
- **Not included:** New reward terms; changing PPO algorithm class.

## Changes required

- Ensure callback reads from **info** dict fields the env already exposes after `step` (or final info on done).
- Folder naming: document pattern `iterN_<tag>_<date>` or match existing repo convention in `experiment_layout.py`.

## Constraints

- Default training without callback must still work (callback optional via flag).
- No mandatory cloud storage; local paths only.

## Implementation steps

1. Trace `best_progress_callback` registration in training scripts.
2. Align progress metric with `GameScene` / `DungeonEnv` info keys (rooms cleared, victory flag).
3. Document env vars or CLI flags that select experiment root.

## Deliverables

- Clear README subsection: how to resume training **and** how to interpret `best_` checkpoints from the callback.

## Sources

- `src/rl/best_progress_callback.py`, `src/rl/experiment_layout.py`, `src/rl/train_ppo.py`
