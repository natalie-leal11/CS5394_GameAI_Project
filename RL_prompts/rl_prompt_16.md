# rl_prompt_16 — Phase 3: offline reward evaluation utilities

**Sequence:** 16 of 18 — *Score candidate parameter sets on logged data.*

**Implementation (repo):** `src/game/rl/reward_eval.py`, `src/game/rl/offline_tuning_spec.py`, `tools/rl/evaluate_candidate_params.py`; `ai_prompts/rl_integration_prompts/Phase3_Reward_Evaluation_Utilities.md`.

---

## Objective

Provide a **deterministic offline** utility to score candidate difficulty parameter sets against exported datasets, aligned with SRS goals (e.g. win-rate band, pacing, avoiding spikes).

## Scope

- **Included:** Read dataset; output overall score + breakdown (`win_rate_score`, early/late/spike penalties as specified).
- **Not included:** Online policy learning; gameplay mutation during evaluation.

## Changes required

- Explicit, documented formulas; deterministic evaluation.

## Constraints

- Offline only; no SB3/PPO in this phase.

## Implementation steps

1. Implement evaluation pipeline on exported data.
2. Document metrics.
3. **STOP AFTER IMPLEMENTATION** per phase file.

## Deliverables

- Runnable `evaluate_candidate_params` workflow and interpretable metrics.

## Sources

- `ai_prompts/rl_integration_prompts/Phase3_Reward_Evaluation_Utilities.md`
