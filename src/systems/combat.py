import math
from dataclasses import dataclass
from typing import List

import pygame

from entities.biome3_miniboss import Biome3MiniBoss
from entities.final_boss import FinalBoss
from entities.mini_boss import MiniBoss
from entities.mini_boss_2 import MiniBoss2
from game.config import (
    PLAYER_SHORT_ATTACK_DAMAGE,
    PLAYER_LONG_ATTACK_DAMAGE,
    PLAYER_DAMAGE_MULT_NORMAL,
    PLAYER_DAMAGE_MULT_MINIBOSS,
    PLAYER_DAMAGE_MULT_FINAL_BOSS,
    PLAYER_SHORT_ATTACK_RANGE_PX,
    PLAYER_LONG_ATTACK_RANGE_PX,
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
    PLAYER_HITBOX_W,
    PLAYER_HITBOX_H,
    FINAL_BOSS_ATTACK_RADIUS,
    FINAL_BOSS_ATTACK_OFFSET,
    FINAL_BOSS_ATTACK_COOLDOWN_SEC,
    ENEMY_MELEE_HIT_RADIUS_MULT_SWARM,
    ENEMY_MELEE_HIT_RADIUS_MULT_FLANKER,
    ENEMY_MELEE_HIT_RADIUS_MULT_BRUTE,
    ENEMY_MELEE_HIT_RADIUS_MULT_HEAVY,
    ENEMY_MELEE_BODY_FALLBACK_EXTRA_SWARM,
    ENEMY_MELEE_BODY_FALLBACK_EXTRA_FLANKER,
    ENEMY_MELEE_BODY_FALLBACK_EXTRA_BRUTE,
    ENEMY_MELEE_BODY_FALLBACK_EXTRA_HEAVY,
    ENEMY_MELEE_FLANKER_SEGMENT_REACH_PX,
    MINI_BOSS_MELEE_HIT_RADIUS_MULT,
    MINI_BOSS_MELEE_BODY_EXTRA_PX,
    MINI_BOSS_MELEE_ARC_BONUS_PX,
    ENEMY_MELEE_BODY_EXTRA_UNIVERSAL_PX,
    DEBUG_MELEE_HIT,
    DEBUG_PLAYER_ATTACK_PROXIMITY,
    DEBUG_BLOCK_PARRY_TRACE,
)

_MINI_BOSS_MELEE_TYPES = frozenset({"mini_boss", "mini_boss_2", "mini_boss_3"})

# Post-hit retaliation delay: shorter for boss entity classes (instance checks).
_POST_HIT_COOLDOWN_BOSS_CLASSES = (MiniBoss, MiniBoss2, Biome3MiniBoss, FinalBoss)


def _player_attack_enemy_type_damage_mult(enemy) -> float:
    """Extra multiplier for player short/long damage vs boss tier (config; base damage unchanged)."""
    if isinstance(enemy, FinalBoss):
        return float(PLAYER_DAMAGE_MULT_FINAL_BOSS)
    if isinstance(enemy, (MiniBoss, MiniBoss2, Biome3MiniBoss)):
        return float(PLAYER_DAMAGE_MULT_MINIBOSS)
    return float(PLAYER_DAMAGE_MULT_NORMAL)


def _apply_post_hit_attack_cooldown(enemy, *, is_long_attack: bool) -> None:
    """
    After player damage, ensure enemy cannot melee/ranged-fire immediately.
    Uses max() so a longer existing attack_cooldown_timer is never shortened.
    """
    if not hasattr(enemy, "attack_cooldown_timer"):
        return
    if isinstance(enemy, _POST_HIT_COOLDOWN_BOSS_CLASSES):
        hit_cd = 0.35 if is_long_attack else 0.2
    else:
        hit_cd = 0.6 if is_long_attack else 0.4
    cur = float(getattr(enemy, "attack_cooldown_timer", 0.0))
    enemy.attack_cooldown_timer = max(cur, hit_cd)

# One-shot: print configured proximity radii when player attacks resolve.
_PLAYER_ATTACK_PROXIMITY_RADII_PRINTED = False


def _distance_point_to_rect(px: float, py: float, rect: pygame.Rect) -> float:
    """Distance from point to axis-aligned rect (0 if point is inside)."""
    cx = max(rect.left, min(px, rect.right))
    cy = max(rect.top, min(py, rect.bottom))
    return math.hypot(px - cx, py - cy)


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


def _dist_point_to_segment_sq(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
    """Squared distance from point P to segment (x1,y1)-(x2,y2)."""
    dx = x2 - x1
    dy = y2 - y1
    len_sq = dx * dx + dy * dy
    if len_sq <= 1e-18:
        return (px - x1) ** 2 + (py - y1) ** 2
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / len_sq))
    qx = x1 + t * dx
    qy = y1 + t * dy
    return (px - qx) ** 2 + (py - qy) ** 2


