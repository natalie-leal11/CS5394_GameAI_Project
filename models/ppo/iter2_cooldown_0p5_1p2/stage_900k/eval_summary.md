# Eval summary (headless)

- **UTC time:** 2026-04-09T08:14:42Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2\stage_900k\dungeon_ppo_best.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** -5.8018 (std 2.7068)
- **mean_episode_length:** 4247.5 (std 1048.5)
- **wins / defeats / timeouts:** 0 / 17 / 33 / 50
- **mean_final_room_index:** 2.62 (std 1.68)
- **mean_max_room_index_during_episode:** 3.64 (std 1.25)
- **mean_max_rooms_cleared_during_episode:** 6.00 (std 2.47)

## Action usage (per env step)

- **total_action_steps:** 212374
- **short_attack:** 5677 (2.67%)
- **long_attack:** 20601 (9.70%)
- **interact:** 0 (0.00%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 3315 (1.56%)
- **safe_room_choice (1+2+3+4):** 15220 (7.17%)
- **safe_room_choice_1:** 0 (0.00%)
- **safe_room_choice_2:** 2701 (1.27%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 12519 (5.89%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model ../models/ppo/iter2_cooldown_0p5_1p2/stage_900k/dungeon_ppo_best.zip --experiment iter2_cooldown_0p5_1p2 --stage 900k --episodes 10 --seeds 0 1 2 3 4
```
