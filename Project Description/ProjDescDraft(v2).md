Core Fantasy: The player explore procedurally generated dungeons where the dungeon acts as the opponent. Rather than relying on intelligent individual enemies, the dungeon adapts 
encounter pacing, pressure, and difficult throughout each run in order to challenge the player.

Gameplay Flow Overview

Start Game
   ↓
Procedural Dungeon Generation
   ↓
Player Enters Dungeon
   ↓
AI Director Monitors Player Performance
   ↓
Enemies Spawn & Act (Enemy AI Stack)
   ↓
Dynamic Difficulty Adjustment
   ↓
Repeat Until Game Ends

1. Dungeon Generation(Pre-Gameplay):

Overview:
The dungeon is designed with a fixed-length structure to ensure consistent pacing, balanced difficulty, and controlled progression. Procedural generation is used to introduce variation within this fixed framework rather than creating entirely unpredictable layouts. 

1.1 Fixed Components (Not Controlled by the Seed):
The following elements are predefined and remain constant for every dungeon run:
-The total number of rooms: 30
-The overall progression length, defined as the number of rooms the player must traverse to complete the dungeon
-Major milestone rooms, including:
   -The starting room
   -One or more rest or checkpoint rooms
   -The final boss room
These fixed components maintain a stable difficulty curve.

1.2 Seed-Controlled Variation:
The procedural seed introduces controlled variation within the fixed dungeon structure:
-Distribution and ordering of room types including start, combat, ambush, etc.
-Branching paths (total progression length remains constant)
-The visual theme of the dungeon, including land, water, lava and environmental styling
-Minor variations such as enemy spawn layouts and environmental details.

2. AI Director Monitoring (Core System):
The AI Director acts as a high-level control system for the dungeon.
It does not control enemies directly.
Instead, it observes player behavior and adjusts the game environment.
The AI Director functions like a game master, shaping encounters rather than fighting.

2.1 Player Data Tracked:
   - Player health
   - Death count
   - Speed of progression
   - Recent combat outcomes
    
2.2 Decisions Made by the AI Director
   - When enemies spawn
   - How many enemies spawn
   - Enemy group composition
   - Ambush frequency
   - Healing item and safe room drop rates
    
    
3 Reinforcement Learning (Parameter Tuning Layer):
Reinforcement Learning (RL) is used only for offline tuning of numerical parameters.
-The AI Director remains deterministic and rule-driven.
-RL training is performed offline using simulated gameplay runs
-The learned policy is fixed during actual gameplay.
3.1 Tuned Parameters:
    -Enemy spawn rate (±10-30%)
    -Ambush probability (±5–15%)
    -Enemy group size or strength scaling
    -Healing item and rest room drop frequency (±5-10%)
-All parameter changes are bounded within predefined limits, and rule-based constraints always override RL outputs to prevent unfair or unstable difficulty changes.

3.2 RL Training Details:

   3.2.1 RL Observations(State):
   -Average player health
   -Death count
   -Speed of progression (rooms cleared per minute)
   
   3.2.2 RL Adjustments (Actions):
   The RL agent adjusts only predefined, safe parameters.
   
   3.2.3 RL Feedback (Reward):
   The RL agent is rewarded when the player survives and progresses smoothly, and penalized when the player dies repeatedly, gets stuck, or experiences sudden difficulty spikes. This encourages gradual and balanced difficulty tuning.

3.3 Gameplay Data Logging:
Gameplay metrics, difficulty adjustments, and outcomes are logged after each game run.
Logged data may be used for offline analysis and for future RL tuning, without affecting live gameplay.

4. Enemy Behavior, Combat Flow, and Difficulty Control:
Enemies in the dungeon are intentionally simple and aggressive, inspired by Hades. Challenge arises from encounter design and pacing rather than complex enemy intelligence. 

Enemies do not:
- patrol 
- inspect sounds
- hide
- move between rooms.
Once combat starts, enemies remain in the same room until defeated.

