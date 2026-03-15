from dataclasses import dataclass
from typing import List, Tuple, Type

import math

from game.config import (
    TILE_SIZE,
    ENEMY_MIN_X,
    ENEMY_MIN_Y,
    ENEMY_MAX_X,
    ENEMY_MAX_Y,
    SPAWN_TELEGRAPH_DURATION_SEC,
)
from systems.vfx import VfxManager


@dataclass
class SpawnSlot:
    """One enemy spawn slot driven by a telegraph → portal → enemy spawn."""

    tile_x: int
    tile_y: int
    enemy_cls: Type
    elite: bool
    start_time: float  # when telegraph should begin (seconds since system start)
    telegraph_duration_sec: float | None = None  # None = use SPAWN_TELEGRAPH_DURATION_SEC
    started: bool = False
    elapsed: float = 0.0
    completed: bool = False
    # When set, use this world (x, y) instead of _tile_to_world(tile_x, tile_y) for advanced spawn patterns.
    world_pos: Tuple[float, float] | None = None


class SpawnSystem:
    """Phase 5 spawn controller for enemy telegraphs and portals.

    - Visual only telegraphs (no collision).
    - Spawns enemies on the tile grid after telegraph completes.
    - Optional room_bounds (min_x, min_y, max_x, max_y) for Phase 7 room-based layout.
    """

    def __init__(self, vfx: VfxManager, room_bounds: Tuple[float, float, float, float] | None = None) -> None:
        self._vfx = vfx
        self._time: float = 0.0
        self._slots: List[SpawnSlot] = []
        self._room_bounds = room_bounds  # (min_x, min_y, max_x, max_y) or None = use config ENEMY_*_X/Y

    def add_spawn(
        self,
        tile_x: int,
        tile_y: int,
        enemy_cls: Type,
        elite: bool,
        start_time_sec: float,
        telegraph_duration_sec: float | None = None,
        world_pos: Tuple[float, float] | None = None,
    ) -> None:
        self._slots.append(
            SpawnSlot(
                tile_x=tile_x,
                tile_y=tile_y,
                enemy_cls=enemy_cls,
                elite=elite,
                start_time=start_time_sec,
                telegraph_duration_sec=telegraph_duration_sec,
                world_pos=world_pos,
            )
        )

    def _tile_to_world(self, tx: int, ty: int) -> Tuple[float, float]:
        # Center of tile in world coordinates.
        x = (tx + 0.5) * TILE_SIZE
        y = (ty + 0.5) * TILE_SIZE
        if self._room_bounds is not None:
            min_x, min_y, max_x, max_y = self._room_bounds
            x = max(min_x, min(max_x, x))
            y = max(min_y, min(max_y, y))
        else:
            x = max(ENEMY_MIN_X, min(ENEMY_MAX_X, x))
            y = max(ENEMY_MIN_Y, min(ENEMY_MAX_Y, y))
        return x, y

    def update(self, dt: float, player, enemies: List) -> None:
        """Advance telegraphs and perform spawns when their timers elapse."""
        if player is None:
            return
        self._time += dt
        px, py = player.world_pos
        player_rect = player.get_hitbox_rect()

        for slot in self._slots:
            if slot.completed:
                continue

            telegraph_sec = slot.telegraph_duration_sec if slot.telegraph_duration_sec is not None else SPAWN_TELEGRAPH_DURATION_SEC
            if not slot.started:
                if self._time >= slot.start_time:
                    slot.started = True
                    slot.elapsed = 0.0
                    world_pos = slot.world_pos if slot.world_pos is not None else self._tile_to_world(slot.tile_x, slot.tile_y)
                    self._vfx.spawn_telegraph(world_pos, is_elite=slot.elite, duration_sec=telegraph_sec)
                else:
                    continue

            else:
                slot.elapsed += dt
                if slot.elapsed < telegraph_sec:
                    continue

                # Telegraph finished → spawn portal + enemy once.
                world_x, world_y = slot.world_pos if slot.world_pos is not None else self._tile_to_world(slot.tile_x, slot.tile_y)
                enemy = slot.enemy_cls((world_x, world_y), elite=slot.elite)

                # Ensure no overlap with player; if overlapping, push enemy outward by 3 tiles.
                enemy_rect = enemy.get_hitbox_rect()
                if enemy_rect.colliderect(player_rect):
                    dx = world_x - px
                    dy = world_y - py
                    dist = math.hypot(dx, dy)
                    nx, ny = (1.0, 0.0)
                    if dist > 1e-3:
                        nx, ny = dx / dist, dy / dist
                    shift = 3 * TILE_SIZE
                    world_x = px + nx * shift
                    world_y = py + ny * shift
                    if self._room_bounds is not None:
                        min_x, min_y, max_x, max_y = self._room_bounds
                        world_x = max(min_x, min(max_x, world_x))
                        world_y = max(min_y, min(max_y, world_y))
                    else:
                        world_x = max(ENEMY_MIN_X, min(ENEMY_MAX_X, world_x))
                        world_y = max(ENEMY_MIN_Y, min(ENEMY_MAX_Y, world_y))
                    enemy.world_pos = (world_x, world_y)

                enemies.append(enemy)
                # Play spawn portal VFX at the final spawn position (Biome 4 may use summon circle for elites).
                self._vfx.spawn_portal((world_x, world_y), is_elite=slot.elite)
                slot.completed = True

    def all_spawns_completed(self) -> bool:
        """True when there are no pending spawn slots (all completed or none configured)."""
        return all(slot.completed for slot in self._slots)

