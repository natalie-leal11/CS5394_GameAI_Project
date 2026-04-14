# Eval summary (headless)

- **UTC time:** 2026-04-13T23:22:14Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2\stage_next_fix\dungeon_ppo_best.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** 2.4138 (std 3.0015)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 4.86 (std 2.78)
- **mean_max_room_index_during_episode:** 7.20 (std 0.98)
- **mean_max_rooms_cleared_during_episode:** 11.82 (std 3.03)

## Action usage (per env step)

- **total_action_steps:** 250000
- **short_attack:** 111385 (44.55%)
- **long_attack:** 19141 (7.66%)
- **interact:** 0 (0.00%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 0 (0.00%)
- **safe_room_choice (1+2+3+4):** 1975 (0.79%)
- **safe_room_choice_1:** 244 (0.10%)
- **safe_room_choice_2:** 1731 (0.69%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 0 (0.00%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model '..\models\ppo\iter2_cooldown_0p5_1p2\stage_next_fix\dungeon_ppo_best.zip' --seeds 0 1 2 3 4 --episodes 10 --deterministic --summary-out '..\models\ppo\iter2_cooldown_0p5_1p2\stage_next_fix\eval_summary_fair_best.md'
```