def _melee_hit_tuning(enemy_type: str) -> tuple[float, float]:
    """(arc radius multiplier, extra px on body-distance fallback) per standard melee identity."""
    if enemy_type == "swarm":
        return float(ENEMY_MELEE_HIT_RADIUS_MULT_SWARM), float(ENEMY_MELEE_BODY_FALLBACK_EXTRA_SWARM)
    if enemy_type == "flanker":
        return float(ENEMY_MELEE_HIT_RADIUS_MULT_FLANKER), float(ENEMY_MELEE_BODY_FALLBACK_EXTRA_FLANKER)
    if enemy_type == "brute":
        return float(ENEMY_MELEE_HIT_RADIUS_MULT_BRUTE), float(ENEMY_MELEE_BODY_FALLBACK_EXTRA_BRUTE)
    if enemy_type == "heavy":
        return float(ENEMY_MELEE_HIT_RADIUS_MULT_HEAVY), float(ENEMY_MELEE_BODY_FALLBACK_EXTRA_HEAVY)
    # default: swarm-like
    return float(ENEMY_MELEE_HIT_RADIUS_MULT_SWARM), float(ENEMY_MELEE_BODY_FALLBACK_EXTRA_SWARM)


def _player_hurtbox_for_melee(player) -> pygame.Rect:
    """Player hurtbox for enemy melee checks; supports real Player and test dummies without get_hitbox_rect."""
    if hasattr(player, "get_hitbox_rect"):
        return player.get_hitbox_rect()
    px, py = float(player.world_pos[0]), float(player.world_pos[1])
    return pygame.Rect(
        int(px - PLAYER_HITBOX_W / 2),
        int(py - PLAYER_HITBOX_H / 2),
        PLAYER_HITBOX_W,
        PLAYER_HITBOX_H,
    )


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


def _enemy_melee_player_in_range(
    enemy_type: str,
    enemy,
    player,
    radius: float,
    offset: float,
) -> bool:
    """
    True if this swing should connect.
    - final_boss: strict center-vs-arc distance.
    - mini_boss / mini_boss_2 / mini_boss_3: forgiving hitbox + body + arc bonus (shared tuning).
    - Other melee: per-type arc scale + body fallback; Flanker adds segment reach.
    """
    px, py = float(player.world_pos[0]), float(player.world_pos[1])
    ex, ey = float(enemy.world_pos[0]), float(enemy.world_pos[1])
    fx, fy = _normalize(px - ex, py - ey)
    if fx == fy == 0.0:
        fx, fy = 1.0, 0.0
    cx = ex + fx * offset
    cy = ey + fy * offset

    if enemy_type == "final_boss":
        dist_hit = math.hypot(px - cx, py - cy)
        return dist_hit <= radius
    u = float(ENEMY_MELEE_BODY_EXTRA_UNIVERSAL_PX)
    if enemy_type in _MINI_BOSS_MELEE_TYPES:
        eff_r = radius * float(MINI_BOSS_MELEE_HIT_RADIUS_MULT) + u
        player_rect = _player_hurtbox_for_melee(player)
        if _rect_overlaps_circle(player_rect, cx, cy, eff_r):
            return True
        d_body = math.hypot(px - ex, py - ey)
        if d_body <= radius + offset + float(MINI_BOSS_MELEE_BODY_EXTRA_PX) + u:
            return True
        if _rect_overlaps_circle(player_rect, cx, cy, eff_r + float(MINI_BOSS_MELEE_ARC_BONUS_PX)):
            return True
        return False

    mult, body_extra = _melee_hit_tuning(enemy_type)
    eff_r = radius * mult + u
    player_rect = _player_hurtbox_for_melee(player)
    if _rect_overlaps_circle(player_rect, cx, cy, eff_r):
        return True
    d_body = math.hypot(px - ex, py - ey)
    if d_body <= radius + offset + body_extra + u:
        return True
    # Flanker: agile approaches — player near the swing line (enemy → arc), not only the arc center.
    if enemy_type == "flanker":
        d_seg = math.sqrt(_dist_point_to_segment_sq(px, py, ex, ey, cx, cy))
        if d_seg <= eff_r + float(ENEMY_MELEE_FLANKER_SEGMENT_REACH_PX):
            return True
    # Brute / Heavy: wider arc at same swing point (larger enemies — fewer “standing there, no hit” cases).
    if enemy_type == "brute":
        if _rect_overlaps_circle(player_rect, cx, cy, eff_r + 6.0):
            return True
    if enemy_type == "heavy":
        if _rect_overlaps_circle(player_rect, cx, cy, eff_r + 10.0):
            return True
    return False


