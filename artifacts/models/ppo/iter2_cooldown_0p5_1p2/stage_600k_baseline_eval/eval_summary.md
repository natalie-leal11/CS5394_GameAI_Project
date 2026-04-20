# Eval summary (headless)

- **UTC time:** 2026-04-09T17:06:30Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2\stage_600k\dungeon_ppo_best.zip`
- **Seed bases:** [0]
- **Episodes per seed:** 10
- **Total episodes:** 10
- **Deterministic:** True

## Metrics

- **mean_reward:** -3.3709 (std 1.4238)
- **mean_episode_length:** 3847.9 (std 458.9)
- **wins / defeats / timeouts:** 0 / 9 / 1 / 10
- **mean_final_room_index:** 1.70 (std 1.19)
- **mean_max_room_index_during_episode:** 5.40 (std 1.11)
- **mean_max_rooms_cleared_during_episode:** 10.20 (std 2.32)

## Action usage (per env step)

- **total_action_steps:** 38479
- **short_attack:** 838 (2.18%)
- **long_attack:** 4442 (11.54%)
- **interact:** 0 (0.00%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 2761 (7.18%)
- **safe_room_choice (1+2+3+4):** 11373 (29.56%)
- **safe_room_choice_1:** 0 (0.00%)
- **safe_room_choice_2:** 3952 (10.27%)
- **safe_room_choice_3:** 9 (0.02%)
- **safe_room_choice_4:** 7412 (19.26%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model ../models/ppo/iter2_cooldown_0p5_1p2/stage_600k/dungeon_ppo_best.zip --episodes 10 --seed 0 --experiment iter2_cooldown_0p5_1p2 --stage 600k_baseline_eval
```
