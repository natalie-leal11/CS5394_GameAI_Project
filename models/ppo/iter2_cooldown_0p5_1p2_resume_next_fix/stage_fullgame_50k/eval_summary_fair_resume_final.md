# Eval summary (headless)

- **UTC time:** 2026-04-13T23:36:30Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2_resume_next_fix\stage_fullgame_50k\dungeon_ppo_final.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** -8.1222 (std 0.6347)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 1.66 (std 0.47)
- **mean_max_room_index_during_episode:** 1.66 (std 0.47)
- **mean_max_rooms_cleared_during_episode:** 2.66 (std 0.47)

## Action usage (per env step)

- **total_action_steps:** 250000
- **short_attack:** 145818 (58.33%)
- **long_attack:** 2905 (1.16%)
- **interact:** 51 (0.02%)
- **safe_room_heal:** 132 (0.05%)
- **reserve_heal:** 0 (0.00%)
- **safe_room_choice (1+2+3+4):** 1447 (0.58%)
- **safe_room_choice_1:** 231 (0.09%)
- **safe_room_choice_2:** 650 (0.26%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 566 (0.23%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model '..\models\ppo\iter2_cooldown_0p5_1p2_resume_next_fix\stage_fullgame_50k\dungeon_ppo_final.zip' --seeds 0 1 2 3 4 --episodes 10 --deterministic --summary-out '..\models\ppo\iter2_cooldown_0p5_1p2_resume_next_fix\stage_fullgame_50k\eval_summary_fair_resume_final.md'
```
