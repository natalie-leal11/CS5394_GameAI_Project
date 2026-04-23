"""
PPO pretraining on E/F curriculum micro-scenarios (room 0 interact + biome-1 SAFE heal).

# RL-only path — safe to remove if RL is abandoned

Does not replace full-game ``rl.train_ppo``; saves under ``models/ppo/{experiment}_curriculum/``.

From ``src/``::

    python -m rl.train_curriculum_ppo --scenario both --timesteps 200000 \\
        --experiment iter2_cooldown_0p5_1p2 --stage ef200k

Resume full-game training from the saved zip::

    python -m rl.train_ppo --resume-model models/ppo/iter2_cooldown_0p5_1p2_curriculum/stage_ef200k/dungeon_ppo_final.zip \\
        --experiment iter2_cooldown_0p5_1p2 --stage fullgame_800k --timesteps 800000
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import gymnasium as gym
from gymnasium.wrappers import TimeLimit
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CallbackList, CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env

from rl.config import PPOConfig, repo_root
from rl.curriculum_wrappers import CurriculumScenarioSamplerWrapper, CurriculumSuccessWrapper
from rl.env import DungeonEnv
from rl.experiment_layout import logs_curriculum_stage_dir, models_curriculum_stage_dir
from rl.wrappers import TimeoutPenaltyWrapper


def _make_curriculum_env_factory(cfg: PPOConfig, scenario: str):
    def _init() -> gym.Env:
        e: gym.Env = DungeonEnv(render_mode=None)
        if scenario == "both":
            e = CurriculumScenarioSamplerWrapper(e)
            e = CurriculumSuccessWrapper(e, default_scenario=None, success_bonus=3.0)
        elif scenario in ("interact", "safe_heal"):
            e = CurriculumSuccessWrapper(e, default_scenario=scenario, success_bonus=3.0)
        else:
            raise ValueError(f"unknown scenario: {scenario}")
        if cfg.use_time_limit:
            e = TimeLimit(e, max_episode_steps=cfg.max_episode_steps)
            e = TimeoutPenaltyWrapper(e)
        return e

    return _init


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PPO on E/F curriculum (interact / safe_heal / both).")
    p.add_argument(
        "--scenario",
        type=str,
        choices=("interact", "safe_heal", "both"),
        default="both",
        help="Focused micro-scenario: room-0 E, SAFE-room F, or random mix.",
    )
    p.add_argument("--timesteps", type=int, default=None, help="Total training timesteps.")
    p.add_argument("--seed", type=int, default=None, help="Random seed (optional).")
    p.add_argument(
        "--no-time-limit",
        action="store_true",
        help="Do not wrap with TimeLimit.",
    )
    p.add_argument(
        "--max-episode-steps",
        type=int,
        default=None,
        help="TimeLimit max steps per curriculum episode (default 800).",
    )
    p.add_argument("--models-dir", type=Path, default=None, help="Override models output directory.")
    p.add_argument("--logs-dir", type=Path, default=None, help="Override TensorBoard logs directory.")
    p.add_argument("--checkpoint-freq", type=int, default=None, help="SB3 checkpoint frequency (0 = off).")
    p.add_argument("--n-envs", type=int, default=None, help="Parallel envs (default from PPOConfig).")
    p.add_argument(
        "--resume-model",
        type=Path,
        default=None,
        help="Load PPO from this .zip and continue curriculum training.",
    )
    p.add_argument(
        "--experiment",
        type=str,
        default=None,
        help="Base experiment name; curriculum files go under models/ppo/{name}_curriculum/ (use with --stage).",
    )
    p.add_argument(
        "--stage",
        type=str,
        default=None,
        help="Stage label, e.g. ef200k -> stage_ef200k under the curriculum tree.",
    )
    p.add_argument(
        "--write-run-summary",
        type=Path,
        default=None,
        help="Write a short markdown summary to this path.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = PPOConfig()
    if args.timesteps is not None:
        cfg.total_timesteps = args.timesteps
    if args.seed is not None:
        cfg.seed = args.seed
    if args.no_time_limit:
        cfg.use_time_limit = False
    if args.max_episode_steps is not None:
        cfg.max_episode_steps = args.max_episode_steps
    else:
        cfg.max_episode_steps = 800
    if args.checkpoint_freq is not None:
        cfg.checkpoint_freq = args.checkpoint_freq
    if args.n_envs is not None:
        if args.n_envs < 1:
            raise SystemExit("--n-envs must be >= 1")
        cfg.n_envs = args.n_envs

    if args.experiment is not None and args.stage is None:
        raise SystemExit("--experiment requires --stage (e.g. --stage ef200k)")
    if args.experiment is not None:
        if args.models_dir is None:
            cfg.models_dir = models_curriculum_stage_dir(args.experiment, args.stage)
        if args.logs_dir is None:
            cfg.logs_dir = logs_curriculum_stage_dir(args.experiment, args.stage)

    root = repo_root()
    cfg.models_dir = Path(cfg.models_dir)
    cfg.logs_dir = Path(cfg.logs_dir)
    cfg.models_dir.mkdir(parents=True, exist_ok=True)
    cfg.logs_dir.mkdir(parents=True, exist_ok=True)
    ckpt_dir = cfg.models_dir / "checkpoints"
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    tb_log = str(cfg.logs_dir / cfg.tensorboard_subdir)

    print(f"[train_curriculum_ppo] repo root: {root}")
    print(f"[train_curriculum_ppo] scenario: {args.scenario}")
    print(f"[train_curriculum_ppo] models dir: {cfg.models_dir.resolve()}")
    print(f"[train_curriculum_ppo] logs dir: {cfg.logs_dir.resolve()}")
    print(f"[train_curriculum_ppo] timesteps: {cfg.total_timesteps}")
    print(f"[train_curriculum_ppo] TimeLimit: {cfg.use_time_limit} max_episode_steps={cfg.max_episode_steps}")

    env_fn = _make_curriculum_env_factory(cfg, args.scenario)
    vec_env = make_vec_env(env_fn, n_envs=cfg.n_envs, seed=cfg.seed)

    if args.resume_model is not None:
        resume_path = Path(args.resume_model)
        if not resume_path.is_file():
            print(f"[train_curriculum_ppo] resume model not found: {resume_path.resolve()}", file=sys.stderr)
            raise SystemExit(1)
        model = PPO.load(
            str(resume_path),
            env=vec_env,
            device="auto",
            tensorboard_log=tb_log,
            verbose=1,
        )
    else:
        model = PPO(
            "MlpPolicy",
            vec_env,
            learning_rate=cfg.learning_rate,
            n_steps=cfg.n_steps,
            batch_size=cfg.batch_size,
            n_epochs=cfg.n_epochs,
            gamma=cfg.gamma,
            gae_lambda=cfg.gae_lambda,
            clip_range=cfg.clip_range,
            ent_coef=cfg.ent_coef,
            vf_coef=cfg.vf_coef,
            max_grad_norm=cfg.max_grad_norm,
            verbose=1,
            device="auto",
            tensorboard_log=tb_log,
            seed=cfg.seed,
        )

    callbacks = []
    if cfg.checkpoint_freq and cfg.checkpoint_freq > 0:
        callbacks.append(
            CheckpointCallback(
                save_freq=cfg.checkpoint_freq,
                save_path=str(ckpt_dir),
                name_prefix=cfg.checkpoint_name_prefix,
                save_replay_buffer=False,
                save_vecnormalize=False,
            )
        )
    cb = CallbackList(callbacks) if len(callbacks) > 1 else (callbacks[0] if callbacks else None)

    model.learn(
        total_timesteps=cfg.total_timesteps,
        callback=cb,
        progress_bar=False,
        reset_num_timesteps=args.resume_model is None,
    )

    final_path = cfg.models_dir / cfg.final_name
    latest_path = cfg.models_dir / cfg.latest_name
    best_curriculum = cfg.models_dir / "dungeon_ppo_curriculum_best.zip"
    model.save(str(final_path))
    shutil.copyfile(final_path, latest_path)
    shutil.copyfile(final_path, best_curriculum)

    print(f"[train_curriculum_ppo] saved: {final_path.resolve()}")
    print(f"[train_curriculum_ppo] curriculum best copy: {best_curriculum.resolve()}")

    summary_path: Path | None = args.write_run_summary
    if summary_path is None and args.experiment and args.stage:
        summary_path = cfg.models_dir / "curriculum_train.md"
    if summary_path is not None:
        summary_path = Path(summary_path)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        resume_s = str(Path(args.resume_model).resolve()) if args.resume_model is not None else "(fresh start)"
        lines = [
            "# Curriculum (E/F) train run",
            "",
            f"- **UTC time:** {ts}",
            f"- **Scenario:** `{args.scenario}`",
            f"- **Experiment:** `{args.experiment or '(custom paths)'}`",
            f"- **Stage:** `{args.stage or '(n/a)'}`",
            f"- **Timesteps:** {cfg.total_timesteps}",
            f"- **Resume from:** {resume_s}",
            f"- **Models directory:** `{cfg.models_dir.resolve()}`",
            f"- **Final:** `{final_path.resolve()}`",
            "",
            "## Full-game fine-tune",
            "",
            "Resume standard training with:",
            "",
            f"`python -m rl.train_ppo --resume-model {final_path.resolve()} ...`",
            "",
        ]
        summary_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"[train_curriculum_ppo] wrote: {summary_path.resolve()}")

    vec_env.close()


if __name__ == "__main__":
    main()
