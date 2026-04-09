STEP 1: Convert the existing Pygame dungeon game into a Gymnasium-compatible RL environment with headless mode, while keeping all changes isolated and reversible.

MAIN GOAL:
Create the environment wrapper and minimal integration needed so the game can be stepped programmatically without keyboard input and without graphics. Do NOT implement reward shaping, PPO, training loop, or policy/model logic yet.

IMPORTANT SAFETY / CHANGE MANAGEMENT RULES:
1. Keep this step isolated and easy to revert.
2. Prefer ADDITIVE changes over destructive refactors.
3. Do NOT rewrite large parts of existing gameplay unless absolutely necessary.
4. If existing code must be touched, keep edits minimal and localized.
5. Put all new RL-specific code under:
   - src/rl/
6. If small hooks are needed in existing gameplay files, add them in a way that:
   - preserves current normal game behavior
   - does not break keyboard/manual play
   - can be removed easily later
7. Add clear comments like:
   - # RL hook
   - # RL-only path
   - # Safe to remove if RL is abandoned

REQUIRED OUTPUT FILES:
1. src/rl/env.py
2. src/rl/test_env.py

OPTIONAL HELPER FILES IF NEEDED:
- src/rl/action_map.py
- src/rl/headless.py
- src/rl/README_step1.md

IMPLEMENTATION REQUIREMENTS:

1. Create file:
   src/rl/env.py

2. Implement class:
   class DungeonEnv(gym.Env):

3. Imports:
   import gymnasium as gym
   from gymnasium import spaces
   import numpy as np

4. DungeonEnv core methods:

   - def __init__(self, render_mode=None):
       - render_mode can be:
         - None for headless
         - "human" for normal graphics
       - initialize or prepare the game using existing core logic
       - DO NOT start a normal Pygame main loop automatically
       - set:
         self.action_space = spaces.Discrete(8)
         self.observation_space = spaces.Box(
             low=0.0,
             high=1.0,
             shape=(20,),
             dtype=np.float32
         )

   - def reset(self, seed=None, options=None):
       - fully reset the run/game state
       - create a fresh run
       - return:
         observation, info
       - observation should be a temporary placeholder vector of shape (20,)
       - info should contain basic debug fields such as:
         room_index, player_hp, lives_remaining if available

   - def step(self, action):
       - apply exactly one RL action
       - advance the game by one fixed simulation tick/frame
       - DO NOT depend on real-time FPS timing
       - compute and return:
         observation
         reward = 0.0   # placeholder for now
         terminated
         truncated
         info
       - terminated should become True if:
         - player dies / run ends in defeat
         - player wins / run ends in victory
       - truncated should be False for now unless a hard safety cap is introduced
       - info should include debug data if available

   - def render(self):
       - if self.render_mode == "human":
         run normal render/draw path
       - if render_mode is None:
         do nothing

   - def close(self):
       - cleanly release any pygame resources if needed
       - should be safe to call multiple times

5. Action space:
   Use:
   self.action_space = spaces.Discrete(8)

   Map actions as:
   0 = no-op
   1 = move up
   2 = move down
   3 = move left
   4 = move right
   5 = short attack
   6 = long attack
   7 = dash

   IMPORTANT:
   - Keep action mapping centralized and easy to edit
   - If useful, create helper function or dict in src/rl/action_map.py

6. Observation space:
   For now use only a placeholder vector:
   shape=(20,), dtype=np.float32

   IMPORTANT:
   - Even if placeholder values are temporary, ensure returned observation:
     - is always numpy array
     - always matches shape exactly
     - never returns NaN
   - Add TODO comments for later real observation extraction

7. Headless mode:
   If render_mode is None:
   - DO NOT call pygame.display.update()
   - DO NOT flip the display
   - DO NOT draw UI or gameplay graphics
   - DO NOT require visible window rendering
   - skip rendering-only code

   If render_mode == "human":
   - preserve normal drawing/render behavior as much as possible

   IMPORTANT:
   - Headless mode must keep full gameplay logic active:
     walls, collisions, enemy AI, combat, damage, room progression, death, victory, etc.
   - Only graphics should be skipped, not game rules

8. Integration with current game code:
   We need a way to step gameplay logic without keyboard input.

   Preferred approach:
   - Extract or expose a function/method like:
     update_game(action)
     or
     rl_step(action)
   that:
     - applies movement/action input
     - updates player
     - updates enemies
     - handles combat
     - updates room state
     - updates progression/win/loss state

   IMPORTANT:
   - Prefer a small hook over a major rewrite
   - Reuse existing game_scene/core logic as much as possible
   - Preserve current manual gameplay path
   - The RL path should call core logic directly, not the normal infinite UI loop

9. Remove keyboard dependency only for RL path:
   - Normal manual game should still work
   - RL environment path should not read keyboard input directly
   - Instead, action passed into step() should drive behavior

10. Fixed-step requirement:
   This is very important.
   - Each env.step(action) must simulate one fixed gameplay tick/frame
   - Do NOT tie step behavior to real-world elapsed time
   - Do NOT require actual display FPS
   - Training and testing should be deterministic as much as current game logic allows

11. Test file:
   Create:
   src/rl/test_env.py

   Include a basic smoke test like:

   env = DungeonEnv(render_mode=None)
   obs, info = env.reset()

   for _ in range(100):
       action = env.action_space.sample()
       obs, reward, terminated, truncated, info = env.step(action)
       assert obs.shape == (20,)
       if terminated or truncated:
           obs, info = env.reset()

   env.close()

12. Add notes / comments for reversibility:
   In every changed existing file, add a short comment marker such as:
   - # RL hook (reversible)
   - # Added for Gymnasium wrapper support
   So these edits can be found and removed later if we abandon RL.

13. Do NOT do these things in Step 1:
   - no PPO
   - no Q-learning
   - no policy network
   - no reward shaping
   - no replay buffer
   - no checkpoint saving
   - no training script
   - no observation engineering beyond placeholder vector
   - no large architectural rewrite unless absolutely necessary

SUCCESS CRITERIA:
1. I can instantiate DungeonEnv(render_mode=None)
2. I can call reset()
3. I can call step(action) repeatedly without keyboard input
4. The environment advances game logic without graphics
5. Normal non-RL gameplay still remains intact
6. Changes are isolated and reversible if full RL is later abandoned

At the end, provide:
1. List of files created
2. List of existing files modified
3. Short explanation of how to revert RL-specific changes if needed
4. Any assumptions you had to make because of current code structure