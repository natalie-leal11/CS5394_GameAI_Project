import math
from dataclasses import dataclass
from typing import List

import pygame

from game.config import (
    PLAYER_SHORT_ATTACK_DAMAGE,
    PLAYER_LONG_ATTACK_DAMAGE,
    PLAYER_SHORT_ATTACK_RANGE_PX,
    PLAYER_LONG_ATTACK_RANGE_PX,
    PLAYER_LONG_ATTACK_WINDUP_SEC,
    PLAYER_BLOCK_DAMAGE_FACTOR,
    DEBUG_COMBAT_HITS,
    ENEMY_HIT_ZONE_RADIUS,
    ENEMY_SWARM_ATTACK_RADIUS,
    ENEMY_SWARM_ATTACK_OFFSET,
    ENEMY_SWARM_ATTACK_COOLDOWN_SEC,
    ENEMY_FLANKER_ATTACK_RADIUS,
    ENEMY_FLANKER_ATTACK_OFFSET,
    ENEMY_FLANKER_ATTACK_COOLDOWN_SEC,
    ENEMY_BRUTE_ATTACK_RADIUS,
    ENEMY_BRUTE_ATTACK_OFFSET,
    ENEMY_BRUTE_ATTACK_COOLDOWN_SEC,
    ENEMY_HEAVY_ATTACK_RADIUS,
    ENEMY_HEAVY_ATTACK_OFFSET,
    ENEMY_HEAVY_ATTACK_COOLDOWN_SEC,
    MINI_BOSS_ATTACK_RADIUS,
    MINI_BOSS_ATTACK_OFFSET,
    MINI_BOSS_ATTACK_COOLDOWN_SEC,
    PLAYER_SIZE,
    FINAL_BOSS_ATTACK_RADIUS,
    FINAL_BOSS_ATTACK_OFFSET,
    FINAL_BOSS_ATTACK_COOLDOWN_SEC,
)


@dataclass
class DamageEvent:
    target: object
    amount: float
    is_player: bool  # True if damage applied to player, False for enemy
    world_pos: tuple[float, float] | None = None  # impact position in world space
    source: str = ""  # "player_short", "player_long", "enemy_melee", etc.


def _normalize(vx: float, vy: float) -> tuple[float, float]:
    length = math.hypot(vx, vy)
    if length <= 1e-6:
        return 0.0, 0.0
    return vx / length, vy / length


def _rect_overlaps_circle(rect: pygame.Rect, cx: float, cy: float, radius: float) -> bool:
    """True if the rect overlaps the circle (distance from center to closest point on rect <= radius)."""
    closest_x = max(rect.left, min(cx, rect.right))
    closest_y = max(rect.top, min(cy, rect.bottom))
    return math.hypot(cx - closest_x, cy - closest_y) <= radius


def _enemy_hurtbox_rect(enemy) -> pygame.Rect:
    """Return a consistent hurtbox rect for any enemy/dummy."""
    if hasattr(enemy, "get_hurtbox_rect"):
        return enemy.get_hurtbox_rect()
    if hasattr(enemy, "get_hitbox_rect"):
        return enemy.get_hitbox_rect()
    # Fallback: small 32x32 rect around world_pos.
    ex, ey = getattr(enemy, "world_pos", (0.0, 0.0))
    return pygame.Rect(int(ex - 16), int(ey - 16), 32, 32)


def _enemy_attack_params(enemy_type: str) -> tuple[float, float, float]:
    """Return (radius, offset, cooldown_sec) for melee attack."""
    if enemy_type == "ranged":
        return 0.0, 0.0, 999.0
    if enemy_type in ("mini_boss", "mini_boss_2", "mini_boss_3"):
        return MINI_BOSS_ATTACK_RADIUS, MINI_BOSS_ATTACK_OFFSET, MINI_BOSS_ATTACK_COOLDOWN_SEC
    if enemy_type == "brute":
        return ENEMY_BRUTE_ATTACK_RADIUS, ENEMY_BRUTE_ATTACK_OFFSET, ENEMY_BRUTE_ATTACK_COOLDOWN_SEC
    if enemy_type == "flanker":
        return ENEMY_FLANKER_ATTACK_RADIUS, ENEMY_FLANKER_ATTACK_OFFSET, ENEMY_FLANKER_ATTACK_COOLDOWN_SEC
    if enemy_type == "heavy":
        return ENEMY_HEAVY_ATTACK_RADIUS, ENEMY_HEAVY_ATTACK_OFFSET, ENEMY_HEAVY_ATTACK_COOLDOWN_SEC
    if enemy_type == "final_boss":
        return FINAL_BOSS_ATTACK_RADIUS, FINAL_BOSS_ATTACK_OFFSET, FINAL_BOSS_ATTACK_COOLDOWN_SEC
    return ENEMY_SWARM_ATTACK_RADIUS, ENEMY_SWARM_ATTACK_OFFSET, ENEMY_SWARM_ATTACK_COOLDOWN_SEC


