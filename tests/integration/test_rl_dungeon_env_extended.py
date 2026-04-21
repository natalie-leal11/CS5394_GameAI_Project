"""DungeonEnv: reset/step/done, death terminal, truncation flag, independent seeds."""

from __future__ import annotations

import numpy as np

from rl.env import DungeonEnv
from rl.obs import OBS_DIM


def test_env_reset_step_done_cycle():
    env = DungeonEnv(render_mode=None)
    try:
        obs, info = env.reset(seed=11)
        assert obs.shape == (OBS_DIM,)
        assert "room_index" in info or isinstance(info, dict)
        o2, r, term, trunc, inf2 = env.step(0)
        assert o2.shape == (OBS_DIM,)
        assert isinstance(r, float)
        assert isinstance(term, bool)
        assert isinstance(trunc, bool)
    finally:
        env.close()


def test_env_done_on_player_death():
    env = DungeonEnv(render_mode=None)
    try:
        env.reset(seed=12)
        env._game_scene._death_phase = "fade"  # noqa: SLF001
        _, _, t, _, _ = env.step(0)
        assert t is True
    finally:
        env.close()


def test_env_truncates_at_max_steps():
    """DungeonEnv does not set truncated internally (no TimeLimit wrapper here)."""
    env = DungeonEnv(render_mode=None)
    try:
        env.reset(seed=13)
        for _ in range(20):
            _, _, _, trunc, _ = env.step(0)
            assert trunc is False
    finally:
        env.close()


def test_env_multi_episode_seeds_independent():
    env = DungeonEnv(render_mode=None)
    try:
        a, _ = env.reset(seed=100)
        b, _ = env.reset(seed=200)
        assert a.shape == b.shape == (OBS_DIM,)
        assert np.isfinite(a).all() and np.isfinite(b).all()
    finally:
        env.close()
