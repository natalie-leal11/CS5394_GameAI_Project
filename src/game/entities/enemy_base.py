"""
Base enemy: room-confined, deterministic timers, chase/attack only.
"""
from dataclasses import dataclass, field
from typing import Optional
import math

from src.game.entities.entity import Entity

ELITE_HP_MULT = 1.40  # +40%
ELITE_DAMAGE_MULT = 1.20  # +20%


@dataclass
class Enemy(Entity):
    """Enemy entity: HP, speed, damage, archetype, elite flag. No randomness."""

    max_hp: int = 30
    hp: int = 30
    speed: float = 190.0  # px/sec
    damage: int = 8
    archetype: str = "swarm"
    elite: bool = False
    # Deterministic timers (sec)
    attack_cooldown_remaining: float = 0.0
    # Ranged only
    fire_interval_remaining: float = 0.0
    is_ranged: bool = False
    projectile_damage: int = 0
    fire_interval: float = 1.5
    # Brute: windup/cooldown
    windup_remaining: float = 0.0
    windup_duration: float = 0.0
    # Hit flash for visual
    hit_flash_remaining: float = 0.0

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)
        self.hit_flash_remaining = 0.08  # brief flash

    def apply_elite_modifier(self) -> None:
        """Apply +40% HP, +20% damage. Call after setting base stats."""
        if not self.elite:
            return
        self.max_hp = int(self.max_hp * ELITE_HP_MULT)
        self.hp = self.max_hp
        self.damage = int(self.damage * ELITE_DAMAGE_MULT)
        if self.projectile_damage > 0:
            self.projectile_damage = int(self.projectile_damage * ELITE_DAMAGE_MULT)
