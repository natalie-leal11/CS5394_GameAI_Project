"""RL package (Gymnasium env: ``from rl.env import DungeonEnv`` or ``from rl import DungeonEnv``)."""

from __future__ import annotations

__all__ = ["DungeonEnv"]


def __getattr__(name: str):
    if name == "DungeonEnv":
        from rl.env import DungeonEnv

        return DungeonEnv
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
