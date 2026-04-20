# rl_prompt_12 — Curriculum PPO training and evaluation (E & F)

**Sequence:** 12 of 18 — *Scenario-specific training before full-game focus.*

**Implementation (repo):** `python -m rl.train_curriculum_ppo`, `python -m rl.eval_curriculum`; outputs under `models/ppo/iter2_cooldown_0p5_1p2_curriculum/` per stage; `ai_prompts/rl_integration_prompts/RL Curriculum Training + Evaluation (E & F Validation).md`.

---

## Objective

Train and evaluate **interact (E)** and **safe heal (F)** curriculum scenarios with fixed `--experiment` and `--stage` names, then evaluate each trained model with deterministic policy and many episodes.

## Scope

- **Included:** `interact` + `ef_E_only` (100k timesteps); `safe_heal` + `ef_F_only` (100k); eval 200 episodes each; paths to `dungeon_ppo_final.zip` per stage.
- **Not included:** Body text under “Important Validation Requirement (Do NOT skip)” — the **repository copy of the source markdown ends at that heading** with no further lines.

## Changes required

- `cd src` then run `train_curriculum_ppo` and `eval_curriculum` commands exactly as listed in the source file.

## Constraints

- **“Follow these steps exactly. Do not modify existing logic.”** (source file header).

## Implementation steps

1. Train E: `--scenario interact --timesteps 100000 --stage ef_E_only`.
2. Eval E model from `models/ppo/iter2_cooldown_0p5_1p2_curriculum/stage_ef_E_only/dungeon_ppo_final.zip`.
3. Train F: `--scenario safe_heal --timesteps 100000 --stage ef_F_only`.
4. Eval F model from `.../stage_ef_F_only/dungeon_ppo_final.zip`.

## Deliverables

- Curriculum checkpoints and eval runs for both scenarios.

## Sources

- `ai_prompts/rl_integration_prompts/RL Curriculum Training + Evaluation (E & F Validation).md`