def apply_player_attacks(player, enemies: list) -> List[DamageEvent]:
    """
    Resolve player short/long attacks using directional rectangular hitboxes.

    - Short attack: close, wide, forgiving rectangle directly in front of player.
    - Long attack: long, thinner rectangle directly in front of player.
    - Damage is applied IFF attack_rect.colliderect(enemy_hurtbox_rect).
    - Each enemy can only be hit once per short-attack swing.
    """
    events: List[DamageEvent] = []

    px = float(getattr(player, "world_pos", (0, 0))[0])
    py = float(getattr(player, "world_pos", (0, 0))[1])
    mult = player.attack_multiplier

    # Player sprite rect from world_pos and configured size (authoritative).
    pw, ph = PLAYER_SIZE
    player_rect = pygame.Rect(int(px - pw / 2), int(py - ph / 2), pw, ph)

    def _player_dir() -> str:
        """Map player's facing vector to one of up/down/left/right.

        Prefer the continuous facing vector (used in tests), and fall back to the
        discrete _facing_dir only when the vector is zero.
        """
        fx, fy = getattr(player, "facing", (1.0, 0.0))
        if fx != 0.0 or fy != 0.0:
            if abs(fx) >= abs(fy):
                return "right" if fx > 0 else "left"
            return "down" if fy > 0 else "up"
        d = getattr(player, "_facing_dir", None)
        if d in ("up", "down", "left", "right"):
            return d
        return "right"

    # Reset debug attack rects for this frame.
    setattr(player, "_debug_short_attack_rect", None)
    setattr(player, "_debug_long_attack_rect", None)

    # Short attack: directional rectangle in front of the player. One hit per enemy per swing.
    # Be generous for gameplay: keep the hitbox active for the entire short-attack state
    # instead of a narrow timer window to avoid whiffing due to frame-perfect timing.
    if getattr(player, "state", None) == "attack_short":
        dir_tag = _player_dir()
        reach = PLAYER_SHORT_ATTACK_RANGE_PX  # 48px forward
        thickness = 70  # 70px wide
        if dir_tag == "right":
            attack_rect = pygame.Rect(
                player_rect.right,
                player_rect.centery - thickness // 2,
                reach,
                thickness,
            )
        elif dir_tag == "left":
            attack_rect = pygame.Rect(
                player_rect.left - reach,
                player_rect.centery - thickness // 2,
                reach,
                thickness,
            )
        elif dir_tag == "up":
            attack_rect = pygame.Rect(
                player_rect.centerx - thickness // 2,
                player_rect.top - reach,
                thickness,
                reach,
            )
        else:  # "down"
            attack_rect = pygame.Rect(
                player_rect.centerx - thickness // 2,
                player_rect.bottom,
                thickness,
                reach,
            )
        setattr(player, "_debug_short_attack_rect", attack_rect.copy())

        for enemy in enemies:
            if getattr(enemy, "inactive", False):
                continue
            if getattr(enemy, "enemy_type", None) == "final_boss" and (getattr(enemy, "_revive_invuln_timer", 0) > 0 or getattr(enemy, "state", None) == "revive_wait"):
                continue
            if not player.can_hit_enemy_with_short(enemy):
                continue
            hurtbox = _enemy_hurtbox_rect(enemy)
            if not attack_rect.colliderect(hurtbox):
                continue
            damage = float(PLAYER_SHORT_ATTACK_DAMAGE * mult)
            new_hp = float(getattr(enemy, "hp", 0.0)) - damage
            enemy.hp = max(0.0, new_hp)
            if enemy.hp <= 0.0 and hasattr(enemy, "_set_state"):
                enemy._set_state("death")
            # Final boss: do not set state to "hit" (stagger resistance); damage_flash_timer is visual only.
            if hasattr(enemy, "damage_flash_timer"):
                enemy.damage_flash_timer = 0.15
            player.register_short_attack_hit(enemy)
            events.append(
                DamageEvent(
                    target=enemy,
                    amount=damage,
                    is_player=False,
                    world_pos=(hurtbox.centerx, hurtbox.centery),
                    source="player_short",
                )
            )
            if DEBUG_COMBAT_HITS:
                et = getattr(enemy, "enemy_type", type(enemy).__name__)
                print(
                    f"[COMBAT] HIT {et} player_short -{damage:.1f} "
                    f"hp={float(getattr(enemy, 'hp', 0.0)):.1f}"
                )

    # Long attack: directional rectangle in front of the player. Triggered once per swing.
    if getattr(player, "should_fire_long_attack", None) is not None and player.should_fire_long_attack():
        dir_tag = _player_dir()
        length = PLAYER_LONG_ATTACK_RANGE_PX  # 192px forward
        thickness = 50  # 50px wide
        if dir_tag == "right":
            attack_rect = pygame.Rect(
                player_rect.right,
                player_rect.centery - thickness // 2,
                length,
                thickness,
            )
        elif dir_tag == "left":
            attack_rect = pygame.Rect(
                player_rect.left - length,
                player_rect.centery - thickness // 2,
                length,
                thickness,
            )
        elif dir_tag == "up":
            attack_rect = pygame.Rect(
                player_rect.centerx - thickness // 2,
                player_rect.top - length,
                thickness,
                length,
            )
        else:  # "down"
            attack_rect = pygame.Rect(
                player_rect.centerx - thickness // 2,
                player_rect.bottom,
                thickness,
                length,
            )

        for enemy in enemies:
            if getattr(enemy, "inactive", False):
                continue
            if getattr(enemy, "enemy_type", None) == "final_boss" and (getattr(enemy, "_revive_invuln_timer", 0) > 0 or getattr(enemy, "state", None) == "revive_wait"):
                continue
            hurtbox = _enemy_hurtbox_rect(enemy)
            if not attack_rect.colliderect(hurtbox):
                continue
            damage = float(PLAYER_LONG_ATTACK_DAMAGE * mult)
            new_hp = float(getattr(enemy, "hp", 0.0)) - damage
            enemy.hp = max(0.0, new_hp)
            if enemy.hp <= 0.0 and hasattr(enemy, "_set_state"):
                enemy._set_state("death")
            # Final boss: do not set state to "hit" (stagger resistance); damage_flash_timer is visual only.
            if hasattr(enemy, "damage_flash_timer"):
                enemy.damage_flash_timer = 0.15
            events.append(
                DamageEvent(
                    target=enemy,
                    amount=damage,
                    is_player=False,
                    world_pos=(hurtbox.centerx, hurtbox.centery),
                    source="player_long",
                )
            )
            if DEBUG_COMBAT_HITS:
                et = getattr(enemy, "enemy_type", type(enemy).__name__)
                print(
                    f"[COMBAT] HIT {et} player_long -{damage:.1f} "
                    f"hp={float(getattr(enemy, 'hp', 0.0)):.1f}"
                )

    return events


