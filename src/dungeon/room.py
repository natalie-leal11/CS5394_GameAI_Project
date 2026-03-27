# Phase 7: Room data and layout. One room at a time; deterministic from SEED + room_index.

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum

from game.config import (
    TILE_SIZE,
    SEED,
    LOGICAL_W,
    LOGICAL_H,
    PLAYER_MOVEMENT_HITBOX_W,
    PLAYER_MOVEMENT_HITBOX_H,
    USE_BIOME2,
    USE_BIOME3,
    USE_BIOME4,
    BIOME1_ROOM_COUNT,
    BIOME2_ROOM_COUNT,
    BIOME2_START_INDEX,
    BIOME3_ROOM_COUNT,
    BIOME3_START_INDEX,
    BIOME4_ROOM_COUNT,
    BIOME4_START_INDEX,
)
from game.rng import channel_key, derive_seed


def total_campaign_rooms() -> int:
    """Total rooms: 8 (Biome 1), +8 if USE_BIOME2, +8 if USE_BIOME3, +6 if USE_BIOME4 (Biome 4)."""
    n = BIOME1_ROOM_COUNT
    if USE_BIOME2:
        n += BIOME2_ROOM_COUNT
    if USE_BIOME3:
        n += BIOME3_ROOM_COUNT
    if USE_BIOME4:
        n += BIOME4_ROOM_COUNT
    return n


class RoomType(str, Enum):
    START = "START"
    CORRIDOR = "CORRIDOR"
    COMBAT = "COMBAT"
    AMBUSH = "AMBUSH"
    SAFE = "SAFE"
    ELITE = "ELITE"
    MINI_BOSS = "MINI_BOSS"
    FINAL_BOSS = "FINAL_BOSS"


# Tile kinds for the grid (inner tiles only; walls are implicit at edges or from layout).
TILE_FLOOR = "floor"
TILE_LAVA = "lava"
TILE_SLOW = "slow"
TILE_WALL = "wall"

# Minimum tiles between door (entrance/exit) and lava/slow so player can enter/leave safely.
DOOR_HAZARD_MARGIN = 3

# Wall border thickness in tiles (32px each). Standard = 2; ambush = 4. Playable = grid minus 2*border.
def wall_border_thickness(room_type: RoomType) -> int:
    """Return wall border thickness in tiles. Ambush = 4; standard combat/safe/start/elite/mini_boss/final_boss = 2."""
    if room_type == RoomType.AMBUSH:
        return 4
    return 2


def _room_grid_size() -> tuple[int, int]:
    """Room cols × rows from viewport so room fills the screen. cols = screen_w // 32, rows = screen_h // 32."""
    cols = LOGICAL_W // TILE_SIZE
    rows = LOGICAL_H // TILE_SIZE
    return (cols, rows)


def _room_order_biome1(seed: int) -> list[RoomType]:
    """Biome 1 rooms 0-7. SRS §4.1.4 distribution + seed shuffle (Beginner Test Mode = fixed order)."""
    from dungeon.srs_biome_order import room_order_biome1_srs

    return room_order_biome1_srs(seed)


def _hazard_counts_for_room(biome_index: int, room_type: RoomType) -> tuple[int, int]:
    """
    Deterministic hazard counts independent of seed.
    Hazards depend only on biome_index and room_type.
    """
    if room_type in (RoomType.START, RoomType.SAFE):
        return (0, 0)
    if room_type == RoomType.FINAL_BOSS:
        return (10, 5)

    # AMBUSH / MINI_BOSS / CORRIDOR follow COMBAT style for their biome.
    key = room_type
    if room_type in (RoomType.AMBUSH, RoomType.MINI_BOSS, RoomType.CORRIDOR):
        key = RoomType.COMBAT

    table: dict[int, dict[RoomType, tuple[int, int]]] = {
        1: {
            RoomType.COMBAT: (8, 20),   # lava 5–10, slow 15–25
            RoomType.ELITE: (10, 25),   # lava 8–12, slow 20–30
        },
        2: {
            RoomType.COMBAT: (11, 25),  # lava 8–14, slow 20–30
            RoomType.ELITE: (15, 30),   # lava 12–18, slow 25–35
        },
        3: {
            RoomType.COMBAT: (14, 30),  # lava 10–18, slow 25–35
            RoomType.ELITE: (18, 35),   # lava 14–22, slow 30–40
        },
        4: {
            RoomType.COMBAT: (16, 35),  # lava 12–20, slow 30–40
            RoomType.ELITE: (20, 40),   # lava 16–24, slow 35–45
        },
    }
    biome_map = table.get(int(biome_index), table[1])
    return biome_map.get(key, biome_map[RoomType.COMBAT])


