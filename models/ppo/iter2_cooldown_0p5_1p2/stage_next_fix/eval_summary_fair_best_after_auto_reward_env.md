# Eval summary (headless)

- **UTC time:** 2026-04-14T00:46:08Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2\stage_next_fix\dungeon_ppo_best.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** 2.6668 (std 3.0401)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 5.16 (std 3.27)
- **mean_max_room_index_during_episode:** 7.52 (std 1.78)
- **mean_max_rooms_cleared_during_episode:** 11.96 (std 3.01)

## Action usage (per env step)

- **total_action_steps:** 250000
- **short_attack:** 109357 (43.74%)
- **long_attack:** 20018 (8.01%)
- **interact:** 0 (0.00%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 0 (0.00%)
- **safe_room_choice (1+2+3+4):** 1845 (0.74%)
- **safe_room_choice_1:** 230 (0.09%)
- **safe_room_choice_2:** 1615 (0.65%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 0 (0.00%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model '..\models\ppo\iter2_cooldown_0p5_1p2\stage_next_fix\dungeon_ppo_best.zip' --seeds 0 1 2 3 4 --episodes 10 --deterministic --summary-out '..\models\ppo\iter2_cooldown_0p5_1p2\stage_next_fix\eval_summary_fair_best_after_auto_reward_env.md'
```
