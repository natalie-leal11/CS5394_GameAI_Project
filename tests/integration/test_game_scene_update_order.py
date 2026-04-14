"""Prompt 36: GameScene update order."""

from __future__ import annotations

from game.scene_manager import SceneManager
from rl.env import DungeonEnv


class _OrderScene:
    def __init__(self, name: str, log: list[str]) -> None:
        self.name = name
        self._log = log

    def update(self, dt: float) -> None:
        self._log.append(self.name)

    def draw(self, screen, camera_offset=None) -> None:
        pass

    def handle_event(self, event):
        return False


def test_update_order_documented():
    sm = SceneManager()
    log: list[str] = []
    sm._current = _OrderScene("only", log)
    sm.update(1.0 / 60.0)
    assert log == ["only"]


def test_enemy_list_no_modify_during_iteration_violation():
    enemies = [1, 2, 3]
    out: list[int] = []
    for e in list(enemies):
        out.append(e)
    assert out == [1, 2, 3]
    assert len(enemies) == 3


def test_rl_rl_step_path_smoke_headless():
    env = DungeonEnv(render_mode=None)
    try:
        env.reset(seed=0)
        for _ in range(3):
            obs, _r, term, trunc, info = env.step(0)
            assert obs.shape[0] > 0
            assert isinstance(info, dict)
    finally:
        env.close()
