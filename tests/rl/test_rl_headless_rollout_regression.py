"""Headless rollout: finite reward + simple regression fingerprint (fixed seed + actions)."""

from __future__ import annotations

import hashlib

import numpy as np

from rl.env import DungeonEnv
from rl.obs import OBS_DIM


def test_short_rollout_all_rewards_and_obs_finite() -> None:
    env = DungeonEnv(render_mode=None)
    try:
        obs, _ = env.reset(seed=42)
        assert obs.shape == (OBS_DIM,)
        total = 0.0
        for _ in range(12):
            obs, r, term, trunc, _ = env.step(0)
            assert obs.shape == (OBS_DIM,)
            assert np.isfinite(obs).all()
            assert np.isfinite(r)
            total += r
            assert np.isfinite(total)
            if term or trunc:
                break
    finally:
        env.close()


def _run_scripted_actions(seed: int) -> tuple[np.ndarray, float]:
    env = DungeonEnv(render_mode=None)
    try:
        o, _ = env.reset(seed=seed)
        actions = (0, 0, 3, 0, 4, 0, 0, 0)
        rsum = 0.0
        for a in actions:
            o, r, term, trunc, _ = env.step(a)
            rsum += r
            if term or trunc:
                break
    finally:
        env.close()
    return o, rsum


def test_scripted_action_sequence_fingerprint() -> None:
    """Two envs, same seed + same small action list => identical final obs and reward sum."""
    o1, s1 = _run_scripted_actions(12_345)
    o2, s2 = _run_scripted_actions(12_345)
    assert s1 == s2
    np.testing.assert_array_equal(o1, o2)
    h1 = hashlib.md5(
        o1.tobytes() + f"{s1:.8f}".encode(), usedforsecurity=False
    ).hexdigest()
    h2 = hashlib.md5(
        o2.tobytes() + f"{s2:.8f}".encode(), usedforsecurity=False
    ).hexdigest()
    assert h1 == h2
