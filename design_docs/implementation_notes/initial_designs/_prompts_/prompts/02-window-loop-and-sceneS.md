# CRITICAL REQUIREMENTS — 02 Window Loop and Scene System

### MANDATORY DIRECTIVE ###
You are an expert Python programmer using **Pygame**.

**CRITICAL**: Implement a scene-based game loop. Do NOT add gameplay systems.


## **MANDATORY**: OBJECTIVE
Create a deterministic scene system supporting Menu → Run → End navigation.


## **MANDATORY**: FILES TO CREATE OR MODIFY 

- `src/game/core/scene_manager.py`
- `src/game/scenes/base_scene.py`
- `src/game/scenes/menu_scene.py`
- `src/game/scenes/run_scene.py`
- `src/game/scenes/end_scene.py`
- `src/game/main.py`


## **CRITICAL**: IMPLEMENTATION REQUIREMENTS

- SceneManager owns the active scene
- Each scene implements: `handle_event`, `update`, `render`
- Menu scene:
  - ENTER → Run
  - ESC → Quit
- Run scene (placeholder):
  - Q → Defeat
  - E → Victory
- End scene:
  - R → Menu


## **MANDATORY**: VERIFICATION 

1. Run `python -m src.game.main`
2. Verify:
   - [ ] Menu appears on launch
   - [ ] ENTER starts Run scene
   - [ ] Q/E go to End scene
   - [ ] R returns to Menu


### CRITICAL REMINDER ###
- No gameplay logic yet
- Deterministic control flow only
