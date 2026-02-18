"""
Player projectiles: long attack. Speed 520 px/sec, lifetime 1.2 sec, radius 6 px.
"""
from dataclasses import dataclass


@dataclass
class Projectile:
    """Single projectile from long attack."""

    x: float
    y: float
    vx: float
    vy: float
    radius: float  # 6 px
    lifetime_remaining: float  # sec
    damage: int  # 15-25, set at spawn
    from_player: bool = True

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime_remaining -= dt

    def is_alive(self) -> bool:
        return self.lifetime_remaining > 0
