# CRITICAL REQUIREMENTS — 01 Project Setup (Python 3.11+, Windowed Pygame)

### MANDATORY DIRECTIVE ###
You are an expert Python programmer using **Pygame**.

**CRITICAL**: Create the repo structure, dependency setup, and a minimal window that opens/closes cleanly.
Do NOT implement gameplay systems in this step.


## **MANDATORY**: OBJECTIVE 
Initialize a windowed Pygame project that runs without errors and establishes the folder structure used by later prompts.


## **MANDATORY**: FILES/FOLDERS TO CREATE OR MODIFY

Create folders:
- `src/game/`
- `src/game/core/`
- `src/game/scenes/`
- `src/game/dungeon/`
- `src/game/ai/`
- `src/game/entities/`
- `src/game/systems/`

Create/modify files:
- `requirements.txt`
- `README.md`
- `src/game/config.py`
- `src/game/rng.py`
- `src/game/main.py`


## **CRITICAL**: IMPLEMENTATION REQUIREMENTS 

### `requirements.txt`
- Must include: `pygame`

### `src/game/config.py`
- Define: `WIDTH`, `HEIGHT`, `FPS`, `TITLE`

### `src/game/rng.py`
- Implement a centralized RNG using a single internal `random.Random`
- Provide:
  - `set_seed(seed: int) -> None`
  - `randint(a: int, b: int) -> int`
  - `choice(seq)`
- **CRITICAL**: No other file may import/use `random`

### `src/game/main.py`
- Initialize pygame and create a window using `config.py`
- Run a stable loop at `FPS`
- Handle QUIT cleanly
- Fill background and call `pygame.display.flip()`


## **MANDATORY**: VERIFICATION
1. Run: `python -m src.game.main`
2. Verify:
   - [ ] Window opens with correct title
   - [ ] Window updates (not frozen)
   - [ ] Closing window exits cleanly
   - [ ] No module import errors
   - [ ] No `random` usage outside `src/game/rng.py`


### CRITICAL REMINDER ###
- Windowed Pygame only
- All randomness must be centralized in `src/game/rng.py`
- Preserve future scope: 30 fixed rooms, deterministic AI Director, room-confined enemies
