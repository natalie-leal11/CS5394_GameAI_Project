"""
Room renderer: draw tile grid as colored rectangles. 32x32 tiles, deterministic.
Lava red, slow blue, walls gray, normal neutral.
"""
from typing import List, Tuple

import pygame

from src.game import config
from src.game.dungeon.hazard_validator import NORMAL, LAVA, SLOW, WALL

TILE_SIZE = config.TILE_SIZE  # 32

# Colors (top-down 2D style)
COLOR_NORMAL = (60, 55, 50)
COLOR_LAVA = (220, 60, 40)
COLOR_SLOW = (70, 100, 180)
COLOR_WALL = (80, 78, 75)


def render_room(
    screen: pygame.Surface,
    grid: List[List[str]],
    offset_x: int = 0,
    offset_y: int = 0,
) -> None:
    """
    Draw the room grid. Each tile is TILE_SIZE x TILE_SIZE.
    offset_x, offset_y: top-left of the room in screen coords.
    """
    for y, row in enumerate(grid):
        for x, tile in enumerate(row):
            rect = pygame.Rect(
                offset_x + x * TILE_SIZE,
                offset_y + y * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE,
            )
            if tile == NORMAL:
                color = COLOR_NORMAL
            elif tile == LAVA:
                color = COLOR_LAVA
            elif tile == SLOW:
                color = COLOR_SLOW
            elif tile == WALL:
                color = COLOR_WALL
            else:
                color = COLOR_NORMAL
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (40, 40, 40), rect, 1)


def tile_to_world(tile_x: int, tile_y: int) -> Tuple[float, float]:
    """Center of tile in world (pixel) coords."""
    return (
        (tile_x + 0.5) * TILE_SIZE,
        (tile_y + 0.5) * TILE_SIZE,
    )


def world_to_tile(wx: float, wy: float) -> Tuple[int, int]:
    """World coords to tile indices."""
    return (int(wx // TILE_SIZE), int(wy // TILE_SIZE))
