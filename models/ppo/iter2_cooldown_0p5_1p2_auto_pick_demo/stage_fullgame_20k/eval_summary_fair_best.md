# Eval summary (headless)

- **UTC time:** 2026-04-14T06:48:50Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2_auto_pick_demo\stage_fullgame_20k\dungeon_ppo_best.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** 5.1923 (std 1.7828)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 10.56 (std 3.87)
- **mean_max_room_index_during_episode:** 11.54 (std 2.28)
- **mean_max_rooms_cleared_during_episode:** 13.02 (std 1.05)

## Action usage (per env step)

- **total_action_steps:** 250000
- **short_attack:** 54324 (21.73%)
- **long_attack:** 31977 (12.79%)
- **interact:** 809 (0.32%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 807 (0.32%)
- **safe_room_choice (1+2+3+4):** 1638 (0.66%)
- **safe_room_choice_1:** 133 (0.05%)
- **safe_room_choice_2:** 1505 (0.60%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 0 (0.00%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model '..\models\ppo\iter2_cooldown_0p5_1p2_auto_pick_demo\stage_fullgame_20k\dungeon_ppo_best.zip' --seeds 0 1 2 3 4 --episodes 10 --deterministic --summary-out '..\models\ppo\iter2_cooldown_0p5_1p2_auto_pick_demo\stage_fullgame_20k\eval_summary_fair_best.md'
```
