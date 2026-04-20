# RL Curriculum Training + Evaluation (E & F Validation)

Follow these steps exactly. Do not modify existing logic.

---

## Step 1: Interaction Scenario (E)

First navigate to source:

```bash
cd src

Run PPO curriculum training:

python -m rl.train_curriculum_ppo --scenario interact --timesteps 100000 --experiment iter2_cooldown_0p5_1p2 --stage ef_E_only

Then evaluate the trained model:

python -m rl.eval_curriculum --model ..\models\ppo\iter2_cooldown_0p5_1p2_curriculum\stage_ef_E_only\dungeon_ppo_final.zip --scenario interact --episodes 200 --deterministic --experiment iter2_cooldown_0p5_1p2 --stage ef_E_only

## Step 2: Safe Heal Scenario (F)

Run PPO curriculum training:

python -m rl.train_curriculum_ppo --scenario safe_heal --timesteps 100000 --experiment iter2_cooldown_0p5_1p2 --stage ef_F_only

Then evaluate the trained model:

python -m rl.eval_curriculum --model ..\models\ppo\iter2_cooldown_0p5_1p2_curriculum\stage_ef_F_only\dungeon_ppo_final.zip --scenario safe_heal --episodes 200 --deterministic --experiment iter2_cooldown_0p5_1p2 --stage ef_F_only
Important Validation Requirement (Do NOT skip)