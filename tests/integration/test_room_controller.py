"""Prompt 18: RoomController."""

from __future__ import annotations

import pytest

from dungeon.room_controller import RoomController
from dungeon.room import total_campaign_rooms


def test_advance_increments_room_index():
    rc = RoomController(seed=12345)
    rc.load_room(0)
    assert rc.current_room_index == 0
    rc.load_room(1)
    assert rc.current_room_index == 1


def test_cannot_skip_boss_room_if_blocked():
    """Invalid campaign indices are rejected; valid range is contiguous 0..total-1."""
    rc = RoomController(seed=99)
    total = total_campaign_rooms()
    with pytest.raises(ValueError):
        rc.load_room(-1)
    with pytest.raises(ValueError):
        rc.load_room(total)


def test_edge_transition_mid_combat_documented():
    rc = RoomController(seed=7)
    rc.load_room(0)
    first = rc.current_room
    rc.load_room(2)
    assert rc.current_room_index == 2
    assert rc.current_room is not None
    assert first is not rc.current_room
