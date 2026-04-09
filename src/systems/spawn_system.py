from dataclasses import dataclass
import random
from typing import List, Tuple, Type, Any, Optional

import math

from game.config import (
    TILE_SIZE,
    ENEMY_MIN_X,
    ENEMY_MIN_Y,
    ENEMY_MAX_X,
    ENEMY_MAX_Y,
    SPAWN_TELEGRAPH_DURATION_SEC,
    DEBUG_MOVEMENT_HITBOX,
    DEBUG_HEAVY_SPAWN_AUDIT,
    DEBUG_RANGED_ENEMY_LIFECYCLE,
    HEAVY_CLEARANCE_PADDING_PX,
    SPAWN_HEAVY_WALL_TILE_MARGIN,
)
from game.config import enemy_movement_size_tuple
from entities.enemy_base import enemy_movement_half_extents_for_class
from systems.spawn_helper import ensure_valid_spawn_position
from systems.vfx import VfxManager


def _heavy_spawn_audit_log(room: Any, wx: float, wy: float, tag: str, extra: str = "") -> None:
    """Runtime audit: why Heavy ended at this world position (enable DEBUG_HEAVY_SPAWN_AUDIT)."""
    if not DEBUG_HEAVY_SPAWN_AUDIT or room is None:
        return
    mw, mh = enemy_movement_size_tuple("heavy")
    pad = float(HEAVY_CLEARANCE_PADDING_PX)
    full_w = mw + 2.0 * pad
    full_h = mh + 2.0 * pad
    tx, ty = room.tile_at_world(wx, wy)
    b = room.wall_border()
    minx, miny, maxx, maxy = room.playable_bounds_pixels()
    print(
        f"[HEAVY SPAWN AUDIT] {tag} tile=({tx},{ty}) world=({wx:.1f},{wy:.1f}) "
        f"dist_from_playable_left={wx - minx:.1f} dist_from_playable_top={wy - miny:.1f} "
        f"wall_border_b={b} movement={mw:.0f}x{mh:.0f} inflated_clearance={full_w:.0f}x{full_h:.0f} "
        f"SPAWN_HEAVY_WALL_TILE_MARGIN={SPAWN_HEAVY_WALL_TILE_MARGIN} {extra}"
    )


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

    def __init__(
        self,
        vfx: VfxManager,
        room_bounds: Tuple[float, float, float, float] | None = None,
        *,
        elite_hp_mult: float | None = None,
        elite_damage_mult: float | None = None,
    ) -> None:
        self._vfx = vfx
        self._time: float = 0.0
        self._slots: List[SpawnSlot] = []
        self._room_bounds = room_bounds  # (min_x, min_y, max_x, max_y) or None = use config ENEMY_*_X/Y
        self._elite_hp_mult = elite_hp_mult
        self._elite_damage_mult = elite_damage_mult

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

    def _tile_to_world(
        self,
        tx: int,
        ty: int,
        enemy_cls: Type,
        room: Any,
    ) -> Tuple[float, float]:
        # Center of tile in world coordinates.
        x = (tx + 0.5) * TILE_SIZE
        y = (ty + 0.5) * TILE_SIZE
        if room is not None:
            hw, hh = enemy_movement_half_extents_for_class(enemy_cls)
            min_x, min_y, max_x, max_y = room.playable_bounds_for_half_extents(hw, hh)
            x = max(min_x, min(max_x, x))
            y = max(min_y, min(max_y, y))
        elif self._room_bounds is not None:
            min_x, min_y, max_x, max_y = self._room_bounds
            x = max(min_x, min(max_x, x))
            y = max(min_y, min(max_y, y))
        else:
            x = max(ENEMY_MIN_X, min(ENEMY_MAX_X, x))
            y = max(ENEMY_MIN_Y, min(ENEMY_MAX_Y, y))
        return x, y

    def _clamp_spawn_world(
        self,
        wx: float,
        wy: float,
        enemy_cls: Type,
        room: Any,
    ) -> Tuple[float, float]:
        if room is None:
            if self._room_bounds is not None:
                min_x, min_y, max_x, max_y = self._room_bounds
                return (max(min_x, min(max_x, wx)), max(min_y, min(max_y, wy)))
            return (
                max(ENEMY_MIN_X, min(ENEMY_MAX_X, wx)),
                max(ENEMY_MIN_Y, min(ENEMY_MAX_Y, wy)),
            )
        hw, hh = enemy_movement_half_extents_for_class(enemy_cls)
        min_x, min_y, max_x, max_y = room.playable_bounds_for_half_extents(hw, hh)
        return (max(min_x, min(max_x, wx)), max(min_y, min(max_y, wy)))

    def update(
        self,
        dt: float,
        player,
        enemies: List,
        room: Optional[Any] = None,
        *,
        heavy_blocked_tiles: Optional[set] = None,
    ) -> None:
        """Advance telegraphs and perform spawns when their timers elapse.

        heavy_blocked_tiles: Biome 4 solid prop tiles for Heavy re-validation after player-overlap nudge.
        """
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
                    world_pos = (
                        slot.world_pos
                        if slot.world_pos is not None
                        else self._tile_to_world(slot.tile_x, slot.tile_y, slot.enemy_cls, room)
                    )
                    self._vfx.spawn_telegraph(world_pos, is_elite=slot.elite, duration_sec=telegraph_sec)
                else:
                    continue

            else:
                slot.elapsed += dt
                if slot.elapsed < telegraph_sec:
                    continue

                # Telegraph finished → spawn portal + enemy once.
                world_x, world_y = (
                    slot.world_pos
                    if slot.world_pos is not None
                    else self._tile_to_world(slot.tile_x, slot.tile_y, slot.enemy_cls, room)
                )
                elite_kw: dict = {}
                if self._elite_hp_mult is not None:
                    elite_kw["elite_hp_mult"] = float(self._elite_hp_mult)
                if self._elite_damage_mult is not None:
                    elite_kw["elite_damage_mult"] = float(self._elite_damage_mult)
                enemy = slot.enemy_cls((world_x, world_y), elite=slot.elite, **elite_kw)

                # Ensure no overlap with player; if overlapping, push enemy outward by 3 tiles.
                overlap_nudged = False
                enemy_rect = (
                    enemy.get_movement_hitbox_rect()
                    if hasattr(enemy, "get_movement_hitbox_rect")
                    else enemy.get_hitbox_rect()
                )
                player_mrect = (
                    player.get_movement_hitbox_rect()
                    if hasattr(player, "get_movement_hitbox_rect")
                    else player_rect
                )
                if enemy_rect.colliderect(player_mrect):
                    overlap_nudged = True
                    dx = world_x - px
                    dy = world_y - py
                    dist = math.hypot(dx, dy)
                    nx, ny = (1.0, 0.0)
                    if dist > 1e-3:
                        nx, ny = dx / dist, dy / dist
                    shift = 3 * TILE_SIZE
                    world_x = px + nx * shift
                    world_y = py + ny * shift
                    world_x, world_y = self._clamp_spawn_world(world_x, world_y, slot.enemy_cls, room)
                    enemy.world_pos = (world_x, world_y)
                    if slot.enemy_cls.__name__ == "Heavy" and room is not None:
                        _heavy_spawn_audit_log(
                            room,
                            world_x,
                            world_y,
                            "after_player_overlap_nudge",
                            "spawn_helper_validation_was_bypassed_until_now",
                        )

                # Heavy: overlap fix only used playable clamp — re-run Heavy spawn validation (same as game_scene).
                # Otherwise the nudge can park the 104×104 clearance box against the top/left wall (common if player is low-right).
                if (
                    overlap_nudged
                    and slot.enemy_cls.__name__ == "Heavy"
                    and room is not None
                ):
                    pre_x, pre_y = world_x, world_y
                    existing = [(float(e.world_pos[0]), float(e.world_pos[1])) for e in enemies]
                    world_x, world_y = ensure_valid_spawn_position(
                        room,
                        world_x,
                        world_y,
                        existing_positions=existing,
                        rng=random.Random((int(pre_x) * 7919 + int(pre_y) * 104729) & 0x7FFFFFFF),
                        for_heavy=True,
                        blocked_tiles=heavy_blocked_tiles,
                        enemy_type="heavy",
                    )
                    enemy.world_pos = (world_x, world_y)
                    _heavy_spawn_audit_log(
                        room,
                        world_x,
                        world_y,
                        "after_heavy_revalidate_post_overlap",
                        f"pre_revalidate=({pre_x:.1f},{pre_y:.1f})",
                    )

                enemies.append(enemy)
                if DEBUG_RANGED_ENEMY_LIFECYCLE and slot.enemy_cls.__name__ == "Ranged":
                    print(
                        f"[RANGED LIFECYCLE] spawn+append cls=Ranged world=({world_x:.1f},{world_y:.1f}) "
                        f"hp={getattr(enemy, 'hp', None)!r} inactive={getattr(enemy, 'inactive', None)}"
                    )
                # Play spawn portal VFX at the final spawn position (Biome 4 may use summon circle for elites).
                self._vfx.spawn_portal((world_x, world_y), is_elite=slot.elite)
                if DEBUG_MOVEMENT_HITBOX:
                    ms = getattr(enemy, "movement_size", (0, 0))
                    mw, mh = ms[0], ms[1]
                    b = room.wall_border() if room is not None else -1
                    ty = int(world_y // TILE_SIZE)
                    room_min_y = float("nan")
                    if room is not None:
                        hw, hh = enemy_movement_half_extents_for_class(slot.enemy_cls)
                        _, room_min_y, _, _ = room.playable_bounds_for_half_extents(hw, hh)
                    print(
                        f"[SPAWN MOVEMENT] cls={slot.enemy_cls.__name__} movement_wh=({mw},{mh}) "
                        f"room_min_y={room_min_y:.1f} final_y={world_y:.1f} tile_row={ty} wall_border_b={b}"
                    )
                slot.completed = True

    def all_spawns_completed(self) -> bool:
        """True when there are no pending spawn slots (all completed or none configured)."""
        return all(slot.completed for slot in self._slots)

