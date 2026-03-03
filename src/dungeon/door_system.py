# Phase 7: Doors — locked during combat, unlock 0.5 s after clear; safe door different color.

from dataclasses import dataclass, field
from enum import Enum

from game.config import TILE_SIZE, DOOR_UNLOCK_DELAY_SEC


class DoorState(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    LOCKED = "locked"


@dataclass
class Door:
    """One door: tile position, state, and whether it leads to safe room (different asset)."""
    tile_x: int
    tile_y: int
    state: DoorState = DoorState.LOCKED
    is_safe_door: bool = False
    # For transition: which room_index we go to when passing through (e.g. +1).
    target_room_index: int = -1

    @property
    def world_x(self) -> float:
        return (self.tile_x + 0.5) * TILE_SIZE

    @property
    def world_y(self) -> float:
        return (self.tile_y + 0.5) * TILE_SIZE

    def can_pass(self) -> bool:
        return self.state == DoorState.OPEN


class DoorSystem:
    """Manages doors for current room: lock during combat, start unlock timer on clear."""

    def __init__(self) -> None:
        self._doors: list[Door] = []
        self._unlock_timer: float | None = None  # When set, count down to unlock.

    def set_doors(self, doors: list[Door]) -> None:
        self._doors = list(doors)
        self._unlock_timer = None

    def close_all(self) -> None:
        """Set all doors to CLOSED (blocks passage, shows closed sprite)."""
        for d in self._doors:
            d.state = DoorState.CLOSED
        self._unlock_timer = None

    def open_all(self) -> None:
        """Set all doors to OPEN (passable)."""
        for d in self._doors:
            d.state = DoorState.OPEN
        self._unlock_timer = None

    def start_unlock_timer(self) -> None:
        """Call when room is clear (enemies dead). Timer will open after DOOR_UNLOCK_DELAY_SEC."""
        if self._unlock_timer is not None:
            return
        self._unlock_timer = DOOR_UNLOCK_DELAY_SEC

    def update(self, dt: float) -> None:
        if self._unlock_timer is None:
            return
        self._unlock_timer -= dt
        if self._unlock_timer <= 0:
            self.open_all()

    def doors(self) -> list[Door]:
        return self._doors

    def any_door_open(self) -> bool:
        return any(d.state == DoorState.OPEN for d in self._doors)

    def get_door_at_world(self, wx: float, wy: float, margin: float = 20.0) -> Door | None:
        """Return door whose center is within margin of (wx, wy), or None."""
        for d in self._doors:
            if not d.can_pass():
                continue
            dx = abs(wx - d.world_x)
            dy = abs(wy - d.world_y)
            if dx <= margin and dy <= margin:
                return d
        return None
