# Adaptive Dungeon

A top-down 2D tile-based dungeon game built with Python and Pygame, featuring procedural generation, dynamic difficulty adjustment, and reinforcement learning integration.

---

## Overview

Adaptive Dungeon is a **30-room dungeon crawler** divided into 4 biomes. The game combines:

- **Seed-controlled procedural generation** for deterministic and replayable runs  
- **AI Director** for adaptive difficulty based on player performance  
- **Reinforcement Learning (RL)** for agent training, evaluation, and behavioral analysis  

Each run maintains structural consistency while allowing controlled variation in encounters and gameplay dynamics.

---

## Key Systems

### AI Director
Adjusts encounter difficulty dynamically using a player state model:
- **DOMINATING**
- **STABLE**
- **STRUGGLING**

The director modifies enemy composition, pressure, and encounter pacing while respecting strict gameplay bounds.

---

### Seed-Controlled Variation
All procedural elements are driven by a run seed:
- Room ordering within biome constraints  
- Enemy composition and counts  
- Spawn patterns and positions  
- Hazard placement  

Same seed → identical run  
Different seed → controlled variation

---

### Reinforcement Learning (RL)
Includes a Gym-compatible environment for training agents:

- PPO-based curriculum training  
- Structured reward system  
- Offline dataset export and evaluation  
- Deterministic environment for reproducibility  

---

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python -m src.game.main
```

## RL Training 
```bash 
cd src
python -m rl.train_curriculum_ppo --scenario interact
```

## Project Structure

- `src/game/` — main game entry and config
- `src/game/core/` — core utilities
- `src/game/scenes/` — menu, run, end scenes
- `src/game/dungeon/` — dungeon generation and rooms
- `src/game/ai/` — AI Director and difficulty
- `src/game/entities/` — player and enemies
- `src/game/systems/` — combat, hazards, etc.

## Logging & Determinism
Seed-based debug logs are generated automatically for each run:
    - `logs/seed_run_<timestamp>.txt`
    - `logs/phase1_seed_debug.txt`
These logs verify deterministic behavior, including room senquencing, biome structure, and encounter generation.
Same seeda and input sequence will produce identical runs.

All randomness is centralized in `src/game/rng.py`.
