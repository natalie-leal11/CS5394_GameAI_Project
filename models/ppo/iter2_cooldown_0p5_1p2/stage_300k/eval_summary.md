# Eval summary (headless)

- **UTC time:** 2026-04-09T07:17:24Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2\stage_300k\dungeon_ppo_best.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** -9.4807 (std 0.0604)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 1.00 (std 0.00)
- **mean_max_room_index_during_episode:** 1.00 (std 0.00)
- **mean_max_rooms_cleared_during_episode:** 2.00 (std 0.00)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model ../models/ppo/iter2_cooldown_0p5_1p2/stage_300k/dungeon_ppo_best.zip --experiment iter2_cooldown_0p5_1p2 --stage 300k --episodes 10 --seeds 0 1 2 3 4
```
