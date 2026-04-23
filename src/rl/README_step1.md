# Step 1: Gymnasium `DungeonEnv` (headless stepping)



## Run smoke test



From the project root (directory containing `assets/`):



```bash

set PYTHONPATH=src

python -m rl.test_env

```



PowerShell:



```powershell

$env:PYTHONPATH="src"

python -m rl.test_env

```



## Dependencies



Install `gymnasium` and `numpy` (see `requirements.txt`).



## Design



- `DungeonEnv` lives in `src/rl/` and does **not** start the normal `main.py` loop.

- Each `step()` advances the game by one fixed tick (`1/FPS` seconds from `game.config`).

- `GameScene` exposes `_rl_controlled` / `_rl_action` / `_rl_skip_draw` hooks (see `# RL hook` comments).

- Headless mode skips `GameScene.draw()` and the env does not flip the display; gameplay logic still runs.



## Action space (`Discrete(17)`)



One discrete action per frame; mapping is centralized in `src/rl/action_map.py`.



| Index | Meaning |

|------:|---------|

| 0 | no-op |

| 1 | move up (W) |

| 2 | move down (S) |

| 3 | move left (A) |

| 4 | move right (D) |

| 5 | short attack (LMB-equivalent) |

| 6 | long attack (RMB-equivalent) |

| 7 | dash (Space-equivalent) |

| 8 | block (hold J-equivalent for this frame) |

| 9 | parry (K tap-equivalent for this frame) |

| 10 | interact (E — Room 0 altar / close story panel; same `handle_event` path as manual) |

| 11 | safe-room heal (F — collect safe-room heal when near prompt) |

| 12 | reserve heal (H — same as manual reserve heal) |

| 13 | safe-room choice 1 (keyboard `1`) |

| 14 | safe-room choice 2 (`2`) |

| 15 | safe-room choice 3 (`3`) |

| 16 | safe-room choice 4 (`4`) |



To **sustain block**, the policy must repeat action `8` on consecutive frames (same idea as holding `J` in manual play). Parry is a one-shot request per frame when action `9` is chosen.



Interaction actions **10–16** are dispatched as synthetic `KEYDOWN` events through `GameScene.handle_event`, matching manual play (no parallel gameplay logic).



## Revert



Remove the `src/rl/` package and undo edits marked `# RL hook (reversible)` in `game_scene.py` and `scene_manager.py`.

