"""
Smoke test for DungeonEnv (headless). Run:

  python -m rl.test_env

from repository root with PYTHONPATH=src, or:

  cd src && python -m rl.test_env
"""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import math

from gymnasium.wrappers import TimeLimit

from rl.env import DungeonEnv  # noqa: E402
from rl.obs import OBS_DIM  # noqa: E402
from rl.reward import R_TIMEOUT_PENALTY  # noqa: E402
from rl.wrappers import TimeoutPenaltyWrapper  # noqa: E402


def test_dungeon_env_smoke() -> None:
    import numpy as np

    env = DungeonEnv(render_mode=None)
    try:
        obs, info = env.reset(seed=42)
        assert obs.shape == (OBS_DIM,)
        assert obs.dtype == np.float32
        assert not np.isnan(obs).any()
        assert not np.isinf(obs).any()
        assert env.action_space.n == 17
        assert env.observation_space.shape == (OBS_DIM,)

        for _ in range(100):
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            assert obs.shape == (OBS_DIM,)
            assert obs.dtype == np.float32
            assert not np.isnan(obs).any()
            assert not np.isinf(obs).any()
            assert isinstance(reward, (float, int))
            assert math.isfinite(float(reward))
            assert "reward_breakdown" in info
            assert isinstance(info["reward_breakdown"], dict)
            rb = info["reward_breakdown"]
            for key in (
                "victory",
                "defeat",
                "damage",
                "life_loss",
                "heal",
                "kill_normal",
                "kill_boss",
                "progress_room",
                "progress_travel",
                "alive_bonus",
                "step_cost",
                "stall_timeout",
                "timeout_penalty",
                "enemy_damage",
                "anti_idle",
                "hazard",
                "benefit_heal",
                "benefit_upgrade",
                "benefit_interact",
                "benefit_safe_heal",
                "failed_interact",
                "failed_safe_heal",
                "reserve_heal_spam",
                "stationary_combat",
                "combat_movement",
                "attack_spam",
            ):
                assert key in rb
            assert "rooms_cleared" in info
            assert not truncated
            if terminated or truncated:
                obs, info = env.reset(seed=43)
                assert obs.shape == (OBS_DIM,)
                assert not np.isnan(obs).any()
    finally:
        env.close()


def test_timeout_penalty_wrapper() -> None:
    """Truncation from TimeLimit adds timeout penalty once; reward stays finite."""
    env = DungeonEnv(render_mode=None)
    try:
        env = TimeLimit(env, max_episode_steps=3)
        env = TimeoutPenaltyWrapper(env)
        env.reset(seed=0)
        _obs, r0, _t0, tr0, info0 = env.step(0)
        assert math.isfinite(float(r0))
        _obs, r1, _t1, tr1, info1 = env.step(0)
        assert math.isfinite(float(r1))
        _obs, r2, _t2, tr2, info2 = env.step(0)
        assert tr2
        assert math.isfinite(float(r2))
        assert float(info2["reward_breakdown"].get("timeout_penalty", 0.0)) == R_TIMEOUT_PENALTY
    finally:
        env.close()


if __name__ == "__main__":
    test_dungeon_env_smoke()
    test_timeout_penalty_wrapper()
    print("DungeonEnv smoke test OK.")
