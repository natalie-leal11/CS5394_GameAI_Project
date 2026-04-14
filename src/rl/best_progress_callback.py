"""
Periodic evaluation callback that saves the best policy by mean final ``room_index``.

# RL-only path — safe to remove if RL is abandoned

Does not modify reward or PPO hyperparameters; only trains ``train_ppo.py`` integration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import numpy as np
from stable_baselines3.common.callbacks import BaseCallback


class BestProgressionEvalCallback(BaseCallback):
    """
    Every ``eval_freq`` environment timesteps, run ``n_eval_episodes`` rollouts on a
    separate eval env and save ``best_model_path`` when **mean final room_index**
    strictly improves (higher = better progression).
    """

    def __init__(
        self,
        eval_env_fn: Callable[[], Any],
        eval_freq: int,
        n_eval_episodes: int,
        best_model_path: Path | str,
        *,
        deterministic: bool = True,
        verbose: int = 0,
    ) -> None:
        super().__init__(verbose)
        self.eval_env_fn = eval_env_fn
        self.eval_freq = int(eval_freq)
        self.n_eval_episodes = int(n_eval_episodes)
        self.best_path = Path(best_model_path)
        self.deterministic = deterministic
        self.best_mean_final_room = float("-inf")
        self._eval_env: Any = None
        self._next_eval_at = 0

    def _init_callback(self) -> None:
        self._eval_env = self.eval_env_fn()
        if self.eval_freq > 0:
            self._next_eval_at = int(self.model.num_timesteps) + self.eval_freq

    def _on_step(self) -> bool:
        if self.eval_freq <= 0:
            return True
        if self.num_timesteps < self._next_eval_at:
            return True
        metrics = self._run_eval()
        self._next_eval_at = int(self.num_timesteps) + self.eval_freq

        mfr = metrics["mean_final_room"]
        if mfr > self.best_mean_final_room:
            self.best_mean_final_room = mfr
            self.best_path.parent.mkdir(parents=True, exist_ok=True)
            self.model.save(str(self.best_path))
            print(
                f"[best_progress] NEW BEST mean_final_room_index={mfr:.4f} "
                f"(mean_max_room={metrics['mean_max_room']:.4f}, "
                f"mean_reward={metrics['mean_reward']:.4f}) -> saved {self.best_path.resolve()}"
            )
        else:
            print(
                f"[best_progress] eval mean_final_room_index={mfr:.4f} "
                f"(best so far={self.best_mean_final_room:.4f}) "
                f"mean_max_room={metrics['mean_max_room']:.4f} "
                f"timeouts={metrics['timeouts']}/{self.n_eval_episodes}"
            )
        return True

    def _run_eval(self) -> dict[str, float]:
        env = self._eval_env
        finals: list[float] = []
        max_room_during: list[float] = []
        max_cleared: list[float] = []
        rewards: list[float] = []
        timeouts = 0

        for ep in range(self.n_eval_episodes):
            obs, _ = env.reset(seed=ep)
            done = False
            ep_reward = 0.0
            max_ri = -1.0
            max_rc = 0.0
            last_trunc = False
            last_info: dict[str, Any] = {}

            while not done:
                action, _ = self.model.predict(obs, deterministic=self.deterministic)
                obs, r, terminated, truncated, info = env.step(action)
                ep_reward += float(r)
                last_info = info
                last_trunc = bool(truncated)
                max_ri = max(max_ri, float(info.get("room_index", -1)))
                max_rc = max(max_rc, float(info.get("rooms_cleared", 0)))
                done = bool(terminated or truncated)

            finals.append(float(last_info.get("room_index", -1)))
            max_room_during.append(max_ri)
            max_cleared.append(max_rc)
            rewards.append(ep_reward)
            if last_trunc:
                timeouts += 1

        return {
            "mean_final_room": float(np.mean(finals)) if finals else 0.0,
            "mean_max_room": float(np.mean(max_room_during)) if max_room_during else 0.0,
            "mean_reward": float(np.mean(rewards)) if rewards else 0.0,
            "mean_rooms_cleared": float(np.mean(max_cleared)) if max_cleared else 0.0,
            "timeouts": float(timeouts),
        }

    def _on_training_end(self) -> None:
        if self._eval_env is not None:
            self._eval_env.close()
            self._eval_env = None
