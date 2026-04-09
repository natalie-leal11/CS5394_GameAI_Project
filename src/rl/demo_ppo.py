"""
Load a trained PPO model and watch it play in a visible window.

# RL-only path — safe to remove if RL is abandoned

Example::

    cd src
    python -m rl.demo_ppo --model ../models/ppo/dungeon_ppo_final.zip

Uses the same ``DungeonEnv`` as training; only ``render_mode`` is ``human``.
"""

from __future__ import annotations

import argparse
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import gymnasium as gym
from gymnasium.wrappers import TimeLimit
from stable_baselines3 import PPO

from rl.config import DemoConfig, default_models_dir
from rl.experiment_layout import demo_milestone_dir
from rl.env import DungeonEnv
from rl.wrappers import TimeoutPenaltyWrapper


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Demo trained PPO with human render.")
    p.add_argument(
        "--model",
        type=Path,
        default=None,
        help="Path to saved .zip (default: models/ppo/dungeon_ppo_final.zip under repo root).",
    )
    p.add_argument("--episodes", type=int, default=None, help="How many episodes to play.")
    p.add_argument("--seed", type=int, default=None, help="Base seed for env resets (optional).")
    p.add_argument(
        "--no-time-limit",
        action="store_true",
        help="Do not wrap with TimeLimit (match training).",
    )
    p.add_argument(
        "--max-episode-steps",
        type=int,
        default=None,
        help="TimeLimit max steps (default from DemoConfig).",
    )
    p.add_argument(
        "--deterministic",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use deterministic actions (default: True).",
    )
    p.add_argument(
        "--experiment",
        type=str,
        default=None,
        help="With --stage, default --summary-out to demos/ppo/{experiment}/demo_{stage}/demo_run.md",
    )
    p.add_argument(
        "--stage",
        type=str,
        default=None,
        help="Milestone label e.g. 300k (requires --experiment for default summary path).",
    )
    p.add_argument(
        "--summary-out",
        type=Path,
        default=None,
        help="Write a markdown record of this demo (model path, time, command). Video export not included.",
    )
    p.add_argument(
        "--notes",
        type=str,
        default="",
        help="Optional notes appended to --summary-out.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if (args.experiment is not None or args.stage is not None) and (
        args.experiment is None or args.stage is None
    ):
        print("[demo_ppo] --experiment and --stage must be used together (or omit both).", file=sys.stderr)
        sys.exit(1)
    dcfg = DemoConfig()
    if args.episodes is not None:
        dcfg.n_episodes = args.episodes
    if args.no_time_limit:
        dcfg.use_time_limit = False
    if args.max_episode_steps is not None:
        dcfg.max_episode_steps = args.max_episode_steps

    model_path = args.model if args.model is not None else (default_models_dir() / "dungeon_ppo_final.zip")
    model_path = Path(model_path)
    if not model_path.is_file():
        print(f"[demo_ppo] model not found: {model_path.resolve()}", file=sys.stderr)
        sys.exit(1)

    def _make_env() -> gym.Env:
        env = DungeonEnv(render_mode="human")
        if dcfg.use_time_limit:
            env = TimeLimit(env, max_episode_steps=dcfg.max_episode_steps)
            env = TimeoutPenaltyWrapper(env)
        return env

    env = _make_env()
    model = PPO.load(str(model_path), env=env)

    print(f"[demo_ppo] model: {model_path.resolve()}")
    print(f"[demo_ppo] episodes: {dcfg.n_episodes} deterministic={args.deterministic}")
    print("[demo_ppo] close the window or Ctrl+C to stop.")

    summary_out: Path | None = args.summary_out
    if summary_out is None and args.experiment and args.stage:
        summary_out = demo_milestone_dir(args.experiment, args.stage) / "demo_run.md"

    try:
        quit_demo = False
        for ep in range(dcfg.n_episodes):
            obs, _ = env.reset(seed=(args.seed + ep) if args.seed is not None else None)
            done = False
            while not done:
                action, _ = model.predict(obs, deterministic=args.deterministic)
                obs, _r, terminated, truncated, info = env.step(action)
                done = terminated or truncated
                if getattr(env.unwrapped, "_demo_quit_requested", False):
                    print("[demo_ppo] window close requested — exiting.")
                    quit_demo = True
                    break
            if quit_demo:
                break
            rb = info.get("reward_breakdown") or {}
            if float(rb.get("victory", 0)) > 0:
                print(f"[demo_ppo] episode {ep + 1}: victory")
            elif float(rb.get("defeat", 0)) < 0:
                print(f"[demo_ppo] episode {ep + 1}: defeat")
            else:
                print(f"[demo_ppo] episode {ep + 1}: end (timeout or other)")
    finally:
        env.close()

    if summary_out is not None:
        summary_out = Path(summary_out)
        summary_out.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        notes = (args.notes or "").strip()
        body = [
            "# PPO human demo record",
            "",
            f"- **UTC time:** {ts}",
            f"- **Model path:** `{model_path.resolve()}`",
            f"- **Episodes:** {dcfg.n_episodes}",
            f"- **Deterministic:** {args.deterministic}",
            f"- **Seed:** {args.seed}",
            "",
            "## Command",
            "",
            "```text",
            shlex.join(sys.argv),
            "```",
            "",
            "## Notes",
            "",
            notes if notes else "(add observations here — behavior, rooms reached, bugs)",
            "",
            "## Video",
            "",
            "Optional: attach screen recording path or link here; this file is not overwritten by later milestones if you use per-stage folders.",
            "",
        ]
        summary_out.write_text("\n".join(body), encoding="utf-8")
        print(f"[demo_ppo] wrote summary: {summary_out.resolve()}")


if __name__ == "__main__":
    main()
