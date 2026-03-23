# Advanced enemy spawn: safe position generator and patterns (spread, triangle, ambush).
# Valid spawn = inside playable bounds, not wall, not decorative obstacles, no overlap with other enemies.
# Lava and slow are allowed (enemies do not take hazard damage).

import math
import random
from typing import List, Set, Tuple

from dungeon.room import TILE_FLOOR, TILE_LAVA, TILE_SLOW
from game.config import (
    TILE_SIZE,
    enemy_movement_half_extents,
    enemy_movement_size_tuple,
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
    SPAWN_EXTRA_INTERIOR_WALL_TILES,
    SPAWN_CORNER_ZONE_TILES,
    SPAWN_MIN_NEIGHBOR_WALKABLE,
    SPAWN_MIN_NEIGHBOR_WALKABLE_HEAVY,
    SPAWN_DEBUG_LOG,
    DEBUG_HEAVY_SPAWN,
)
from systems.collisions import tile_range_for_centered_aabb


# Walkable tile types for enemy spawn (lava/slow allowed; enemies do not take hazard damage).
_VALID_SPAWN_TILE_TYPES = (TILE_FLOOR, TILE_LAVA, TILE_SLOW)

# When SPAWN_DEBUG_LOG: log [PLAYABLE BOUNDS] at most once per room index.
_PLAYABLE_BOUNDS_LOGGED: set[int] = set()


def _effective_spawn_enemy_type(for_heavy: bool, enemy_type: str) -> str:
    """Heavy tile rules + movement clamp use heavy movement body."""
    return "heavy" if for_heavy else enemy_type


def _spawn_playable_bounds(room, enemy_type: str) -> Tuple[float, float, float, float]:
    """Playable AABB aligned with movement half extents for this spawn type (not generic clamp)."""
    hw, hh = enemy_movement_half_extents(enemy_type)
    return room.playable_bounds_for_half_extents(hw, hh)


def _is_tile_valid_for_spawn(room, col: int, row: int) -> bool:
    """True if (col, row) is inside playable bounds, not a wall, and not a decorative obstacle. Lava and slow are allowed."""
    if room.is_tile_in_wall_band(col, row):
        return False
    return room.get_tile_type(col, row) in _VALID_SPAWN_TILE_TYPES


def _room_debug_id(room) -> int:
    return int(getattr(room, "room_index", -1))


def _spawn_log_enabled(*, for_heavy: bool) -> bool:
    return bool(SPAWN_DEBUG_LOG or (for_heavy and DEBUG_HEAVY_SPAWN))


def _spawn_reject_log(
    room, reason: str, world_x: float, world_y: float, *, for_heavy: bool = False
) -> None:
    if not _spawn_log_enabled(for_heavy=for_heavy):
        return
    tag = "enemy=heavy " if for_heavy else ""
    print(
        f"[SPAWN REJECT] {tag}reason={reason} room={_room_debug_id(room)} x={world_x:.1f} y={world_y:.1f}"
    )


def _log_playable_bounds_once(room, enemy_type: str = "swarm") -> None:
    if not SPAWN_DEBUG_LOG:
        return
    rid = _room_debug_id(room)
    if rid in _PLAYABLE_BOUNDS_LOGGED:
        return
    _PLAYABLE_BOUNDS_LOGGED.add(rid)
    min_x, min_y, max_x, max_y = _spawn_playable_bounds(room, enemy_type)
    print(
        f"[PLAYABLE BOUNDS] room={rid} enemy_type={enemy_type} min_x={min_x:.1f} min_y={min_y:.1f} "
        f"max_x={max_x:.1f} max_y={max_y:.1f}"
    )


def _spawn_accept_log(room, world_x: float, world_y: float, *, for_heavy: bool = False) -> None:
    if not _spawn_log_enabled(for_heavy=for_heavy):
        return
    col, row = room.tile_at_world(world_x, world_y)
    in_band = room.is_tile_in_wall_band(col, row)
    tag = "enemy=heavy " if for_heavy else ""
    print(
        f"[SPAWN ACCEPT] {tag}room={_room_debug_id(room)} tile=({col},{row}) "
        f"x={world_x:.1f} y={world_y:.1f} in_wall_band={in_band}"
    )


