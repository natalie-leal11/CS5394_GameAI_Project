"""
Boss entities: Mini Boss (rooms 7, 15, 23) and Final Boss (room 29).
Deterministic patterns; no internal random calls.
"""
from dataclasses import dataclass, field

from src.game.entities.entity import Entity

# Mini Boss: HP 600-700 (use midpoint or from rng at spawn)
MINI_BOSS_HP_MIN = 600
MINI_BOSS_HP_MAX = 700
MINI_BOSS_SPEED = 100
MINI_BOSS_DAMAGE = 18

# Final Boss: HP 1200, 2 phases
FINAL_BOSS_HP = 1200
FINAL_BOSS_SPEED_PHASE1 = 140
FINAL_BOSS_SPEED_PHASE2 = 140 * 1.10  # +10%
FINAL_BOSS_DAMAGE = 20
FINAL_BOSS_PHASE2_INVULN_SEC = 2.0
FINAL_BOSS_COOLDOWN_MULT_PHASE2 = 0.80  # -20%


@dataclass
class Boss(Entity):
    """Single boss: mini or final. Deterministic timers only."""

    max_hp: int = 1200
    hp: int = 1200
    speed: float = 140.0
    damage: int = 20
    is_final_boss: bool = False
    # Phase 2 (final boss only)
    phase2: bool = False
    phase2_invuln_remaining: float = 0.0
    attack_cooldown_remaining: float = 0.0
    attack_cooldown_base: float = 1.5
    hit_flash_remaining: float = 0.0
    summoned: bool = False  # one summon at phase 2 start

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        if self.phase2_invuln_remaining > 0:
            return
        self.hp = max(0, self.hp - amount)
        self.hit_flash_remaining = 0.08
        if self.is_final_boss and not self.phase2 and self.hp <= self.max_hp // 2:
            self.phase2 = True
            self.phase2_invuln_remaining = FINAL_BOSS_PHASE2_INVULN_SEC
            self.speed = FINAL_BOSS_SPEED_PHASE2
            self.attack_cooldown_base *= FINAL_BOSS_COOLDOWN_MULT_PHASE2

    def tick(self, dt: float) -> None:
        if self.phase2_invuln_remaining > 0:
            self.phase2_invuln_remaining -= dt
            if self.phase2_invuln_remaining < 0:
                self.phase2_invuln_remaining = 0.0
        if self.attack_cooldown_remaining > 0:
            self.attack_cooldown_remaining -= dt
            if self.attack_cooldown_remaining < 0:
                self.attack_cooldown_remaining = 0.0
        if self.hit_flash_remaining > 0:
            self.hit_flash_remaining -= dt
            if self.hit_flash_remaining < 0:
                self.hit_flash_remaining = 0.0


def create_mini_boss(x: float, y: float, hp: int = 650) -> Boss:
    """Mini boss for rooms 7, 15, 23. HP in [600, 700]."""
    return Boss(
        x=x, y=y, radius=24.0,
        max_hp=hp, hp=hp,
        speed=MINI_BOSS_SPEED,
        damage=MINI_BOSS_DAMAGE,
        is_final_boss=False,
        attack_cooldown_base=1.8,
    )


def create_final_boss(x: float, y: float) -> Boss:
    """Final boss for room 29 only."""
    return Boss(
        x=x, y=y, radius=28.0,
        max_hp=FINAL_BOSS_HP, hp=FINAL_BOSS_HP,
        speed=FINAL_BOSS_SPEED_PHASE1,
        damage=FINAL_BOSS_DAMAGE,
        is_final_boss=True,
        attack_cooldown_base=1.5,
    )
