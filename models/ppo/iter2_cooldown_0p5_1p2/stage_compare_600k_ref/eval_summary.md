# Eval summary (headless)

- **UTC time:** 2026-04-09T17:53:50Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2\stage_600k\dungeon_ppo_best.zip`
- **Seed bases:** [0]
- **Episodes per seed:** 10
- **Total episodes:** 10
- **Deterministic:** True

## Metrics

- **mean_reward:** -3.3110 (std 1.4392)
- **mean_episode_length:** 3781.1 (std 480.0)
- **wins / defeats / timeouts:** 0 / 9 / 1 / 10
- **mean_final_room_index:** 1.70 (std 1.19)
- **mean_max_room_index_during_episode:** 5.40 (std 1.11)
- **mean_max_rooms_cleared_during_episode:** 10.20 (std 2.32)

## Action usage (per env step)

- **total_action_steps:** 37811
- **short_attack:** 838 (2.22%)
- **long_attack:** 4447 (11.76%)
- **interact:** 0 (0.00%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 2764 (7.31%)
- **safe_room_choice (1+2+3+4):** 10912 (28.86%)
- **safe_room_choice_1:** 0 (0.00%)
- **safe_room_choice_2:** 3951 (10.45%)
- **safe_room_choice_3:** 9 (0.02%)
- **safe_room_choice_4:** 6952 (18.39%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model ../models/ppo/iter2_cooldown_0p5_1p2/stage_600k/dungeon_ppo_best.zip --episodes 10 --seed 0 --experiment iter2_cooldown_0p5_1p2 --stage compare_600k_ref
```