def _spawn_check_debug(room, wx: float, wy: float, enemy_type: str = "swarm") -> None:
    """Temporary: final-position validation probe (toggle SPAWN_DEBUG_LOG)."""
    if not SPAWN_DEBUG_LOG:
        return
    _log_playable_bounds_once(room, enemy_type)
    col, row = room.tile_at_world(wx, wy)
    in_band = room.is_tile_in_wall_band(col, row)
    print(
        f"[SPAWN CHECK] room={_room_debug_id(room)} tile=({col},{row}) "
        f"x={wx:.1f} y={wy:.1f} in_wall_band={in_band}"
    )


def _hard_corner_zone(room, col: int, row: int, cz: int) -> bool:
    """True if (col,row) lies in an axis-aligned corner pocket (too close to two perpendicular outer edges)."""
    if cz <= 0:
        return False
    b = room.wall_border()
    pmin_c, pmax_c = b, room.width - b - 1
    pmin_r, pmax_r = b, room.height - b - 1
    dl = col - pmin_c
    dr = pmax_c - col
    dt = row - pmin_r
    db = pmax_r - row
    if dl < cz and dt < cz:
        return True
    if dr < cz and dt < cz:
        return True
    if dl < cz and db < cz:
        return True
    if dr < cz and db < cz:
        return True
    return False


def _local_neighbor_walkable_count(room, col: int, row: int) -> int:
    """Count 8-neighbor tiles that pass basic walkable spawn check (in-bounds)."""
    n = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            c2, r2 = col + dc, row + dr
            if not (0 <= c2 < room.width and 0 <= r2 < room.height):
                continue
            if _is_tile_valid_for_spawn(room, c2, r2):
                n += 1
    return n


def _reject_reason_standard_spawn(room, col: int, row: int) -> str | None:
    """None if tile is acceptable for normal spawns; else a short reason for debug."""
    if not _is_tile_valid_for_spawn(room, col, row):
        return "invalid_tile"
    b = room.wall_border()
    pmin_c, pmax_c = b, room.width - b - 1
    pmin_r, pmax_r = b, room.height - b - 1
    wm = MIN_TILES_FROM_WALL + SPAWN_EXTRA_INTERIOR_WALL_TILES
    if col < pmin_c + wm or col > pmax_c - wm or row < pmin_r + wm or row > pmax_r - wm:
        return "edge_margin"
    if _hard_corner_zone(room, col, row, SPAWN_CORNER_ZONE_TILES):
        return "corner"
    if _local_neighbor_walkable_count(room, col, row) < SPAWN_MIN_NEIGHBOR_WALKABLE:
        return "low_clearance"
    return None


def _is_tile_good_standard_spawn(room, col: int, row: int) -> bool:
    """Walkable tile plus interior margin, hard corner exclusion, and local clearance."""
    return _reject_reason_standard_spawn(room, col, row) is None


def _validate_final_spawn_world(
    room,
    wx: float,
    wy: float,
    for_heavy: bool,
    blocked_tiles: Set[Tuple[int, int]] | None,
    enemy_type: str = "swarm",
) -> str | None:
    """Re-validate tile under final world position (post-clamp). None = acceptable."""
    et = _effective_spawn_enemy_type(for_heavy, enemy_type)
    _spawn_check_debug(room, wx, wy, et)
    col, row = room.tile_at_world(wx, wy)
    if room.is_tile_in_wall_band(col, row):
        return "wall_band"
    if not (0 <= col < room.width and 0 <= row < room.height):
        return "invalid_tile"
    if for_heavy:
        return _reject_reason_heavy_spawn(room, col, row, blocked_tiles)
    return _reject_reason_standard_spawn(room, col, row)


