# Eval summary (headless)

- **UTC time:** 2026-04-13T22:59:29Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2_resume_next_fix\stage_fullgame_50k\dungeon_ppo_final.zip`
- **Seed bases:** [None]
- **Episodes per seed:** 50
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** -8.0413 (std 0.6018)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 1.72 (std 0.45)
- **mean_max_room_index_during_episode:** 1.72 (std 0.45)
- **mean_max_rooms_cleared_during_episode:** 2.72 (std 0.45)

## Action usage (per env step)

- **total_action_steps:** 250000
- **short_attack:** 158995 (63.60%)
- **long_attack:** 3045 (1.22%)
- **interact:** 42 (0.02%)
- **safe_room_heal:** 144 (0.06%)
- **reserve_heal:** 0 (0.00%)
- **safe_room_choice (1+2+3+4):** 1474 (0.59%)
- **safe_room_choice_1:** 252 (0.10%)
- **safe_room_choice_2:** 650 (0.26%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 572 (0.23%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model '..\models\ppo\iter2_cooldown_0p5_1p2_resume_next_fix\stage_fullgame_50k\dungeon_ppo_final.zip' --episodes 50 --deterministic --experiment iter2_cooldown_0p5_1p2_resume_next_fix --stage fullgame_50k
```
