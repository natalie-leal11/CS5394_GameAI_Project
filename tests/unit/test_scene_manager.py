"""Unit tests for SceneManager using lightweight mock scenes."""

from __future__ import annotations

import pytest

from game.scene_manager import SceneManager


class MockScene:
    """Minimal scene matching SceneManager's update/draw/handle_event usage."""

    def __init__(self, label: str = "mock") -> None:
        self.label = label
        self.update_called = 0
        self.last_dt: float | None = None

    def update(self, dt: float) -> None:
        self.update_called += 1
        self.last_dt = dt

    def draw(self, screen, camera_offset=None) -> None:
        pass

    def handle_event(self, event):
        return False


def test_only_one_scene_updates_per_frame():
    sm = SceneManager()
    scene = MockScene("active")
    sm._current = scene

    sm.update(1.0 / 60.0)

    assert scene.update_called == 1
    assert scene.last_dt == pytest.approx(1.0 / 60.0)


def test_double_transition_second_ignored_or_queued_documented():
    """
    Transitions are synchronous: the last switch_* call sets ``_current``.
    There is no queue; the second request replaces the first before any update.
    A single ``update`` tick runs exactly one scene ``update`` — the current one only.
    """
    sm = SceneManager()
    controls = MockScene("controls")
    settings = MockScene("settings")
    sm._controls_scene = controls
    sm._settings_scene = settings
    sm._start_scene = MockScene("start")
    sm._game_scene = MockScene("game")

    sm.switch_to_controls()
    assert sm.current is controls

    sm.switch_to_settings()
    assert sm.current is settings

    assert controls.update_called == 0
    assert settings.update_called == 0

    sm.update(0.016)
    assert settings.update_called == 1
    assert controls.update_called == 0

    sm.update(0.016)
    assert settings.update_called == 2
    assert controls.update_called == 0
