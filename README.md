# Adaptive Dungeon

A top-down 2D tile-based dungeon game built with Python and Pygame.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python -m src.game.main
```

## Structure

- `src/game/` — main game entry and config
- `src/game/core/` — core utilities
- `src/game/scenes/` — menu, run, end scenes
- `src/game/dungeon/` — dungeon generation and rooms
- `src/game/ai/` — AI Director and difficulty
- `src/game/entities/` — player and enemies
- `src/game/systems/` — combat, hazards, etc.

All randomness is centralized in `src/game/rng.py`.
