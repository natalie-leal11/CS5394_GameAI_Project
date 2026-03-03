# Phase 7: Lava (6 HP/sec, 3-frame 6 FPS) and slow tile (speed factor). No hardcoding.

import pygame

from game.config import (
    TILE_SIZE,
    LAVA_DAMAGE_PER_SECOND,
    LAVA_ANIM_FRAMES,
    LAVA_ANIM_FPS,
    SLOW_TILE_SPEED_FACTOR,
)
from dungeon.room import Room, TILE_LAVA, TILE_SLOW


class HazardSystem:
    """Applies lava damage and provides slow factor for a room. Lava anim: 3 frames at 6 FPS."""

    def __init__(self, room: Room | None = None) -> None:
        self._room = room
        self._lava_anim_time: float = 0.0

    def set_room(self, room: Room | None) -> None:
        self._room = room
        self._lava_anim_time = 0.0

    def update(self, dt: float) -> None:
        self._lava_anim_time += dt

    def lava_frame_index(self) -> int:
        """Current lava animation frame 0..LAVA_ANIM_FRAMES-1."""
        if LAVA_ANIM_FPS <= 0 or LAVA_ANIM_FRAMES <= 0:
            return 0
        cycle = 1.0 / LAVA_ANIM_FPS * LAVA_ANIM_FRAMES
        t = self._lava_anim_time % cycle
        frame = int(t * LAVA_ANIM_FPS) % LAVA_ANIM_FRAMES
        return frame

    def damage_per_second_for_lava(self) -> float:
        return float(LAVA_DAMAGE_PER_SECOND)

    def slow_speed_factor(self) -> float:
        return float(SLOW_TILE_SPEED_FACTOR)

    def is_lava_tile(self, tx: int, ty: int) -> bool:
        if self._room is None:
            return False
        return self._room.get_tile_type(tx, ty) == TILE_LAVA

    def is_slow_tile(self, tx: int, ty: int) -> bool:
        if self._room is None:
            return False
        return self._room.get_tile_type(tx, ty) == TILE_SLOW

    def tile_at_world(self, wx: float, wy: float) -> tuple[int, int]:
        if self._room is None:
            return (0, 0)
        return self._room.tile_at_world(wx, wy)
