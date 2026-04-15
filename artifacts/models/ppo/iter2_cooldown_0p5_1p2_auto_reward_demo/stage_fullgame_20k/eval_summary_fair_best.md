# Eval summary (headless)

- **UTC time:** 2026-04-14T00:38:27Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2_auto_reward_demo\stage_fullgame_20k\dungeon_ppo_best.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** 0.9447 (std 4.4154)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 6.50 (std 3.34)
- **mean_max_room_index_during_episode:** 9.14 (std 3.81)
- **mean_max_rooms_cleared_during_episode:** 10.46 (std 3.71)

## Action usage (per env step)

- **total_action_steps:** 250000
- **short_attack:** 55262 (22.10%)
- **long_attack:** 20866 (8.35%)
- **interact:** 0 (0.00%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 0 (0.00%)
- **safe_room_choice (1+2+3+4):** 286 (0.11%)
- **safe_room_choice_1:** 170 (0.07%)
- **safe_room_choice_2:** 116 (0.05%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 0 (0.00%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model '..\models\ppo\iter2_cooldown_0p5_1p2_auto_reward_demo\stage_fullgame_20k\dungeon_ppo_best.zip' --seeds 0 1 2 3 4 --episodes 10 --deterministic --summary-out '..\models\ppo\iter2_cooldown_0p5_1p2_auto_reward_demo\stage_fullgame_20k\eval_summary_fair_best.md'
```
