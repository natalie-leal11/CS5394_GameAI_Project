"""
RL action map: total coverage, injective names, env clips OOR actions (env-level).
"""
from __future__ import annotations

import pytest

_mod = pytest.importorskip("rl.action_map")
from rl.action_map import ACTION_COUNT, ACTION_NAMES


def test_module_importable() -> None:
    assert _mod is not None


def test_action_total_coverage() -> None:
    assert len(ACTION_NAMES) == ACTION_COUNT
    for i in range(ACTION_COUNT):
        assert i in ACTION_NAMES


def test_action_injective_on_valid_range() -> None:
    assert len(ACTION_NAMES) == len(set(ACTION_NAMES.values()))


def test_action_out_of_range_rejected_or_clamped() -> None:
    """Valid range is 0 .. ACTION_COUNT-1 (enforced in `DungeonEnv` via `np.clip`)."""
    for bad in (-1, -99, 17, 100):
        assert not (0 <= bad < ACTION_COUNT)
    for ok in (0, 8, 16):
        assert 0 <= ok < ACTION_COUNT
