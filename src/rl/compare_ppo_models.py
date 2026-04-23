"""
Compare several saved PPO models on the same eval protocol (headless).

# RL-only path — safe to remove if RL is abandoned

Example::

    cd src
    python -m rl.compare_ppo_models ../models/ppo/dungeon_ppo_ckpt_100000_steps.zip \\
        ../models/ppo/dungeon_ppo_ckpt_500000_steps.zip ../models/ppo/dungeon_ppo_final.zip
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import numpy as np
from gymnasium.wrappers import TimeLimit
from stable_baselines3 import PPO

from rl.config import EvalConfig
from rl.env import DungeonEnv
from rl.wrappers import TimeoutPenaltyWrapper


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare PPO checkpoints on the same eval settings.")
    p.add_argument(
        "models",
        nargs="+",
        type=Path,
        help="Paths to .zip model files (checkpoint or final).",
    )
    p.add_argument("--episodes", type=int, default=10, help="Episodes per seed block.")
    p.add_argument(
        "--seeds",
        type=int,
        nargs="*",
        default=None,
        help="Seed bases (default: 0 1 2 3 4).",
    )
    p.add_argument(
        "--deterministic",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Deterministic policy (default: True).",
    )
    p.add_argument(
        "--no-time-limit",
        action="store_true",
        help="Match training without TimeLimit (rare).",
    )
    p.add_argument(
        "--max-episode-steps",
        type=int,
        default=None,
        help="Override TimeLimit steps.",
    )
    return p.parse_args()


def _resolve_seeds(args: argparse.Namespace) -> list[int | None]:
    if args.seeds is not None and len(args.seeds) > 0:
        return list(args.seeds)
    return [0, 1, 2, 3, 4]


def _eval_one_model(
    model_path: Path,
    ecfg: EvalConfig,
    seed_bases: list[int | None],
    deterministic: bool,
) -> dict[str, float]:
    def _make_env():
        env = DungeonEnv(render_mode=None)
        if ecfg.use_time_limit:
            env = TimeLimit(env, max_episode_steps=ecfg.max_episode_steps)
            env = TimeoutPenaltyWrapper(env)
        return env

    env = _make_env()
    model = PPO.load(str(model_path), env=env)

    rewards: list[float] = []
    finals: list[float] = []
    max_rooms: list[float] = []
    max_cleared: list[float] = []
    timeouts = 0

    for s_base in seed_bases:
        for ep in range(ecfg.n_episodes):
            reset_seed = (s_base + ep) if s_base is not None else None
            obs, _ = env.reset(seed=reset_seed)
            done = False
            ep_reward = 0.0
            max_ri = -1.0
            max_rc = 0.0
            last_trunc = False
            last_info: dict = {}
            while not done:
                action, _ = model.predict(obs, deterministic=deterministic)
                obs, r, terminated, truncated, info = env.step(action)
                ep_reward += float(r)
                last_info = info
                last_trunc = bool(truncated)
                max_ri = max(max_ri, float(info.get("room_index", -1)))
                max_rc = max(max_rc, float(info.get("rooms_cleared", 0)))
                done = terminated or truncated
            rewards.append(ep_reward)
            finals.append(float(last_info.get("room_index", -1)))
            max_rooms.append(max_ri)
            max_cleared.append(max_rc)
            if last_trunc:
                timeouts += 1

    env.close()
    n = len(rewards)
    return {
        "mean_reward": float(np.mean(rewards)),
        "std_reward": float(np.std(rewards)),
        "mean_final_room": float(np.mean(finals)),
        "std_final_room": float(np.std(finals)),
        "mean_max_room": float(np.mean(max_rooms)),
        "mean_rooms_cleared": float(np.mean(max_cleared)),
        "timeouts": float(timeouts),
        "total_episodes": float(n),
    }


def main() -> None:
    args = parse_args()
    ecfg = EvalConfig()
    ecfg.n_episodes = int(args.episodes)
    if args.no_time_limit:
        ecfg.use_time_limit = False
    if args.max_episode_steps is not None:
        ecfg.max_episode_steps = args.max_episode_steps

    seed_bases = _resolve_seeds(args)
    total_ep = ecfg.n_episodes * len(seed_bases)

    rows: list[tuple[str, dict[str, float]]] = []
    for mp in args.models:
        mp = Path(mp)
        if not mp.is_file():
            print(f"[compare_ppo_models] skip (not found): {mp}", file=sys.stderr)
            continue
        print(f"[compare_ppo_models] evaluating {mp.resolve()} ...")
        m = _eval_one_model(mp, ecfg, seed_bases, args.deterministic)
        rows.append((str(mp.name), m))

    if not rows:
        print("[compare_ppo_models] no valid models.", file=sys.stderr)
        sys.exit(1)

    print("\n--- comparison (higher mean_final_room is better for progression) ---")
    hdr = (
        f"{'model':<40} {'mean_R':>10} {'timeouts':>12} {'final_ri':>10} {'max_ri':>10} {'rooms_clr':>10}"
    )
    print(hdr)
    print("-" * len(hdr))
    best_name = ""
    best_fr = float("-inf")
    for name, m in rows:
        fr = m["mean_final_room"]
        if fr > best_fr:
            best_fr = fr
            best_name = name
        print(
            f"{name:<40} {m['mean_reward']:>10.3f} {int(m['timeouts'])}/{int(m['total_episodes']):<4} "
            f"{m['mean_final_room']:>10.3f} {m['mean_max_room']:>10.3f} {m['mean_rooms_cleared']:>10.3f}"
        )
    print(f"\nBest by mean_final_room_index: {best_name} ({best_fr:.4f})")
    print(f"(eval: episodes_per_seed={ecfg.n_episodes} seeds={seed_bases} total_ep={total_ep} deterministic={args.deterministic})")


if __name__ == "__main__":
    main()
