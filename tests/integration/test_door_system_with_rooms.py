"""Doors + RoomController: locked combat rooms, unlock delay, index advances."""

from __future__ import annotations

from dungeon.room import RoomType, generate_room, total_campaign_rooms
from dungeon.room_controller import RoomController
from game.config import DOOR_UNLOCK_DELAY_SEC


def test_doors_locked_during_combat():
    """COMBAT rooms start with doors closed until room clear starts unlock timer."""
    seed = 12345
    rc = RoomController(seed=seed)
    combat_idx = None
    for i in range(total_campaign_rooms()):
        r = generate_room(i, seed)
        if r.room_type == RoomType.COMBAT:
            combat_idx = i
            break
    assert combat_idx is not None
    rc.load_room(combat_idx)
    assert rc.current_room is not None
    assert rc.current_room.room_type == RoomType.COMBAT
    assert not rc.door_system.any_door_open()


def test_doors_unlock_after_clear_with_delay():
    """start_unlock_timer + elapsed delay opens doors (same DoorSystem as RoomController)."""
    rc = RoomController(seed=42)
    rc.load_room(3)
    ds = rc.door_system
    ds.close_all()
    ds.start_unlock_timer()
    ds.update(DOOR_UNLOCK_DELAY_SEC * 0.5)
    assert not ds.any_door_open()
    ds.update(DOOR_UNLOCK_DELAY_SEC * 0.6)
    assert ds.any_door_open()


def test_traversal_advances_room_index():
    """load_room changes current_room_index deterministically."""
    rc = RoomController(seed=7)
    rc.load_room(0)
    assert rc.current_room_index == 0
    rc.load_room(1)
    assert rc.current_room_index == 1
    total = total_campaign_rooms()
    rc.load_room(total - 1)
    assert rc.current_room_index == total - 1
