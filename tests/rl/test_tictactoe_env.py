"""
Unit and integration tests for TicTacToeEnv.

These tests validate the environment contract independently of the dungeon
game. All imports are from rl.envs.tictactoe_env, standard library, numpy,
and gymnasium only. No game engine imports.

Run with: pytest tests/rl/test_tictactoe_env.py
"""
from __future__ import annotations

import numpy as np
import pytest
from gymnasium.utils.env_checker import check_env

from rl.envs.tictactoe_env import R_DRAW, R_INVALID, R_LOSS, R_WIN, TicTacToeEnv


def _make() -> TicTacToeEnv:
    return TicTacToeEnv(opponent="random")


def test_observation_space_shape():
    env = _make()
    obs, _ = env.reset()
    assert obs.shape == (9,)
    assert obs.dtype == np.float32
    assert np.all(obs == 0.0)


def test_action_space():
    env = _make()
    assert env.action_space.n == 9
    for a in range(9):
        assert env.action_space.contains(a)


def test_reset_returns_empty_board():
    env = _make()
    obs, info = env.reset()
    assert np.all(obs == 0.0)
    assert isinstance(info, dict)


def test_valid_move_places_mark():
    env = _make()
    env.reset(seed=0)
    obs, _, _, _, _ = env.step(4)
    assert obs[4] == 1.0 or obs[4] == -1.0  # cell 4 is now occupied


def test_invalid_move_terminates():
    env = _make()
    env.reset(seed=0)
    # Force opponent to not take cell 0 by using minimax logic awareness — instead manually test:
    env._board = [1, 0, 0, 0, 0, 0, 0, 0, 0]  # cell 0 already taken by agent
    obs, reward, terminated, truncated, info = env.step(0)
    assert terminated is True
    assert reward == pytest.approx(R_INVALID)
    assert info["outcome"] == "invalid"


def test_win_detection_row():
    env = _make()
    env.reset()
    env._board = [1, 1, 0, -1, -1, 0, 0, 0, 0]
    obs, reward, terminated, _, info = env.step(2)
    assert terminated is True
    assert reward == pytest.approx(R_WIN)
    assert info["outcome"] == "win"


def test_win_detection_column():
    env = _make()
    env.reset()
    env._board = [1, -1, 0, 1, -1, 0, 0, 0, 0]
    obs, reward, terminated, _, info = env.step(6)
    assert terminated is True
    assert reward == pytest.approx(R_WIN)
    assert info["outcome"] == "win"


def test_win_detection_diagonal():
    env = _make()
    env.reset()
    env._board = [1, -1, 0, -1, 1, 0, 0, 0, 0]
    obs, reward, terminated, _, info = env.step(8)
    assert terminated is True
    assert reward == pytest.approx(R_WIN)
    assert info["outcome"] == "win"


def test_draw_detection():
    env = _make()
    env.reset()
    # Board one move from a true draw — no diagonal or row/col win possible on cell 8.
    # O X O / X X O / X O .  →  [-1,1,-1,1,1,-1,1,-1,0]
    # After agent plays 8: no line of three for either player, board full → draw.
    env._board = [-1, 1, -1, 1, 1, -1, 1, -1, 0]
    obs, reward, terminated, _, info = env.step(8)
    assert terminated is True
    assert reward == pytest.approx(R_DRAW)
    assert info["outcome"] == "draw"


def test_loss_detection():
    env = TicTacToeEnv(opponent="minimax")
    env.reset()
    # Opponent has -1 at cells 3 and 4 (needs 5 to win row 1).
    # Agent has 1 at cells 6 and 7 — no immediate win available on cell 0.
    # Agent plays 0 (does not complete any agent line).
    # Minimax opponent immediately takes 5 to complete row [-1,-1,-1] → agent loses.
    env._board = [0, 0, 0, -1, -1, 0, 1, 1, 0]
    _, reward, terminated, _, info = env.step(0)
    assert terminated is True
    assert reward == pytest.approx(R_LOSS)
    assert info["outcome"] == "loss"


def test_seed_reproducibility():
    def run(seed):
        env = TicTacToeEnv(opponent="random")
        obs, _ = env.reset(seed=seed)
        env.action_space.seed(seed)   # seed action space so sample() is deterministic too
        traj = [obs.copy()]
        for _ in range(5):
            obs, _, done, _, _ = env.step(env.action_space.sample())
            traj.append(obs.copy())
            if done:
                break
        return traj

    t1 = run(42)
    t2 = run(42)
    for a, b in zip(t1, t2):
        assert np.array_equal(a, b)


def test_info_keys():
    env = _make()
    env.reset()
    _, _, _, _, info = env.step(0)
    for key in ("board", "outcome", "invalid_moves", "move_count"):
        assert key in info


def test_gymnasium_api_compliance():
    check_env(TicTacToeEnv(), warn=True, skip_render_check=True)


def test_random_opponent_never_picks_occupied():
    env = TicTacToeEnv(opponent="random")
    for _ in range(100):
        obs, _ = env.reset(seed=_)
        done = False
        while not done:
            action = env.action_space.sample()
            obs, _, terminated, truncated, info = env.step(action)
            done = terminated or truncated
        # Opponent-caused invalid moves are impossible; only agent can pick occupied cells
        assert info["invalid_moves"] == 0 or info["outcome"] == "invalid"


def test_minimax_never_loses_to_random():
    env = TicTacToeEnv(opponent="minimax")
    losses = 0
    for seed in range(500):
        obs, _ = env.reset(seed=seed)
        done = False
        while not done:
            action = int(np.random.default_rng(seed).integers(0, 9))
            obs, _, terminated, truncated, info = env.step(action)
            done = terminated or truncated
        if info["outcome"] == "loss":
            losses += 1
    assert losses == 0


def test_episode_length_at_most_9_steps():
    env = TicTacToeEnv(opponent="random")
    for seed in range(200):
        obs, _ = env.reset(seed=seed)
        done = False
        while not done:
            action = env.action_space.sample()
            _, _, terminated, truncated, info = env.step(action)
            done = terminated or truncated
        assert info["move_count"] <= 9


def test_render_human_does_not_crash():
    env = TicTacToeEnv(render_mode="human")
    env.reset()
    env.step(4)
    env.render()  # should print to stdout without raising
