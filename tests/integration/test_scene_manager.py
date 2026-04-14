"""Prompt 35: Scene manager."""

from __future__ import annotations

from game.scene_manager import SceneManager


class _MockScene:
    def __init__(self) -> None:
        self.update_called = 0

    def update(self, dt: float) -> None:
        self.update_called += 1

    def draw(self, screen, camera_offset=None) -> None:
        pass

    def handle_event(self, event):
        return False


def test_only_one_scene_updates_per_frame():
    sm = SceneManager()
    sc = _MockScene()
    sm._current = sc
    sm.update(1.0 / 60.0)
    assert sc.update_called == 1


def test_double_transition_second_ignored_or_queued_documented():
    sm = SceneManager()
    a = _MockScene()
    b = _MockScene()
    sm._controls_scene = a
    sm._settings_scene = b
    sm._start_scene = _MockScene()
    sm._game_scene = _MockScene()
    sm.switch_to_controls()
    sm.switch_to_settings()
    assert sm.current is b
    sm.update(0.016)
    assert b.update_called == 1
    assert a.update_called == 0
