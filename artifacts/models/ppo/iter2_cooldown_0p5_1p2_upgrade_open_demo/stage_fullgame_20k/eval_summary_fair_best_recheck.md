# Eval summary (headless)

- **UTC time:** 2026-04-14T03:03:37Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2_upgrade_open_demo\stage_fullgame_20k\dungeon_ppo_best.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** 4.5524 (std 1.2461)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 7.68 (std 2.89)
- **mean_max_room_index_during_episode:** 8.94 (std 2.13)
- **mean_max_rooms_cleared_during_episode:** 13.60 (std 1.15)

## Action usage (per env step)

- **total_action_steps:** 250000
- **short_attack:** 42623 (17.05%)
- **long_attack:** 35908 (14.36%)
- **interact:** 0 (0.00%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 0 (0.00%)
- **safe_room_choice (1+2+3+4):** 328 (0.13%)
- **safe_room_choice_1:** 274 (0.11%)
- **safe_room_choice_2:** 54 (0.02%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 0 (0.00%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model '..\models\ppo\iter2_cooldown_0p5_1p2_upgrade_open_demo\stage_fullgame_20k\dungeon_ppo_best.zip' --seeds 0 1 2 3 4 --episodes 10 --deterministic --summary-out '..\models\ppo\iter2_cooldown_0p5_1p2_upgrade_open_demo\stage_fullgame_20k\eval_summary_fair_best_recheck.md'
```
