# Scene lifecycle and switching. Game starts in StartScene; Main menu has Play, Controls, Settings, Quit (§2).

import pygame

from game.scenes import StartScene, GameScene, ControlsScene, SettingsScene


class SceneManager:
    def __init__(self):
        self._current = None
        self._game_scene = None
        self._start_scene = None
        self._controls_scene = None
        self._settings_scene = None

    def init(self):
        """Create and set initial scene to StartScene (main menu)."""
        self._game_scene = GameScene(self)
        self._start_scene = StartScene(self)
        self._controls_scene = ControlsScene(self)
        self._settings_scene = SettingsScene(self)
        self.switch_to_start()

    def switch_to_start(self):
        self._current = self._start_scene

    def switch_to_game(self):
        # Ensure fresh run each time Play is pressed.
        if self._game_scene is not None and hasattr(self._game_scene, "reset"):
            self._game_scene.reset()
        self._current = self._game_scene

    def switch_to_controls(self):
        self._current = self._controls_scene
        if hasattr(self._controls_scene, "prepare_enter"):
            self._controls_scene.prepare_enter()

    def switch_to_settings(self):
        self._current = self._settings_scene
        if hasattr(self._settings_scene, "prepare_enter"):
            self._settings_scene.prepare_enter()

    @property
    def current(self):
        return self._current

    def update(self, dt: float) -> None:
        if self._current is not None:
            self._current.update(dt)

    def draw(self, screen: pygame.Surface, camera_offset: tuple[float, float] | None = None) -> None:
        if self._current is not None:
            self._current.draw(screen, camera_offset)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if self._current is not None:
            return self._current.handle_event(event)
        return False
