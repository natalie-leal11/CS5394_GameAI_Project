# Advanced enemy spawn: safe position generator and patterns (spread, triangle, ambush).

import math
from typing import List, Tuple

from game.config import (
    TILE_SIZE,
    MIN_DISTANCE_FROM_PLAYER_PX,
    MIN_TILES_FROM_WALL,
    MIN_TILES_FROM_DOOR,
    MIN_DISTANCE_BETWEEN_ENEMIES_PX,
    ELITE_EXTRA_SPACING_PX,
    MAX_SPAWN_ATTEMPTS,
    AMBUSH_SPAWN_RADIUS_PX,
    TRIANGLE_OFFSET_PX,
)


def generate_valid_spawn_position(
    room,
    player_center_xy: Tuple[float, float],
    existing_positions: List[Tuple[float, float]],
    is_elite: bool = False,
    rng=None,
) -> Tuple[float, float]:
    """
    Return (x, y) world center for one enemy spawn.
    Respects: MIN_DISTANCE_FROM_PLAYER, MIN_TILES_FROM_WALL, MIN_TILES_FROM_DOOR,
    MIN_DISTANCE_BETWEEN_ENEMIES (plus ELITE_EXTRA_SPACING_PX if is_elite).
    Uses room.wall_border(), room.playable_bounds_pixels(), room.door_positions (or caller passes doors).
    Fallback: center of playable area.
    """
    import random
    if rng is None:
        rng = random.Random()

    wall_b = room.wall_border()
    rows, cols = room.height, room.width
    playable_min_row = wall_b
    playable_max_row = rows - wall_b - 1
    playable_min_col = wall_b
    playable_max_col = cols - wall_b - 1

    if playable_min_row > playable_max_row or playable_min_col > playable_max_col:
        min_x, min_y, max_x, max_y = room.playable_bounds_pixels()
        return ((min_x + max_x) / 2.0, (min_y + max_y) / 2.0)

    # Inner playable band: at least MIN_TILES_FROM_WALL away from playable edge
    inner_min_row = playable_min_row + MIN_TILES_FROM_WALL
    inner_max_row = playable_max_row - MIN_TILES_FROM_WALL
    inner_min_col = playable_min_col + MIN_TILES_FROM_WALL
    inner_max_col = playable_max_col - MIN_TILES_FROM_WALL
    if inner_min_row > inner_max_row:
        inner_min_row = inner_max_row = (playable_min_row + playable_max_row) // 2
    if inner_min_col > inner_max_col:
        inner_min_col = inner_max_col = (playable_min_col + playable_max_col) // 2

    spacing = MIN_DISTANCE_BETWEEN_ENEMIES_PX
    if is_elite:
        spacing += ELITE_EXTRA_SPACING_PX

    px, py = player_center_xy
    door_positions = getattr(room, "door_positions_world", None)
    if door_positions is None:
        door_positions = []

    min_x, min_y, max_x, max_y = room.playable_bounds_pixels()
    center_fallback = ((min_x + max_x) / 2.0, (min_y + max_y) / 2.0)

    for _ in range(MAX_SPAWN_ATTEMPTS):
        row = rng.randint(inner_min_row, inner_max_row)
        col = rng.randint(inner_min_col, inner_max_col)
        x = col * TILE_SIZE + TILE_SIZE // 2
        y = row * TILE_SIZE + TILE_SIZE // 2

        # 1) Distance from player
        dist_to_player = math.hypot(x - px, y - py)
        if dist_to_player < MIN_DISTANCE_FROM_PLAYER_PX:
            continue

        # 2) Wall proximity (already in inner band)
        # no extra check needed

        # 3) Door proximity
        too_close_to_door = False
        for (dx, dy) in door_positions:
            if math.hypot(x - dx, y - dy) < MIN_TILES_FROM_DOOR * TILE_SIZE:
                too_close_to_door = True
                break
        if too_close_to_door:
            continue

        # 4) Prevent overlapping existing spawns
        overlap = False
        for (ex, ey) in existing_positions:
            if math.hypot(x - ex, y - ey) < spacing:
                overlap = True
                break
        if overlap:
            continue

        # Clamp to playable (safety)
        x = max(min_x, min(max_x, x))
        y = max(min_y, min(max_y, y))
        return (x, y)

    return center_fallback


def spawn_spread(
    room,
    player_center_xy: Tuple[float, float],
    count: int,
    is_elite: bool,
    rng,
    door_positions: List[Tuple[float, float]],
) -> List[Tuple[float, float]]:
    """Spread pattern: count random valid positions, spaced from each other and player."""
    setattr(room, "door_positions_world", door_positions)
    positions: List[Tuple[float, float]] = []
    for _ in range(count):
        x, y = generate_valid_spawn_position(
            room, player_center_xy, positions, is_elite=is_elite, rng=rng
        )
        positions.append((x, y))
    return positions


def spawn_triangle(
    room,
    player_center_xy: Tuple[float, float],
    is_elite: bool,
    rng,
    door_positions: List[Tuple[float, float]],
) -> List[Tuple[float, float]]:
    """Triangle formation: one base position, then three at base + (0,0), (-TRIANGLE_OFFSET, TRIANGLE_OFFSET), (TRIANGLE_OFFSET, TRIANGLE_OFFSET)."""
    setattr(room, "door_positions_world", door_positions)
    base_xy = generate_valid_spawn_position(room, player_center_xy, [], is_elite=is_elite, rng=rng)
    bx, by = base_xy
    offsets = [
        (0, 0),
        (-TRIANGLE_OFFSET_PX, TRIANGLE_OFFSET_PX),
        (TRIANGLE_OFFSET_PX, TRIANGLE_OFFSET_PX),
    ]
    min_x, min_y, max_x, max_y = room.playable_bounds_pixels()
    positions = []
    for (dx, dy) in offsets:
        x = max(min_x, min(max_x, bx + dx))
        y = max(min_y, min(max_y, by + dy))
        positions.append((x, y))
    return positions


def spawn_ambush(
    room,
    player_center_xy: Tuple[float, float],
    count: int,
    rng,
) -> List[Tuple[float, float]]:
    """Ambush pattern: count enemies around player at AMBUSH_SPAWN_RADIUS_PX, evenly spaced by angle. Clamped to playable."""
    px, py = player_center_xy
    min_x, min_y, max_x, max_y = room.playable_bounds_pixels()
    positions = []
    for i in range(count):
        angle_deg = (360.0 / max(1, count)) * i
        angle_rad = math.radians(angle_deg)
        dx = math.cos(angle_rad) * AMBUSH_SPAWN_RADIUS_PX
        dy = math.sin(angle_rad) * AMBUSH_SPAWN_RADIUS_PX
        x = max(min_x, min(max_x, px + dx))
        y = max(min_y, min(max_y, py + dy))
        positions.append((x, y))
    return positions
