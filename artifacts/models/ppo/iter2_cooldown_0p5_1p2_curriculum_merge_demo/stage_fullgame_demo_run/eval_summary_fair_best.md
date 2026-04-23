# Eval summary (headless)

- **UTC time:** 2026-04-13T23:55:52Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2_curriculum_merge_demo\stage_fullgame_demo_run\dungeon_ppo_best.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** 989.0028 (std 0.0000)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 0.00 (std 0.00)
- **mean_max_room_index_during_episode:** 0.00 (std 0.00)
- **mean_max_rooms_cleared_during_episode:** 0.00 (std 0.00)

## Action usage (per env step)

- **total_action_steps:** 250000
- **short_attack:** 0 (0.00%)
- **long_attack:** 0 (0.00%)
- **interact:** 250000 (100.00%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 0 (0.00%)
- **safe_room_choice (1+2+3+4):** 0 (0.00%)
- **safe_room_choice_1:** 0 (0.00%)
- **safe_room_choice_2:** 0 (0.00%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 0 (0.00%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model '..\models\ppo\iter2_cooldown_0p5_1p2_curriculum_merge_demo\stage_fullgame_demo_run\dungeon_ppo_best.zip' --seeds 0 1 2 3 4 --episodes 10 --deterministic --summary-out '..\models\ppo\iter2_cooldown_0p5_1p2_curriculum_merge_demo\stage_fullgame_demo_run\eval_summary_fair_best.md'
```
