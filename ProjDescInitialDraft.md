Core Fantasy: You explore procedurally generated dungeons where the dungeon acts as an opponent. It adapts 
encounters and pacing to challenge you throughout the run.

Step-by-Step: How the Game Actually Works
Start Game
   ↓
Procedural Dungeon Generation
   ↓
Player Enters Dungeon
   ↓
AI Director Monitors Player
   ↓
Enemies Spawn & Act (Enemy AI Stack)
   ↓
Dynamic Difficulty Adjustment
   ↓
Repeat Until Game Ends

1. Dungeon Generation(Before Gameplay Starts):
Overview:
The dungeon is designed with a fixed-length structure to ensure consistent pacing and controlled progression across each run.

1.1 Fixed Components (Not Controlled by the Seed):
The following elements are predefined and remain constant for every dungeon run:
-The total number of rooms (e.g., 20–30 rooms)
-The overall progression length, defined as the number of rooms the player must traverse to complete the dungeon
-Major milestone rooms, including:
   -The starting room
   -One or more rest or checkpoint rooms
   -The final or boss room
These components are fixed to maintain a stable difficulty curve and predictable game flow.

1.2 Seed-Controlled Variation:
The procedural seed is used exclusively to introduce controlled variation within the fixed dungeon structure:
-The distribution of room types, such as:
    Combat arenas
    Ambush zones
    Safe or rest rooms
-The ordering and branching of rooms within the dungeon
-The visual theme of the dungeon, including land, water, lava and environmental styling
-Minor variations such as enemy spawn layouts and environmental details.

2. AI Director Monitoring (Core System):
The AI Director acts as a high-level control system for the dungeon.
It does not control enemies directly.
Instead, it observes player behavior and adjusts the game environment.
The AI Director functions like a game master, shaping encounters rather than fighting.
2.1 Data Tracked by the AI Director:
    Player health
    Death count
    Speed of progression
    Recent combat outcomes
    Decisions Made by the AI Director
    When enemies spawn
    How many enemies spawn
    Enemy group composition
    Ambush frequency
    Drop rates (healing items, rest rooms)

2.2 Reinforcement Learning (Tuning Layer):
Reinforcement Learning (RL) is used only to tune numerical parameters of the rule-based AI Director.
-The AI Director itself remains deterministic and rule-driven.
-RL tuning is performed offline using simulated gameplay runs, and the learned policy is fixed during actual gameplay.
-RL adjusts parameters such as:
    -Enemy spawn rate (e.g., increase or decrease by a small percentage)
    -Ambush probability (e.g., ±5–15%)
    -Enemy group size or strength scaling
    -Healing item and rest room drop frequency
-All parameter changes are bounded within predefined limits, and rule-based constraints always override RL outputs to prevent unfair or unstable difficulty changes.

2.3 Gameplay Data Logging:
Gameplay metrics, difficulty adjustments, and outcomes are logged after each game run.
Logged data may be used for offline analysis and for future RL tuning, without affecting live gameplay.

3. Reinforcement Learning (RL)-Parameter Tuning Overview:

3.1 RL Observations(State):
During simulated gameplay runs, the RL agent observes player performance metrics such as:
-Average player health
-Death count
-Speed of progression (rooms cleared per minute)
These metrics together form the state.

3.2 RL Adjustments (Actions):
The RL agent adjusts only predefined, safe parameters, including:
Enemy spawn rate (e.g., ±10–30%)
Ambush probability (e.g., ±5–10%)
Healing item and rest room drop frequency (e.g., ±5–10%)
All adjustments are bounded by rule-based limits

3.3 RL Feedback (Reward):
The RL agent is rewarded when the player survives and progresses smoothly, and penalized when the player dies repeatedly, gets stuck, or experiences sudden difficulty spikes. This encourages gradual and balanced difficulty tuning.

3.4 RL Policy and Gameplay Use:
The learned policy is fixed after offline training and used only to tune parameters during gameplay. The AI Director remains rule-based and deterministic, ensuring stable, predictable, and explainable behavior.

4. Enemy Behavior, Combat Flow, and Difficulty Control:
Enemies in the dungeon are intentionally simple and aggressive, inspired by Hades.
Enemies do not patrol, do not inspect sounds, do not hide, and do not move between rooms.
Once combat starts, enemies remain in the same room and fight until defeated.

4.1 Enemy States (Simplified State Machine):
Each enemy is always in one simple state:
Idle / Guarding
Standing idle or safeguarding treasure or a fixed location. Activated when the player enters the room

Ambush
Enemy attacks the player unexpectedly upon room entry. Immediately transitions into Combat

Combat
Enemy actively fights using basic attacks and movement. This is the primary state during encounters

Fallback (Short Pull-Back)
A brief step back during combat, used only to reposition or call allies. Enemy stays in the same room and quickly returns to Combat

Dead
Enemy is defeated and removed from the encounter

4.2 Enemy Spawn and Encounter Control:
When the player enters a room, the AI Director evaluates:
-Room type (combat, ambush, safe)
-Current intensity level
-Player performance (health, deaths, progression speed)

Based on this evaluation, the AI Director determines:
-No enemies (safe room)
-Normal combat encounter
-Ambush encounter
-Reinforced enemies (larger or stronger groups)

4.3 Combat Behavior (Rule-Based):
During combat, enemies make simple rule-based decisions, such as:
-Attack directly
-Flank the player
-Briefly move back (fallback) to reposition or call allies

Enemies do not:
-Take cover
-Hide behind objects
-Leave the room
-Disengage permanently

4.4 Calling Allies (Rare and Controlled):
-Calling allies is a rare event across an entire game run.
-Enemies may call allies only a limited number of times (e.g., 2–3 times per run).

When allies are called:
A small number of additional enemies may join, or One stronger enemy may appear

Ally calls usually occur when:
An enemy is close to being defeated. Combat intensity is already high

4.5 Movement Logic
Enemy movement uses A* pathfinding with weighted terrain.
Enemies use movement only to:
-Approach the player
-Flank within the room
-Briefly reposition during fallback
-Enemies may block exits or cut off escape paths within the same room only.

4.6 Dynamic Difficulty Adjustment (Invisible):
During or after encounters, the AI Director adjusts difficulty based on player performance.

If the player is doing well:
Enemies coordinate more effectively
Ambush frequency increases
Healing drops are reduced

If the player is struggling:
Enemy spawns slow down
More safe or rest rooms appear
Enemy aggression is reduced
All adjustments are gradual and invisible, ensuring fair and natural gameplay.

4.7 Design Intent:
Enemies themselves are not smart.
Challenge comes from:
Enemy numbers
Encounter timing
Rare reinforcements
Overall pacing
-The dungeon adapts, not individual enemies.

5. Event-Based Narration Using Fixed Tickers + LLM(Optional):
The game defines fixed event tickers (e.g., ambush, low health, player dominating) to decide when narration should appear. Instead of displaying static text, the event is sent to an LLM, which generates a short narrative line. This keeps gameplay logic fully deterministic, while the LLM is used only to vary wording and enhance immersion, with no impact on game mechanics.

6. Graphics:
The game will use 2D top-down graphics to represent dungeon rooms, enemies, and combat
