# WASD velocity, delta-time scaling, dash timers and velocity, bounds clamping.

import pygame

from game.config import (
    LOGICAL_W,
    LOGICAL_H,
    PLAYER_MOVE_SPEED,
    PLAYER_DASH_SPEED_MULT,
    PLAYER_DASH_DURATION_SEC,
    PLAYER_DASH_COOLDOWN_SEC,
    DEBUG_PLAYER_MOVEMENT,
)

# Bounds for Phase 2: keep player on screen (padding so sprite doesn't clip).
BOUNDS_PAD = 32
MIN_X = BOUNDS_PAD
MIN_Y = BOUNDS_PAD
MAX_X = LOGICAL_W - BOUNDS_PAD
MAX_Y = LOGICAL_H - BOUNDS_PAD


def _get_wasd_vector(keys: set[int]) -> tuple[float, float]:
    """Return normalized (dx, dy) from WASD; (0,0) if none held."""
    dx, dy = 0.0, 0.0
    if keys is None:
        return dx, dy
    if pygame.K_w in keys:
        dy -= 1
    if pygame.K_s in keys:
        dy += 1
    if pygame.K_a in keys:
        dx -= 1
    if pygame.K_d in keys:
        dx += 1
    if dx == 0 and dy == 0:
        return 0.0, 0.0
    # Normalize so diagonal isn't faster
    length = (dx * dx + dy * dy) ** 0.5
    return dx / length, dy / length


def apply_player_movement(
    player,
    keys_pressed: set[int],
    dt: float,
    *,
    min_x: float | None = None,
    min_y: float | None = None,
    max_x: float | None = None,
    max_y: float | None = None,
    speed_factor: float | None = None,
) -> None:
    """
    Update player.world_pos from input. Handles dash (duration + cooldown) and normal WASD.
    Sets player.velocity_xy to (vx, vy) for this frame (for facing and idle vs walk).
    Bounds: use min_x/min_y/max_x/max_y if provided, else MIN_X/MIN_Y/MAX_X/MAX_Y.
    speed_factor: applied to normal movement only (Phase 7 slow tile); dash ignores.
    If bounds/speed_factor not passed, uses getattr(player, 'room_bounds', None) and player.speed_factor (Phase 7).
    """
    if speed_factor is None:
        speed_factor = getattr(player, "speed_factor", 1.0)
    room_bounds = getattr(player, "room_bounds", None)
    if room_bounds is not None:
        rb_min_x, rb_min_y, rb_max_x, rb_max_y = room_bounds
        if min_x is None: min_x = rb_min_x
        if min_y is None: min_y = rb_min_y
        if max_x is None: max_x = rb_max_x
        if max_y is None: max_y = rb_max_y
    # States that lock movement (player decides in player.update)
    locking_states = {"attack_short", "attack_long", "dash", "hit", "death"}
    can_move = getattr(player, "state", "idle") not in locking_states

    vx, vy = 0.0, 0.0

    if getattr(player, "dash_active", False):
        # During dash: apply dash velocity (dash ignores slow tile per Requirements)
        dash_dir = getattr(player, "dash_direction", (1, 0))
        speed = PLAYER_MOVE_SPEED * PLAYER_DASH_SPEED_MULT
        vx = dash_dir[0] * speed
        vy = dash_dir[1] * speed
        player.dash_timer -= dt
        if player.dash_timer <= 0:
            player.dash_active = False
            player.dash_cooldown_timer = PLAYER_DASH_COOLDOWN_SEC
    elif can_move:
        dx, dy = _get_wasd_vector(keys_pressed)
        vx = dx * PLAYER_MOVE_SPEED * (speed_factor if speed_factor is not None else 1.0)
        vy = dy * PLAYER_MOVE_SPEED * (speed_factor if speed_factor is not None else 1.0)
        # Tick down dash cooldown
        if getattr(player, "dash_cooldown_timer", 0) > 0:
            player.dash_cooldown_timer = max(0, player.dash_cooldown_timer - dt)

    player.velocity_xy = (vx, vy)

    # Apply velocity to position
    x, y = player.world_pos[0], player.world_pos[1]
    x += vx * dt
    y += vy * dt
    use_min_x = min_x if min_x is not None else MIN_X
    use_min_y = min_y if min_y is not None else MIN_Y
    use_max_x = max_x if max_x is not None else MAX_X
    use_max_y = max_y if max_y is not None else MAX_Y
    x = max(use_min_x, min(use_max_x, x))
    y = max(use_min_y, min(use_max_y, y))
    player.world_pos = (x, y)

    # Movement debug: skip spam when idle, only log when not idle.
    state = getattr(player, "state", "?")
    if DEBUG_PLAYER_MOVEMENT and state != "idle":
        dash = getattr(player, "dash_active", False)
        keys = keys_pressed or set()
        keys_str = "".join(
            ch for ch, key in (("w", pygame.K_w), ("a", pygame.K_a), ("s", pygame.K_s), ("d", pygame.K_d))
            if key in keys
        )
        print(
            f"[MOVE] state={state} dash={dash} "
            f"x={x:.1f} y={y:.1f} vx={vx:.1f} vy={vy:.1f} keys={{{{keys_str}}}}"
        )
