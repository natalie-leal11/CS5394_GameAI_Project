# Advanced enemy spawn: safe position generator and patterns (spread, triangle, ambush).
# Valid spawn = inside playable bounds, not wall, not decorative obstacles, no overlap with other enemies.
# Lava and slow are allowed (enemies do not take hazard damage).

import math
import random
from typing import List, Set, Tuple

from dungeon.room import TILE_FLOOR, TILE_LAVA, TILE_SLOW
from game.config import (
    TILE_SIZE,
    MIN_DISTANCE_FROM_PLAYER_PX,
    MIN_TILES_FROM_WALL,
    MIN_TILES_FROM_WALL_HEAVY,
    MIN_TILES_FROM_CORNER_HEAVY,
    MIN_TILES_FROM_DOOR,
    MIN_DISTANCE_BETWEEN_ENEMIES_PX,
    ELITE_EXTRA_SPACING_PX,
    MAX_SPAWN_ATTEMPTS,
    SPAWN_VALIDATION_RETRY_NEARBY_ATTEMPTS,
    SPAWN_NEARBY_TILES_RADIUS,
    HEAVY_MIN_TILES_FROM_PROP,
    AMBUSH_SPAWN_RADIUS_PX,
    TRIANGLE_OFFSET_PX,
)


# Walkable tile types for enemy spawn (lava/slow allowed; enemies do not take hazard damage).
_VALID_SPAWN_TILE_TYPES = (TILE_FLOOR, TILE_LAVA, TILE_SLOW)


def _is_tile_valid_for_spawn(room, col: int, row: int) -> bool:
    """True if (col, row) is inside playable bounds, not a wall, and not a decorative obstacle. Lava and slow are allowed."""
    if room.is_tile_in_wall_band(col, row):
        return False
    return room.get_tile_type(col, row) in _VALID_SPAWN_TILE_TYPES


def _is_tile_near_corner(room, col: int, row: int, min_tiles_from_corner: int) -> bool:
    """True if (col, row) is within min_tiles_from_corner (Chebyshev distance) of any playable-area corner.
    Corners = the four corners of the playable rectangle (wall_border inset)."""
    if min_tiles_from_corner <= 0:
        return False
    b = room.wall_border()
    c0, c1 = b, room.width - b - 1
    r0, r1 = b, room.height - b - 1
    corners = [(c0, r0), (c0, r1), (c1, r0), (c1, r1)]
    for (cc, rr) in corners:
        if max(abs(col - cc), abs(row - rr)) <= min_tiles_from_corner:
            return True
    return False


def _is_tile_valid_for_heavy_spawn(
    room, col: int, row: int, blocked_tiles: Set[Tuple[int, int]] | None = None
) -> bool:
    """True if tile is valid for spawn and satisfies Heavy constraints: extra wall clearance, no corner zone, and (if blocked_tiles) not near solid props."""
    if not _is_tile_valid_for_spawn(room, col, row):
        return False
    if _is_tile_near_corner(room, col, row, MIN_TILES_FROM_CORNER_HEAVY):
        return False
    b = room.wall_border()
    if col < b + MIN_TILES_FROM_WALL_HEAVY or col >= room.width - b - MIN_TILES_FROM_WALL_HEAVY:
        return False
    if row < b + MIN_TILES_FROM_WALL_HEAVY or row >= room.height - b - MIN_TILES_FROM_WALL_HEAVY:
        return False
    if blocked_tiles:
        # Reject if any prop is too close
        for (bx, by) in blocked_tiles:
            if max(abs(col - bx), abs(row - by)) <= HEAVY_MIN_TILES_FROM_PROP:
                return False
        # Reject spawn near obstacle clusters (2+ blockers within range = corner trap)
        cluster_radius = HEAVY_MIN_TILES_FROM_PROP + 1
        count_near = sum(1 for (bx, by) in blocked_tiles if max(abs(col - bx), abs(row - by)) <= cluster_radius)
        if count_near >= 2:
            return False
    return True


def _position_overlaps_existing(
    world_x: float,
    world_y: float,
    existing_positions: List[Tuple[float, float]],
    spacing: float,
) -> bool:
    """True if (world_x, world_y) is within spacing of any existing position."""
    for (ex, ey) in existing_positions:
        if math.hypot(world_x - ex, world_y - ey) < spacing:
            return True
    return False


