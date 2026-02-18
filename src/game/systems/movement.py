"""
Movement system: WASD, dash, clamp to bounds. Deterministic, delta-time scaled.
"""
from typing import Tuple

from src.game.entities.player import (
    Player,
    MOVE_SPEED_PX_SEC,
    DASH_SPEED_MULTIPLIER,
    DASH_DURATION_SEC,
    DASH_COOLDOWN_SEC,
)


def _normalize_dir(dx: float, dy: float) -> Tuple[float, float]:
    if dx == 0 and dy == 0:
        return (0.0, 0.0)
    import math
    s = math.sqrt(dx * dx + dy * dy)
    return (dx / s, dy / s)


def update_player_movement(
    player: Player,
    move_x: float,
    move_y: float,
    dash_requested: bool,
    bounds: Tuple[float, float, float, float],
    dt: float,
    current_time: float,
) -> None:
    """
    Update player position and dash state. Clamp to bounds (left, top, width, height).
    move_x, move_y in [-1, 1]. Dash cannot stack; cannot exit boundaries.
    """
    left, top, width, height = bounds
    right = left + width
    bottom = top + height
    r = player.radius
    min_x = left + r
    max_x = right - r
    min_y = top + r
    max_y = bottom - r

    # Reduce dash and cooldown timers
    if player.dash_remaining > 0:
        player.dash_remaining -= dt
        if player.dash_remaining < 0:
            player.dash_remaining = 0.0
    if player.dash_cooldown_remaining > 0:
        player.dash_cooldown_remaining -= dt
        if player.dash_cooldown_remaining < 0:
            player.dash_cooldown_remaining = 0.0

    # Start new dash if requested and allowed (deterministic; no stack)
    if dash_requested and player.can_dash():
        player.dash_remaining = DASH_DURATION_SEC
        player.dash_cooldown_remaining = DASH_COOLDOWN_SEC

    # Compute velocity (player may have move speed upgrade)
    dx, dy = _normalize_dir(move_x, move_y)
    speed = getattr(player, "get_move_speed", lambda: MOVE_SPEED_PX_SEC)()
    if player.is_dashing():
        speed *= DASH_SPEED_MULTIPLIER
        # Record trail position for visual
        player.trail.append((player.x, player.y, current_time))

    move_dx = dx * speed * dt
    move_dy = dy * speed * dt

    # Clamp so we don't exit boundaries
    new_x = player.x + move_dx
    new_y = player.y + move_dy
    new_x = max(min_x, min(max_x, new_x))
    new_y = max(min_y, min(max_y, new_y))
    player.x = new_x
    player.y = new_y
