# Eval summary (headless)

- **UTC time:** 2026-04-14T20:49:49Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2_auto_pick_demo\stage_fullgame_20k\dungeon_ppo_best.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** 5.5495 (std 1.3641)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 11.82 (std 1.92)
- **mean_max_room_index_during_episode:** 12.26 (std 1.37)
- **mean_max_rooms_cleared_during_episode:** 12.90 (std 0.92)

## Action usage (per env step)

- **total_action_steps:** 250000
- **short_attack:** 49309 (19.72%)
- **long_attack:** 33333 (13.33%)
- **interact:** 874 (0.35%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 846 (0.34%)
- **safe_room_choice (1+2+3+4):** 1264 (0.51%)
- **safe_room_choice_1:** 165 (0.07%)
- **safe_room_choice_2:** 1099 (0.44%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 0 (0.00%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model ../models/ppo/iter2_cooldown_0p5_1p2_auto_pick_demo/stage_fullgame_20k/dungeon_ppo_best.zip --seeds 0 1 2 3 4 --episodes 10 --deterministic --summary-out ../models/ppo/iter2_cooldown_0p5_1p2_auto_pick_demo/stage_fullgame_20k/eval_summary_fair_rebaseline_auto_fix_compare.md
```
