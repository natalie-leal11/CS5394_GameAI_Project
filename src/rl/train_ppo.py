"""
Train PPO on ``DungeonEnv`` (headless) with Stable-Baselines3.

# RL-only path — safe to remove if RL is abandoned

Run from repo root (with ``src`` on ``PYTHONPATH``)::

    cd src
    python -m rl.train_ppo

Or::

    set PYTHONPATH=src
    python -m rl.train_ppo
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure ``src`` is importable when launched as ``python -m rl.train_ppo`` from ``src/``.
_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import gymnasium as gym
from gymnasium.wrappers import TimeLimit
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CallbackList, CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env

from rl.best_progress_callback import BestProgressionEvalCallback
from rl.config import PPOConfig, repo_root
from rl.env import DungeonEnv
from rl.experiment_layout import logs_stage_dir, models_stage_dir
from rl.wrappers import TimeoutPenaltyWrapper


def _make_env_factory(cfg: PPOConfig):
    def _init() -> gym.Env:
        env = DungeonEnv(render_mode=None)
        if cfg.use_time_limit:
            env = TimeLimit(env, max_episode_steps=cfg.max_episode_steps)
            env = TimeoutPenaltyWrapper(env)
        return env

    return _init


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train PPO on DungeonEnv (headless).")
    p.add_argument("--timesteps", type=int, default=None, help="Total training timesteps.")
    p.add_argument("--seed", type=int, default=None, help="Random seed (optional).")
    p.add_argument(
        "--no-time-limit",
        action="store_true",
        help="Do not wrap with TimeLimit (truncated stays False in base env).",
    )
    p.add_argument(
        "--max-episode-steps",
        type=int,
        default=None,
        help="TimeLimit max steps (default from rl.config.PPOConfig).",
    )
    p.add_argument(
        "--models-dir",
        type=Path,
        default=None,
        help="Directory for saved models (default: models/ppo under repo root).",
    )
    p.add_argument(
        "--logs-dir",
        type=Path,
        default=None,
        help="Directory for TensorBoard logs (default: logs/ppo under repo root).",
    )
    p.add_argument(
        "--checkpoint-freq",
        type=int,
        default=None,
        help="Save checkpoint every N steps (0 = checkpoints off; final still saved).",
    )
    p.add_argument(
        "--n-envs",
        type=int,
        default=None,
        help="Number of parallel envs for rollouts (default from rl.config.PPOConfig).",
    )
    p.add_argument(
        "--resume-model",
        type=Path,
        default=None,
        help="Load PPO weights from this .zip and continue training (same env/hyperparams as config).",
    )
    p.add_argument(
        "--eval-freq",
        type=int,
        default=None,
        help="Every N env timesteps, eval on a separate env and save best model by mean final room_index (0 = off).",
    )
    p.add_argument(
        "--eval-episodes",
        type=int,
        default=None,
        help="Episodes per eval when --eval-freq > 0 (default from PPOConfig).",
    )
    p.add_argument(
        "--best-model",
        type=Path,
        default=None,
        help="Path for best-by-progression checkpoint (default: models_dir / dungeon_ppo_best.zip).",
    )
    p.add_argument(
        "--experiment",
        type=str,
        default=None,
        help="Experiment name under models/ppo/ and logs/ppo/ (requires --stage). Ignored if --models-dir is set.",
    )
    p.add_argument(
        "--stage",
        type=str,
        default=None,
        help="Milestone label, e.g. 300k -> folder stage_300k (requires --experiment). Ignored if --models-dir is set.",
    )
    p.add_argument(
        "--write-run-summary",
        type=Path,
        default=None,
        help="Write milestone_train.md-style summary to this path. If omitted but --experiment and --stage are set, writes to models_dir/milestone_train.md.",
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
    if args.models_dir is not None:
        cfg.models_dir = args.models_dir
    if args.logs_dir is not None:
        cfg.logs_dir = args.logs_dir
    if args.checkpoint_freq is not None:
        cfg.checkpoint_freq = args.checkpoint_freq
    if args.n_envs is not None:
        if args.n_envs < 1:
            raise SystemExit("--n-envs must be >= 1")
        cfg.n_envs = args.n_envs
    if args.eval_freq is not None:
        cfg.eval_freq = args.eval_freq
    if args.eval_episodes is not None:
        if args.eval_episodes < 1:
            raise SystemExit("--eval-episodes must be >= 1")
        cfg.eval_episodes = args.eval_episodes

    if args.experiment is not None and args.stage is None:
        raise SystemExit("--experiment requires --stage (e.g. --stage 300k)")
    if args.experiment is not None:
        if args.models_dir is None:
            cfg.models_dir = models_stage_dir(args.experiment, args.stage)
        if args.logs_dir is None:
            cfg.logs_dir = logs_stage_dir(args.experiment, args.stage)

    root = repo_root()
    cfg.models_dir = Path(cfg.models_dir)
    cfg.logs_dir = Path(cfg.logs_dir)
    cfg.models_dir.mkdir(parents=True, exist_ok=True)
    cfg.logs_dir.mkdir(parents=True, exist_ok=True)
    ckpt_dir = cfg.models_dir / "checkpoints"
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    tb_log = str(cfg.logs_dir / cfg.tensorboard_subdir)

    print(f"[train_ppo] repo root: {root}")
    print(f"[train_ppo] models dir: {cfg.models_dir.resolve()}")
    print(f"[train_ppo] logs dir: {cfg.logs_dir.resolve()}")
    print(f"[train_ppo] tensorboard: {tb_log}")
    print(f"[train_ppo] timesteps (this run): {cfg.total_timesteps}")
    print(f"[train_ppo] n_envs: {cfg.n_envs}")
    print(f"[train_ppo] TimeLimit: {cfg.use_time_limit} max_episode_steps={cfg.max_episode_steps}")
    best_path = Path(args.best_model) if args.best_model is not None else (cfg.models_dir / cfg.best_model_name)
    if cfg.eval_freq and cfg.eval_freq > 0:
        print(
            f"[train_ppo] best-progress eval: every {cfg.eval_freq} steps, "
            f"{cfg.eval_episodes} episodes -> {best_path.resolve()} (only when mean final room_index improves)"
        )
    else:
        print("[train_ppo] best-progress eval: off (use --eval-freq N to enable)")

    env_fn = _make_env_factory(cfg)
    vec_env = make_vec_env(
        env_fn,
        n_envs=cfg.n_envs,
        seed=cfg.seed,
    )

    if args.resume_model is not None:
        resume_path = Path(args.resume_model)
        if not resume_path.is_file():
            print(f"[train_ppo] resume model not found: {resume_path.resolve()}", file=sys.stderr)
            raise SystemExit(1)
        print("[train_ppo] mode: RESUMING — loading policy/value weights from disk and continuing training")
        print(f"[train_ppo] resume checkpoint: {resume_path.resolve()}")
        model = PPO.load(
            str(resume_path),
            env=vec_env,
            device="auto",
            tensorboard_log=tb_log,
            verbose=1,
        )
    else:
        print("[train_ppo] mode: STARTING FRESH — new PPO (use --resume-model to continue from a saved .zip)")
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
    if cfg.eval_freq and cfg.eval_freq > 0:
        callbacks.append(
            BestProgressionEvalCallback(
                eval_env_fn=lambda: _make_env_factory(cfg)(),
                eval_freq=cfg.eval_freq,
                n_eval_episodes=cfg.eval_episodes,
                best_model_path=best_path,
                deterministic=True,
                verbose=0,
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
    model.save(str(final_path))
    shutil.copyfile(final_path, latest_path)

    print(f"[train_ppo] saved: {final_path.resolve()}")
    print(f"[train_ppo] saved: {latest_path.resolve()} (copy of final)")

    summary_path: Path | None = args.write_run_summary
    if summary_path is None and args.experiment and args.stage:
        summary_path = cfg.models_dir / "milestone_train.md"
    if summary_path is not None:
        summary_path = Path(summary_path)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        resume_s = str(Path(args.resume_model).resolve()) if args.resume_model is not None else "(fresh start)"
        lines = [
            "# Milestone train run",
            "",
            f"- **UTC time:** {ts}",
            f"- **Experiment:** `{args.experiment or '(custom paths)'}`",
            f"- **Stage:** `{args.stage or '(n/a)'}`",
            f"- **Timesteps this run:** {cfg.total_timesteps}",
            f"- **Resume from:** {resume_s}",
            f"- **Total env timesteps after run:** {int(getattr(model, 'num_timesteps', 0))}",
            f"- **Models directory:** `{cfg.models_dir.resolve()}`",
            f"- **Logs directory:** `{cfg.logs_dir.resolve()}`",
            f"- **Final model:** `{final_path.resolve()}`",
            f"- **Latest copy:** `{latest_path.resolve()}`",
            f"- **Best model (if eval enabled):** `{best_path.resolve()}`",
            "",
            "## Command (approximate)",
            "",
            "See shell history or README; this file is auto-generated.",
            "",
        ]
        summary_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"[train_ppo] wrote run summary: {summary_path.resolve()}")

    vec_env.close()


if __name__ == "__main__":
    main()
