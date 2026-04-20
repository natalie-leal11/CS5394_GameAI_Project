Implement Phase 2 PlayerModel integration for the existing src codebase.

Goal:
Create a deterministic PlayerModel that reads MetricsTracker summaries and classifies the player into exactly one of:
- STRUGGLING
- STABLE
- DOMINATING

Files to create/update:
- src/game/ai/player_model.py
- src/game/ai/difficulty_params.py
- src/game/scenes/game_scene.py (minimal wiring only)

Requirements:

1. player_model.py
Create:
- PlayerState enum or constants:
  - STRUGGLING
  - STABLE
  - DOMINATING
- PlayerModel class
- classify(summary) method

Classification must be:
- deterministic
- parameter-driven
- pure or near-pure
- based only on metrics summary + fixed thresholds
- no random usage
- no direct game mutations

2. difficulty_params.py
Add fixed read-only thresholds for classification.
Keep them simple and implementation-aligned.

Include thresholds for signals such as:
- low hp percent
- near death hp percent
- heavy room damage threshold
- clean clear threshold
- slow clear threshold
- struggling room ratio threshold
- dominating room ratio threshold
- recent death penalty
- high healing dependency threshold

Do not add runtime tuning logic.
Do not mutate params during gameplay.

3. Metrics PlayerModel Inputs
Use only metrics that are already tracked in MetricsTracker, such as:
- hp_percent_current
- hp_percent_end_room
- hp_lost_in_room
- damage_taken_in_room
- room_clear_time
- rooms_cleared
- total_deaths
- total_healing_received
- healing_wasted
- reward_collected_flag
- last_3_rooms_hp_loss
- last_3_rooms_clear_time
- last_3_rooms_result
- recent_death_flag
- struggling_rooms_count
- dominating_rooms_count

Do not invent unsupported inputs.

4. Classification Rules
Implement simple bounded rules.

Suggested interpretation:
- STRUGGLING if player frequently ends rooms low on HP, takes heavy damage, has recent death, or has repeated near_death / death outcomes
- DOMINATING if player repeatedly gets clean clears, low damage taken, fast clear times, and no recent deaths
- otherwise STABLE

Use a scoring or rules approach, but keep it:
- explainable
- deterministic
- easy to inspect
- easy to tune later

5. Output
PlayerModel should return a small summary object or dataclass containing:
- player_state
- reasons or signal flags used for the decision
- optional score breakdown for debugging/logging

Keep this compact and read-only.

6. game_scene.py integration
Add minimal wiring only:
- instantiate PlayerModel
- after room end / summary update, recompute current player state
- store current player state on game_scene
- do not apply AI Director decisions yet
- do not change combat, enemy, UI, safe-room, or spawn behavior

7. Strict constraints
Do NOT:
- add randomness
- redesign gameplay
- modify room generation
- modify boss behavior
- change menu / settings / victory flow
- change player combat systems
- implement AI Director logic here

8. Success criteria
- imports cleanly
- game still runs
- PlayerModel classifies deterministically
- thresholds come from difficulty_params.py
- game_scene can access current player state
- no gameplay behavior changes beyond internal state computation

Please implement the code directly, keep changes minimal, and preserve the current repository behavior.

Use a weighted deterministic interpretation for PlayerModel classification.

Classify STRUGGLING when multiple of these are true:
- recent_death_flag is true
- hp_percent_current or hp_percent_end_room is below struggling threshold
- last_3_rooms_result contains repeated near_death or death
- average recent hp loss is high
- struggling_rooms_count is rising
- total_healing_received is high relative to rooms_cleared

Classify DOMINATING when multiple of these are true:
- no recent death
- hp_percent_current and hp_percent_end_room stay comfortably high
- last_3_rooms_result contains mostly clean_clear
- damage_taken_in_room and recent hp loss stay low
- room_clear_time is consistently fast
- dominating_rooms_count is rising

Otherwise classify STABLE.

Implementation rules:
- use only tracked metrics already present
- keep logic deterministic and explainable
- return both player_state and a compact reasons list
- do not use every attribute; only the most meaningful ones
- thresholds must come from difficulty_params.py