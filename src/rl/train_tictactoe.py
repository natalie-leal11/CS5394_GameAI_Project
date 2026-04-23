"""
train_tictactoe.py — PPO training script for TicTacToeEnv.

Mirrors the structure and conventions of train_ppo.py (staged checkpoints,
milestone markdown, best-model callback, repo_root path resolution) but is a
fully independent implementation. Do not import from train_ppo.py.

Usage:
    cd src
    python -m rl.train_tictactoe
    python -m rl.train_tictactoe --opponent minimax --timesteps 300000
    python -m rl.train_tictactoe --resume-model ../models/tictactoe/tictactoe_ppo/tictactoe_ppo_best.zip
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

import numpy as np
from gymnasium.wrappers import TimeLimit
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env

from rl.config import repo_root
from rl.envs.tictactoe_env import TicTacToeEnv

PPO_KWARGS: dict[str, Any] = dict(
    learning_rate=3e-4,
    n_steps=512,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2,
    ent_coef=0.01,
    vf_coef=0.5,
    max_grad_norm=0.5,
    verbose=1,
)


class BestWinRateCallback(BaseCallback):
    """Save model when mean win-rate strictly improves. Parallel to BestProgressionEvalCallback."""

    def __init__(
        self,
        eval_env_fn: Callable[[], Any],
        eval_freq: int,
        n_eval_episodes: int,
        best_model_path: Path,
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
        self.best_win_rate: float = -1.0
        self._next_eval_at = 0

    def _init_callback(self) -> None:
        self._eval_env = self.eval_env_fn()
        if self.eval_freq > 0:
            self._next_eval_at = int(self.model.num_timesteps) + self.eval_freq

    def _on_step(self) -> bool:
        if self.eval_freq <= 0 or self.num_timesteps < self._next_eval_at:
            return True
        self._next_eval_at = int(self.num_timesteps) + self.eval_freq
        outcomes: dict[str, int] = {"win": 0, "loss": 0, "draw": 0, "invalid": 0}
        obs, _ = self._eval_env.reset()
        ep = 0
        while ep < self.n_eval_episodes:
            action, _ = self.model.predict(obs, deterministic=self.deterministic)
            obs, _, terminated, truncated, info = self._eval_env.step(action)
            if terminated or truncated:
                outcomes[info.get("outcome", "ongoing")] += 1
                ep += 1
                obs, _ = self._eval_env.reset()
        n = self.n_eval_episodes
        win_rate = outcomes["win"] / n
        self.logger.record("ttt/win_rate",     win_rate)
        self.logger.record("ttt/draw_rate",    outcomes["draw"]    / n)
        self.logger.record("ttt/loss_rate",    outcomes["loss"]    / n)
        self.logger.record("ttt/invalid_rate", outcomes["invalid"] / n)
        if win_rate > self.best_win_rate:
            self.best_win_rate = win_rate
            self.model.save(str(self.best_path))
            if self.verbose:
                print(f"[BestWinRateCallback] New best win_rate={win_rate:.3f} → saved {self.best_path}")
        return True


def make_env(opponent: str) -> TicTacToeEnv:
    return TimeLimit(TicTacToeEnv(opponent=opponent), max_episode_steps=10)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train PPO on TicTacToeEnv")
    p.add_argument("--opponent",      choices=["random", "minimax"], default="random")
    p.add_argument("--timesteps",     type=int,   default=200_000)
    p.add_argument("--experiment",    type=str,   default="tictactoe_ppo")
    p.add_argument("--eval-freq",     type=int,   default=20_000)
    p.add_argument("--eval-episodes", type=int,   default=200)
    p.add_argument("--seed",          type=int,   default=None)
    p.add_argument("--resume-model",  type=str,   default=None)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    root = repo_root()
    models_dir = root / "models" / "tictactoe" / args.experiment
    logs_dir   = root / "logs"   / "tictactoe" / args.experiment / "tensorboard"
    models_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    env = make_vec_env(lambda: make_env(args.opponent), n_envs=1)
    kwargs = {**PPO_KWARGS, "tensorboard_log": str(logs_dir)}
    if args.seed is not None:
        kwargs["seed"] = args.seed

    if args.resume_model:
        model = PPO.load(args.resume_model, env=env, **{k: v for k, v in kwargs.items() if k != "verbose"})
        model.verbose = 1
        reset_timesteps = False
    else:
        model = PPO("MlpPolicy", env, **kwargs)
        reset_timesteps = True

    best_path = models_dir / "tictactoe_ppo_best.zip"
    callback = BestWinRateCallback(
        eval_env_fn=lambda: make_env(args.opponent),
        eval_freq=args.eval_freq,
        n_eval_episodes=args.eval_episodes,
        best_model_path=best_path,
        verbose=1,
    )
    ckpt_cb = CheckpointCallback(
        save_freq=max(args.eval_freq, 10_000),
        save_path=str(models_dir / "checkpoints"),
        name_prefix="tictactoe_ppo_ckpt",
    )

    model.learn(
        total_timesteps=args.timesteps,
        callback=[callback, ckpt_cb],
        reset_num_timesteps=reset_timesteps,
    )

    final_path  = models_dir / "tictactoe_ppo_final.zip"
    latest_path = models_dir / "tictactoe_ppo_latest.zip"
    model.save(str(final_path))
    model.save(str(latest_path))

    milestone = models_dir / "milestone_tictactoe.md"
    milestone.write_text(
        f"# Tic-Tac-Toe PPO milestone\n"
        f"- UTC: {datetime.now(timezone.utc).isoformat()}\n"
        f"- Experiment: {args.experiment}\n"
        f"- Opponent: {args.opponent}\n"
        f"- Timesteps trained: {args.timesteps}\n"
        f"- Resumed from: {args.resume_model}\n"
        f"- Final model: {final_path}\n"
    )
    print(f"Training complete. Models saved to {models_dir}")


if __name__ == "__main__":
    main()
