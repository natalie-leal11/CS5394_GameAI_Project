"""Prompt 30: Door system."""

from __future__ import annotations

from dungeon.door_system import Door, DoorState, DoorSystem
from game.config import DOOR_UNLOCK_DELAY_SEC


def test_doors_locked_while_enemies_alive():
    ds = DoorSystem()
    ds.set_doors(
        [
            Door(tile_x=10, tile_y=14, state=DoorState.CLOSED, is_safe_door=False, target_room_index=1),
        ]
    )
    ds.close_all()
    assert not ds.any_door_open()
    assert all(d.state != DoorState.OPEN for d in ds.doors())


def test_unlock_after_clear_with_delay():
    ds = DoorSystem()
    ds.set_doors([Door(tile_x=10, tile_y=14, state=DoorState.CLOSED, target_room_index=1)])
    ds.close_all()
    ds.start_unlock_timer()
    ds.update(DOOR_UNLOCK_DELAY_SEC * 0.4)
    assert not ds.any_door_open()
    ds.update(DOOR_UNLOCK_DELAY_SEC * 0.7)
    assert ds.any_door_open()


def test_edge_last_enemy_and_player_death_same_frame():
    """Room clear still starts unlock timer; timer is idempotent if called twice same tick."""
    ds = DoorSystem()
    ds.set_doors([Door(tile_x=5, tile_y=12, state=DoorState.CLOSED, target_room_index=1)])
    ds.close_all()
    ds.start_unlock_timer()
    ds.start_unlock_timer()
    ds.update(DOOR_UNLOCK_DELAY_SEC + 0.01)
    assert ds.any_door_open()
