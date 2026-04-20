# Eval summary (headless)

- **UTC time:** 2026-04-14T20:20:08Z
- **Model:** `C:\Users\maham\Downloads\CS5394_GameAI_Project\models\ppo\iter2_cooldown_0p5_1p2_auto_heal_demo\stage_fullgame_20k\dungeon_ppo_best.zip`
- **Seed bases:** [0, 1, 2, 3, 4]
- **Episodes per seed:** 10
- **Total episodes:** 50
- **Deterministic:** True

## Metrics

- **mean_reward:** -4.4935 (std 6.3752)
- **mean_episode_length:** 5000.0 (std 0.0)
- **wins / defeats / timeouts:** 0 / 0 / 50 / 50
- **mean_final_room_index:** 3.04 (std 2.84)
- **mean_max_room_index_during_episode:** 3.04 (std 2.84)
- **mean_max_rooms_cleared_during_episode:** 5.86 (std 5.65)

## Action usage (per env step)

- **total_action_steps:** 250000
- **short_attack:** 24859 (9.94%)
- **long_attack:** 8542 (3.42%)
- **interact:** 228 (0.09%)
- **safe_room_heal:** 0 (0.00%)
- **reserve_heal:** 0 (0.00%)
- **safe_room_choice (1+2+3+4):** 86394 (34.56%)
- **safe_room_choice_1:** 84705 (33.88%)
- **safe_room_choice_2:** 1689 (0.68%)
- **safe_room_choice_3:** 0 (0.00%)
- **safe_room_choice_4:** 0 (0.00%)

## Command

```text
'C:\Users\maham\Downloads\CS5394_GameAI_Project\src\rl\eval_ppo.py' --model ../models/ppo/iter2_cooldown_0p5_1p2_auto_heal_demo/stage_fullgame_20k/dungeon_ppo_best.zip --seeds 0 1 2 3 4 --episodes 10 --deterministic --summary-out ../models/ppo/iter2_cooldown_0p5_1p2_auto_heal_demo/stage_fullgame_20k/eval_summary_fair_best.md
```
