"""Headless DungeonEnv: short rollouts, stable obs shape, terminal when flagged."""

from __future__ import annotations

from rl.env import DungeonEnv
from rl.obs import OBS_DIM


def test_headless_few_steps_runs():
    env = DungeonEnv(render_mode=None)
    try:
        env.reset(seed=0)
        for _ in range(8):
            obs, _, _, _, _ = env.step(0)
            assert obs.shape == (OBS_DIM,)
    finally:
        env.close()


def test_headless_step_shapes_stable():
    env = DungeonEnv(render_mode=None)
    try:
        o0, _ = env.reset(seed=5)
        for a in (0, 3, 9, 16):
            o, _, _, _, _ = env.step(min(a, 16))
            assert o.shape == o0.shape
    finally:
        env.close()


def test_headless_terminates_on_done():
    env = DungeonEnv(render_mode=None)
    try:
        env.reset(seed=6)
        env._game_scene._victory_phase = True  # noqa: SLF001
        _, _, done, _, _ = env.step(0)
        assert done is True
    finally:
        env.close()
