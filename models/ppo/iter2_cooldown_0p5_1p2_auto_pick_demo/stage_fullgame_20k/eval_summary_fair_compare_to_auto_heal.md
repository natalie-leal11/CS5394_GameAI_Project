# Eval summary (headless)

- **UTC time:** 2026-04-14T20:26:24Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2_auto_pick_demo\stage_fullgame_20k\dungeon_ppo_best.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** 5.2650 (std 1.7149)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 11.48 (std 2.56)
- **mean_max_room_index_during_episode:** 11.84 (std 1.78)
- **mean_max_rooms_cleared_during_episode:** 12.80 (std 0.98)

## Action usage (per env step)

- **total_action_steps:** 250000
- **short_attack:** 54760 (21.90%)
- **long_attack:** 32769 (13.11%)
- **interact:** 879 (0.35%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 889 (0.36%)
- **safe_room_choice (1+2+3+4):** 1666 (0.67%)
- **safe_room_choice_1:** 149 (0.06%)
- **safe_room_choice_2:** 1517 (0.61%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 0 (0.00%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model ../models/ppo/iter2_cooldown_0p5_1p2_auto_pick_demo/stage_fullgame_20k/dungeon_ppo_best.zip --seeds 0 1 2 3 4 --episodes 10 --deterministic --summary-out ../models/ppo/iter2_cooldown_0p5_1p2_auto_pick_demo/stage_fullgame_20k/eval_summary_fair_compare_to_auto_heal.md
```
