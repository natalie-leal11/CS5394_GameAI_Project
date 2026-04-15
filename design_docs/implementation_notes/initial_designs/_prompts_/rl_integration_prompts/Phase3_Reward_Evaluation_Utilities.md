PHASE 3 — Reward Evaluation Utilities

Goal
Add a deterministic offline reward utility for candidate parameter sets.

Create files:

src/game/rl/reward_eval.py
src/game/rl/offline_tuning_spec.py
tools/rl/evaluate_candidate_params.py

Requirements

Implement a deterministic reward function aligned with SRS goals:

- balanced win rate around 55% to 65%
- avoid early biome frustration
- prevent trivial late-game encounters
- avoid extreme difficulty spikes

Implementation guidance

1. Read exported offline dataset
2. Evaluate candidate parameter sets against logged outcomes
3. Produce a score and a metrics breakdown
4. Keep this utility offline only
5. Do not implement online policy learning
6. Do not modify gameplay code during evaluation

Suggested outputs

- overall_reward
- win_rate_score
- early_biome_penalty
- late_game_triviality_penalty
- difficulty_spike_penalty

Keep formulas explicit and documented.

STOP AFTER IMPLEMENTATION
