# System Statechart Diagrams

This folder contains Mermaid statecharts for core runtime systems in Adaptive Dungeon.

## Files

- `master_system_statechart.md` - Consolidated high-level statechart across scenes, gameplay, AI adaptation, and RL episode control.
- `scene_and_gameplay_statechart.md` - SceneManager navigation and GameScene runtime states.
- `ai_director_statechart.md` - Player model and AI Director state transitions.
- `rl_episode_statechart.md` - Gymnasium RL episode lifecycle and terminal handling.

## Notes

- Diagrams are aligned to current implementation under `src/game/` and `src/rl/`.
- Mermaid rendering is supported by most Markdown viewers and GitHub.
