Implement Phase 1 — Runtime Parameter Contract for RL integration.

Goal:
Create a centralized, read-only difficulty parameter system using a JSON config, based on existing hardcoded values.

Context:
We already identified ~20 high-impact parameters currently hardcoded across:

* ai_director.py
* difficulty_params.py (PlayerModel)
* metrics_tracker.py
* config.py

We want to:

* move these values into config/difficulty_params.json
* define a typed schema in src/game/ai/difficulty_params.py
* DO NOT change gameplay logic yet
* DO NOT add RL training
* DO NOT modify AI Director behavior yet

This step is ONLY about defining and loading parameters.

---

1. Create JSON config file

File:
config/difficulty_params.json

Include the following parameters with sensible default values based on current code:

{
"player_model": {
"struggling_hp_critical_percent": 25.0,
"struggling_hp_weak_percent": 40.0,
"dominating_hp_min_percent": 70.0,
"dominating_avg_hp_loss_max_percent": 5.0
},
"director": {
"difficulty_modifier": {
"struggling": 0.85,
"stable": 1.0,
"dominating": 1.15
},
"enemy_adjustment": {
"struggling": -1,
"stable": 0,
"dominating": 1
},
"reinforcement_chance": {
"struggling": 0.05,
"stable": 0.15,
"dominating": 0.30
}
},
"rewards": {
"heal_drop_base_chance": 0.25,
"safe_room_heal_percent": 0.30,
"mini_boss_reward_heal_percent": 0.30
},
"metrics": {
"struggle_hp_loss_percent_threshold": 30.0,
"dominating_hp_loss_percent_threshold": 5.0,
"spike_damage_threshold": 30.0
},
"combat": {
"elite_hp_multiplier": 1.4,
"elite_damage_multiplier": 1.2
}
}

---

2. Create parameter schema

File:
src/game/ai/difficulty_params.py

Requirements:

* Define structured classes (dataclasses or typed objects)

* Mirror the JSON structure exactly

* Include:

  * PlayerModelParams
  * DirectorParams
  * RewardParams
  * MetricsParams
  * CombatParams
  * Root DifficultyParams

* Add:

  * from_dict() or equivalent loader helper
  * validation (basic range checks, e.g. probabilities 0–1)

* Add clear docstring:
  "These parameters are loaded at runtime and must not be modified during gameplay. They are tuned offline."

---

3. Do NOT integrate into gameplay yet

Important:

* Do NOT modify ai_director.py
* Do NOT modify PlayerModel logic
* Do NOT replace existing constants yet
* Do NOT change any behavior

This phase is ONLY:

* defining schema
* defining JSON
* ensuring it loads correctly

---

4. Deliverables

Report:

* files created
* schema structure
* confirmation JSON loads successfully
* no gameplay behavior changed

## STOP after this phase.
