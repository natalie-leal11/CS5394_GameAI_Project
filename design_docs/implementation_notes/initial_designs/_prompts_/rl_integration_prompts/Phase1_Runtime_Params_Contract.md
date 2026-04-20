PHASE 1 — Runtime Parameter Contract

Goal
Create the read-only runtime parameter schema used by AI systems.

Create files:

src/game/ai/difficulty_params.py
config/difficulty_params.json

Requirements

1. Define a typed parameter model for runtime-loaded values.
2. Parameters must be numerical and deterministic.
3. Parameters must be loaded from file, not learned at runtime.
4. Include only values allowed by SRS offline RL scope.

Include fields such as:
- struggling_thresholds
- stable_thresholds
- dominating_thresholds
- enemy_count_multiplier
- elite_bias
- ambush_bias
- reinforcement_probability
- healing_bias

Implementation notes

- Provide sane default values in config/difficulty_params.json
- Keep the schema additive and easy to validate
- Include comments or docstrings explaining that runtime mutation is forbidden
- Do not wire into gameplay yet

STOP AFTER FILE CREATION