4.1 Enemy Types
- Melee Enemy: Close-range pressure: high health, low damage
- Fast Enemy: Mobile flanker
- Heavy Enemy: Slow, high health, area attacks
- Elite Variante: Enhanced versions with higher stats or abilities

4.2 Enemy Scaling 
Enemy strength scales with dungeon depth:
- Health: +10-15% per tier
- Damage: +8-12% per tier

4.3 Enemy characterists
- Health
- Armor
- Movement speed
- Agression level
- Awareness radius (room-limited)

4.4 Enemy Attacks
- Melee damage: 6-12 per hit
- Ranged damageL: 10-18 per hit
- Elite abilites:
   - Area slams
   - Rapid multi-hit attacks


4.5 Enemy States (Simplified State Machine):
Each enemy is always in one simple state:
- Idle / Guarding
Standing idle or safeguarding treasure or a fixed location. Activated when the player enters the room

- Ambush
Enemy attacks the player unexpectedly upon room entry. Immediately transitions into Combat

- Combat
Enemy actively fights using basic attacks and movement. This is the primary state during encounters

- Fallback (Short Pull-Back)
A brief step back during combat, used only to reposition or call allies. Enemy stays in the same room and quickly returns to Combat

- Dead
Enemy is defeated and removed from the encounter

4.6 Enemy Spawn and Encounter Control:
When the player enters a room, the AI Director evaluates:
-Room type (combat, ambush, safe)
-Current intensity level
-Player performance (health, deaths, progression speed)

Based on this evaluation, the AI Director determines:
-No enemies (safe room)
-Normal combat encounter
-Ambush encounter
-Reinforced enemies (larger or stronger groups)

4.7 Calling Allies (Rare and Controlled):
- Global limit: 3 times per run
- Triggered when: 
   - Enemy is near defeat
   - Encounter intensity is high
- Results in the addition of:
   - A small group of enemies or
   - One stronger enemy

4.8 Movement Logic
Enemy movement uses A* pathfinding with weighted terrain.
Enemies use movement only to:
-Approach the player
-Flank within the room
-Briefly reposition during fallback
-Enemies may block exits or cut off escape paths within the same room only.

4.9 Dynamic Difficulty Adjustment (Invisible):
During or after encounters, the AI Director adjusts difficulty based on player performance.

If the player is doing well:
- Enemies coordinate more effectively
- Ambush frequency increases
- Healing drops are reduced

If the player is struggling:
- Enemy spawns slow down
- More safe or rest rooms appear
- Enemy aggression is reduced

All adjustments are gradual and invisible, ensuring fair and natural gameplay.

5. Player Characterists

5.1 Player Attacks
- Short-range attack: Fast, low, damage, crowd control
- Long-range attack: Slower, higher damage, cooldown-limited

5.2 Movement
- Dash / Jump: Avoid attacks and cross hazards
- Block / Parry: Reduced or negates damage; perfect timing grants bonuses.

5.3 Player Stats
- Base Health: 100
- Short attack damage: 8-12
- Long attack damage: 15-25
- Block reduction: 60-100% (timing based)

6. Game Ending Conditions

6.1 Win Conditions
- Defeat the final boss
- Complete th edungone run

6.2 Loss Conditions
- Player health reaches zero
- Current run ends (roguelike reset)

7. Narrative & Story Design:
 
 7.1 Narrative Style
 Minimal, atmospheric storytelling that reacts to gameplay events

 7.2 Story Premise
 The dungeon is a sentient construct designed to test and eliminate intruders. Each run represents another attempt by the dungeon to adapt to the player. 
 The AI Director represents the dungeon's will: measuring, responding, and correcting.

 7.3 Event-Based Narrative System
 Narration is triggered by deterministic events, such as:
 - Entering an ambush room
 - Player health dropping below 20%
 - Clearing multiple rooms without damage
 - Ally call activation
 - Player death
 Optional LLM integration is used only to vary narrative wording, with no impact on gameplay or logic

8. Graphics:
The game will use 2D top-down graphics to represent dungeon rooms, enemies, and combat