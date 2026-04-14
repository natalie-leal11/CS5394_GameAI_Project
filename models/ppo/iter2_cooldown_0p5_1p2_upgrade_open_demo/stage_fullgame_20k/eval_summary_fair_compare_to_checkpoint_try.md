# Eval summary (headless)

- **UTC time:** 2026-04-14T03:28:53Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2_upgrade_open_demo\stage_fullgame_20k\dungeon_ppo_best.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** 4.5389 (std 1.2268)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 7.42 (std 3.24)
- **mean_max_room_index_during_episode:** 8.82 (std 2.12)
- **mean_max_rooms_cleared_during_episode:** 13.62 (std 1.16)

## Action usage (per env step)

- **total_action_steps:** 250000
- **short_attack:** 41728 (16.69%)
- **long_attack:** 35930 (14.37%)
- **interact:** 0 (0.00%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 0 (0.00%)
- **safe_room_choice (1+2+3+4):** 328 (0.13%)
- **safe_room_choice_1:** 264 (0.11%)
- **safe_room_choice_2:** 64 (0.03%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 0 (0.00%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model '..\models\ppo\iter2_cooldown_0p5_1p2_upgrade_open_demo\stage_fullgame_20k\dungeon_ppo_best.zip' --seeds 0 1 2 3 4 --episodes 10 --deterministic --summary-out '..\models\ppo\iter2_cooldown_0p5_1p2_upgrade_open_demo\stage_fullgame_20k\eval_summary_fair_compare_to_checkpoint_try.md'
```
