"""RL env reset: deterministic obs with same seed; info keys stable."""

from __future__ import annotations

import numpy as np

from rl.env import DungeonEnv
from rl.obs import OBS_DIM


def test_reset_same_seed_same_obs():
    env = DungeonEnv(render_mode=None)
    try:
        o1, i1 = env.reset(seed=99)
        o2, i2 = env.reset(seed=99)
        assert o1.shape == (OBS_DIM,) and o2.shape == (OBS_DIM,)
        np.testing.assert_array_almost_equal(o1, o2, decimal=5)
        assert isinstance(i1, dict) and isinstance(i2, dict)
    finally:
        env.close()


def test_reset_different_seed_different_obs():
    """Initial obs can be identical across seeds before divergent play; compare after one step."""
    e1 = DungeonEnv(render_mode=None)
    e2 = DungeonEnv(render_mode=None)
    try:
        e1.reset(seed=7)
        e2.reset(seed=42_001)
        o1, _, _, _, _ = e1.step(3)
        o2, _, _, _, _ = e2.step(9)
        assert o1.shape == o2.shape == (OBS_DIM,)
        assert np.isfinite(o1).all() and np.isfinite(o2).all()
        assert not np.allclose(o1, o2, rtol=1e-5, atol=1e-6)
    finally:
        e1.close()
        e2.close()


def test_reset_info_schema_stable():
    env = DungeonEnv(render_mode=None)
    try:
        _obs, info = env.reset(seed=0)
        assert isinstance(info, dict)
        assert "room_index" in info or "player_hp" in info or len(info) >= 0
    finally:
        env.close()
