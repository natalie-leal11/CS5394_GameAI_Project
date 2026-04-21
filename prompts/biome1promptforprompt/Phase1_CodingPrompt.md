# Phase 1 — Incremental Coding Prompt
# Core Engine + Asset Loader + StartScene + Scene Manager + Camera Baseline

Implement **only** the following. Do not add player movement, enemies, combat, dungeon, or any later-phase features. Stop when this phase is complete.

---

## 1. Scope

- **Phase 1 deliverables:** Core engine loop, centralized asset loader, StartScene (title screen), scene manager, and camera baseline (world vs screen space).
- **Source of truth:** Requirements_Analysis_Biome1.md and the master prompt (promptForpromptDungeon-v1.md). Use exact asset paths from the Requirements; do not invent paths.
- **Architecture:** Place files under `src/game/` as in the master prompt. No monolithic single file.

---

## 2. config.py

- Add `src/game/config.py` with:
  - `SEED = 42`
  - `LOGICAL_W = 960`, `LOGICAL_H = 640` (fixed logical resolution; do not auto-size)
  - `FPS = 60`, `TILE_SIZE = 32`
  - `BACKGROUND_COLOR = (18, 18, 18)`
  - `ASSETS_ROOT` and `PLACEHOLDER_IMAGE = "assets/placeholders/missing.png"`
  - Optional: sprite size constants (e.g. player 64×64, mini_boss 96×96) for later use.
- Do not hardcode gameplay values elsewhere; centralize in config.

---

## 3. asset_loader.py

- Add `src/game/asset_loader.py` as the **single canonical API** for loading images and animations. No other code may call `pygame.image.load` directly.
- **Initialization order:** All loading that uses `convert_alpha()` must happen **after** `pygame.display.set_mode()` has been called (e.g. in main after set_mode, then load assets or load on first use in a scene).
- **API:**
  - `load_image(path, size=None, use_colorkey=False)` → returns a `pygame.Surface`. Scale at load time if `size` is given; preserve aspect ratio (no non-uniform stretch).
  - `load_animation(folder_path, size=None, use_colorkey=False)` → returns a list of surfaces (frames). Use **natural sort** for frame filenames (e.g. frame_01, frame_02, …, frame_10), not lexicographic (0, 1, 10, 2).
- **Missing assets:** If a path fails to load, try `assets/placeholders/missing.png`. If that also fails, create a small placeholder surface (e.g. gray rect) so the game **never crashes** on a missing asset. Placeholder must use `convert_alpha()`.
- **Pipeline:** load → convert_alpha() → (optional colorkey) → scale. Do not apply colorkey after scaling. Centralize any colorkey/speckle handling in this module.
- **Debug (optional):** If a debug flag in config is set, log loaded frame paths and resulting scaled sizes.

---

## 4. logger.py

- Add `src/game/logger.py` as a stub: e.g. `init_logger(log_path)`, `log_line(line)`, and optionally `debug(msg)`. No RL events yet; Phase 8 will add JSONL hooks. Game must not crash if logging is unavailable.

---

## 5. Scene manager and scenes

- **Scene manager:** Add `src/game/scene_manager.py` that:
  - Holds the current scene (StartScene or GameScene).
  - Provides `switch_to_start()` and `switch_to_game()`.
  - Delegates `update(dt)`, `draw(screen, camera_offset)`, and `handle_event(event)` to the current scene.
- **Base scene:** Add a base scene type (e.g. in `src/game/scenes/base_scene.py`) with methods: `update(dt)`, `draw(screen, camera_offset)`, `handle_event(event)`.
- **StartScene (title screen):**
  - Game **must** start in this scene. If StartScene is missing, the implementation does not satisfy the requirement.
  - Draw a title screen: background (use `assets/backgrounds/main_menu_bg.png` per Requirements if present; otherwise use placeholder), and text such as “Press Enter to play” and “Esc to quit”. Use screen-space only (no camera offset).
  - **Enter (or KP_Enter):** switch to GameScene.
  - **Esc:** quit the application (post QUIT or set running = false).
- **GameScene (camera baseline only):**
  - No player entity yet. Maintain a camera target in world space (e.g. a pair `(world_x, world_y)` or a placeholder at `(LOGICAL_W/2, LOGICAL_H/2)`).
  - **Camera formula:** `camera_offset = camera_target_world - (LOGICAL_W/2, LOGICAL_H/2)`. All world-space draw positions use `draw_pos = world_pos - camera_offset`. UI is drawn in screen-space only (no camera offset).
  - Each frame: clear screen with `screen.fill((18, 18, 18))`, then draw the current scene. GameScene may draw a simple placeholder (e.g. a small rect at world center) to verify the camera; no tiles, enemies, or player yet.

---

## 6. main.py and boot order

- **Entry point:** `src/game/main.py`.
- **Order:**
  1. `random.seed(SEED)` (from config).
  2. `pygame.init()`.
  3. `pygame.display.set_mode((LOGICAL_W, LOGICAL_H))`.
  4. Only after this, load assets (or allow scenes to load on first draw).
  5. Create scene manager and set initial scene to **StartScene**.
- **Main loop:**
  - At the **start** of each frame: `screen.fill((18, 18, 18))`.
  - Get `camera_offset` from the current scene when it is GameScene (e.g. from `camera_target_world`); for StartScene use (0, 0) or equivalent for UI-only.
  - Call current scene’s `update(dt)` then `draw(screen, camera_offset)`.
  - Use a clock at 60 FPS.
- Handle QUIT and Esc (if not already handled in StartScene) so the game exits cleanly.

---

## 7. Checklist (satisfy before considering Phase 1 done)

- [ ] Display is initialized with `set_mode` before any `convert_alpha()`.
- [ ] Game starts in StartScene (title screen).
- [ ] Press Enter → switch to GameScene; Press Esc → quit.
- [ ] Screen is cleared every frame with `(18, 18, 18)`.
- [ ] World-space vs screen-space separation is in place: `draw_pos = world_pos - camera_offset`; UI in screen-space only.
- [ ] Camera baseline: `camera_offset = camera_target_world - (LOGICAL_W/2, LOGICAL_H/2)` (GameScene).
- [ ] All image/animation loading goes through `asset_loader.py` (no direct `pygame.image.load` elsewhere).
- [ ] Missing asset → placeholder path → generated placeholder surface; game does not crash.
- [ ] Animation frames are naturally sorted.
- [ ] No Phase 2+ content (no player controller, no enemies, no combat, no dungeon).

---

**Stop after Phase 1. Wait for user confirmation before proceeding to Phase 2.**
