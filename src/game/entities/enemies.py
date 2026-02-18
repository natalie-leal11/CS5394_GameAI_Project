"""
Enemy archetypes: Swarm, Flanker, Brute, Heavy, Ranged Suppressor.
Stats from Section 10. Deterministic, room-confined, chase/attack only.
"""
from typing import List

from src.game.entities.entity import Entity
from src.game.entities.enemy_base import Enemy

# Archetype stat blocks (HP, speed px/sec, melee damage, attack cooldown, optional ranged/fire_interval/windup)
SWARM_HP = 30
SWARM_SPEED = 190
SWARM_DAMAGE = 8
SWARM_ATTACK_CD = 1.2

FLANKER_HP = 40
FLANKER_SPEED = 260
FLANKER_DAMAGE = 10
FLANKER_ATTACK_CD = 1.0

BRUTE_HP = 110
BRUTE_SPEED = 120
BRUTE_DAMAGE = 16
BRUTE_WINDUP = 2.0
BRUTE_COOLDOWN = 4.0

HEAVY_HP = 160
HEAVY_SPEED = 100
HEAVY_DAMAGE = 18
HEAVY_ATTACK_CD = 3.5

RANGED_HP = 60
RANGED_SPEED = 150
RANGED_PROJECTILE_DAMAGE = 10
RANGED_FIRE_INTERVAL = 1.5

DEFAULT_ENEMY_RADIUS = 14.0


def create_swarm(x: float, y: float, elite: bool = False) -> Enemy:
    e = Enemy(x=x, y=y, radius=DEFAULT_ENEMY_RADIUS, max_hp=SWARM_HP, hp=SWARM_HP,
              speed=SWARM_SPEED, damage=SWARM_DAMAGE, archetype="swarm", elite=elite,
              attack_cooldown_remaining=0.0)
    e.apply_elite_modifier()
    return e


def create_flanker(x: float, y: float, elite: bool = False) -> Enemy:
    e = Enemy(x=x, y=y, radius=DEFAULT_ENEMY_RADIUS, max_hp=FLANKER_HP, hp=FLANKER_HP,
              speed=FLANKER_SPEED, damage=FLANKER_DAMAGE, archetype="flanker", elite=elite,
              attack_cooldown_remaining=0.0)
    e.apply_elite_modifier()
    return e


def create_brute(x: float, y: float, elite: bool = False) -> Enemy:
    e = Enemy(x=x, y=y, radius=DEFAULT_ENEMY_RADIUS, max_hp=BRUTE_HP, hp=BRUTE_HP,
              speed=BRUTE_SPEED, damage=BRUTE_DAMAGE, archetype="brute", elite=elite,
              attack_cooldown_remaining=0.0, windup_duration=BRUTE_WINDUP)
    e.apply_elite_modifier()
    return e


def create_heavy(x: float, y: float, elite: bool = False) -> Enemy:
    e = Enemy(x=x, y=y, radius=DEFAULT_ENEMY_RADIUS, max_hp=HEAVY_HP, hp=HEAVY_HP,
              speed=HEAVY_SPEED, damage=HEAVY_DAMAGE, archetype="heavy", elite=elite,
              attack_cooldown_remaining=0.0)
    e.apply_elite_modifier()
    return e


def create_ranged_suppressor(x: float, y: float, elite: bool = False) -> Enemy:
    e = Enemy(x=x, y=y, radius=DEFAULT_ENEMY_RADIUS, max_hp=RANGED_HP, hp=RANGED_HP,
              speed=RANGED_SPEED, damage=0, archetype="ranged_suppressor", elite=elite,
              is_ranged=True, projectile_damage=RANGED_PROJECTILE_DAMAGE,
              fire_interval=RANGED_FIRE_INTERVAL, fire_interval_remaining=0.0)
    e.apply_elite_modifier()
    return e


def update_enemy_chase(
    enemy: Enemy,
    player_x: float,
    player_y: float,
    bounds: tuple,
    dt: float,
) -> None:
    """
    Simple chase: move toward player. Clamp to bounds. No patrol.
    """
    left, top, width, height = bounds
    right = left + width
    bottom = top + height
    r = enemy.radius
    dx = player_x - enemy.x
    dy = player_y - enemy.y
    dist = (dx * dx + dy * dy) ** 0.5
    if dist > 0.001:
        dx /= dist
        dy /= dist
        move = enemy.speed * dt
        enemy.x = max(left + r, min(right - r, enemy.x + dx * move))
        enemy.y = max(top + r, min(bottom - r, enemy.y + dy * move))


def tick_attack_cooldowns(enemies: List[Enemy], dt: float) -> None:
    """Tick down attack and fire interval timers."""
    for e in enemies:
        if e.attack_cooldown_remaining > 0:
            e.attack_cooldown_remaining -= dt
            if e.attack_cooldown_remaining < 0:
                e.attack_cooldown_remaining = 0.0
        if e.windup_remaining > 0:
            e.windup_remaining -= dt
            if e.windup_remaining < 0:
                e.windup_remaining = 0.0
        if e.is_ranged and e.fire_interval_remaining > 0:
            e.fire_interval_remaining -= dt
            if e.fire_interval_remaining < 0:
                e.fire_interval_remaining = 0.0
        if e.hit_flash_remaining > 0:
            e.hit_flash_remaining -= dt
            if e.hit_flash_remaining < 0:
                e.hit_flash_remaining = 0.0
