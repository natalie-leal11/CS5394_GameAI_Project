# Phase 7: Room data and layout. One room at a time; deterministic from SEED + room_index.

from dataclasses import dataclass, field
from enum import Enum
import random

from game.config import (
    TILE_SIZE,
    SEED,
    LOGICAL_W,
    LOGICAL_H,
    HAZARD_LAVA_MAX_FRACTION,
    HAZARD_SLOW_MIN_FRACTION,
    HAZARD_SLOW_MAX_FRACTION,
    BEGINNER_TEST_MODE,
)


class RoomType(str, Enum):
    START = "START"
    CORRIDOR = "CORRIDOR"
    COMBAT = "COMBAT"
    AMBUSH = "AMBUSH"
    SAFE = "SAFE"
    ELITE = "ELITE"
    MINI_BOSS = "MINI_BOSS"


# Tile kinds for the grid (inner tiles only; walls are implicit at edges or from layout).
TILE_FLOOR = "floor"
TILE_LAVA = "lava"
TILE_SLOW = "slow"
TILE_WALL = "wall"

# Minimum tiles between door (entrance/exit) and lava/slow so player can enter/leave safely.
DOOR_HAZARD_MARGIN = 3

# Wall border thickness in tiles (32px each). Standard = 2; small/ambush = 4. Playable = grid minus 2*border.
def wall_border_thickness(room_type: RoomType) -> int:
    """Return wall border thickness in tiles. Ambush = 4; standard combat/safe/start/elite/mini_boss = 2."""
    if room_type == RoomType.AMBUSH:
        return 4
    return 2


def _room_grid_size() -> tuple[int, int]:
    """Room cols × rows from viewport so room fills the screen. cols = screen_w // 32, rows = screen_h // 32."""
    cols = LOGICAL_W // TILE_SIZE
    rows = LOGICAL_H // TILE_SIZE
    return (cols, rows)


def _room_order_biome1(seed: int) -> list[RoomType]:
    """Biome 1 rooms 0-7. Beginner Test Mode: fixed order (no shuffle). Otherwise deterministic shuffle."""
    if BEGINNER_TEST_MODE:
        # Fixed order per Biome1_Beginner_Test_Mode_Spec §4: 0 Start, 1-2 Combat, 3 Safe, 4 Combat, 5 Elite, 6 Ambush, 7 Mini Boss
        return [
            RoomType.START,
            RoomType.COMBAT,   # 1 Combat 1
            RoomType.COMBAT,   # 2 Combat 2
            RoomType.SAFE,    # 3 Safe
            RoomType.COMBAT,   # 4 Combat 3
            RoomType.ELITE,   # 5 Elite
            RoomType.AMBUSH,  # 6 Ambush
            RoomType.MINI_BOSS,  # 7 Mini Boss
        ]
    rng = random.Random(seed)
    mid = [RoomType.COMBAT, RoomType.COMBAT, RoomType.COMBAT, RoomType.SAFE, RoomType.ELITE, RoomType.AMBUSH]
    rng.shuffle(mid)
    return [RoomType.START] + mid + [RoomType.MINI_BOSS]


def _make_tile_grid(width: int, height: int, room_type: RoomType, room_index: int, seed: int) -> list[list[str]]:
    """Fill grid with floor; place lava/slow only in playable area; ensure one 3x3 safe zone. Deterministic."""
    rng = random.Random(seed + room_index * 1000)
    grid = [[TILE_FLOOR for _ in range(width)] for _ in range(height)]
    border = wall_border_thickness(room_type)
    # Playable tile indices: row [border, height-border), col [border, width-border)
    r0, r1 = border, height - border
    c0, c1 = border, width - border

    if room_type == RoomType.START or room_type == RoomType.SAFE:
        # No lava in Start or Safe; minimal/no slow in Safe per spec.
        if room_type == RoomType.SAFE:
            slow_pct = rng.uniform(0, min(0.05, HAZARD_SLOW_MAX_FRACTION))
            total = (r1 - r0) * (c1 - c0)
            n_slow = max(0, int(total * slow_pct))
            cells = [(r, c) for r in range(r0, r1) for c in range(c0, c1)]
            rng.shuffle(cells)
            for i, (r, c) in enumerate(cells):
                if i >= n_slow:
                    break
                grid[r][c] = TILE_SLOW
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

    total = (r1 - r0) * (c1 - c0)
    if BEGINNER_TEST_MODE:
        # §12: Lava 0-3%, Slow 5-8%, Safe ≥75%
        lava_cap = int(total * 0.03)
        slow_min = int(total * 0.05)
        slow_max = int(total * 0.08)
    else:
        lava_cap = int(total * HAZARD_LAVA_MAX_FRACTION)
        slow_min = int(total * HAZARD_SLOW_MIN_FRACTION)
        slow_max = int(total * HAZARD_SLOW_MAX_FRACTION)
    n_lava = rng.randint(0, max(0, lava_cap))
    n_slow = rng.randint(slow_min, min(slow_max, total - n_lava))

    cells = []
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
    rng.shuffle(cells)

    for i, (r, c) in enumerate(cells):
        if i < n_lava:
            grid[r][c] = TILE_LAVA
        elif i < n_lava + n_slow:
            grid[r][c] = TILE_SLOW
        # else stays floor

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

    def playable_bounds_pixels(self) -> tuple[float, float, float, float]:
        """(min_x, min_y, max_x, max_y) in world pixels for playable area."""
        b = self.wall_border()
        min_x = b * TILE_SIZE
        min_y = b * TILE_SIZE
        max_x = (self.width - b) * TILE_SIZE
        max_y = (self.height - b) * TILE_SIZE
        return (min_x, min_y, max_x, max_y)

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


def generate_room(room_index: int, seed: int | None = None) -> Room:
    """Generate one room deterministically. Room index 0-7 only. Grid size = viewport (fills screen)."""
    if seed is None:
        seed = SEED
    if room_index < 0 or room_index > 7:
        raise ValueError("Phase 7: only rooms 0-7")
    order = _room_order_biome1(seed)
    room_type = order[room_index]
    width, height = _room_grid_size()
    grid = _make_tile_grid(width, height, room_type, room_index, seed)
    border = wall_border_thickness(room_type)
    spawn_tile = _choose_spawn_tile(width, height, grid, border)
    total = width * height
    hazard_count = sum(1 for row in grid for c in row if c in (TILE_LAVA, TILE_SLOW))
    hazard_percentage = hazard_count / total if total else 0.0
    return Room(
        room_index=room_index,
        biome_index=1,
        room_type=room_type,
        hazard_percentage=hazard_percentage,
        width=width,
        height=height,
        tile_grid=grid,
        spawn_tile=spawn_tile,
    )
