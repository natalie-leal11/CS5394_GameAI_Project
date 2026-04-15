# Eval summary (headless)

- **UTC time:** 2026-04-09T07:52:12Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2\stage_600k\dungeon_ppo_best.zip`
- **Seed bases:** [0]
- **Episodes per seed:** 1
- **Total episodes:** 1
- **Deterministic:** True

## Metrics

- **mean_reward:** -2.6364 (std 0.0000)
- **mean_episode_length:** 3425.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 1 / 0 / 1
- **mean_final_room_index:** 1.00 (std 0.00)
- **mean_max_room_index_during_episode:** 5.00 (std 0.00)
- **mean_max_rooms_cleared_during_episode:** 10.00 (std 0.00)

## Action usage (per env step)

- **total_action_steps:** 3425
- **short_attack:** 36 (1.05%)
- **long_attack:** 507 (14.80%)
- **interact:** 0 (0.00%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 56 (1.64%)
- **safe_room_choice (1+2+3+4):** 1140 (33.28%)
- **safe_room_choice_1:** 0 (0.00%)
- **safe_room_choice_2:** 317 (9.26%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 823 (24.03%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model ../models/ppo/iter2_cooldown_0p5_1p2/stage_600k/dungeon_ppo_best.zip --experiment iter2_cooldown_0p5_1p2 --stage 600k --episodes 1 --seeds 0
```