def _nearest_valid_spawn_in_room(
    room,
    preferred_xy: Tuple[float, float],
    existing_positions: List[Tuple[float, float]] | None = None,
    for_heavy: bool = False,
    blocked_tiles: Set[Tuple[int, int]] | None = None,
) -> Tuple[float, float]:
    """Return world (x,y) of the valid spawn tile closest to preferred_xy. Skip tiles that overlap existing_positions.
    When for_heavy=True, use Heavy wall/corner clearance and only tiles valid for Heavy. blocked_tiles = solid prop tiles to avoid."""
    wall_b = room.wall_border()
    rows, cols = room.height, room.width
    playable_min_row = wall_b
    playable_max_row = rows - wall_b - 1
    playable_min_col = wall_b
    playable_max_col = cols - wall_b - 1
    wall_margin = MIN_TILES_FROM_WALL_HEAVY if for_heavy else MIN_TILES_FROM_WALL
    inner_min_row = playable_min_row + wall_margin
    inner_max_row = playable_max_row - wall_margin
    inner_min_col = playable_min_col + wall_margin
    inner_max_col = playable_max_col - wall_margin
    inner_min_row = max(inner_min_row, playable_min_row)
    inner_max_row = min(inner_max_row, playable_max_row)
    inner_min_col = max(inner_min_col, playable_min_col)
    inner_max_col = min(inner_max_col, playable_max_col)
    spacing = MIN_DISTANCE_BETWEEN_ENEMIES_PX
    existing = existing_positions or []
    px, py = preferred_xy
    best = None
    best_dist_sq = float("inf")

    def _is_valid(c: int, r: int):
        if for_heavy:
            return _is_tile_valid_for_heavy_spawn(room, c, r, blocked_tiles)
        return _is_tile_valid_for_spawn(room, c, r)

    for r in range(inner_min_row, inner_max_row + 1):
        for c in range(inner_min_col, inner_max_col + 1):
            if not _is_valid(c, r):
                continue
            wx = c * TILE_SIZE + TILE_SIZE // 2
            wy = r * TILE_SIZE + TILE_SIZE // 2
            if _position_overlaps_existing(wx, wy, existing, spacing):
                continue
            d2 = (wx - px) ** 2 + (wy - py) ** 2
            if d2 < best_dist_sq:
                best_dist_sq = d2
                best = (wx, wy)
    if best is not None:
        return best
    min_x, min_y, max_x, max_y = room.playable_bounds_pixels()
    return ((min_x + max_x) / 2.0, (min_y + max_y) / 2.0)


