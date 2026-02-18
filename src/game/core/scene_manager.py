"""
Scene manager: owns the active scene and handles Menu → Run → End navigation.
"""
from typing import Any, Optional

import pygame

from src.game import config
from src.game.scenes.base_scene import BaseScene
from src.game.scenes.menu_scene import MenuScene
from src.game.scenes.run_scene import RunScene
from src.game.scenes.end_scene import EndScene


class SceneManager:
    """Owns the active scene and dispatches events, update, and render."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self._scenes: dict[str, BaseScene] = {}
        self._current_id: str = "menu"
        self._quit_requested = False
        self.run_result: Optional[bool] = None  # True=win, False=loss, None=not set

        menu = MenuScene(self)
        run = RunScene(self)
        end = EndScene(self)
        self._scenes["menu"] = menu
        self._scenes["run"] = run
        self._scenes["end"] = end

    @property
    def current_scene(self) -> BaseScene:
        return self._scenes[self._current_id]

    def switch_to(self, scene_id: str) -> None:
        if scene_id == "quit":
            self._quit_requested = True
            return
        if scene_id in self._scenes:
            self._current_id = scene_id
            scene = self._scenes[scene_id]
            if hasattr(scene, "on_enter") and callable(getattr(scene, "on_enter")):
                scene.on_enter()

    def quit_requested(self) -> bool:
        return self._quit_requested

    def handle_event(self, event: pygame.event.Event) -> None:
        self.current_scene.handle_event(event)

    def update(self, dt: float) -> None:
        self.current_scene.update(dt)

    def render(self) -> None:
        self.current_scene.render(self.screen)
