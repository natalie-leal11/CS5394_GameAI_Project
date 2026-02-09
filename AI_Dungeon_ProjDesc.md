## Adaptive Dungeon Design with an AI Director

### Core Fantasy

The player explore procedurally generated dungeons where the dungeon acts as the opponent. Rather than relying on intelligent individual enemies, the dungeon adapts encounter pacing, pressure, and difficult throughout each run in order to challenge the player.

### Gameplay Flow Overview

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


## 1. Dungeon Generation (Pre-Gameplay)

### Overview

The dungeon is designed with a fixed-length structure to ensure consistent pacing, balanced difficulty, and controlled progression. Procedural generation is used to introduce variation within this fixed framework rather than creating entirely unpredictable layouts.

The dungeon consists of a predefined maximum number of rooms per run, ensuring that progression length remains consistent while allowing variation in room order, encounter type, and presentation.

### 1.1 Fixed Components (Not Controlled by the Seed)

The following elements are predefined and remain constant for every dungeon run:

- The total number of rooms: 30  
- The overall progression length, defined as the number of rooms the player must traverse to complete the dungeon  
- Major milestone rooms, including:  
  - The starting room  
  - One or more rest or checkpoint rooms  
  - The final boss room  

These fixed components maintain a stable difficulty curve.

### 1.2 Seed-Controlled Variation

The procedural seed introduces controlled variation within the fixed dungeon structure:

- Distribution and ordering of room types including start, combat, ambush, and special encounter rooms  
- Branching paths (total progression length remains constant)  
- The visual theme of the dungeon, including land, water, lava and environmental styling  
- Minor variations such as enemy spawn layouts and environmental details  
- Some rooms act as transitional or safe spaces, allowing pacing adjustments between combat-heavy encounters.

## 2. AI Director Monitoring (Core System)

The AI Director acts as a high-level control system for the dungeon.  
It does not control enemies directly.  
Instead, it observes player behavior and adjusts the game environment.  
The AI Director functions like a game master, shaping encounters rather than fighting.

### 2.1 Player Data Tracked

- Player health  
- Death count  
- Speed of progression  
- Recent combat outcomes  

### 2.2 Decisions Made by the AI Director

- When enemies spawn  
- How many enemies spawn  
- Enemy group composition  
- Ambush frequency  
- Healing item and safe room drop rates  

## 3. Reinforcement Learning (Parameter Tuning Layer)

Reinforcement Learning (RL) is used only for offline tuning of numerical parameters.

- The AI Director remains deterministic and rule-driven  
- RL training is performed offline using simulated gameplay runs  
- The learned policy is fixed during actual gameplay  

## 4. Enemy Behavior, Combat Flow, and Difficulty Control

Enemies in the dungeon are intentionally simple and aggressive, inspired by Hades. Challenge arises from encounter design and pacing rather than complex enemy intelligence.

Enemies do not:

- patrol  
- inspect sounds  
- hide  
- move between rooms 

Once combat starts, enemies remain in the same room until defeated.
In addition to standard enemy encounters, certain rooms introduce elite or high-pressure encounters, and the final boss encounter serves as a distinct challenge at the end of the run.

### 4.1 Enemy Types

- Melee Enemy  
- Fast Enemy  
- Heavy Enemy  
- Elite Variant

A final boss variant appears at the end of the dungeon run and represents a major milestone encounter distinct from regular and elite enemies.


## 5. Player Characterists

### 5.1 Player Attacks

- Short-range attack  
- Long-range attack  

### 5.2 Movement

- Dash / Jump  
- Block / Parry  

### 5.3 Player Stats

- Base Health: 100  
- Short attack damage: 8-12  
- Long attack damage: 15-25  
- Block reduction: 60-100% (timing based)  

## 6. Game Ending Conditions

### 6.1 Win Conditions

- Defeat the final boss  
- Complete the dungeon run  

### 6.2 Loss Conditions

- Player health reaches zero  
- Current run ends (roguelike reset)

## 7. Narrative & Story Design(Optional Enhancement)

### 7.1 Narrative Style

Minimal, atmospheric storytelling that reacts to gameplay events.

### 7.2 Story Premise

The dungeon is a sentient construct designed to test and eliminate intruders. Each run represents another attempt by the dungeon to adapt to the player.  
The AI Director represents the dungeon's will: measuring, responding, and correcting.

### 7.3 Event-Based Narrative System

Narration is triggered by deterministic events, such as:

- Entering an ambush room  
- Player health dropping below 20%  
- Clearing multiple rooms without damage  
- Ally call activation  
- Player death  

Optional LLM integration is used only to vary narrative wording, with no impact on gameplay or logic.

## 8. Graphics

The game will use 2D top-down graphics to represent dungeon rooms, enemies, and combat.
