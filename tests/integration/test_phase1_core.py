import importlib

import pygame

from game.config import (
    SEED,
    LOGICAL_W,
    LOGICAL_H,
    FPS,
    TILE_SIZE,
    BACKGROUND_COLOR,
    PLACEHOLDER_IMAGE,
    PROJECT_ROOT,
)
from game.scene_manager import SceneManager
from game.scenes.start_scene import StartScene
from game.scenes.game_scene import GameScene
from game.scenes.controls_scene import ControlsScene
from game.scenes.settings_scene import SettingsScene

# Display required for load_image/load_animation (convert_alpha).
pygame.init()
pygame.display.set_mode((1, 1))


def test_config_basics():
    """Core constants for Phase 1 are correctly set."""
    assert SEED == 42
    assert LOGICAL_W == 960
    assert LOGICAL_H == 640
    assert FPS == 60
    assert TILE_SIZE == 32
    assert BACKGROUND_COLOR == (18, 18, 18)
    assert PLACEHOLDER_IMAGE.endswith("assets/placeholders/missing.png")


def test_scene_manager_starts_in_start_scene():
    """Scene manager boots into StartScene and has a GameScene ready."""
    sm = SceneManager()
    sm.init()
    assert isinstance(sm.current, StartScene)
    # GameScene should also be constructed during init()
    assert isinstance(getattr(sm, "_game_scene", None), GameScene)


def test_asset_loader_api_exists():
    """Asset loader exposes the expected Phase 1 API."""
    asset_loader = importlib.import_module("game.asset_loader")
    assert hasattr(asset_loader, "load_image")
    assert hasattr(asset_loader, "load_animation")


def test_main_module_has_entrypoint():
    """main.py defines a callable main() entrypoint."""
    main_mod = importlib.import_module("game.main")
    assert hasattr(main_mod, "main")
    assert callable(main_mod.main)


def test_asset_loader_missing_file_returns_surface():
    """Load_image with non-existent path returns a surface (placeholder or made), does not crash."""
    from game.asset_loader import load_image
    surf = load_image("nonexistent/path/fake_asset_xyz.png")
    assert surf is not None
    assert hasattr(surf, "get_size")
    w, h = surf.get_size()
    assert w > 0 and h > 0


def test_asset_loader_load_image_scales_to_size():
    """Load_image with size=(w,h) and exact_size=True returns surface of that size."""
    from game.asset_loader import load_image
    # Use an existing asset if present; otherwise missing path still yields placeholder with size
    surf = load_image("assets/ui/buttons/btn_play.png", size=(100, 50), exact_size=True)
    assert surf is not None
    assert surf.get_size() == (100, 50)


def test_scene_manager_switch_to_controls():
    """switch_to_controls() sets current to ControlsScene."""
    sm = SceneManager()
    sm.init()
    sm.switch_to_controls()
    assert isinstance(sm.current, ControlsScene)


def test_scene_manager_switch_to_settings():
    """switch_to_settings() sets current to SettingsScene."""
    sm = SceneManager()
    sm.init()
    sm.switch_to_settings()
    assert isinstance(sm.current, SettingsScene)


def test_scene_manager_switch_to_game_then_start():
    """switch_to_game() then switch_to_start() returns to StartScene."""
    sm = SceneManager()
    sm.init()
    sm.switch_to_game()
    assert isinstance(sm.current, GameScene)
    sm.switch_to_start()
    assert isinstance(sm.current, StartScene)

