"""Regression: door unlock after room clear (boss death scenario) — DoorSystem semantics."""

from __future__ import annotations

from dungeon.door_system import Door, DoorState, DoorSystem
from game.config import DOOR_UNLOCK_DELAY_SEC


def test_door_unlocks_after_boss_death():
    """After clear, timer runs; doors open — mirrors post-boss unlock delay."""
    ds = DoorSystem()
    ds.set_doors([Door(tile_x=8, tile_y=10, state=DoorState.CLOSED, target_room_index=3)])
    ds.close_all()
    assert not ds.any_door_open()
    ds.start_unlock_timer()
    ds.update(DOOR_UNLOCK_DELAY_SEC + 0.02)
    assert ds.any_door_open()


def test_door_does_not_unlock_before_clear():
    """Timer never starts without start_unlock_timer — doors stay closed."""
    ds = DoorSystem()
    ds.set_doors([Door(tile_x=8, tile_y=10, state=DoorState.CLOSED, target_room_index=3)])
    ds.close_all()
    ds.update(DOOR_UNLOCK_DELAY_SEC * 2.0)
    assert not ds.any_door_open()


def test_concurrent_death_and_damage_does_not_relock():
    """Double start_unlock_timer is idempotent; doors still open after delay."""
    ds = DoorSystem()
    ds.set_doors([Door(tile_x=5, tile_y=12, state=DoorState.CLOSED, target_room_index=1)])
    ds.close_all()
    ds.start_unlock_timer()
    ds.start_unlock_timer()
    ds.update(DOOR_UNLOCK_DELAY_SEC + 0.01)
    assert ds.any_door_open()
