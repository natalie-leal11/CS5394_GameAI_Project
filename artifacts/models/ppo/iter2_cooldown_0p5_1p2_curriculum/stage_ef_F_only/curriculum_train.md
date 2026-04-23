# Curriculum (E/F) train run

- **UTC time:** 2026-04-13T19:50:41Z
- **Scenario:** `safe_heal`
- **Experiment:** `iter2_cooldown_0p5_1p2`
- **Stage:** `ef_F_only`
- **Timesteps:** 50000
- **Resume from:** (fresh start)
- **Models directory:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2_curriculum\stage_ef_F_only`
- **Final:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2_curriculum\stage_ef_F_only\dungeon_ppo_final.zip`

## Full-game fine-tune

Resume standard training with:

`python -m rl.train_ppo --resume-model C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2_curriculum\stage_ef_F_only\dungeon_ppo_final.zip ...`
