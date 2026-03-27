# Hitbox-based collision for combat. Use entity.get_hitbox_rect() so the transparent
# sprite background does not count as hittable (only the body rect matters).

import math

import pygame

from game.config import TILE_SIZE

# Small epsilon on the max (right/bottom) edges only so an AABB sitting exactly on the
# inner boundary between floor and wall does not count the adjacent wall tile.
# Do NOT add epsilon on min (left/top): adding it can map a box whose top is still in the
# wall band (e.g. top≈63.99px) to the first floor row and skip wall resolution — felt as
# top-edge-only blocking when combined with clamp/wall_collision order.
TILE_OVERLAP_EPS = 0.01


def tile_range_for_centered_aabb(
    cx: float, cy: float, full_w: float, full_h: float
) -> tuple[int, int, int, int]:
    """Tile index range (min_tx, max_tx, min_ty, max_ty) overlapping a centered axis-aligned box.

    Uses float geometry only (do not use pygame.Rect.{left,top} for tile indices).
    """
    hw = full_w * 0.5
    hh = full_h * 0.5
    left = cx - hw
    top = cy - hh
    right = cx + hw
    bottom = cy + hh
    min_tx = int(math.floor(left / TILE_SIZE))
    max_tx = int(math.floor((right - TILE_OVERLAP_EPS - 1e-9) / TILE_SIZE))
    min_ty = int(math.floor(top / TILE_SIZE))
    max_ty = int(math.floor((bottom - TILE_OVERLAP_EPS - 1e-9) / TILE_SIZE))
    return min_tx, max_tx, min_ty, max_ty


def hitbox_overlap(a: pygame.Rect, b: pygame.Rect) -> bool:
    """True if the two hitbox rects overlap. Use for player vs enemy, attack vs body."""
    return a.colliderect(b)
