"""
eval_tictactoe.py — headless evaluation for a trained TicTacToeEnv PPO model.

Mirrors eval_ppo.py conventions (multi-episode, seed, summary markdown).
Exit code 0 = pass, 1 = fail (below win-rate threshold).

Usage:
    cd src
    python -m rl.eval_tictactoe --model ../models/tictactoe/tictactoe_ppo/tictactoe_ppo_best.zip
    python -m rl.eval_tictactoe --model <path> --opponent minimax --episodes 500
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from stable_baselines3 import PPO

from rl.envs.tictactoe_env import TicTacToeEnv


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate a trained TicTacToe PPO model")
    p.add_argument("--model",    required=True, type=str)
    p.add_argument("--opponent", choices=["random", "minimax"], default="random")
    p.add_argument("--episodes", type=int, default=1000)
    p.add_argument("--seed",     type=int, default=0)
    p.add_argument("--verbose",  action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    model = PPO.load(args.model)
    env = TicTacToeEnv(
        opponent=args.opponent,
        render_mode="human" if args.verbose else None,
    )

    outcomes: dict[str, int] = {"win": 0, "loss": 0, "draw": 0, "invalid": 0}
    total_moves = 0
    valid_episodes = 0

    obs, _ = env.reset(seed=args.seed)
    ep = 0
    while ep < args.episodes:
        action, _ = model.predict(obs, deterministic=True)
        obs, _, terminated, truncated, info = env.step(action)
        if args.verbose:
            env.render()
        if terminated or truncated:
            outcome = info.get("outcome", "ongoing")
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
            if outcome != "invalid":
                total_moves += info.get("move_count", 0)
                valid_episodes += 1
            ep += 1
            obs, _ = env.reset()

    n = args.episodes
    win_rate     = outcomes["win"]     / n
    draw_rate    = outcomes["draw"]    / n
    loss_rate    = outcomes["loss"]    / n
    invalid_rate = outcomes["invalid"] / n
    avg_moves    = total_moves / valid_episodes if valid_episodes else 0.0

    lines = [
        "── Tic-Tac-Toe Eval ──────────────────────────────",
        f"Model:       {args.model}",
        f"Opponent:    {args.opponent}",
        f"Episodes:    {n}",
        f"Seed:        {args.seed}",
        "",
        f"win_rate    :  {win_rate*100:5.1f} %",
        f"draw_rate   :  {draw_rate*100:5.1f} %",
        f"loss_rate   :  {loss_rate*100:5.1f} %",
        f"invalid_rate:  {invalid_rate*100:5.1f} %",
        f"avg_moves   :   {avg_moves:.1f}",
        "",
        "Baseline (random vs random):",
        "  Expected win  ~58.5 %",
        "  Expected draw ~28.7 %",
        "  Expected loss ~12.8 %",
        "──────────────────────────────────────────────────",
    ]
    report = "\n".join(lines)
    print(report)

    model_dir = Path(args.model).parent
    (model_dir / "eval_tictactoe_summary.md").write_text(report)

    if args.opponent == "random":
        passed = win_rate >= 0.80
    else:
        passed = loss_rate == 0.0

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
