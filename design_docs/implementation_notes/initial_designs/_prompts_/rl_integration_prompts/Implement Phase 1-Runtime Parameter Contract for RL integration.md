Implement Phase 4 — Runtime Loader Integration.

Goal:
Load difficulty parameters from config/difficulty_params.json at game startup and use them inside AI Director and PlayerModel.

Requirements:

* Do NOT change gameplay logic
* Replace only hardcoded numeric values with values from loaded params
* Keep everything deterministic
* No runtime mutation

---

1. Load params at game start

Modify:
src/game/main.py

* Call load_difficulty_params_json()
* Store result as a global or pass into GameScene / AI systems

---

2. Pass params into systems

Modify constructors:

* AI Director
* PlayerModel

Pass DifficultyParams object into them

---

3. Replace hardcoded values

In ai_director.py:
Replace:

* difficulty_modifier values
* enemy_adjustment
* reinforcement_chance

Use:
params.director.*

In player_model.py:
Replace:

* HP thresholds
* dominating/struggling logic thresholds

Use:
params.player_model.*

In metrics_tracker.py:
Replace:

* struggle_hp_loss_percent_threshold
* dominating_hp_loss_percent_threshold
* spike_damage_threshold

Use:
params.metrics.*

In config/reward usage:
Replace:

* heal_drop_base_chance
* safe_room_heal_percent
* mini_boss_reward_heal_percent

Use:
params.rewards.*

In combat (if already configurable safely):
Replace:

* elite_hp_multiplier
* elite_damage_multiplier

Use:
params.combat.*

---

4. Enforce read-only

* Do NOT allow params to be modified after load
* Pass as immutable object

---

5. Validation

After implementation:

* Game runs normally
* No behavior change with default JSON
* Logs still correct
* No randomness introduced

---

6. Report

List:

* files modified
* where parameters replaced
* confirm gameplay unchanged

STOP after integration.
