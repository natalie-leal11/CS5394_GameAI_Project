"""Terminal states via DungeonEnv: death / victory terminate episode; step stays terminal until reset."""

from __future__ import annotations

from rl.env import DungeonEnv
from rl.obs import OBS_DIM


def test_player_death_transitions_to_game_over():
    env = DungeonEnv(render_mode=None)
    try:
        env.reset(seed=0)
        assert env._episode_terminated() is False
        env._game_scene._death_phase = "fade"  # noqa: SLF001
        _obs, _r, terminated, _trunc, _info = env.step(0)
        assert terminated is True
    finally:
        env.close()


def test_victory_transitions_to_end():
    env = DungeonEnv(render_mode=None)
    try:
        env.reset(seed=1)
        env._game_scene._victory_phase = True  # noqa: SLF001
        _, _, terminated, _, _ = env.step(0)
        assert terminated is True
    finally:
        env.close()


def test_terminal_fires_once():
    """After terminal, stepping stays terminated; reset clears terminal."""
    env = DungeonEnv(render_mode=None)
    try:
        env.reset(seed=2)
        env._game_scene._death_phase = "fade"  # noqa: SLF001
        _, _, t1, _, _ = env.step(0)
        _, _, t2, _, _ = env.step(0)
        assert t1 is True and t2 is True
        obs, _ = env.reset(seed=3)
        assert obs.shape == (OBS_DIM,)
        _, _, t3, _, _ = env.step(0)
        assert t3 is False
    finally:
        env.close()
