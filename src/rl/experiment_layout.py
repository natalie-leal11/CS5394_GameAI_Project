"""
Experiment folder layout for isolated PPO runs (Step 11).

# RL-only path — safe to remove if RL is abandoned

Default iteration-2 experiment name (cooldown 0.5s / 1.2s); override via CLI --experiment.
"""

from __future__ import annotations

from pathlib import Path

from rl.config import repo_root

# Default experiment slug for README / examples (folder under models/ppo/, logs/ppo/, demos/ppo/).
DEFAULT_EXPERIMENT_NAME = "iter2_cooldown_0p5_1p2"


def models_stage_dir(experiment: str, stage_label: str) -> Path:
    """
    ``stage_label`` e.g. ``\"300k\"`` -> ``.../models/ppo/{experiment}/stage_300k``.
    """
    lab = stage_label.strip()
    return repo_root() / "models" / "ppo" / experiment / f"stage_{lab}"


def logs_stage_dir(experiment: str, stage_label: str) -> Path:
    """TensorBoard / run logs for this stage."""
    lab = stage_label.strip()
    return repo_root() / "logs" / "ppo" / experiment / f"stage_{lab}"


def demo_milestone_dir(experiment: str, stage_label: str) -> Path:
    """
    Human demo artifacts for this milestone (separate from model checkpoints).
    ``demo_300k``, ``demo_600k``, etc.
    """
    lab = stage_label.strip()
    return repo_root() / "demos" / "ppo" / experiment / f"demo_{lab}"


def eval_summary_path(experiment: str, stage_label: str) -> Path:
    """Suggested path for eval markdown summary next to the stage models."""
    return models_stage_dir(experiment, stage_label) / "eval_summary.md"


def models_curriculum_stage_dir(experiment: str, stage_label: str) -> Path:
    """
    Isolated curriculum artifacts: ``models/ppo/{experiment}_curriculum/stage_{label}/``.

    Example: experiment ``iter2_cooldown_0p5_1p2`` → ``.../iter2_cooldown_0p5_1p2_curriculum/stage_ef100k``.
    """
    lab = stage_label.strip()
    return repo_root() / "models" / "ppo" / f"{experiment}_curriculum" / f"stage_{lab}"


def logs_curriculum_stage_dir(experiment: str, stage_label: str) -> Path:
    """TensorBoard logs for curriculum pretraining."""
    lab = stage_label.strip()
    return repo_root() / "logs" / "ppo" / f"{experiment}_curriculum" / f"stage_{lab}"


def curriculum_eval_summary_path(experiment: str, stage_label: str) -> Path:
    return models_curriculum_stage_dir(experiment, stage_label) / "curriculum_eval_summary.md"
