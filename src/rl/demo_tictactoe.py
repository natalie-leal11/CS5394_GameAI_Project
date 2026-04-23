"""
demo_tictactoe.py — play one or more games with a trained TicTacToe PPO and print
the board after each move (agent X, opponent O). Training is not used here.

Usage (from project root):
    cd src
    python -m rl.demo_tictactoe --model ../models/tictactoe/tictactoe_ppo/tictactoe_ppo_best.zip

    python -m rl.demo_tictactoe --model <path> --opponent random --games 3 --seed 0
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from stable_baselines3 import PPO

from rl.envs.tictactoe_env import TicTacToeEnv


def _board_cells(obs: np.ndarray) -> list[int]:
    return [int(round(float(x))) for x in np.asarray(obs).flatten()[:9]]


def _format_row(row: int, cells: list[int], *, show_index: bool) -> str:
    parts: list[str] = []
    for c in range(3):
        i = row * 3 + c
        v = cells[i]
        if v == 1:
            parts.append(" X ")
        elif v == -1:
            parts.append(" O ")
        else:
            parts.append(f" {i} " if show_index else " . ")
    return "│".join(parts)


def print_board(cells: list[int], *, title: str, show_index: bool) -> None:
    line = "────┼───┼────"
    print(f"  {title}")
    print(f"  {_format_row(0, cells, show_index=show_index)}")
    print(f"  {line}")
    print(f"  {_format_row(1, cells, show_index=show_index)}")
    print(f"  {line}")
    print(f"  {_format_row(2, cells, show_index=show_index)}")
    print()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Demo a trained TicTacToe PPO (terminal, step-by-step)")
    p.add_argument(
        "--model",
        type=str,
        required=True,
        help="Path to PPO .zip (e.g. models/tictactoe/tictactoe_ppo/tictactoe_ppo_best.zip)",
    )
    p.add_argument("--opponent", choices=["random", "minimax"], default="random")
    p.add_argument("--games", type=int, default=1, help="Number of full games")
    p.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Base RNG seed for env (each game uses seed+game index). PPO is deterministic=True.",
    )
    p.add_argument(
        "--show-cell-indices",
        action="store_true",
        help="Show 0-8 in empty cells (easier to read cell ids)",
    )
    return p.parse_args()


def _outcome_label(out: str) -> str:
    return {
        "win": "Win for agent (X)",
        "loss": "Win for opponent (O)",
        "draw": "Draw",
        "invalid": "Invalid move (loss episode)",
    }.get(out, out)


def main() -> None:
    args = parse_args()
    model_path = Path(args.model)
    if not model_path.is_file():
        raise SystemExit(
            f"Model not found: {model_path.resolve()}\n"
            f"  Train with:  cd src && python -m rl.train_tictactoe\n"
            f"  Or pass a path to an existing tictactoe_ppo_*.zip"
        )

    model = PPO.load(str(model_path))
    env = TicTacToeEnv(opponent=args.opponent, render_mode=None)
    show_idx = bool(args.show_cell_indices)

    for g in range(args.games):
        print()
        print("=" * 56)
        print(f"  Game {g + 1}/{args.games}  |  opponent={args.opponent!r}  |  env_seed={args.seed + g}")
        print("  Agent = X (PPO, deterministic)  |  Opponent = O")
        print("=" * 56)
        print()

        obs, _ = env.reset(seed=args.seed + g)
        while True:
            before = _board_cells(obs)
            print_board(before, title="Current board (X to move)", show_index=show_idx)

            action, _ = model.predict(obs, deterministic=True)
            a = int(np.asarray(action).item())

            obs, _rew, terminated, truncated, info = env.step(a)
            after = _board_cells(obs)
            outcome = str(info.get("outcome", "ongoing"))
            done = bool(terminated or truncated)

            if outcome == "invalid":
                print(f"  Agent (X) chose cell {a} — invalid (not empty).")
                print_board(after, title="Unchanged (invalid)", show_index=show_idx)
                print(f"  Final: {_outcome_label(outcome)}\n")
                break

            # Valid X at cell a: reconstruct board with only X placed, before O.
            after_x = list(before)
            after_x[a] = 1

            o_cells = [i for i in range(9) if after_x[i] == 0 and after[i] == -1]

            if not done and o_cells:
                print(f"  Agent (X) → cell {a}")
                print_board(after_x, title="After X", show_index=show_idx)
                o_cell = o_cells[0]
                print(f"  Opponent (O) → cell {o_cell}")
                print_board(after, title="After O", show_index=show_idx)
            elif outcome == "win":
                print(f"  Agent (X) → cell {a} (wins immediately)")
                print_board(after, title="Final board", show_index=show_idx)
                print(f"  Final: {_outcome_label(outcome)}\n")
                break
            elif done and outcome in ("draw", "loss"):
                # Either O just moved, or (draw) last X filled the last cell
                o_played = len(o_cells) == 1
                if o_played:
                    print(f"  Agent (X) → cell {a}")
                    print_board(after_x, title="After X", show_index=show_idx)
                    print(f"  Opponent (O) → cell {o_cells[0]}")
                    if outcome == "loss":
                        print("  (O completes a line)")
                else:
                    print(f"  Agent (X) → cell {a} (last move; board full)")
                print_board(after, title="Final board", show_index=show_idx)
                print(f"  Final: {_outcome_label(outcome)}\n")
                break
            # else: ongoing without O? should not happen for valid+not done
            if done:
                print(f"  Final: {_outcome_label(outcome)}\n")
                break

    env.close()
    print("Done.")


if __name__ == "__main__":
    main()
