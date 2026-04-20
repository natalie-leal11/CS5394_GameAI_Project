# Eval summary (headless)

- **UTC time:** 2026-04-14T02:29:38Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2\stage_next_fix\dungeon_ppo_best.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** 2.8154 (std 3.0216)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 5.40 (std 3.30)
- **mean_max_room_index_during_episode:** 7.60 (std 1.84)
- **mean_max_rooms_cleared_during_episode:** 12.06 (std 2.94)

## Action usage (per env step)

- **total_action_steps:** 250000
- **short_attack:** 107551 (43.02%)
- **long_attack:** 20433 (8.17%)
- **interact:** 0 (0.00%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 0 (0.00%)
- **safe_room_choice (1+2+3+4):** 1872 (0.75%)
- **safe_room_choice_1:** 240 (0.10%)
- **safe_room_choice_2:** 1632 (0.65%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 0 (0.00%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model '..\models\ppo\iter2_cooldown_0p5_1p2\stage_next_fix\dungeon_ppo_best.zip' --seeds 0 1 2 3 4 --episodes 10 --deterministic --summary-out '..\models\ppo\iter2_cooldown_0p5_1p2\stage_next_fix\eval_summary_fair_best_after_upgrade_open.md'
```
