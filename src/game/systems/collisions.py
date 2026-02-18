"""
Collision helpers. Used for pickups, hazards, etc.
"""
from typing import Tuple


def circle_vs_circle(
    x1: float, y1: float, r1: float,
    x2: float, y2: float, r2: float,
) -> bool:
    """True if circles overlap."""
    dx = x2 - x1
    dy = y2 - y1
    return (dx * dx + dy * dy) <= (r1 + r2) ** 2


def point_in_rect(px: float, py: float, left: float, top: float, w: float, h: float) -> bool:
    return left <= px <= left + w and top <= py <= top + h