def _first_valid_spawn_row_major(
    room,
    for_heavy: bool,
    blocked_tiles: Set[Tuple[int, int]] | None,
    existing_positions: List[Tuple[float, float]],
    spacing: float,
) -> Tuple[float, float] | None:
    """Deterministic first valid spawn (row-major scan) for fallback when preferred position fails final check."""
    wall_b = room.wall_border()
    existing = existing_positions or []
    for r in range(wall_b, room.height - wall_b):
        for c in range(wall_b, room.width - wall_b):
            if for_heavy:
                if _reject_reason_heavy_spawn(room, c, r, blocked_tiles) is not None:
                    continue
            else:
                if _reject_reason_standard_spawn(room, c, r) is not None:
                    continue
            twx = c * TILE_SIZE + TILE_SIZE // 2
            twy = r * TILE_SIZE + TILE_SIZE // 2
            if _position_overlaps_existing(twx, twy, existing, spacing):
                continue
            return (twx, twy)
    return None


def _heavy_movement_body_tiles_clear(
    room,
    wx: float,
    wy: float,
    blocked_tiles: Set[Tuple[int, int]] | None,
) -> bool:
    """True if Heavy movement AABB at (wx,wy) does not overlap wall band or solid prop tiles."""
    mw, mh = enemy_movement_size_tuple("heavy")
    min_tx, max_tx, min_ty, max_ty = tile_range_for_centered_aabb(wx, wy, float(mw), float(mh))
    for ty in range(min_ty, max_ty + 1):
        for tx in range(min_tx, max_tx + 1):
            if tx < 0 or ty < 0 or tx >= room.width or ty >= room.height:
                return False
            if room.is_tile_in_wall_band(tx, ty):
                return False
            if blocked_tiles and (tx, ty) in blocked_tiles:
                return False
    return True


def _reject_reason_heavy_spawn(
    room, col: int, row: int, blocked_tiles: Set[Tuple[int, int]] | None = None
) -> str | None:
    """None if tile is acceptable for Heavy; else reason string."""
    if not _is_tile_valid_for_spawn(room, col, row):
        return "invalid_tile"
    # Stronger than standard spawns: avoid axis-aligned corner pockets + large body margin.
    cz = max(SPAWN_CORNER_ZONE_TILES + 1, MIN_TILES_FROM_CORNER_HEAVY + 2)
    if _hard_corner_zone(room, col, row, cz):
        return "corner"
    b = room.wall_border()
    if col < b + MIN_TILES_FROM_WALL_HEAVY or col >= room.width - b - MIN_TILES_FROM_WALL_HEAVY:
        return "edge_margin"
    if row < b + MIN_TILES_FROM_WALL_HEAVY or row >= room.height - b - MIN_TILES_FROM_WALL_HEAVY:
        return "edge_margin"
    if blocked_tiles:
        for (bx, by) in blocked_tiles:
            if max(abs(col - bx), abs(row - by)) <= HEAVY_MIN_TILES_FROM_PROP:
                return "low_clearance"
        cluster_radius = HEAVY_MIN_TILES_FROM_PROP + 1
        count_near = sum(1 for (bx, by) in blocked_tiles if max(abs(col - bx), abs(row - by)) <= cluster_radius)
        if count_near >= 2:
            return "low_clearance"
    if _local_neighbor_walkable_count(room, col, row) < SPAWN_MIN_NEIGHBOR_WALKABLE_HEAVY:
        return "low_clearance"
    tcx = col * TILE_SIZE + TILE_SIZE // 2
    twy = row * TILE_SIZE + TILE_SIZE // 2
    if not _heavy_movement_body_tiles_clear(room, float(tcx), float(twy), blocked_tiles):
        return "movement_body"
    return None