def apply_enemy_attacks(player, enemies: list, dt: float) -> List[DamageEvent]:
    """
    Resolve enemy melee attacks against player.
    - Uses per-type radius/offset and cooldown from config.
    - Honors player block/parry: parry negates, block scales damage.
    """
    events: List[DamageEvent] = []
    px, py = player.world_pos
    is_blocking = getattr(player, "is_blocking", lambda: False)()
    parry_active = getattr(player, "is_parry_active", lambda: False)()

    for enemy in enemies:
        if getattr(enemy, "inactive", False):
            continue
        enemy_type = getattr(enemy, "enemy_type", "swarm")
        if enemy_type == "ranged":
            continue
        state = getattr(enemy, "state", "")
        attacking = (
            state == "attack"
            or (enemy_type in ("mini_boss", "mini_boss_2", "mini_boss_3") and state in ("attack_01", "attack_02"))
            or (enemy_type == "final_boss" and state == "attack2" and getattr(enemy, "_teleport_strike_damage_frame", False))
        )
        if not attacking:
            continue
        radius, offset, cooldown = _enemy_attack_params(enemy_type)
        if getattr(enemy, "attack_cooldown_timer", 0.0) > 0.0:
            continue
        ex, ey = enemy.world_pos
        fx, fy = _normalize(px - ex, py - ey)
        if fx == fy == 0.0:
            fx, fy = 1.0, 0.0
        cx = ex + fx * offset
        cy = ey + fy * offset
        dist = math.hypot(px - cx, py - cy)
        if dist <= radius:
            enemy.attack_cooldown_timer = cooldown
            if enemy_type == "final_boss" and getattr(enemy, "_teleport_strike_damage_frame", False):
                setattr(enemy, "_teleport_strike_damage_frame", False)
            if parry_active:
                continue
            dmg = getattr(enemy, "damage", 0.0)
            if is_blocking:
                dmg *= PLAYER_BLOCK_DAMAGE_FACTOR
            dmg *= getattr(player, "damage_taken_mult", 1.0)
            if dmg <= 0:
                continue
            player.hp = max(0.0, player.hp - dmg)
            if hasattr(player, "damage_flash_timer"):
                player.damage_flash_timer = 0.15
            events.append(
                DamageEvent(
                    target=player,
                    amount=dmg,
                    is_player=True,
                    world_pos=(px, py),
                    source="enemy_melee",
                )
            )

    return events


def apply_projectile_hits(player, projectiles: list) -> List[DamageEvent]:
    """Resolve enemy projectiles vs player. On hit: apply damage, mark projectile inactive."""
    events: List[DamageEvent] = []
    player_rect = player.get_hitbox_rect()
    for proj in projectiles:
        if getattr(proj, "inactive", True):
            continue
        if not player_rect.colliderect(proj.get_hitbox_rect()):
            continue
        proj.inactive = True
        dmg = getattr(proj, "damage", 0.0)
        if dmg <= 0:
            continue
        dmg *= getattr(player, "damage_taken_mult", 1.0)
        player.hp = max(0.0, player.hp - dmg)
        if hasattr(player, "damage_flash_timer"):
            player.damage_flash_timer = 0.15
        events.append(
            DamageEvent(
                target=player,
                amount=dmg,
                is_player=True,
                world_pos=player.world_pos,
                source="enemy_projectile",
            )
        )
    return events

