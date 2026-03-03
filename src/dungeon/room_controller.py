# Phase 7: Current room, one-at-a-time generation, doors for current room.

from game.config import SEED
from dungeon.room import Room, RoomType, generate_room, wall_border_thickness
from dungeon.door_system import DoorSystem, Door, DoorState
from dungeon.hazard_system import HazardSystem


def _place_doors_for_room(room: Room) -> list[Door]:
    """Bottom doors on INNER face: 2 cols × B rows corridor through wall. inner_bottom_row = rows - B - 1; carve rows (h-B)..(h-1) so player can reach opening."""
    doors = []
    w, h = room.width, room.height
    B = wall_border_thickness(room.room_type)
    is_safe_exit = room.room_type == RoomType.SAFE
    exit_state = DoorState.OPEN if room.room_type == RoomType.START else DoorState.LOCKED
    # Exit (right): 2 cols (w-2, w-1) × B rows from inner wall edge (h-B) to outer (h-1)
    for ty in range(h - B, h):
        for tx in (w - 2, w - 1):
            doors.append(Door(
                tile_x=tx,
                tile_y=ty,
                state=exit_state,
                is_safe_door=is_safe_exit,
                target_room_index=room.room_index + 1,
            ))
    if room.room_index > 0:
        for ty in range(h - B, h):
            for tx in (0, 1):
                doors.append(Door(
                    tile_x=tx,
                    tile_y=ty,
                    state=DoorState.OPEN,
                    is_safe_door=False,
                    target_room_index=room.room_index - 1,
                ))
    return doors


class RoomController:
    """Holds current room (0-7), generates one at a time, manages doors and hazards."""

    def __init__(self, seed: int | None = None) -> None:
        self._seed = seed if seed is not None else SEED
        self._current_room: Room | None = None
        self._current_room_index: int = -1
        self._door_system = DoorSystem()
        self._hazard_system = HazardSystem()

    @property
    def current_room(self) -> Room | None:
        return self._current_room

    @property
    def current_room_index(self) -> int:
        return self._current_room_index

    @property
    def door_system(self) -> DoorSystem:
        return self._door_system

    @property
    def hazard_system(self) -> HazardSystem:
        return self._hazard_system

    def load_room(self, room_index: int) -> Room:
        """Generate and set room 0-7. Deterministic. Returns the room."""
        if room_index < 0 or room_index > 7:
            raise ValueError("Phase 7: only rooms 0-7")
        room = generate_room(room_index, self._seed)
        self._current_room = room
        self._current_room_index = room_index
        doors = _place_doors_for_room(room)
        self._door_system.set_doors(doors)
        if room_index == 0:
            self._door_system.open_all()  # Start room: doors open immediately
        elif room.room_type == RoomType.SAFE:
            self._door_system.open_all()  # Safe room: no combat, exit open so player can leave
        else:
            self._door_system.close_all()
        self._hazard_system.set_room(room)
        return room

    def update(self, dt: float) -> None:
        self._door_system.update(dt)
        self._hazard_system.update(dt)

    def on_room_clear(self) -> None:
        """Call when all enemies are dead. Starts 0.5 s unlock timer."""
        self._door_system.start_unlock_timer()

    def can_transition(self) -> bool:
        return self._door_system.any_door_open()
