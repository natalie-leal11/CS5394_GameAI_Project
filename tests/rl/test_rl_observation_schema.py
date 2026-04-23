"""
RL observation: dtype, shape, finiteness vs `gym` space — via headless `DungeonEnv`.
"""
from __future__ import annotations

import numpy as np

import pytest

_mod = pytest.importorskip("rl.obs")
from rl.env import DungeonEnv
from rl.obs import OBS_DIM


def test_module_importable() -> None:
    assert _mod is not None


def test_observation_dtype_matches_space() -> None:
    env = DungeonEnv(render_mode=None)
    try:
        obs, _ = env.reset(seed=0)
        assert obs.dtype == np.float32
    finally:
        env.close()


def test_observation_shape_matches_space() -> None:
    env = DungeonEnv(render_mode=None)
    try:
        obs, _ = env.reset(seed=0)
        assert obs.shape == (OBS_DIM,) == env.observation_space.shape
    finally:
        env.close()


def test_observation_no_nan_or_inf() -> None:
    env = DungeonEnv(render_mode=None)
    try:
        obs, _ = env.reset(seed=3)
        assert not np.isnan(obs).any()
        assert not np.isposinf(obs).any() and not np.isneginf(obs).any()
        o2, _, _, _, _ = env.step(0)
        assert not np.isnan(o2).any() and np.isfinite(o2).all()
    finally:
        env.close()


def test_observation_respects_box_low_high() -> None:
    """`DungeonEnv` uses a Box in [-1,1]; builder clamps features per `rl/obs.py`."""
    env = DungeonEnv(render_mode=None)
    try:
        lo, hi = env.observation_space.low, env.observation_space.high
        assert (lo == -1.0).all() and (hi == 1.0).all()
        o, _ = env.reset(seed=0)
        assert (o >= lo).all() and (o <= hi).all()
    finally:
        env.close()
