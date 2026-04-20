# Eval summary (headless)

- **UTC time:** 2026-04-09T17:53:40Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2\stage_800k_fix\dungeon_ppo_best.zip`
- **Seed bases:** [0]
- **Episodes per seed:** 10
- **Total episodes:** 10
- **Deterministic:** True

## Metrics

- **mean_reward:** -5.0212 (std 0.7945)
- **mean_episode_length:** 3136.8 (std 150.9)
- **wins / defeats / timeouts:** 0 / 10 / 0 / 10
- **mean_final_room_index:** 1.30 (std 0.46)
- **mean_max_room_index_during_episode:** 2.00 (std 0.00)
- **mean_max_rooms_cleared_during_episode:** 6.60 (std 0.92)

## Action usage (per env step)

- **total_action_steps:** 31368
- **short_attack:** 1469 (4.68%)
- **long_attack:** 1490 (4.75%)
- **interact:** 0 (0.00%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 9598 (30.60%)
- **safe_room_choice (1+2+3+4):** 114 (0.36%)
- **safe_room_choice_1:** 0 (0.00%)
- **safe_room_choice_2:** 0 (0.00%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 114 (0.36%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model ../models/ppo/iter2_cooldown_0p5_1p2/stage_800k_fix/dungeon_ppo_best.zip --episodes 10 --seed 0 --experiment iter2_cooldown_0p5_1p2 --stage compare_800k_fix
```
