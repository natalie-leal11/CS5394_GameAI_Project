"""
Defaults for PPO training / evaluation (Step 4).

# RL-only path — safe to remove if RL is abandoned

Paths are resolved relative to the repository root (parent of ``src/``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


def repo_root() -> Path:
    """``src/rl/config.py`` → repository root."""
    return Path(__file__).resolve().parent.parent.parent


def default_models_dir() -> Path:
    return repo_root() / "models" / "ppo"


def default_logs_dir() -> Path:
    return repo_root() / "logs" / "ppo"


@dataclass
class PPOConfig:
    """Training defaults; edit here or override via CLI in ``train_ppo.py``."""

    total_timesteps: int = 100_000
    # Periodic SB3 checkpoints (0 = disable intermediate checkpoints; final always saved).
    checkpoint_freq: int = 10_000
    # Optional run seed (None = SB3 default).
    seed: int | None = None

    # TimeLimit: caps episode length so PPO sees truncated episodes and gradients are not stuck.
    # Base DungeonEnv does not set truncated; wrapper adds it for training/eval only.
    use_time_limit: bool = True
    max_episode_steps: int = 5000

    # Parallel envs for rollouts (SB3 ``make_vec_env``; default 1 = DummyVecEnv only).
    n_envs: int = 1

    # Paths (under repo root)
    models_dir: Path = field(default_factory=default_models_dir)
    logs_dir: Path = field(default_factory=default_logs_dir)
    tensorboard_subdir: str = "tensorboard"

    # Saved model filenames (under models_dir)
    final_name: str = "dungeon_ppo_final.zip"
    latest_name: str = "dungeon_ppo_latest.zip"
    best_model_name: str = "dungeon_ppo_best.zip"
    checkpoint_name_prefix: str = "dungeon_ppo_ckpt"

    # Periodic progression eval: save best_model_name when mean final room_index improves (0 = off).
    eval_freq: int = 0
    eval_episodes: int = 5

    # PPO hyperparameters (simple first pass)
    learning_rate: float = 3e-4
    n_steps: int = 2048
    batch_size: int = 64
    n_epochs: int = 10
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_range: float = 0.2
    ent_coef: float = 0.0
    vf_coef: float = 0.5
    max_grad_norm: float = 0.5


@dataclass
class EvalConfig:
    """Evaluation defaults."""

    n_episodes: int = 10
    deterministic: bool = True
    # Match training TimeLimit for comparable metrics (ignored if use_time_limit False in eval script).
    use_time_limit: bool = True
    max_episode_steps: int = 5000


@dataclass
class DemoConfig:
    """Visible demo defaults."""

    n_episodes: int = 1
    deterministic: bool = True
    use_time_limit: bool = True
    max_episode_steps: int = 5000
