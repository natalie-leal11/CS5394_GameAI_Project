"""
Evaluate a trained PPO model on ``DungeonEnv`` (headless).

# RL-only path — safe to remove if RL is abandoned

Example::

    cd src
    python -m rl.eval_ppo --model ../models/ppo/dungeon_ppo_final.zip

Multi-seed (more reliable aggregates)::

    python -m rl.eval_ppo --model ../models/ppo/dungeon_ppo_final.zip --seeds 0 1 2 3 4 --episodes 10
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

import numpy as np
from gymnasium.wrappers import TimeLimit
from stable_baselines3 import PPO

from rl.action_map import (
    ACTION_COUNT,
    ACTION_INTERACT,
    ACTION_LONG_ATTACK,
    ACTION_RESERVE_HEAL,
    ACTION_SAFE_CHOICE_1,
    ACTION_SAFE_CHOICE_2,
    ACTION_SAFE_CHOICE_3,
    ACTION_SAFE_CHOICE_4,
    ACTION_SAFE_ROOM_HEAL,
    ACTION_SHORT_ATTACK,
)
from rl.config import EvalConfig, default_models_dir, repo_root
from rl.experiment_layout import eval_summary_path
from rl.env import DungeonEnv
from rl.wrappers import TimeoutPenaltyWrapper


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate PPO on DungeonEnv (headless).")
    p.add_argument(
        "--model",
        type=Path,
        default=None,
        help="Path to saved .zip (default: models/ppo/dungeon_ppo_final.zip under repo root).",
    )
    p.add_argument("--episodes", type=int, default=None, help="Episodes per seed (when using --seeds).")
    p.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Base seed when --seeds is not used (episode i uses seed+i if set).",
    )
    p.add_argument(
        "--seeds",
        type=int,
        nargs="*",
        default=None,
        help="Optional list of seed bases; runs episodes×len(seeds) total. Omit to use --seed only.",
    )
    p.add_argument(
        "--no-time-limit",
        action="store_true",
        help="Do not wrap with TimeLimit (must match how the model was trained).",
    )
    p.add_argument(
        "--max-episode-steps",
        type=int,
        default=None,
        help="TimeLimit max steps (default from EvalConfig).",
    )
    p.add_argument(
        "--deterministic",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use deterministic policy actions (default: True). Use --no-deterministic for stochastic.",
    )
    p.add_argument(
        "--experiment",
        type=str,
        default=None,
        help="With --stage, default --summary-out to models/.../stage_{stage}/eval_summary.md",
    )
    p.add_argument("--stage", type=str, default=None, help="Milestone label e.g. 300k (requires --experiment).")
    p.add_argument(
        "--summary-out",
        type=Path,
        default=None,
        help="Write eval metrics to this markdown file.",
    )
    return p.parse_args()


def _int_action(raw: object) -> int:
    """Normalize policy output to a single discrete index in [0, ACTION_COUNT)."""
    a = raw
    if isinstance(a, np.ndarray):
        a = a.flat[0]
    return int(np.clip(int(a), 0, ACTION_COUNT - 1))


def _bump_action_usage(counts: dict[str, int], action: int) -> None:
    """Increment eval action buckets (one step = one action)."""
    if action == ACTION_SHORT_ATTACK:
        counts["short_attack"] += 1
    elif action == ACTION_LONG_ATTACK:
        counts["long_attack"] += 1
    elif action == ACTION_INTERACT:
        counts["interact"] += 1
    elif action == ACTION_SAFE_ROOM_HEAL:
        counts["safe_room_heal"] += 1
    elif action == ACTION_RESERVE_HEAL:
        counts["reserve_heal"] += 1
    elif action == ACTION_SAFE_CHOICE_1:
        counts["safe_room_choice_1"] += 1
    elif action == ACTION_SAFE_CHOICE_2:
        counts["safe_room_choice_2"] += 1
    elif action == ACTION_SAFE_CHOICE_3:
        counts["safe_room_choice_3"] += 1
    elif action == ACTION_SAFE_CHOICE_4:
        counts["safe_room_choice_4"] += 1


def _pct(n: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return 100.0 * float(n) / float(total)


def _episode_outcome(info: dict) -> str:
    rb = info.get("reward_breakdown") or {}
    if float(rb.get("victory", 0)) > 0:
        return "win"
    if float(rb.get("defeat", 0)) < 0:
        return "defeat"
    return "other"


def _resolve_seed_bases(args: argparse.Namespace) -> list[int | None]:
    if args.seeds is not None and len(args.seeds) > 0:
        return list(args.seeds)
    if args.seed is not None:
        return [args.seed]
    return [None]


def main() -> None:
    args = parse_args()
    ecfg = EvalConfig()
    if args.episodes is not None:
        ecfg.n_episodes = args.episodes
    if args.no_time_limit:
        ecfg.use_time_limit = False
    if args.max_episode_steps is not None:
        ecfg.max_episode_steps = args.max_episode_steps

    _ = repo_root()
    model_path = args.model if args.model is not None else (default_models_dir() / "dungeon_ppo_final.zip")
    model_path = Path(model_path)
    if not model_path.is_file():
        print(f"[eval_ppo] model not found: {model_path.resolve()}", file=sys.stderr)
        sys.exit(1)

    def _make_env() -> gym.Env:
        env = DungeonEnv(render_mode=None)
        if ecfg.use_time_limit:
            env = TimeLimit(env, max_episode_steps=ecfg.max_episode_steps)
            env = TimeoutPenaltyWrapper(env)
        return env

    env = _make_env()
    model = PPO.load(str(model_path), env=env)

    seed_bases = _resolve_seed_bases(args)
    total_episodes = ecfg.n_episodes * len(seed_bases)

    rewards: list[float] = []
    lengths: list[int] = []
    wins = 0
    defeats = 0
    timeouts = 0
    final_room_indices: list[float] = []
    max_room_during_ep: list[float] = []
    max_rooms_cleared_during_ep: list[float] = []

    action_usage: dict[str, int] = {
        "short_attack": 0,
        "long_attack": 0,
        "interact": 0,
        "safe_room_heal": 0,
        "reserve_heal": 0,
        "safe_room_choice_1": 0,
        "safe_room_choice_2": 0,
        "safe_room_choice_3": 0,
        "safe_room_choice_4": 0,
    }
    total_action_steps = 0

    print(f"[eval_ppo] model: {model_path.resolve()}")
    print(f"[eval_ppo] seed_bases: {seed_bases}  episodes_per_seed: {ecfg.n_episodes}  total_episodes: {total_episodes}")
    print(f"[eval_ppo] deterministic: {args.deterministic}")

    for s_base in seed_bases:
        for ep in range(ecfg.n_episodes):
            reset_seed = (s_base + ep) if s_base is not None else None
            obs, _ = env.reset(seed=reset_seed)
            ep_reward = 0.0
            steps = 0
            done = False
            last_info: dict = {}
            last_truncated = False
            max_ri = -1.0
            max_rc = 0.0

            while not done:
                action, _ = model.predict(obs, deterministic=args.deterministic)
                ai = _int_action(action)
                total_action_steps += 1
                _bump_action_usage(action_usage, ai)
                obs, r, terminated, truncated, info = env.step(ai)
                ep_reward += float(r)
                steps += 1
                last_info = info
                last_truncated = bool(truncated)
                ri = float(info.get("room_index", -1))
                max_ri = max(max_ri, ri)
                rc = float(info.get("rooms_cleared", 0))
                max_rc = max(max_rc, rc)
                done = terminated or truncated

            rewards.append(ep_reward)
            lengths.append(steps)
            final_room_indices.append(float(last_info.get("room_index", -1)))
            max_room_during_ep.append(max_ri)
            max_rooms_cleared_during_ep.append(max_rc)

            if last_truncated:
                timeouts += 1

            out = _episode_outcome(last_info)
            if out == "win":
                wins += 1
            elif out == "defeat":
                defeats += 1

    env.close()

    def _mean_std(xs: list[float]) -> tuple[float, float]:
        if not xs:
            return 0.0, 0.0
        return float(np.mean(xs)), float(np.std(xs))

    r_mean, r_std = _mean_std(rewards)
    l_mean, l_std = _mean_std([float(x) for x in lengths])
    fri_mean, fri_std = _mean_std(final_room_indices)
    mri_mean, mri_std = _mean_std(max_room_during_ep)
    mrc_mean, mrc_std = _mean_std(max_rooms_cleared_during_ep)

    print("--- summary ---")
    print(f"mean_reward: {r_mean:.4f} (std {r_std:.4f})")
    print(f"mean_episode_length: {l_mean:.1f} (std {l_std:.1f})")
    print(f"wins: {wins}  defeats: {defeats}  timeouts: {timeouts} / {total_episodes}")
    print(f"mean_final_room_index: {fri_mean:.2f} (std {fri_std:.2f})")
    print(f"mean_max_room_index_during_episode: {mri_mean:.2f} (std {mri_std:.2f})")
    print(f"mean_max_rooms_cleared_during_episode: {mrc_mean:.2f} (std {mrc_std:.2f})")

    sc_sum = (
        action_usage["safe_room_choice_1"]
        + action_usage["safe_room_choice_2"]
        + action_usage["safe_room_choice_3"]
        + action_usage["safe_room_choice_4"]
    )
    print("--- action usage (all env steps) ---")
    print(f"total_action_steps: {total_action_steps}")
    for key in (
        "short_attack",
        "long_attack",
        "interact",
        "safe_room_heal",
        "reserve_heal",
    ):
        c = action_usage[key]
        print(f"{key}: count={c}  pct={_pct(c, total_action_steps):.2f}%")
    print(
        f"safe_room_choice (1+2+3+4): count={sc_sum}  pct={_pct(sc_sum, total_action_steps):.2f}%"
    )
    for i in range(1, 5):
        k = f"safe_room_choice_{i}"
        c = action_usage[k]
        print(f"  {k}: count={c}  pct={_pct(c, total_action_steps):.2f}%")

    summary_out: Path | None = args.summary_out
    if summary_out is None and args.experiment and args.stage:
        summary_out = eval_summary_path(args.experiment, args.stage)
    if summary_out is not None:
        summary_out = Path(summary_out)
        summary_out.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        lines = [
            "# Eval summary (headless)",
            "",
            f"- **UTC time:** {ts}",
            f"- **Model:** `{model_path.resolve()}`",
            f"- **Seed bases:** {seed_bases}",
            f"- **Episodes per seed:** {ecfg.n_episodes}",
            f"- **Total episodes:** {total_episodes}",
            f"- **Deterministic:** {args.deterministic}",
            "",
            "## Metrics",
            "",
            f"- **mean_reward:** {r_mean:.4f} (std {r_std:.4f})",
            f"- **mean_episode_length:** {l_mean:.1f} (std {l_std:.1f})",
            f"- **wins / defeats / timeouts:** {wins} / {defeats} / {timeouts} / {total_episodes}",
            f"- **mean_final_room_index:** {fri_mean:.2f} (std {fri_std:.2f})",
            f"- **mean_max_room_index_during_episode:** {mri_mean:.2f} (std {mri_std:.2f})",
            f"- **mean_max_rooms_cleared_during_episode:** {mrc_mean:.2f} (std {mrc_std:.2f})",
            "",
            "## Action usage (per env step)",
            "",
            f"- **total_action_steps:** {total_action_steps}",
            f"- **short_attack:** {action_usage['short_attack']} ({_pct(action_usage['short_attack'], total_action_steps):.2f}%)",
            f"- **long_attack:** {action_usage['long_attack']} ({_pct(action_usage['long_attack'], total_action_steps):.2f}%)",
            f"- **interact:** {action_usage['interact']} ({_pct(action_usage['interact'], total_action_steps):.2f}%)",
            f"- **safe_room_heal:** {action_usage['safe_room_heal']} ({_pct(action_usage['safe_room_heal'], total_action_steps):.2f}%)",
            f"- **reserve_heal:** {action_usage['reserve_heal']} ({_pct(action_usage['reserve_heal'], total_action_steps):.2f}%)",
            f"- **safe_room_choice (1+2+3+4):** {sc_sum} ({_pct(sc_sum, total_action_steps):.2f}%)",
            f"- **safe_room_choice_1:** {action_usage['safe_room_choice_1']} ({_pct(action_usage['safe_room_choice_1'], total_action_steps):.2f}%)",
            f"- **safe_room_choice_2:** {action_usage['safe_room_choice_2']} ({_pct(action_usage['safe_room_choice_2'], total_action_steps):.2f}%)",
            f"- **safe_room_choice_3:** {action_usage['safe_room_choice_3']} ({_pct(action_usage['safe_room_choice_3'], total_action_steps):.2f}%)",
            f"- **safe_room_choice_4:** {action_usage['safe_room_choice_4']} ({_pct(action_usage['safe_room_choice_4'], total_action_steps):.2f}%)",
            "",
            "## Command",
            "",
            "```text",
            shlex.join(sys.argv),
            "```",
            "",
        ]
        summary_out.write_text("\n".join(lines), encoding="utf-8")
        print(f"[eval_ppo] wrote: {summary_out.resolve()}")


if __name__ == "__main__":
    main()
