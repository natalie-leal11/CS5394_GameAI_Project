# Eval summary (headless)

- **UTC time:** 2026-04-13T23:30:23Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2\stage_next_fix\dungeon_ppo_final.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** 1.6355 (std 3.5341)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 5.04 (std 3.31)
- **mean_max_room_index_during_episode:** 7.12 (std 1.07)
- **mean_max_rooms_cleared_during_episode:** 11.20 (std 3.29)

## Action usage (per env step)

- **total_action_steps:** 250000
- **short_attack:** 103828 (41.53%)
- **long_attack:** 24379 (9.75%)
- **interact:** 0 (0.00%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 0 (0.00%)
- **safe_room_choice (1+2+3+4):** 833 (0.33%)
- **safe_room_choice_1:** 216 (0.09%)
- **safe_room_choice_2:** 617 (0.25%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 0 (0.00%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model '..\models\ppo\iter2_cooldown_0p5_1p2\stage_next_fix\dungeon_ppo_final.zip' --seeds 0 1 2 3 4 --episodes 10 --deterministic --summary-out '..\models\ppo\iter2_cooldown_0p5_1p2\stage_next_fix\eval_summary_fair_final.md'
```
