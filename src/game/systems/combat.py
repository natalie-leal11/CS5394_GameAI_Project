"""
Combat: short (melee) and long (projectile) attacks. Damage via rng only.
Damage resolution order: hit check -> block/parry -> reduction -> HP change -> death check.
"""
import math
from typing import List, Optional, Tuple, Any

from src.game import rng
from src.game.entities.player import Player
from src.game.entities.projectiles import Projectile

# Short attack (melee)
SHORT_DAMAGE_MIN = 8
SHORT_DAMAGE_MAX = 12
SHORT_COOLDOWN_SEC = 0.50
SHORT_HITBOX_RANGE_PX = 50
SHORT_HITBOX_WIDTH_PX = 70
SHORT_KNOCKBACK_PX = 8

# Long attack (projectile)
LONG_DAMAGE_MIN = 15
LONG_DAMAGE_MAX = 25
LONG_COOLDOWN_SEC = 0.80
LONG_PROJECTILE_SPEED = 520
LONG_PROJECTILE_LIFETIME = 1.2
LONG_PROJECTILE_RADIUS = 6
LONG_MAX_ACTIVE = 3


def _normalize(x: float, y: float) -> Tuple[float, float]:
    if x == 0 and y == 0:
        return (1.0, 0.0)
    s = math.sqrt(x * x + y * y)
    return (x / s, y / s)


def get_melee_hitbox_rect(
    player_x: float, player_y: float, player_radius: float,
    facing_x: float, facing_y: float,
) -> Tuple[float, float, float, float]:
    """Return (left, top, width, height) of melee hitbox in front of player. Range 50 px, width 70 px."""
    dx, dy = _normalize(facing_x, facing_y)
    half_w = SHORT_HITBOX_WIDTH_PX / 2.0
    # Axis-aligned rect in front: depth 50, width 70
    if abs(dx) >= abs(dy):  # horizontal
        depth, width = SHORT_HITBOX_RANGE_PX, SHORT_HITBOX_WIDTH_PX
        if dx >= 0:
            left = player_x + player_radius
            top = player_y - half_w
        else:
            left = player_x - player_radius - depth
            top = player_y - half_w
        return (left, top, depth, width)
    else:
        depth, width = SHORT_HITBOX_RANGE_PX, SHORT_HITBOX_WIDTH_PX
        if dy >= 0:
            top = player_y + player_radius
            left = player_x - half_w
        else:
            top = player_y - player_radius - depth
            left = player_x - half_w
        return (left, top, width, depth)


def point_in_rect(px: float, py: float, left: float, top: float, w: float, h: float) -> bool:
    return left <= px <= left + w and top <= py <= top + h


def update_attack_cooldowns(player: Player, dt: float) -> None:
    """Reduce short and long attack cooldowns. Call every frame."""
    if player.short_cooldown_remaining > 0:
        player.short_cooldown_remaining -= dt
        if player.short_cooldown_remaining < 0:
            player.short_cooldown_remaining = 0.0
    if player.long_cooldown_remaining > 0:
        player.long_cooldown_remaining -= dt
        if player.long_cooldown_remaining < 0:
            player.long_cooldown_remaining = 0.0
    if getattr(player, "short_attack_active_remaining", 0) > 0:
        player.short_attack_active_remaining -= dt
        if player.short_attack_active_remaining < 0:
            player.short_attack_active_remaining = 0.0


def try_short_attack(player: Player) -> Optional[Tuple[int, Tuple[float, float, float, float]]]:
    """
    If short attack off cooldown, start attack and return (damage, hitbox_rect).
    Damage from rng in [8, 12]. Otherwise return None.
    """
    if player.short_cooldown_remaining > 0:
        return None
    player.short_cooldown_remaining = SHORT_COOLDOWN_SEC
    player.short_attack_active_remaining = 0.15  # brief visual
    damage = rng.randint(SHORT_DAMAGE_MIN, SHORT_DAMAGE_MAX)
    rect = get_melee_hitbox_rect(
        player.x, player.y, player.radius,
        player.facing_x, player.facing_y,
    )
    return (damage, rect)


def try_long_attack(player: Player, projectiles: List[Projectile]) -> bool:
    """
    If long attack off cooldown and active projectiles < 3, spawn one. Return True if spawned.
    """
    if player.long_cooldown_remaining > 0:
        return False
    active = [p for p in projectiles if p.is_alive()]
    if len(active) >= LONG_MAX_ACTIVE:
        return False
    damage = rng.randint(LONG_DAMAGE_MIN, LONG_DAMAGE_MAX)
    dx, dy = _normalize(player.facing_x, player.facing_y)
    vx = dx * LONG_PROJECTILE_SPEED
    vy = dy * LONG_PROJECTILE_SPEED
    # Spawn at player edge
    sx = player.x + dx * (player.radius + LONG_PROJECTILE_RADIUS)
    sy = player.y + dy * (player.radius + LONG_PROJECTILE_RADIUS)
    projectiles.append(Projectile(
        x=sx, y=sy, vx=vx, vy=vy,
        radius=LONG_PROJECTILE_RADIUS,
        lifetime_remaining=LONG_PROJECTILE_LIFETIME,
        damage=damage,
        from_player=True,
    ))
    player.long_cooldown_remaining = LONG_COOLDOWN_SEC
    return True


def update_projectiles(projectiles: List[Projectile], dt: float) -> None:
    """Update all projectiles; remove dead ones."""
    for p in projectiles:
        p.update(dt)
    # Remove dead in place
    dead = [i for i, p in enumerate(projectiles) if not p.is_alive()]
    for i in reversed(dead):
        projectiles.pop(i)


# Block/parry (Section 4)
BLOCK_REDUCTION = 0.60  # 60%
PARRY_REDUCTION = 1.0   # 100%
PARRY_WINDOW_SEC = 0.120  # 120 ms


def resolve_damage_to_player(
    player: Player,
    raw_damage: int,
    current_time: float,
    block_held: bool,
) -> int:
    """
    Apply damage resolution order: parry overrides block. Returns final damage applied.
    If hit in parry window (L pressed within 120 ms): 100% reduction + parry flash.
    Else if block held: 60% reduction. Else full damage.
    """
    reduction = 0.0
    if player.parry_press_time >= 0 and (current_time - player.parry_press_time) <= PARRY_WINDOW_SEC:
        reduction = PARRY_REDUCTION
        player.parry_press_time = -1.0  # consume parry
        player.parry_flash_remaining = 0.1  # brief white flash
    elif block_held:
        reduction = BLOCK_REDUCTION
    return apply_damage(player, raw_damage, reduction)


def apply_damage(target: Any, raw_damage: int, reduction: float = 0.0) -> int:
    """
    Apply damage following resolution order. reduction in [0, 1] (e.g. block/parry).
    Returns final damage applied.
    """
    final = max(0, int(raw_damage * (1.0 - reduction)))
    if hasattr(target, "hp"):
        target.hp = max(0, target.hp - final)
    return final


def apply_knockback(target: Any, from_x: float, from_y: float, amount: float) -> None:
    """Push target away from (from_x, from_y) by amount px."""
    if not hasattr(target, "x") or not hasattr(target, "y"):
        return
    dx = target.x - from_x
    dy = target.y - from_y
    d = math.sqrt(dx * dx + dy * dy)
    if d <= 0:
        return
    dx /= d
    dy /= d
    target.x += dx * amount
    target.y += dy * amount