def _is_tile_valid_for_heavy_spawn(
    room, col: int, row: int, blocked_tiles: Set[Tuple[int, int]] | None = None
) -> bool:
    """True if tile is valid for spawn and satisfies Heavy constraints."""
    return _reject_reason_heavy_spawn(room, col, row, blocked_tiles) is None


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
    enemy_type: str = "swarm",
) -> Tuple[float, float]:
    """Return world (x,y) of the valid spawn tile closest to preferred_xy. Skip tiles that overlap existing_positions.
    When for_heavy=True, use Heavy wall/corner clearance and only tiles valid for Heavy. blocked_tiles = solid prop tiles to avoid."""
    wall_b = room.wall_border()
    rows, cols = room.height, room.width
    playable_min_row = wall_b
    playable_max_row = rows - wall_b - 1
    playable_min_col = wall_b
    playable_max_col = cols - wall_b - 1
    wall_margin = MIN_TILES_FROM_WALL_HEAVY if for_heavy else MIN_TILES_FROM_WALL + SPAWN_EXTRA_INTERIOR_WALL_TILES
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
        return _is_tile_good_standard_spawn(room, c, r)

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
    blocked = blocked_tiles if for_heavy else None
    et = _effective_spawn_enemy_type(for_heavy, enemy_type)
    if best is not None:
        vr = _validate_final_spawn_world(room, best[0], best[1], for_heavy, blocked, enemy_type=enemy_type)
        if vr is None:
            _spawn_accept_log(room, best[0], best[1], for_heavy=for_heavy)
            return best
        _spawn_reject_log(room, f"final_{vr}", best[0], best[1], for_heavy=for_heavy)
        alt = _first_valid_spawn_row_major(room, for_heavy, blocked, existing, spacing)
        if alt is not None:
            _spawn_accept_log(room, alt[0], alt[1], for_heavy=for_heavy)
            return alt
    min_x, min_y, max_x, max_y = _spawn_playable_bounds(room, et)
    cx = (min_x + max_x) / 2.0
    cy = (min_y + max_y) / 2.0
    if _validate_final_spawn_world(room, cx, cy, for_heavy, blocked, enemy_type=enemy_type) is None:
        _spawn_accept_log(room, cx, cy, for_heavy=for_heavy)
        return (cx, cy)
    alt2 = _first_valid_spawn_row_major(room, for_heavy, blocked, existing, spacing)
    if alt2 is not None:
        _spawn_accept_log(room, alt2[0], alt2[1], for_heavy=for_heavy)
        return alt2
    _spawn_accept_log(room, cx, cy, for_heavy=for_heavy)
    return (cx, cy)


