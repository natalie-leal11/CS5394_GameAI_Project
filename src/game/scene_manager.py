# Scene lifecycle and switching. Game starts in StartScene; Main menu has Play, Controls, Settings, Quit (§2).

import pygame

from game.ai.difficulty_params import DifficultyParams, load_difficulty_params_json
from game.scenes import StartScene, GameScene, ControlsScene, SettingsScene


class SceneManager:
    def __init__(self, difficulty_params: DifficultyParams | None = None):
        self.difficulty_params: DifficultyParams = difficulty_params or load_difficulty_params_json()
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
        # RL logging: ensure session_end if leaving GameScene without a terminal row (logging only).
        if self._current is self._game_scene and self._game_scene is not None:
            fin = getattr(self._game_scene, "finalize_rl_log_on_leave", None)
            if callable(fin):
                fin()
        self._current = self._start_scene

    def switch_to_game(
        self,
        run_seed_override: int | None = None,
        rl_curriculum_scenario: str | None = None,
    ):
        # Ensure fresh run each time Play is pressed.
        # run_seed_override: RL hook (reversible) — optional seed from Gymnasium env.reset(seed=...).
        # rl_curriculum_scenario: RL-only micro-scenario (interact / safe_heal); None = full-game layout.
        if self._game_scene is not None and hasattr(self._game_scene, "reset"):
            self._game_scene.reset(
                for_new_run=True,
                run_seed_override=run_seed_override,
                rl_curriculum_scenario=rl_curriculum_scenario,
            )
        self._current = self._game_scene

    def switch_to_controls(self):
        self._current = self._controls_scene
        if hasattr(self._controls_scene, "prepare_enter"):
            self._controls_scene.prepare_enter()

    def switch_to_settings(self):
        self._current = self._settings_scene
        if hasattr(self._settings_scene, "prepare_enter"):
            self._settings_scene.prepare_enter()

    def on_app_quit(self) -> None:
        """Window close while in GameScene: optional RL session_end (logging only)."""
        if self._game_scene is not None and self._current is self._game_scene:
            if hasattr(self._game_scene, "log_session_end_on_app_quit"):
                self._game_scene.log_session_end_on_app_quit()

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
