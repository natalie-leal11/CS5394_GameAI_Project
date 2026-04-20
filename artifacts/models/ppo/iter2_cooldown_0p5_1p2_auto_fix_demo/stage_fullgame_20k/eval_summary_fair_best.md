# Eval summary (headless)

- **UTC time:** 2026-04-14T20:44:07Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2_auto_fix_demo\stage_fullgame_20k\dungeon_ppo_best.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** -1.2427 (std 1.8912)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 4.00 (std 3.07)
- **mean_max_room_index_during_episode:** 6.40 (std 1.34)
- **mean_max_rooms_cleared_during_episode:** 8.56 (std 1.61)

## Action usage (per env step)

- **total_action_steps:** 250000
- **short_attack:** 71510 (28.60%)
- **long_attack:** 14472 (5.79%)
- **interact:** 17 (0.01%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 0 (0.00%)
- **safe_room_choice (1+2+3+4):** 2237 (0.89%)
- **safe_room_choice_1:** 594 (0.24%)
- **safe_room_choice_2:** 1643 (0.66%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 0 (0.00%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model ../models/ppo/iter2_cooldown_0p5_1p2_auto_fix_demo/stage_fullgame_20k/dungeon_ppo_best.zip --seeds 0 1 2 3 4 --episodes 10 --deterministic --summary-out ../models/ppo/iter2_cooldown_0p5_1p2_auto_fix_demo/stage_fullgame_20k/eval_summary_fair_best.md
```