def _placement_rng(room_index: int, biome_index: int, room_type: RoomType, phase: str) -> random.Random:
    """
    PRNG for hazard *placement* only. Uses fixed config.SEED + room geometry — not run_seed —
    so counts stay independent of run seed while layouts stay reproducible per room.
    """
    s = derive_seed(
        int(SEED),
        int(room_index),
        int(biome_index),
        channel_key(f"hazard_scatter_{phase}"),
        channel_key(room_type.value),
    )
    return random.Random(s)


def _would_form_three_in_line(
    grid: list[list[str]],
    height: int,
    width: int,
    r: int,
    c: int,
    tile: str,
) -> bool:
    """True if setting (r,c) to `tile` would create a contiguous run of 3+ on row, column, or diagonal."""
    dirs = ((0, 1), (1, 0), (1, 1), (1, -1))

    def at(rr: int, cc: int) -> str:
        if rr == r and cc == c:
            return tile
        return grid[rr][cc]

    for dr, dc in dirs:
        total = 1
        rr, cc = r + dr, c + dc
        while 0 <= rr < height and 0 <= cc < width and at(rr, cc) == tile:
            total += 1
            rr += dr
            cc += dc
        rr, cc = r - dr, c - dc
        while 0 <= rr < height and 0 <= cc < width and at(rr, cc) == tile:
            total += 1
            rr -= dr
            cc -= dc
        if total >= 3:
            return True
    return False


def _scatter_place_tiles(
    grid: list[list[str]],
    height: int,
    width: int,
    candidates: list[tuple[int, int]],
    n_place: int,
    tile: str,
    rng: random.Random,
) -> None:
    """
    Scatter `n_place` hazard tiles onto floor cells from `candidates` using shuffled sampling.
    Prefer placements that do not form 3-in-a-row lines (cardinal + diagonal); relax if needed
    to preserve exact counts.
    """
    if n_place <= 0:
        return
    pool = [(r, c) for r, c in candidates if grid[r][c] == TILE_FLOOR]
    rng.shuffle(pool)
    placed = 0
    deferred: list[tuple[int, int]] = []
    for r, c in pool:
        if placed >= n_place:
            break
        if grid[r][c] != TILE_FLOOR:
            continue
        if _would_form_three_in_line(grid, height, width, r, c, tile):
            deferred.append((r, c))
            continue
        grid[r][c] = tile
        placed += 1
    rng.shuffle(deferred)
    for r, c in deferred:
        if placed >= n_place:
            break
        if grid[r][c] != TILE_FLOOR:
            continue
        grid[r][c] = tile
        placed += 1
    if placed < n_place:
        remainder = [(r, c) for r, c in candidates if grid[r][c] == TILE_FLOOR]
        rng.shuffle(remainder)
        for r, c in remainder:
            if placed >= n_place:
                break
            grid[r][c] = tile
            placed += 1


def _make_tile_grid(width: int, height: int, room_type: RoomType, room_index: int, seed: int, biome_index: int) -> list[list[str]]:
    """Fill grid with floor; lava/slow counts from biome+room_type; scattered placement (not run_seed-driven)."""
    grid = [[TILE_FLOOR for _ in range(width)] for _ in range(height)]
    border = wall_border_thickness(room_type)
    # Playable tile indices: row [border, height-border), col [border, width-border)
    r0, r1 = border, height - border
    c0, c1 = border, width - border

    if room_type == RoomType.START or room_type == RoomType.SAFE:
        # SAFE and START must always be hazard-free.
        return grid

    # Reserve center 3x3 of playable area as safe zone (no lava/slow).
    cx, cy = (c0 + c1) // 2, (r0 + r1) // 2
    safe_r0 = max(r0, cy - 1)
    safe_r1 = min(r1, cy + 2)
    safe_c0 = max(c0, cx - 1)
    safe_c1 = min(c1, cx + 2)

    # Reserve door-adjacent zones: no lava/slow near exit (right, bottom) or entrance (left, bottom).
    margin = DOOR_HAZARD_MARGIN
    exit_safe_c_min = c1 - margin  # exit door is at cols w-2, w-1; playable ends at c1
    exit_safe_r_min = r1 - margin  # exit door at bottom 2 rows
    entrance_safe_c_max = c0 + margin
    entrance_safe_r_min = r1 - margin

    n_lava, n_slow = _hazard_counts_for_room(int(biome_index), room_type)

    cells: list[tuple[int, int]] = []
    for r in range(r0, r1):
        for c in range(c0, c1):
            if safe_r0 <= r < safe_r1 and safe_c0 <= c < safe_c1:
                continue
            # Exclude exit door zone (bottom-right of playable)
            if c >= exit_safe_c_min and r >= exit_safe_r_min:
                continue
            # Exclude entrance door zone (bottom-left) for rooms 1–7
            if room_index > 0 and c < entrance_safe_c_max and r >= entrance_safe_r_min:
                continue
            cells.append((r, c))

    max_cells = len(cells)
    n_lava = max(0, min(int(n_lava), max_cells))
    n_slow = max(0, min(int(n_slow), max_cells - n_lava))

    h, w = height, width
    rng_lava = _placement_rng(room_index, biome_index, room_type, "lava")
    _scatter_place_tiles(grid, h, w, cells, n_lava, TILE_LAVA, rng_lava)
    rng_slow = _placement_rng(room_index, biome_index, room_type, "slow")
    _scatter_place_tiles(grid, h, w, cells, n_slow, TILE_SLOW, rng_slow)

    return grid


