"""
Gymnasium wrappers for RL training (Step 6).

# RL-only path — safe to remove if RL is abandoned

``TimeoutPenaltyWrapper`` applies a penalty when ``TimeLimit`` truncates, because the base
``DungeonEnv`` cannot see the outer wrapper's ``truncated`` flag during reward computation.
"""

from __future__ import annotations

from typing import Any

import gymnasium as gym

from rl.reward import R_TIMEOUT_PENALTY, merge_timeout_penalty_into_breakdown


class TimeoutPenaltyWrapper(gym.Wrapper):
    """Add ``timeout_penalty`` to reward and ``info[\"reward_breakdown\"]`` when ``truncated``."""

    def step(self, action: Any) -> tuple[Any, float, bool, bool, dict]:
        obs, reward, terminated, truncated, info = self.env.step(action)
        if truncated:
            reward = float(reward) + R_TIMEOUT_PENALTY
            rb = info.get("reward_breakdown")
            if isinstance(rb, dict):
                info["reward_breakdown"] = merge_timeout_penalty_into_breakdown(rb)
            else:
                info["reward_breakdown"] = merge_timeout_penalty_into_breakdown({})
        return obs, reward, terminated, truncated, info
