# Eval summary (headless)

- **UTC time:** 2026-04-14T03:28:44Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2_checkpoint_try\stage_fullgame_20k_more\dungeon_ppo_best.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** 1.7745 (std 3.3538)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 6.28 (std 1.89)
- **mean_max_room_index_during_episode:** 6.84 (std 0.37)
- **mean_max_rooms_cleared_during_episode:** 11.04 (std 3.23)

## Action usage (per env step)

- **total_action_steps:** 250000
- **short_attack:** 105161 (42.06%)
- **long_attack:** 22813 (9.13%)
- **interact:** 0 (0.00%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 0 (0.00%)
- **safe_room_choice (1+2+3+4):** 8808 (3.52%)
- **safe_room_choice_1:** 346 (0.14%)
- **safe_room_choice_2:** 1055 (0.42%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 7407 (2.96%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model '..\models\ppo\iter2_cooldown_0p5_1p2_checkpoint_try\stage_fullgame_20k_more\dungeon_ppo_best.zip' --seeds 0 1 2 3 4 --episodes 10 --deterministic --summary-out '..\models\ppo\iter2_cooldown_0p5_1p2_checkpoint_try\stage_fullgame_20k_more\eval_summary_fair_best.md'
```
