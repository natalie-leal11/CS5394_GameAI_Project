"""
Smoke tests for the TicTacToe PPO training pipeline.

Fast tests run in under a second. Slow tests (marked with @pytest.mark.slow)
perform abbreviated training loops and serve as the primary regression gate
for the PPO implementation.

Skip slow tests in CI with: pytest -m "not slow"
Run only slow tests with:   pytest -m slow
"""
from __future__ import annotations

import numpy as np
import pytest
from gymnasium.wrappers import TimeLimit
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

from rl.envs.tictactoe_env import TicTacToeEnv


def _make_env(opponent: str = "random") -> TicTacToeEnv:
    return TimeLimit(TicTacToeEnv(opponent=opponent), max_episode_steps=10)


def test_env_integrates_with_sb3_make_vec_env():
    vec_env = make_vec_env(lambda: _make_env(), n_envs=1)
    obs = vec_env.reset()
    obs, rewards, dones, infos = vec_env.step([0])
    assert obs.shape == (1, 9)


def test_ppo_initialises_on_tictactoe():
    model = PPO("MlpPolicy", _make_env(), verbose=0)
    assert model.policy is not None


def test_ppo_learns_short_run(tmp_path):
    model = PPO("MlpPolicy", _make_env(), verbose=0, n_steps=64, batch_size=32)
    model.learn(total_timesteps=512)
    save_path = str(tmp_path / "model.zip")
    model.save(save_path)
    loaded = PPO.load(save_path)
    obs = np.zeros((9,), dtype=np.float32)
    action, _ = loaded.predict(obs, deterministic=True)
    assert 0 <= int(action) <= 8


def test_timelimit_wrapper_compatible():
    env = _make_env()
    obs, _ = env.reset()
    truncations = 0
    for _ in range(5):
        done = False
        steps = 0
        obs, _ = env.reset()
        while not done:
            obs, _, terminated, truncated, _ = env.step(env.action_space.sample())
            done = terminated or truncated
            steps += 1
            if truncated:
                truncations += 1
        assert steps <= 10
    # Tic-tac-toe always ends naturally in <=9 moves; TimeLimit should never fire
    assert truncations == 0


@pytest.mark.slow
def test_agent_beats_random_baseline():
    env = make_vec_env(lambda: _make_env("random"), n_envs=1)
    model = PPO("MlpPolicy", env, verbose=0, n_steps=512, batch_size=64,
                ent_coef=0.01, seed=0)
    model.learn(total_timesteps=50_000)

    eval_env = TicTacToeEnv(opponent="random")
    wins = 0
    episodes = 500
    obs, _ = eval_env.reset(seed=1)
    ep = 0
    while ep < episodes:
        action, _ = model.predict(obs, deterministic=True)
        obs, _, terminated, truncated, info = eval_env.step(action)
        if terminated or truncated:
            if info.get("outcome") == "win":
                wins += 1
            ep += 1
            obs, _ = eval_env.reset()
    win_rate = wins / episodes
    assert win_rate > 0.55, f"Expected win_rate > 0.55 vs random, got {win_rate:.3f}"


@pytest.mark.slow
def test_agent_never_makes_invalid_moves_after_training():
    # MaskablePPO from sb3-contrib uses action_masks() to zero out occupied cells
    # before sampling. This structurally guarantees zero invalid moves after any
    # amount of training, validating that the masking integration works correctly.
    try:
        from sb3_contrib import MaskablePPO
        from sb3_contrib.common.wrappers import ActionMasker
    except ImportError:
        pytest.skip("sb3-contrib not installed; run: pip install sb3-contrib")

    def mask_fn(env):
        return env.unwrapped.action_masks()

    def make_masked_env():
        base = TimeLimit(TicTacToeEnv(opponent="random"), max_episode_steps=10)
        return ActionMasker(base, mask_fn)

    env = make_vec_env(make_masked_env, n_envs=1)
    model = MaskablePPO("MlpPolicy", env, verbose=0, n_steps=512, batch_size=64,
                        ent_coef=0.01, seed=0)
    model.learn(total_timesteps=50_000)

    eval_env = make_masked_env()
    invalid_eps = 0
    episodes = 200
    obs, _ = eval_env.reset(seed=2)
    ep = 0
    while ep < episodes:
        masks = eval_env.action_masks()
        action, _ = model.predict(obs, deterministic=True, action_masks=masks)
        obs, _, terminated, truncated, info = eval_env.step(action)
        if terminated or truncated:
            if info.get("outcome") == "invalid":
                invalid_eps += 1
            ep += 1
            obs, _ = eval_env.reset()
    assert invalid_eps == 0, f"MaskablePPO made {invalid_eps} invalid-move episodes — masking is broken"


@pytest.mark.slow
def test_draw_vs_minimax_after_training():
    env = make_vec_env(lambda: _make_env("random"), n_envs=1)
    model = PPO("MlpPolicy", env, verbose=0, n_steps=512, batch_size=64,
                ent_coef=0.01, seed=0)
    model.learn(total_timesteps=100_000)

    eval_env = TicTacToeEnv(opponent="minimax")
    losses = 0
    episodes = 200
    obs, _ = eval_env.reset(seed=3)
    ep = 0
    while ep < episodes:
        action, _ = model.predict(obs, deterministic=True)
        obs, _, terminated, truncated, info = eval_env.step(action)
        if terminated or truncated:
            if info.get("outcome") == "loss":
                losses += 1
            ep += 1
            obs, _ = eval_env.reset()
    loss_rate = losses / episodes
    assert loss_rate <= 0.10, f"Loss rate vs minimax too high: {loss_rate:.3f} (expected ≤ 0.10)"