def apply_player_attacks(player, enemies: list) -> List[DamageEvent]:
    """
    Resolve player short/long attacks using proximity radii from the player center.

    Damage does not depend on facing direction (animations still do). Each enemy must be
    within the configured radius of the player position to the enemy hurtbox (closest-point
    distance). Short uses a smaller radius than long. Short: one hit per enemy per swing.
    Long: one damage resolution per swing (should_fire_long_attack).
    """
    global _PLAYER_ATTACK_PROXIMITY_RADII_PRINTED
    events: List[DamageEvent] = []

    if DEBUG_PLAYER_ATTACK_PROXIMITY and not _PLAYER_ATTACK_PROXIMITY_RADII_PRINTED:
        _PLAYER_ATTACK_PROXIMITY_RADII_PRINTED = True
        print(
            f"[COMBAT] Player attack radii (proximity, facing-independent): "
            f"short={PLAYER_SHORT_ATTACK_RANGE_PX}px, long={PLAYER_LONG_ATTACK_RANGE_PX}px"
        )

    px = float(getattr(player, "world_pos", (0, 0))[0])
    py = float(getattr(player, "world_pos", (0, 0))[1])
    mult = player.attack_multiplier

    setattr(player, "_debug_short_attack_rect", None)
    setattr(player, "_debug_long_attack_rect", None)

    short_r = float(PLAYER_SHORT_ATTACK_RANGE_PX)
    long_r = float(PLAYER_LONG_ATTACK_RANGE_PX)

    # Short attack: entire attack_short state — proximity ring, one hit per enemy per swing.
    if getattr(player, "state", None) == "attack_short":
        short_hits: list[str] = []
        for enemy in enemies:
            if getattr(enemy, "inactive", False):
                continue
            if getattr(enemy, "enemy_type", None) == "final_boss" and (getattr(enemy, "_revive_invuln_timer", 0) > 0 or getattr(enemy, "state", None) == "revive_wait"):
                continue
            if not player.can_hit_enemy_with_short(enemy):
                continue
            hurtbox = _enemy_hurtbox_rect(enemy)
            if _distance_point_to_rect(px, py, hurtbox) > short_r:
                continue
            damage = float(PLAYER_SHORT_ATTACK_DAMAGE * mult)
            damage *= _player_attack_enemy_type_damage_mult(enemy)
            new_hp = float(getattr(enemy, "hp", 0.0)) - damage
            enemy.hp = max(0.0, new_hp)
            if enemy.hp <= 0.0 and hasattr(enemy, "_set_state"):
                enemy._set_state("death")
            if hasattr(enemy, "damage_flash_timer"):
                enemy.damage_flash_timer = 0.15
            _apply_post_hit_attack_cooldown(enemy, is_long_attack=False)
            player.register_short_attack_hit(enemy)
            et = getattr(enemy, "enemy_type", type(enemy).__name__)
            short_hits.append(str(et))
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
                print(
                    f"[COMBAT] HIT {et} player_short -{damage:.1f} "
                    f"hp={float(getattr(enemy, 'hp', 0.0)):.1f}"
                )
        if DEBUG_PLAYER_ATTACK_PROXIMITY and short_hits:
            print(
                f"[COMBAT] player_short hits (proximity, facing-independent): "
                f"radius={short_r}px, enemies={short_hits}"
            )

    # Long attack: once per swing — larger proximity ring.
    if getattr(player, "should_fire_long_attack", None) is not None and player.should_fire_long_attack():
        long_hits: list[str] = []
        for enemy in enemies:
            if getattr(enemy, "inactive", False):
                continue
            if getattr(enemy, "enemy_type", None) == "final_boss" and (getattr(enemy, "_revive_invuln_timer", 0) > 0 or getattr(enemy, "state", None) == "revive_wait"):
                continue
            hurtbox = _enemy_hurtbox_rect(enemy)
            if _distance_point_to_rect(px, py, hurtbox) > long_r:
                continue
            damage = float(PLAYER_LONG_ATTACK_DAMAGE * mult)
            damage *= _player_attack_enemy_type_damage_mult(enemy)
            new_hp = float(getattr(enemy, "hp", 0.0)) - damage
            enemy.hp = max(0.0, new_hp)
            if enemy.hp <= 0.0 and hasattr(enemy, "_set_state"):
                enemy._set_state("death")
            if hasattr(enemy, "damage_flash_timer"):
                enemy.damage_flash_timer = 0.15
            _apply_post_hit_attack_cooldown(enemy, is_long_attack=True)
            et = getattr(enemy, "enemy_type", type(enemy).__name__)
            long_hits.append(str(et))
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
                print(
                    f"[COMBAT] HIT {et} player_long -{damage:.1f} "
                    f"hp={float(getattr(enemy, 'hp', 0.0)):.1f}"
                )
        if DEBUG_PLAYER_ATTACK_PROXIMITY and long_hits:
            print(
                f"[COMBAT] player_long hits (proximity, facing-independent): "
                f"radius={long_r}px, enemies={long_hits}"
            )

    return events