def ensure_valid_spawn_position(
    room,
    world_x: float,
    world_y: float,
    existing_positions: List[Tuple[float, float]] | None = None,
    rng=None,
    for_heavy: bool = False,
    blocked_tiles: Set[Tuple[int, int]] | None = None,
    enemy_type: str = "swarm",
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

    def reject_at(c: int, r: int) -> str | None:
        if for_heavy:
            return _reject_reason_heavy_spawn(room, c, r, blocked_tiles if for_heavy else None)
        return _reject_reason_standard_spawn(room, c, r)

    blocked = blocked_tiles if for_heavy else None
    # Initial position: same structural rules as spread/ambush (not only raw walkable).
    if 0 <= col < room.width and 0 <= row < room.height:
        rr = reject_at(col, row)
        if rr is not None:
            _spawn_reject_log(room, rr, world_x, world_y, for_heavy=for_heavy)
        elif not _position_overlaps_existing(world_x, world_y, existing, spacing):
            fv = _validate_final_spawn_world(room, world_x, world_y, for_heavy, blocked, enemy_type=enemy_type)
            if fv is None:
                _spawn_accept_log(room, world_x, world_y, for_heavy=for_heavy)
                return (world_x, world_y)
            _spawn_reject_log(room, f"final_{fv}", world_x, world_y, for_heavy=for_heavy)
    else:
        _spawn_reject_log(room, "invalid_tile", world_x, world_y, for_heavy=for_heavy)

    wall_b = room.wall_border()
    wall_margin = MIN_TILES_FROM_WALL_HEAVY if for_heavy else MIN_TILES_FROM_WALL + SPAWN_EXTRA_INTERIOR_WALL_TILES
    playable_min_row = wall_b
    playable_max_row = room.height - wall_b - 1
    playable_min_col = wall_b
    playable_max_col = room.width - wall_b - 1
    inner_min_row = max(playable_min_row + wall_margin, playable_min_row)
    inner_max_row = min(playable_max_row - wall_margin, playable_max_row)
    inner_min_col = max(playable_min_col + wall_margin, playable_min_col)
    inner_max_col = min(playable_max_col - wall_margin, playable_max_col)
    radius = SPAWN_NEARBY_TILES_RADIUS

    if inner_min_row > inner_max_row or inner_min_col > inner_max_col:
        return _nearest_valid_spawn_in_room(
            room,
            (world_x, world_y),
            existing,
            for_heavy=for_heavy,
            blocked_tiles=blocked_tiles if for_heavy else None,
            enemy_type=enemy_type,
        )

    for _ in range(SPAWN_VALIDATION_RETRY_NEARBY_ATTEMPTS):
        nc = col + rng.randint(-radius, radius)
        nr = row + rng.randint(-radius, radius)
        nc = max(inner_min_col, min(inner_max_col, nc))
        nr = max(inner_min_row, min(inner_max_row, nr))
        rr = reject_at(nc, nr)
        wx = nc * TILE_SIZE + TILE_SIZE // 2
        wy = nr * TILE_SIZE + TILE_SIZE // 2
        if rr is not None:
            _spawn_reject_log(room, rr, wx, wy, for_heavy=for_heavy)
            continue
        if _position_overlaps_existing(wx, wy, existing, spacing):
            continue
        fv = _validate_final_spawn_world(room, wx, wy, for_heavy, blocked, enemy_type=enemy_type)
        if fv is not None:
            _spawn_reject_log(room, f"final_{fv}", wx, wy, for_heavy=for_heavy)
            continue
        _spawn_accept_log(room, wx, wy, for_heavy=for_heavy)
        return (wx, wy)

    return _nearest_valid_spawn_in_room(
        room,
        (world_x, world_y),
        existing,
        for_heavy=for_heavy,
        blocked_tiles=blocked_tiles if for_heavy else None,
        enemy_type=enemy_type,
    )


def generate_valid_spawn_position(
    room,
    player_center_xy: Tuple[float, float],
    existing_positions: List[Tuple[float, float]],
    is_elite: bool = False,
    rng=None,
    for_heavy: bool = False,
    enemy_type: str = "swarm",
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

    spacing = MIN_DISTANCE_BETWEEN_ENEMIES_PX
    if is_elite:
        spacing += ELITE_EXTRA_SPACING_PX

    wall_b = room.wall_border()
    rows, cols = room.height, room.width
    playable_min_row = wall_b
    playable_max_row = rows - wall_b - 1
    playable_min_col = wall_b
    playable_max_col = cols - wall_b - 1

    wall_margin = MIN_TILES_FROM_WALL_HEAVY if for_heavy else MIN_TILES_FROM_WALL + SPAWN_EXTRA_INTERIOR_WALL_TILES
    et = _effective_spawn_enemy_type(for_heavy, enemy_type)
    if playable_min_row > playable_max_row or playable_min_col > playable_max_col:
        min_x, min_y, max_x, max_y = _spawn_playable_bounds(room, et)
        cx = (min_x + max_x) / 2.0
        cy = (min_y + max_y) / 2.0
        if _validate_final_spawn_world(room, cx, cy, for_heavy, None, enemy_type=enemy_type) is None:
            _spawn_accept_log(room, cx, cy, for_heavy=for_heavy)
            return (cx, cy)
        alt = _first_valid_spawn_row_major(room, for_heavy, None, existing_positions, spacing)
        if alt is not None:
            _spawn_accept_log(room, alt[0], alt[1], for_heavy=for_heavy)
            return alt
        _spawn_accept_log(room, cx, cy, for_heavy=for_heavy)
        return (cx, cy)

    # Inner playable band: at least wall_margin away from playable edge
    inner_min_row = playable_min_row + wall_margin
    inner_max_row = playable_max_row - wall_margin
    inner_min_col = playable_min_col + wall_margin
    inner_max_col = playable_max_col - wall_margin
    if inner_min_row > inner_max_row:
        inner_min_row = inner_max_row = (playable_min_row + playable_max_row) // 2
    if inner_min_col > inner_max_col:
        inner_min_col = inner_max_col = (playable_min_col + playable_max_col) // 2

    px, py = player_center_xy
    door_positions = getattr(room, "door_positions_world", None)
    if door_positions is None:
        door_positions = []

    min_x, min_y, max_x, max_y = _spawn_playable_bounds(room, et)
    center_fallback = ((min_x + max_x) / 2.0, (min_y + max_y) / 2.0)

    for _ in range(MAX_SPAWN_ATTEMPTS):
        row = rng.randint(inner_min_row, inner_max_row)
        col = rng.randint(inner_min_col, inner_max_col)
        if for_heavy:
            rr = _reject_reason_heavy_spawn(room, col, row, None)
        else:
            rr = _reject_reason_standard_spawn(room, col, row)
        if rr is not None:
            _spawn_reject_log(room, rr, col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2)
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
        fv = _validate_final_spawn_world(room, x, y, for_heavy, None, enemy_type=enemy_type)
        if fv is not None:
            _spawn_reject_log(room, f"final_{fv}", x, y, for_heavy=for_heavy)
            continue
        _spawn_accept_log(room, x, y, for_heavy=for_heavy)
        return (x, y)

    return _nearest_valid_spawn_in_room(
        room, center_fallback, existing_positions, for_heavy=for_heavy, enemy_type=enemy_type
    )


def spawn_spread(
    room,
    player_center_xy: Tuple[float, float],
    count: int,
    is_elite: bool,
    rng,
    door_positions: List[Tuple[float, float]],
    enemy_type: str = "swarm",
) -> List[Tuple[float, float]]:
    """Spread pattern: count random valid positions, spaced from each other and player."""
    setattr(room, "door_positions_world", door_positions)
    positions: List[Tuple[float, float]] = []
    for _ in range(count):
        x, y = generate_valid_spawn_position(
            room, player_center_xy, positions, is_elite=is_elite, rng=rng, enemy_type=enemy_type
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
    enemy_type: str = "swarm",
) -> List[Tuple[float, float]]:
    """Triangle formation: one base position, then three at base + (0,0), (-offset, offset), (offset, offset)."""
    setattr(room, "door_positions_world", door_positions)
    base_xy = generate_valid_spawn_position(
        room, player_center_xy, [], is_elite=is_elite, rng=rng, enemy_type=enemy_type
    )
    bx, by = base_xy
    off = offset_px if offset_px is not None else TRIANGLE_OFFSET_PX
    offsets = [
        (0, 0),
        (-off, off),
        (off, off),
    ]
    et = _effective_spawn_enemy_type(False, enemy_type)
    min_x, min_y, max_x, max_y = _spawn_playable_bounds(room, et)
    positions = []
    for (dx, dy) in offsets:
        x = max(min_x, min(max_x, bx + dx))
        y = max(min_y, min(max_y, by + dy))
        x, y = ensure_valid_spawn_position(
            room, x, y, existing_positions=positions, rng=rng, enemy_type=enemy_type
        )
        positions.append((x, y))
    return positions


def spawn_ambush(
    room,
    player_center_xy: Tuple[float, float],
    count: int,
    rng,
    radius_px: float | None = None,
    enemy_type: str = "swarm",
) -> List[Tuple[float, float]]:
    """Ambush pattern: count enemies around player at radius_px (or AMBUSH_SPAWN_RADIUS_PX), evenly spaced by angle. Clamped to playable."""
    px, py = player_center_xy
    et = _effective_spawn_enemy_type(False, enemy_type)
    min_x, min_y, max_x, max_y = _spawn_playable_bounds(room, et)
    radius = radius_px if radius_px is not None else AMBUSH_SPAWN_RADIUS_PX
    positions = []
    for i in range(count):
        angle_deg = (360.0 / max(1, count)) * i
        angle_rad = math.radians(angle_deg)
        dx = math.cos(angle_rad) * radius
        dy = math.sin(angle_rad) * radius
        x = max(min_x, min(max_x, px + dx))
        y = max(min_y, min(max_y, py + dy))
        x, y = ensure_valid_spawn_position(
            room, x, y, existing_positions=positions, rng=rng, enemy_type=enemy_type
        )
        positions.append((x, y))
    return positions
