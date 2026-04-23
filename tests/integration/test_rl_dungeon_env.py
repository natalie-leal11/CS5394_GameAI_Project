"""Prompt 38: DungeonEnv."""

from __future__ import annotations

from rl.env import DungeonEnv
from rl.obs import OBS_DIM


def test_reset_returns_valid_obs():
    env = DungeonEnv(render_mode=None)
    try:
        obs, _info = env.reset(seed=0)
        assert obs.shape == (OBS_DIM,)
    finally:
        env.close()


def test_step_after_terminal_requires_reset():
    env = DungeonEnv(render_mode=None)
    try:
        env.reset(seed=42)
        gs = env._game_scene
        gs._victory_phase = True  # noqa: SLF001
        _, _, terminated, _, _ = env.step(0)
        assert terminated is True
        _, _, term2, _, _ = env.step(0)
        assert term2 is True
        env.reset(seed=43)
        _, _, term3, _, _ = env.step(0)
        assert term3 is False
    finally:
        env.close()


def test_headless_no_display_smoke():
    env = DungeonEnv(render_mode=None)
    env.close()
