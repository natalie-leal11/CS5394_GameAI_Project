# Eval summary (headless)

- **UTC time:** 2026-04-14T02:55:30Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2_upgrade_open_demo_cont\stage_fullgame_plus30k\dungeon_ppo_best.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** -3.4483 (std 6.2102)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 5.36 (std 5.20)
- **mean_max_room_index_during_episode:** 5.54 (std 5.39)
- **mean_max_rooms_cleared_during_episode:** 6.42 (std 5.15)

## Action usage (per env step)

- **total_action_steps:** 250000
- **short_attack:** 20065 (8.03%)
- **long_attack:** 17966 (7.19%)
- **interact:** 0 (0.00%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 0 (0.00%)
- **safe_room_choice (1+2+3+4):** 1259 (0.50%)
- **safe_room_choice_1:** 337 (0.13%)
- **safe_room_choice_2:** 65 (0.03%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 857 (0.34%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model '..\models\ppo\iter2_cooldown_0p5_1p2_upgrade_open_demo_cont\stage_fullgame_plus30k\dungeon_ppo_best.zip' --seeds 0 1 2 3 4 --episodes 10 --deterministic --summary-out '..\models\ppo\iter2_cooldown_0p5_1p2_upgrade_open_demo_cont\stage_fullgame_plus30k\eval_summary_fair_best.md'
```
