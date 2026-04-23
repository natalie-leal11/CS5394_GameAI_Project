# rl_prompt_22 — Curriculum evaluation (`eval_curriculum`) and scenario harness

**Sequence:** 22 — *Evaluate trained policies on curriculum scenarios with deterministic runs.*

**Implementation (repo):** `src/rl/eval_curriculum.py`, `src/rl/curriculum_wrappers.py`, `src/rl/curriculum_layout.py` (or equivalent scenario registry), `DungeonEnv` / wrappers as used by training.

---

## Objective

Provide a **repeatable evaluation entry point** for curriculum-defined scenarios (e.g. labeled rooms or difficulty stages) so that checkpointed PPO models can be scored **per scenario** with fixed seeds, max episode length, and consistent termination semantics—without running full training.

## Scope

- **Included:** CLI or `python -m` entry pattern; load `.zip` policy; map scenario IDs to env factory or wrapper stack; aggregate returns, length, success flags; write compact results (CSV/JSON) for comparison across runs.
- **Not included:** Changing reward weights, new observation dimensions, or live TensorBoard training.

## Changes required

- Wire `eval_curriculum` to the same **wrapper order** as training (e.g. `TimeLimit`, normalization) unless a deliberate eval-only simplification is documented.
- Support **seed** and **n_episodes** per scenario; fail fast on unknown scenario IDs.
- Document how scenario names align with `curriculum_layout` / README.

## Constraints

- Deterministic when seed + model are fixed; no reliance on wall-clock randomness.
- Must not alter manual gameplay or non-RL `GameScene` behavior.

## Implementation steps

1. Inspect existing curriculum scenario registration and env construction used by `train_curriculum_ppo.py`.
2. Implement evaluation loop: reset → step until done/truncated → log metrics.
3. Add minimal usage example in `src/rl/README` or project README pointer.

## Deliverables

- Runnable evaluation command and saved metrics artifact suitable for regression checks between training iterations.

## Sources

- `src/rl/eval_curriculum.py`, `src/rl/train_curriculum_ppo.py`, `src/rl/curriculum_wrappers.py`
