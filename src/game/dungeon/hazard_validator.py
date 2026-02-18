"""
Hazard validation: connectivity (BFS), safe area %, hazard caps, boss arena override.
"""
from collections import deque
from typing import List, Tuple

# Tile type constants
NORMAL = "normal"
LAVA = "lava"
SLOW = "slow"
WALL = "wall"

# Safe = walkable and not lava
def _is_walkable(tile: str) -> bool:
    return tile in (NORMAL, SLOW)

def _is_safe(tile: str) -> bool:
    return tile == NORMAL or tile == SLOW  # no lava

def _is_safe_strict(tile: str) -> bool:
    """Strict safe = normal floor only (for spawn/exit and 3x3 zone)."""
    return tile == NORMAL


def get_biome_caps(biome: int, is_final_boss: bool) -> dict:
    """Return lava_pct, slow_pct, wall_pct (min, max), min_safe_area_pct."""
    if is_final_boss:
        return {"lava_max": 0.20, "wall_max": 0.20, "min_safe": 0.65}
    caps = {
        1: {"lava_lo": 0.00, "lava_hi": 0.05, "slow_lo": 0.05, "slow_hi": 0.10, "wall_lo": 0.10, "wall_hi": 0.15, "min_safe": 0.70},
        2: {"lava_lo": 0.05, "lava_hi": 0.15, "slow_lo": 0.05, "slow_hi": 0.15, "wall_lo": 0.15, "wall_hi": 0.20, "min_safe": 0.60},
        3: {"lava_lo": 0.15, "lava_hi": 0.25, "slow_lo": 0.10, "slow_hi": 0.20, "wall_lo": 0.20, "wall_hi": 0.25, "min_safe": 0.50},
        4: {"lava_lo": 0.20, "lava_hi": 0.30, "slow_lo": 0.10, "slow_hi": 0.20, "wall_lo": 0.20, "wall_hi": 0.30, "min_safe": 0.45},
    }
    return caps.get(biome, caps[1])


def count_tiles(grid: List[List[str]]) -> Tuple[int, int, int, int]:
    """Return (normal, lava, slow, wall) counts."""
    n = l = s = w = 0
    for row in grid:
        for t in row:
            if t == NORMAL: n += 1
            elif t == LAVA: l += 1
            elif t == SLOW: s += 1
            elif t == WALL: w += 1
    return (n, l, s, w)


def safe_area_ratio(grid: List[List[str]]) -> float:
    """Fraction of tiles that are normal or slow (no lava)."""
    total = 0
    safe = 0
    for row in grid:
        for t in row:
            total += 1
            if _is_safe(t):
                safe += 1
    return safe / total if total else 0.0


def has_3x3_safe_zone(grid: List[List[str]]) -> bool:
    """At least one 3x3 region of strictly safe (normal) tiles."""
    h, w = len(grid), len(grid[0]) if grid else 0
    for y in range(h - 2):
        for x in range(w - 2):
            ok = True
            for dy in range(3):
                for dx in range(3):
                    if grid[y + dy][x + dx] != NORMAL:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                return True
    return False


def connected_bfs(grid: List[List[str]], start: Tuple[int, int], walkable_only: bool) -> set:
    """BFS from start; return set of (x,y) reachable. Walkable = normal/slow if walkable_only."""
    h, w = len(grid), len(grid[0]) if grid else 0
    seen = set()
    q = deque([start])
    seen.add(start)
    while q:
        x, y = q.popleft()
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen:
                t = grid[ny][nx]
                if walkable_only and not _is_walkable(t):
                    continue
                if not walkable_only and t == WALL:
                    continue
                seen.add((nx, ny))
                q.append((nx, ny))
    return seen


def valid_path(grid: List[List[str]], spawn: Tuple[int, int], exit_pos: Tuple[int, int]) -> bool:
    """True if path exists from spawn to exit (walkable tiles only)."""
    reachable = connected_bfs(grid, spawn, walkable_only=True)
    return exit_pos in reachable


def validate_room(
    grid: List[List[str]],
    spawn: Tuple[int, int],
    exit_pos: Tuple[int, int],
    biome: int,
    is_final_boss: bool,
    is_safe_room: bool,
) -> Tuple[bool, str]:
    """
    Validate layout. Return (ok, message).
    Checks: spawn/exit safe, 3x3 safe zone, path spawn->exit, hazard caps, safe room zero lava.
    """
    h, w = len(grid), len(grid[0]) if grid else 0
    if h == 0 or w == 0:
        return (False, "empty grid")
    sx, sy = spawn
    ex, ey = exit_pos
    if not (0 <= sx < w and 0 <= sy < h):
        return (False, "spawn out of bounds")
    if not (0 <= ex < w and 0 <= ey < h):
        return (False, "exit out of bounds")
    if grid[sy][sx] != NORMAL:
        return (False, "spawn tile not safe")
    if grid[ey][ex] != NORMAL:
        return (False, "exit tile not safe")
    if not has_3x3_safe_zone(grid):
        return (False, "no 3x3 safe zone")
    if not valid_path(grid, spawn, exit_pos):
        return (False, "no path spawn to exit")

    total = h * w
    n, l, s, w_cnt = count_tiles(grid)
    lava_pct = l / total
    slow_pct = s / total
    wall_pct = w_cnt / total
    safe_pct = safe_area_ratio(grid)

    if is_safe_room and l > 0:
        return (False, "safe room must have zero lava")

    caps = get_biome_caps(biome, is_final_boss)
    if is_final_boss:
        if lava_pct > caps["lava_max"]:
            return (False, f"boss lava cap exceeded: {lava_pct:.2%}")
        if wall_pct > caps["wall_max"]:
            return (False, f"boss wall cap exceeded: {wall_pct:.2%}")
        if safe_pct < caps["min_safe"]:
            return (False, f"boss min safe area: {safe_pct:.2%}")
    else:
        if lava_pct > caps["lava_hi"]:
            return (False, f"lava over cap: {lava_pct:.2%}")
        if lava_pct < caps.get("lava_lo", 0):
            pass  # under is ok
        if wall_pct > caps["wall_hi"]:
            return (False, f"walls over cap: {wall_pct:.2%}")
        if safe_pct < caps["min_safe"]:
            return (False, f"min safe area not met: {safe_pct:.2%}")

    return (True, "ok")
