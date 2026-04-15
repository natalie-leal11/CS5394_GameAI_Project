# Eval summary (headless)

- **UTC time:** 2026-04-09T17:25:54Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2\stage_900k\dungeon_ppo_best.zip`
- **Seed bases:** [0]
- **Episodes per seed:** 10
- **Total episodes:** 10
- **Deterministic:** True

## Metrics

- **mean_reward:** -3.3453 (std 3.5282)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 10 / 10
- **mean_final_room_index:** 4.70 (std 1.90)
- **mean_max_room_index_during_episode:** 5.30 (std 2.19)
- **mean_max_rooms_cleared_during_episode:** 10.70 (std 5.08)

## Action usage (per env step)

- **total_action_steps:** 50000
- **short_attack:** 10754 (21.51%)
- **long_attack:** 1294 (2.59%)
- **interact:** 0 (0.00%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 3759 (7.52%)
- **safe_room_choice (1+2+3+4):** 3380 (6.76%)
- **safe_room_choice_1:** 12 (0.02%)
- **safe_room_choice_2:** 0 (0.00%)
- **safe_room_choice_3:** 3368 (6.74%)
- **safe_room_choice_4:** 0 (0.00%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model ../models/ppo/iter2_cooldown_0p5_1p2/stage_900k/dungeon_ppo_best.zip --episodes 10 --seed 0 --experiment iter2_cooldown_0p5_1p2 --stage 900k_eval
```
