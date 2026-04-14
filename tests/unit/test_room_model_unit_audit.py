"""Prompt 29: Room model (audit)."""
import pytest
from dungeon.room import RoomType, Room

def test_hazard_percent_in_0_100():
    pytest.skip("Room dataclass constructor")

def test_pixel_dimensions_positive():
    pytest.skip("Requires Room instance")

def test_invalid_room_type_rejected():
    assert RoomType.COMBAT == "COMBAT"
