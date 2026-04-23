"""
RL wrappers: `TimeoutPenaltyWrapper` (see `rl/wrappers.py`).

`flatten` / `normalize` / `framestack` are not in this project — replaced with
the timeout wrapper that actually exists.
"""
from __future__ import annotations

import numpy as np
import gymnasium as gym
from gymnasium import spaces

import pytest

_mod = pytest.importorskip("rl.wrappers")
from rl.reward import R_TIMEOUT_PENALTY, merge_timeout_penalty_into_breakdown


class _TruncatesSecondStepEnv(gym.Env):
    """Returns truncated=True on the second `step` after `reset` (stub)."""

    def __init__(self) -> None:
        super().__init__()
        self.observation_space = spaces.Box(low=0, high=1, shape=(2,), dtype=np.float32)
        self.action_space = spaces.Discrete(2)
        self._n = 0

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        self._n = 0
        return np.zeros(2, dtype=np.float32), {}

    def step(self, action: int):
        self._n += 1
        if self._n >= 2:
            return (
                np.zeros(2, dtype=np.float32),
                0.1,
                False,
                True,
                {"reward_breakdown": {"damage": 0.1, "heal": 0.0}},
            )
        return (
            np.zeros(2, dtype=np.float32),
            0.0,
            False,
            False,
            {"reward_breakdown": {"damage": 0.0, "heal": 0.0}},
        )


def test_module_importable() -> None:
    assert _mod is not None


def test_timeout_penalty_on_truncated() -> None:
    w = _mod.TimeoutPenaltyWrapper(_TruncatesSecondStepEnv())
    w.reset()
    w.step(0)
    obs, rew, term, trunc, info = w.step(0)
    assert trunc is True
    assert rew == pytest.approx(0.1 + R_TIMEOUT_PENALTY)


def test_timeout_penalty_merges_breakdown() -> None:
    w = _mod.TimeoutPenaltyWrapper(_TruncatesSecondStepEnv())
    w.reset()
    w.step(0)
    _obs, _r, _t, _tr, info = w.step(0)
    assert "timeout_penalty" in info.get("reward_breakdown", {})


def test_no_truncation_passthrough() -> None:
    w = _mod.TimeoutPenaltyWrapper(_TruncatesSecondStepEnv())
    w.reset()
    obs, rew, term, trunc, info = w.step(0)
    assert trunc is False
    assert rew == 0.0
    assert info.get("reward_breakdown", {}).get("timeout_penalty", 0.0) == 0.0


def test_merge_timeout_helper_matches_wrapper_increment() -> None:
    rb = {"damage": 0.1}
    m = merge_timeout_penalty_into_breakdown(rb)
    assert m["timeout_penalty"] == pytest.approx(R_TIMEOUT_PENALTY)
    assert m["damage"] == pytest.approx(0.1)

