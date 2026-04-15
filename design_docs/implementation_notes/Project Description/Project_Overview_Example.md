# Project Overview

## 1. Game Concept

Our project is s **Hades-inspired procedural dungeon game** built around deterministic strcuture and controlled randomness. 

Each run is generated from a **single global seed**. This seed determines dungeon variation while preserving a fixed structural framework to maintain balance and pacing.

### Fixed Strcutural Elements (Not Controlled by Seed)

- Total number of rooms: 30
- Biome progression order
- Major milestone rooms:
    - Starting Room
    - Mini-boss Rooms
    - Final boss room

These fixed components ensure:
- Stable difficulty curve
- Predictable progression length
- Balanced gameplay pacing

### Seed-Controlled Variation

The global seed determines:
- Room type distribution (combat, ambush, safe)
- Room ordering (within structural constraints)
- Environmental themes and hazards (lava, water, etc.)
- Wall density
- Slow terrain placement 
- Spawn zones
- Minos enemy spawn patterns
- Branching path variations

#### Example:
- Seed A: Biome 1 may contain 3 combat rooms followed by an ambush room in a lava-themed layout
- Seed B: The same biome may begin with a safer layout and delay the ambush. 
However:
- Total rooms remain 30
- Mini-boss placement remains fixed
- Final boss placement remains fixed

This system combines **replayability through controlled randomness** with **deterministic balance**.

## 2. AI Director System

Once the dungeon is generated, the **AI Director** becomes active during gameplay.

The AI Director does **not** control individual enemy behavior. Instead, it adjusts encounter intensity dynamically based on player performance.

### What AI Director Tracks

- Player health
- Death count
- Speed of progression
- Recent combat outcomes

### Adaptive Behavior

If the player is performing well:
- Increase enemy count
- Increase ambush frequency
- Introduce stronger compositions
- Increase elite probability

If the player is struggling:
- Reduce enemy count
- Delay spawn timing
- Increasae safe room likelihood
- Increase healing drop bias

## 3. Responsibility Separation

### Seed Controls (Pre-Run)

- Lava percentage within defined limits
- Wall density
- Slow terrain
- Layout templates
- Spawn zones
- Room ordering

### AI Director Controls (During Run)

- Enemy count
- Spawn timing
- Reinforcement waves
- Ambush intensity
- Elite probability
- Healing bias

This separation keeps generation deterministic and runtime adaption controlled.

## 4. Reinforcement Learning (Offline Tuning)

Reinforcement Learning (RL) is used **offline only** to tune difficulty parameters.

We simulate hundreds or thousands of automated runs and log:
- Win rate
- Damage taken
- Death distribution by room
- Enemy distribution per room
- Time spent per room

### Design Principle

**RL defines the numeric parameters. The AI Director enforces them**

RL optimizes basaed on measurable metrics such as:
- Target with rate (~60%)
- Early death frequency
- Difficulty variance
- Spike detection

### Reward Function

The reward function decreases if:
- The game becomes too easy
- The game becomes too difficult
- Difficulty spikes exceed acceptable thresholds

RL adjusts numeric values such as:
- Enemy count multipliers
- Healing bias
- Reinforcement frequency

Once optional parameters are found:
- They are fixed 
- The runtime system remains deterministic

## 5. Enemy Design Philosophy

Enemies are intentionally simple and aggressive

Difficulty comes from:
- Encounter composition
- Pacing 
- Pressure stacking

Not from: 
- Complex AI
- Stealth behavior
- Patrol systems
- Room transitions

Once combat begins: 
- Enemies remain in that room until defeated. 

This keeps behavior predictable while challenge is controlled systemically.

## 6. Enemy Types

We use four core enemy types:
- **Melee** - direct pressure
- **Fast** - speed disruption
- **Heavy** - area control
- **Elite variants** - enhanced difficulty

Additional encounter:
- Mini-boss per biome
- Final boss in the final room (major milestone encounter)

## 7. Player Mechanics 

The player has a deterministic, dkill-based combat system.

### Combat

- Short-range attack (8-12 damage)
- Long-range attack (15-25 damage)
- Dash for mobility
- Block/Parry system

Block reduces damage:
- 60-100% depending on timing

### Core Stats

- Base health: 100
- No randomness in damage calculation
- All combat outcomes are deterministic

## 8. Game End Conditions

### Win condition

- Death the final boss
- Complete the 30-room dungeon

### Loss condition

- Health reaches zero 
- Run resets (roguelike structure)

## 9. Optional LLM Narrative Layer

An optional LLM generates short narrative text during specific gameplay events, such as:
- Low health
- Entering an ambush
- Boss encounters

The LLM:
- Affects storytelling only
- Has no impact on mechanics or difficulty 

## 10. Graphics & Technical Stack

- 2D top-down perspective
- Built with Pygame
- Simple visual clarity prioritizing gameplay readability