"""
Deterministic room layout generation: tile grid + hazards within biome caps.
Same seed + room_index -> identical layout. Uses only rng.
"""
from typing import List, Tuple

from src.game import rng
from src.game.dungeon.room_types import (
    START, CORRIDOR, COMBAT, AMBUSH, SAFE_REST, ELITE, MINI_BOSS, FINAL_BOSS,
    BIOME_1_RANGE, BIOME_2_RANGE, BIOME_3_RANGE, BIOME_4_RANGE,
    FINAL_BOSS_INDEX,
)
from src.game.dungeon.hazard_validator import (
    NORMAL, LAVA, SLOW, WALL,
    get_biome_caps,
    validate_room,
)

# Grid sizes in tiles
SIZE_SMALL = 8   # 8x8
SIZE_MEDIUM = 12 # 12x12
SIZE_LARGE = 16  # 16x16


def _room_size(room_type: str) -> int:
    """Start, Elite, Boss -> Large; Combat, Safe, Corridor -> Medium; Ambush -> Small."""
    if room_type in (START, ELITE, MINI_BOSS, FINAL_BOSS):
        return SIZE_LARGE
    if room_type in (COMBAT, SAFE_REST, CORRIDOR):
        return SIZE_MEDIUM
    return SIZE_SMALL  # Ambush


def _biome_from_index(room_index: int) -> int:
    if BIOME_1_RANGE[0] <= room_index <= BIOME_1_RANGE[1]:
        return 1
    if BIOME_2_RANGE[0] <= room_index <= BIOME_2_RANGE[1]:
        return 2
    if BIOME_3_RANGE[0] <= room_index <= BIOME_3_RANGE[1]:
        return 3
    return 4


def _fallback_safe_layout(size: int) -> Tuple[List[List[str]], Tuple[int, int], Tuple[int, int]]:
    """Predefined safe layout: border walls, rest normal, spawn (1,1), exit (size-2, size-2)."""
    grid = [[NORMAL for _ in range(size)] for _ in range(size)]
    for i in range(size):
        grid[0][i] = grid[size - 1][i] = WALL
        grid[i][0] = grid[i][size - 1] = WALL
    spawn = (1, 1)
    exit_pos = (size - 2, size - 2)
    return (grid, spawn, exit_pos)


def _generate_with_caps(
    size: int,
    lava_pct: float,
    slow_pct: float,
    wall_pct: float,
    spawn: Tuple[int, int],
    exit_pos: Tuple[int, int],
    lava_allowed: bool,
) -> List[List[str]]:
    """Fill grid with hazards; spawn and exit stay NORMAL. Returns grid."""
    grid = [[NORMAL for _ in range(size)] for _ in range(size)]
    total = size * size
    n_lava = int(total * lava_pct) if lava_allowed else 0
    n_slow = int(total * slow_pct)
    n_wall = int(total * wall_pct)
    # Reserve spawn and exit
    cells = []
    for y in range(size):
        for x in range(size):
            if (x, y) == spawn or (x, y) == exit_pos:
                continue
            cells.append((x, y))
    rng.shuffle(cells)
    idx = 0
    for _ in range(n_lava):
        if idx < len(cells):
            x, y = cells[idx]
            grid[y][x] = LAVA
            idx += 1
    for _ in range(n_slow):
        if idx < len(cells):
            x, y = cells[idx]
            grid[y][x] = SLOW
            idx += 1
    for _ in range(n_wall):
        if idx < len(cells):
            x, y = cells[idx]
            grid[y][x] = WALL
            idx += 1
    return grid


def generate_room_layout(
    seed: int,
    room_index: int,
    room_type: str,
) -> Tuple[List[List[str]], Tuple[int, int], Tuple[int, int]]:
    """
    Deterministic layout for one room. Returns (grid, spawn_xy, exit_xy).
    Validates; retries up to 10 times with seed+room_index+retry; then fallback safe layout.
    """
    rng.set_seed(seed)
    size = _room_size(room_type)
    biome = _biome_from_index(room_index)
    is_final_boss = room_index == FINAL_BOSS_INDEX
    is_safe_room = room_type == SAFE_REST

    spawn = (1, 1)
    exit_pos = (size - 2, size - 2)

    caps = get_biome_caps(biome, is_final_boss)
    if is_final_boss:
        lava_pct = min(0.20, caps["lava_max"])
        wall_pct = min(0.20, caps["wall_max"])
        slow_pct = 0.10
    else:
        lava_lo, lava_hi = caps.get("lava_lo", 0), caps.get("lava_hi", 0.05)
        lava_pct = lava_lo + (lava_hi - lava_lo) * (rng.randint(0, 100) / 100.0)
        slow_lo, slow_hi = caps["slow_lo"], caps["slow_hi"]
        slow_pct = slow_lo + (slow_hi - slow_lo) * (rng.randint(0, 100) / 100.0)
        wall_lo, wall_hi = caps["wall_lo"], caps["wall_hi"]
        wall_pct = wall_lo + (wall_hi - wall_lo) * (rng.randint(0, 100) / 100.0)

    if is_safe_room:
        lava_pct = 0.0

    for retry in range(10):
        use_seed = seed + room_index * 1000 + retry * 100
        rng.set_seed(use_seed)
        grid = _generate_with_caps(size, lava_pct, slow_pct, wall_pct, spawn, exit_pos, not is_safe_room and room_type != SAFE_REST)
        ok, msg = validate_room(grid, spawn, exit_pos, biome, is_final_boss, is_safe_room)
        if ok:
            return (grid, spawn, exit_pos)

    return _fallback_safe_layout(size)