def _player_is_invulnerable(player) -> bool:
    """True during post-respawn i-frames (no HP loss)."""
    return float(getattr(player, "invulnerable_timer", 0.0)) > 0.0


def apply_enemy_attacks(player, enemies: list, dt: float) -> tuple[List[DamageEvent], int]:
    """
    Resolve enemy melee attacks against player.
    - Uses per-type radius/offset and cooldown from config.
    - Standard melee: forgiving hitbox-vs-arc + close body fallback; bosses unchanged (center vs arc).
    - Honors player block/parry: parry negates, block scales damage.
    Returns (damage events, count of melee hits fully negated by parry) for VFX/feedback.
    """
    events: List[DamageEvent] = []
    melee_parry_negations = 0
    px, py = player.world_pos
    is_blocking = getattr(player, "is_blocking", lambda: False)()
    parry_active = getattr(player, "is_parry_active", lambda: False)()
    p_state = getattr(player, "state", "")
    p_parry_t = float(getattr(player, "parry_window_timer", 0.0))
    if DEBUG_BLOCK_PARRY_TRACE:
        print(
            f"[BLOCK_PARRY_TRACE] apply_enemy_attacks snapshot "
            f"player.state={p_state!r} is_blocking={is_blocking} is_parry_active={parry_active} "
            f"parry_window_timer={p_parry_t:.4f}"
        )

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
        in_range = _enemy_melee_player_in_range(enemy_type, enemy, player, radius, offset)
        if not in_range:
            if DEBUG_MELEE_HIT:
                print(
                    f"[HIT DEBUG] enemy={enemy_type} state={state} in_range=False damage_applied=False"
                )
            continue
        if DEBUG_BLOCK_PARRY_TRACE:
            print(
                f"[BLOCK_PARRY_TRACE] melee hit collision enemy={enemy_type} atk_state={state!r} "
                f"player.state={getattr(player, 'state', '')!r} parry_timer={float(getattr(player, 'parry_window_timer', 0.0)):.4f}"
            )
        enemy.attack_cooldown_timer = cooldown
        if enemy_type == "final_boss" and getattr(enemy, "_teleport_strike_damage_frame", False):
            setattr(enemy, "_teleport_strike_damage_frame", False)
        if parry_active:
            melee_parry_negations += 1
            if DEBUG_BLOCK_PARRY_TRACE:
                print(
                    f"[BLOCK_PARRY_TRACE] parry NEGATES dmg (no HP change) raw_enemy_dmg={getattr(enemy, 'damage', 0.0)}"
                )
            if DEBUG_MELEE_HIT:
                print(
                    f"[HIT DEBUG] enemy={enemy_type} state={state} in_range=True damage_applied=False"
                )
            continue
        if _player_is_invulnerable(player):
            continue
        dmg = getattr(enemy, "damage", 0.0)
        if is_blocking:
            if DEBUG_BLOCK_PARRY_TRACE:
                print(
                    f"[BLOCK_PARRY_TRACE] block applies factor={PLAYER_BLOCK_DAMAGE_FACTOR} "
                    f"raw_dmg={dmg} -> scaled={dmg * PLAYER_BLOCK_DAMAGE_FACTOR}"
                )
            dmg *= PLAYER_BLOCK_DAMAGE_FACTOR
        dmg *= getattr(player, "damage_taken_mult", 1.0)
        if dmg <= 0:
            if DEBUG_MELEE_HIT:
                print(
                    f"[HIT DEBUG] enemy={enemy_type} state={state} in_range=True damage_applied=False"
                )
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
        if DEBUG_MELEE_HIT:
            print(
                f"[HIT DEBUG] enemy={enemy_type} state={state} in_range=True damage_applied=True"
            )

    return events, melee_parry_negations


def apply_projectile_hits(player, projectiles: list) -> List[DamageEvent]:
    """Resolve enemy projectiles vs player. On hit: apply damage, mark projectile inactive."""
    events: List[DamageEvent] = []
    player_rect = player.get_hitbox_rect()
    for proj in projectiles:
        if getattr(proj, "inactive", True):
            continue
        if not player_rect.colliderect(proj.get_hitbox_rect()):
            continue
        if _player_is_invulnerable(player):
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

