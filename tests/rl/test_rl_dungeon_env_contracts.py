"""DungeonEnv: step tuple, terminal persistence, action clipping, finite obs."""

from __future__ import annotations

import numpy as np

import pytest

from rl.env import DungeonEnv
from rl.obs import OBS_DIM


def test_step_returns_five_tuple_with_correct_shapes() -> None:
    env = DungeonEnv(render_mode=None)
    try:
        obs, info = env.reset(seed=0)
        assert obs.shape == (OBS_DIM,)
        assert isinstance(info, dict)
        out = env.step(0)
        assert len(out) == 5
        o, r, term, trunc, inf = out
        assert o.shape == (OBS_DIM,)
        assert isinstance(r, float) and np.isfinite(r)
        assert isinstance(term, bool)
        assert isinstance(trunc, bool)
        assert isinstance(inf, dict)
    finally:
        env.close()


def test_terminal_persists_until_reset() -> None:
    env = DungeonEnv(render_mode=None)
    try:
        env.reset(seed=1)
        env._game_scene._victory_phase = True  # noqa: SLF001
        o1, _, t1, tr1, _ = env.step(0)
        assert t1 is True and tr1 is False
        o2, _, t2, tr2, _ = env.step(0)
        assert t2 is True
        o3, _ = env.reset(seed=2)
        assert o3.shape == (OBS_DIM,)
        o4, _, t4, _, _ = env.step(0)
        assert t4 is False
    finally:
        env.close()


def test_out_of_range_action_is_clipped_to_valid_discrete() -> None:
    """`DungeonEnv.step` uses np.clip to [0, n-1] — out-of-range actions are not an error."""
    env = DungeonEnv(render_mode=None)
    try:
        env.reset(seed=0)
        env.step(9999)
        assert int(getattr(env._game_scene, "_rl_action", -1)) == 16  # noqa: SLF001
        env.reset(seed=0)
        env.step(-5)
        assert int(getattr(env._game_scene, "_rl_action", -1)) == 0  # noqa: SLF001
    finally:
        env.close()


def test_reset_and_step_observations_are_finite() -> None:
    env = DungeonEnv(render_mode=None)
    try:
        o, _ = env.reset(seed=11)
        assert np.isfinite(o).all()
        for _ in range(6):
            o, _, term, _, _ = env.step(0)
            assert np.isfinite(o).all()
            if term:
                break
    finally:
        env.close()