def ensure_valid_spawn_position(
    room,
    world_x: float,
    world_y: float,
    existing_positions: List[Tuple[float, float]] | None = None,
    rng=None,
    for_heavy: bool = False,
    blocked_tiles: Set[Tuple[int, int]] | None = None,
) -> Tuple[float, float]:
    """
    Validate spawn position; if invalid, try up to SPAWN_VALIDATION_RETRY_NEARBY_ATTEMPTS nearby positions.
    If still none valid, return nearest valid walkable tile in room.
    When for_heavy=True, also require Heavy wall/corner clearance and (if blocked_tiles) clearance from solid props.
    """
    if rng is None:
        rng = random.Random()
    existing = existing_positions or []
    spacing = MIN_DISTANCE_BETWEEN_ENEMIES_PX
    col = int(world_x // TILE_SIZE)
    row = int(world_y // TILE_SIZE)

    def is_valid_tile(room, c, r):
        if for_heavy:
            return _is_tile_valid_for_heavy_spawn(room, c, r, blocked_tiles)
        return _is_tile_valid_for_spawn(room, c, r)
    # Initial position valid?
    if (
        0 <= col < room.width
        and 0 <= row < room.height
        and is_valid_tile(room, col, row)
        and not _position_overlaps_existing(world_x, world_y, existing, spacing)
    ):
        return (world_x, world_y)

    wall_b = room.wall_border()
    wall_margin = MIN_TILES_FROM_WALL_HEAVY if for_heavy else MIN_TILES_FROM_WALL
    playable_min_row = wall_b
    playable_max_row = room.height - wall_b - 1
    playable_min_col = wall_b
    playable_max_col = room.width - wall_b - 1
    inner_min_row = max(playable_min_row + wall_margin, playable_min_row)
    inner_max_row = min(playable_max_row - wall_margin, playable_max_row)
    inner_min_col = max(playable_min_col + wall_margin, playable_min_col)
    inner_max_col = min(playable_max_col - wall_margin, playable_max_col)
    radius = SPAWN_NEARBY_TILES_RADIUS

    for _ in range(SPAWN_VALIDATION_RETRY_NEARBY_ATTEMPTS):
        nc = col + rng.randint(-radius, radius)
        nr = row + rng.randint(-radius, radius)
        nc = max(inner_min_col, min(inner_max_col, nc))
        nr = max(inner_min_row, min(inner_max_row, nr))
        if not is_valid_tile(room, nc, nr):
            continue
        wx = nc * TILE_SIZE + TILE_SIZE // 2
        wy = nr * TILE_SIZE + TILE_SIZE // 2
        if _position_overlaps_existing(wx, wy, existing, spacing):
            continue
        return (wx, wy)

    return _nearest_valid_spawn_in_room(room, (world_x, world_y), existing, for_heavy=for_heavy, blocked_tiles=blocked_tiles if for_heavy else None)


def generate_valid_spawn_position(
    room,
    player_center_xy: Tuple[float, float],
    existing_positions: List[Tuple[float, float]],
    is_elite: bool = False,
    rng=None,
    for_heavy: bool = False,
) -> Tuple[float, float]:
    """
    Return (x, y) world center for one enemy spawn.
    Respects: MIN_DISTANCE_FROM_PLAYER, MIN_TILES_FROM_WALL (or MIN_TILES_FROM_WALL_HEAVY if for_heavy),
    MIN_TILES_FROM_DOOR, MIN_DISTANCE_BETWEEN_ENEMIES (plus ELITE_EXTRA_SPACING_PX if is_elite).
    When for_heavy=True, also excludes corner zones (MIN_TILES_FROM_CORNER_HEAVY).
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

    wall_margin = MIN_TILES_FROM_WALL_HEAVY if for_heavy else MIN_TILES_FROM_WALL
    if playable_min_row > playable_max_row or playable_min_col > playable_max_col:
        min_x, min_y, max_x, max_y = room.playable_bounds_pixels()
        return ((min_x + max_x) / 2.0, (min_y + max_y) / 2.0)

    # Inner playable band: at least wall_margin away from playable edge
    inner_min_row = playable_min_row + wall_margin
    inner_max_row = playable_max_row - wall_margin
    inner_min_col = playable_min_col + wall_margin
    inner_max_col = playable_max_col - wall_margin
    if inner_min_row > inner_max_row:
        inner_min_row = inner_max_row = (playable_min_row + playable_max_row) // 2
    if inner_min_col > inner_max_col:
        inner_min_col = inner_max_col = (playable_min_col + playable_max_col) // 2

    spacing = MIN_DISTANCE_BETWEEN_ENEMIES_PX
    if is_elite:
        spacing += ELITE_EXTRA_SPACING_PX

    is_valid_tile = _is_tile_valid_for_heavy_spawn if for_heavy else _is_tile_valid_for_spawn
    px, py = player_center_xy
    door_positions = getattr(room, "door_positions_world", None)
    if door_positions is None:
        door_positions = []

    min_x, min_y, max_x, max_y = room.playable_bounds_pixels()
    center_fallback = ((min_x + max_x) / 2.0, (min_y + max_y) / 2.0)

    for _ in range(MAX_SPAWN_ATTEMPTS):
        row = rng.randint(inner_min_row, inner_max_row)
        col = rng.randint(inner_min_col, inner_max_col)
        if not is_valid_tile(room, col, row):
            continue
        x = col * TILE_SIZE + TILE_SIZE // 2
        y = row * TILE_SIZE + TILE_SIZE // 2

        # 1) Distance from player
        dist_to_player = math.hypot(x - px, y - py)
        if dist_to_player < MIN_DISTANCE_FROM_PLAYER_PX:
            continue

        # 2) Door proximity
        too_close_to_door = False
        for (dx, dy) in door_positions:
            if math.hypot(x - dx, y - dy) < MIN_TILES_FROM_DOOR * TILE_SIZE:
                too_close_to_door = True
                break
        if too_close_to_door:
            continue

        # 3) Prevent overlapping existing spawns
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

    return _nearest_valid_spawn_in_room(room, center_fallback, existing_positions, for_heavy=for_heavy)


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
    offset_px: float | None = None,
) -> List[Tuple[float, float]]:
    """Triangle formation: one base position, then three at base + (0,0), (-offset, offset), (offset, offset)."""
    setattr(room, "door_positions_world", door_positions)
    base_xy = generate_valid_spawn_position(room, player_center_xy, [], is_elite=is_elite, rng=rng)
    bx, by = base_xy
    off = offset_px if offset_px is not None else TRIANGLE_OFFSET_PX
    offsets = [
        (0, 0),
        (-off, off),
        (off, off),
    ]
    min_x, min_y, max_x, max_y = room.playable_bounds_pixels()
    positions = []
    for (dx, dy) in offsets:
        x = max(min_x, min(max_x, bx + dx))
        y = max(min_y, min(max_y, by + dy))
        x, y = ensure_valid_spawn_position(room, x, y, existing_positions=positions, rng=rng)
        positions.append((x, y))
    return positions


def spawn_ambush(
    room,
    player_center_xy: Tuple[float, float],
    count: int,
    rng,
    radius_px: float | None = None,
) -> List[Tuple[float, float]]:
    """Ambush pattern: count enemies around player at radius_px (or AMBUSH_SPAWN_RADIUS_PX), evenly spaced by angle. Clamped to playable."""
    px, py = player_center_xy
    min_x, min_y, max_x, max_y = room.playable_bounds_pixels()
    radius = radius_px if radius_px is not None else AMBUSH_SPAWN_RADIUS_PX
    positions = []
    for i in range(count):
        angle_deg = (360.0 / max(1, count)) * i
        angle_rad = math.radians(angle_deg)
        dx = math.cos(angle_rad) * radius
        dy = math.sin(angle_rad) * radius
        x = max(min_x, min(max_x, px + dx))
        y = max(min_y, min(max_y, py + dy))
        x, y = ensure_valid_spawn_position(room, x, y, existing_positions=positions, rng=rng)
        positions.append((x, y))
    return positions
