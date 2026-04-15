STEP 2: Replace the placeholder observation vector with a real structured observation vector for the RL environment.

MAIN GOAL:
Implement a stable, fixed-size, numeric observation extractor for DungeonEnv so the RL agent receives meaningful game-state information on every reset() and step().

IMPORTANT RULES:
1. Keep changes additive and reversible.
2. Put new logic under:
   - src/rl/
3. Preserve manual gameplay.
4. Use stable/public fields and helper methods first whenever possible.
5. Use private/internal fields only if absolutely necessary, and mark them clearly with comments.
6. Keep the observation vector modest in size and easy to reason about.
7. Do NOT include raw tile_grid or full room layout tensors in Step 2.
8. Do NOT implement reward shaping, PPO, model code, or training loop.

FILES TO CREATE / UPDATE:
- src/rl/obs.py
- src/rl/env.py
- src/rl/test_env.py
- optionally src/rl/README_step2.md

DATA SOURCES TO USE:
Read observations primarily from:
- game_scene = env._game_scene
- game_scene._player
- game_scene._room_controller
- game_scene._enemies
- game_scene._victory_phase
- game_scene._death_phase

OBSERVATION DESIGN GOAL:
Create one fixed-size float32 vector, normalized where practical, using a compact set of meaningful features.

PREFERRED OBSERVATION CONTENT:
Use approximately 25–35 features total.

A. PLAYER FEATURES
Include:
1. current hp ratio = hp / max_hp
2. max hp normalized
3. lives normalized
4. life_index normalized
5. player x normalized to room/world bounds
6. player y normalized to room/world bounds
7. player vx normalized
8. player vy normalized
9. facing x
10. facing y
11. dash_active as 0/1
12. dash cooldown normalized
13. long attack cooldown normalized
14. block active as 0/1
15. parry active as 0/1
16. invulnerable timer normalized

B. ROOM / PROGRESSION FEATURES
Include:
17. current room index normalized
18. biome index normalized
19. room type encoded numerically and normalized
20. enemies alive count normalized
21. room cleared / door open flag as 0/1 if available
22. is boss or miniboss room as 0/1
23. campaign progress normalized
24. victory flag as 0/1
25. defeat flag as 0/1

C. NEAREST ENEMY FEATURES
Compute nearest active/non-inactive enemy from player position.
Include:
26. has enemy flag as 0/1
27. nearest enemy distance normalized
28. nearest enemy relative x normalized
29. nearest enemy relative y normalized
30. nearest enemy hp ratio
31. nearest enemy type encoded numerically and normalized
32. nearest enemy active/combat-relevant flag as 0/1 if useful

D. HAZARD / LOCAL RISK FEATURES
Include a small amount only if easily available:
33. near hazard flag or normalized hazard proximity
34. player currently in hazard tile as 0/1
35. reserve heal cooldown normalized OR reserve heal availability if easy to read

NORMALIZATION RULES:
1. Every feature must be numeric float32.
2. Avoid NaN and inf.
3. Prefer values in:
   - [0,1] for ratios/flags/counts
   - [-1,1] for signed relative positions/velocities/facing
4. Clamp values where necessary.
5. If some field is unavailable, use a safe default like 0.0 and document it.

IMPORTANT ENCODING RULES:
1. Facing:
   - encode as two values if possible (fx, fy), preferably in {-1,0,1} or normalized equivalent.
2. Room type:
   - convert enum/string into a small stable mapping in src/rl/obs.py
3. Enemy type:
   - convert enemy class/type into a stable mapping in src/rl/obs.py
4. Nearest enemy:
   - only use active, relevant enemies
   - ignore inactive/dead enemies
5. If there is no active enemy:
   - has_enemy = 0
   - distance/relative coords/hp/type features = 0

IMPLEMENTATION DETAILS:

1. Create:
   src/rl/obs.py

2. In obs.py implement something like:
   - build_observation(game_scene) -> np.ndarray
   - helper functions for normalization/clamping
   - helper mappings:
     - room_type_to_id(...)
     - enemy_type_to_id(...)

3. Update src/rl/env.py:
   - replace placeholder observation with build_observation(self._game_scene)
   - update self.observation_space shape to exact final dimension
   - ensure both reset() and step() return the same exact shape

4. Update src/rl/test_env.py:
   Add assertions:
   - obs.dtype == np.float32
   - obs.shape == (<final_dim>,)
   - no NaN
   - no inf
   - observation stays same shape across repeated steps and resets

5. Add concise comments documenting:
   - what each feature means
   - how it is normalized
   - any approximations used

PREFERRED ENGINEERING APPROACH:
- Use stable/public Player helpers first:
  - is_short_attack_active()
  - is_blocking()
  - is_parry_active()
- Use private/internal fields only when there is no clean alternative.
- For nearest enemy, compute from game_scene._enemies using player world_pos and ignore inactive enemies.
- Do NOT use full tile_grid.
- Do NOT overcomplicate with one-hot encoding right now unless clearly needed.

SUCCESS CRITERIA:
1. reset() returns a real non-placeholder observation vector
2. step() returns the same fixed-size vector shape every time
3. vector is numeric, normalized, float32, and stable
4. vector includes player + room/progression + nearest enemy information
5. tests pass in headless mode
6. manual gameplay remains unaffected

AT THE END, REPORT:
1. final observation dimension
2. exact feature list in order
3. any fields approximated
4. any private fields used
5. files created/modified