def _choose_spawn_tile(
    width: int, height: int, grid: list[list[str]], border: int
) -> tuple[int, int]:
    """Pick a safe (floor) tile for player spawn inside playable area; prefer center."""
    r0, r1 = border, height - border
    c0, c1 = border, width - border
    cx, cy = (c0 + c1) // 2, (r0 + r1) // 2
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            r = min(max(r0, cy + dr), r1 - 1)
            c = min(max(c0, cx + dc), c1 - 1)
            if grid[r][c] == TILE_FLOOR:
                return (c, r)
    for r in range(r0, r1):
        for c in range(c0, c1):
            if grid[r][c] == TILE_FLOOR:
                return (c, r)
    return (cx, cy)


@dataclass
class Room:
    """Single dungeon room: index 0-7, type, hazard layout, spawn tile."""

    room_index: int
    biome_index: int = 1
    room_type: RoomType = RoomType.COMBAT
    hazard_percentage: float = 0.0  # Summary (e.g. lava+slow fraction) for display/tuning
    width: int = 12
    height: int = 12
    tile_grid: list[list[str]] = field(default_factory=list)
    spawn_tile: tuple[int, int] = (0, 0)

    @property
    def pixel_width(self) -> int:
        return self.width * TILE_SIZE

    @property
    def pixel_height(self) -> int:
        return self.height * TILE_SIZE

    def world_pos_for_tile(self, tx: int, ty: int) -> tuple[float, float]:
        """Center of tile in world coordinates."""
        x = (tx + 0.5) * TILE_SIZE
        y = (ty + 0.5) * TILE_SIZE
        return (x, y)

    def tile_at_world(self, wx: float, wy: float) -> tuple[int, int]:
        """Tile index for world position (clamped to room)."""
        tx = int(wx // TILE_SIZE)
        ty = int(wy // TILE_SIZE)
        tx = max(0, min(self.width - 1, tx))
        ty = max(0, min(self.height - 1, ty))
        return (tx, ty)

    def get_tile_type(self, tx: int, ty: int) -> str:
        if 0 <= ty < len(self.tile_grid) and 0 <= tx < len(self.tile_grid[0]):
            return self.tile_grid[ty][tx]
        return TILE_FLOOR

    def is_safe_tile(self, tx: int, ty: int) -> bool:
        return self.get_tile_type(tx, ty) == TILE_FLOOR

    def wall_border(self) -> int:
        """Wall border thickness in tiles (2 or 4)."""
        return wall_border_thickness(self.room_type)

    def is_tile_in_wall_band(self, tx: int, ty: int) -> bool:
        """True if (tx, ty) is in the wall border band (solid)."""
        b = self.wall_border()
        return (
            ty < b or ty >= self.height - b or tx < b or tx >= self.width - b
        )

    def playable_bounds_for_half_extents(
        self, half_w: float, half_h: float
    ) -> tuple[float, float, float, float]:
        """Inclusive world bounds for an entity center given half-width/half-height of its AABB.

        Inner edges of the wall band are at ``b*TILE`` and ``(width-b)*TILE`` / ``(height-b)*TILE``.
        Center (cx, cy) is valid if the axis-aligned box stays inside those edges (same rule as
        wall collision). Use movement half extents (player movement box; enemy ``movement_size`` /
        config), not full sprite/combat hitbox.
        """
        b = self.wall_border()
        inner_w = self.width - 2 * b
        inner_h = self.height - 2 * b
        if inner_w <= 0 or inner_h <= 0:
            cx = (self.width // 2) + 0.5
            cy = (self.height // 2) + 0.5
            p = cx * TILE_SIZE
            q = cy * TILE_SIZE
            return (p, q, p, q)
        min_x = b * TILE_SIZE + half_w
        min_y = b * TILE_SIZE + half_h
        max_x = (self.width - b) * TILE_SIZE - half_w
        max_y = (self.height - b) * TILE_SIZE - half_h
        if min_x > max_x or min_y > max_y:
            cx = (self.width // 2) + 0.5
            cy = (self.height // 2) + 0.5
            p = cx * TILE_SIZE
            q = cy * TILE_SIZE
            return (p, q, p, q)
        return (min_x, min_y, max_x, max_y)

    def playable_bounds_pixels(self) -> tuple[float, float, float, float]:
        """Bounds for player movement body center (Player.world_pos). See ``playable_bounds_for_half_extents``."""
        return self.playable_bounds_for_half_extents(
            PLAYER_MOVEMENT_HITBOX_W * 0.5, PLAYER_MOVEMENT_HITBOX_H * 0.5
        )

    def get_valid_enemy_spawn_tiles(
        self,
        door_tile_set: set[tuple[int, int]],
        exclude_radius_tiles: int = 4,
        min_dist_from_wall_tiles: int = 3,
        max_retries: int = 50,
    ) -> list[tuple[int, int]]:
        """Tiles valid for enemy spawn: playable, floor, ≥min_dist_from_wall_tiles from wall, ≥exclude_radius_tiles from spawn, not within 3 of doors."""
        b = self.wall_border()
        r0, r1 = b + min_dist_from_wall_tiles, self.height - b - min_dist_from_wall_tiles
        c0, c1 = b + min_dist_from_wall_tiles, self.width - b - min_dist_from_wall_tiles
        if r0 >= r1 or c0 >= c1:
            return []
        out = []
        stx, sty = self.spawn_tile
        for r in range(r0, r1):
            for c in range(c0, c1):
                if self.get_tile_type(c, r) != TILE_FLOOR:
                    continue
                if abs(c - stx) <= exclude_radius_tiles and abs(r - sty) <= exclude_radius_tiles:
                    continue
                near_door = False
                for (dx, dy) in door_tile_set:
                    if abs(c - dx) <= 3 and abs(r - dy) <= 3:
                        near_door = True
                        break
                if near_door:
                    continue
                out.append((c, r))
        return out


def generate_room(campaign_index: int, seed: int | None = None) -> Room:
    """
    Generate one room deterministically by campaign index.
    Campaign 0-7: Biome 1 rooms. Campaign 8-15: Biome 2 rooms (when USE_BIOME2).
    """
    if seed is None:
        seed = SEED
    total = total_campaign_rooms()
    if campaign_index < 0 or campaign_index >= total:
        raise ValueError(f"Campaign index must be 0-{total - 1}, got {campaign_index}")

    if campaign_index < BIOME2_START_INDEX:
        # Biome 1
        order = _room_order_biome1(seed)
        room_type = order[campaign_index]
        biome_index = 1
    elif campaign_index < BIOME3_START_INDEX:
        # Biome 2
        from dungeon.biome2_sequence import room_order_biome2
        order = room_order_biome2(seed)
        local_idx = campaign_index - BIOME2_START_INDEX
        room_type = order[local_idx]
        biome_index = 2
    elif campaign_index < BIOME4_START_INDEX:
        # Biome 3
        from dungeon.biome3_sequence import room_order_biome3
        order = room_order_biome3(seed)
        local_idx = campaign_index - BIOME3_START_INDEX
        room_type = order[local_idx]
        biome_index = 3
    else:
        # Biome 4 (rooms 24-29)
        from dungeon.biome4_sequence import room_order_biome4
        order = room_order_biome4(seed)
        local_idx = campaign_index - BIOME4_START_INDEX
        room_type = order[local_idx]
        biome_index = 4

    width, height = _room_grid_size()
    grid = _make_tile_grid(width, height, room_type, campaign_index, seed, biome_index)
    border = wall_border_thickness(room_type)
    spawn_tile = _choose_spawn_tile(width, height, grid, border)
    total_cells = width * height
    hazard_count = sum(1 for row in grid for c in row if c in (TILE_LAVA, TILE_SLOW))
    hazard_percentage = hazard_count / total_cells if total_cells else 0.0
    return Room(
        room_index=campaign_index,
        biome_index=biome_index,
        room_type=room_type,
        hazard_percentage=hazard_percentage,
        width=width,
        height=height,
        tile_grid=grid,
        spawn_tile=spawn_tile,
    )
