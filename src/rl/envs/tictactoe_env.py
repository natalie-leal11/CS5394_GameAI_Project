"""
TicTacToeEnv: a Gymnasium environment for two-player tic-tac-toe.

Used as a correctness test for the PPO training loop in train_ppo.py.
The game is fully solved (optimal play always draws), giving a ground-truth
benchmark that the dungeon environment cannot provide.

The agent always plays as X (player 1). The opponent strategy is set at
construction time: "random" (default) or "minimax".

Do not import anything from src/game, src/entities, src/dungeon, or src/systems.
"""
from __future__ import annotations

import functools
from typing import Any, Optional
import numpy as np
import gymnasium as gym
from gymnasium import spaces

R_WIN     =  1.0
R_LOSS    = -1.0
R_DRAW    =  0.0
R_INVALID = -0.5
R_STEP    =  0.0

WINS = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]

def _check_winner(board: tuple, mark: int) -> bool:
    return any(board[a]==mark and board[b]==mark and board[c]==mark for a,b,c in WINS)

@functools.lru_cache(maxsize=None)
def _minimax(board: tuple, is_maximising: bool) -> float:
    if _check_winner(board, 1):  return 1.0
    if _check_winner(board, -1): return -1.0
    empties = [i for i,v in enumerate(board) if v == 0]
    if not empties: return 0.0
    mark = 1 if is_maximising else -1
    scores = [_minimax(board[:i]+(mark,)+board[i+1:], not is_maximising) for i in empties]
    return max(scores) if is_maximising else min(scores)

def _minimax_move(board: tuple) -> int:
    empties = [i for i,v in enumerate(board) if v == 0]
    best_score, best_move = float("inf"), empties[0]
    for i in empties:
        s = _minimax(board[:i]+(-1,)+board[i+1:], True)
        if s < best_score:
            best_score, best_move = s, i
    return best_move

class TicTacToeEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self, opponent: str = "random", render_mode: Optional[str] = None):
        super().__init__()
        assert opponent in ("random", "minimax"), f"Unknown opponent: {opponent}"
        self.opponent = opponent
        self.render_mode = render_mode
        self.observation_space = spaces.Box(low=-1.0, high=1.0, shape=(9,), dtype=np.float32)
        self.action_space = spaces.Discrete(9)
        self._board: list[int] = [0] * 9
        self._invalid_moves = 0
        self._move_count = 0

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        self._board = [0] * 9
        self._invalid_moves = 0
        self._move_count = 0
        return self._obs(), {}

    def step(self, action: int):
        action = int(action)
        if self._board[action] != 0:
            self._invalid_moves += 1
            return self._obs(), R_INVALID, True, False, self._info("invalid")

        self._board[action] = 1
        self._move_count += 1

        if _check_winner(tuple(self._board), 1):
            return self._obs(), R_WIN, True, False, self._info("win")
        if all(c != 0 for c in self._board):
            return self._obs(), R_DRAW, True, False, self._info("draw")

        opp_move = self._opponent_move()
        self._board[opp_move] = -1

        if _check_winner(tuple(self._board), -1):
            return self._obs(), R_LOSS, True, False, self._info("loss")
        if all(c != 0 for c in self._board):
            return self._obs(), R_DRAW, True, False, self._info("draw")

        return self._obs(), R_STEP, False, False, self._info("ongoing")

    def _opponent_move(self) -> int:
        empties = [i for i,v in enumerate(self._board) if v == 0]
        if self.opponent == "minimax":
            return _minimax_move(tuple(self._board))
        return int(self.np_random.choice(empties))

    def _obs(self) -> np.ndarray:
        return np.array(self._board, dtype=np.float32)

    def _info(self, outcome: str) -> dict:
        return {
            "board": self._obs(),
            "outcome": outcome,
            "invalid_moves": self._invalid_moves,
            "move_count": self._move_count,
        }

    def render(self):
        if self.render_mode != "human":
            return
        symbols = {1: "X", -1: "O", 0: "."}
        for row in range(3):
            print(" ".join(symbols[self._board[row*3+col]] for col in range(3)))
        print()

    def action_masks(self) -> list[bool]:
        """Return a boolean mask of valid actions. True = cell is empty and playable."""
        return [c == 0 for c in self._board]
