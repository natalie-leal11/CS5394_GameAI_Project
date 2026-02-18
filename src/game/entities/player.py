"""
Player entity: HP, movement state, dash state, trail for visual.
Base HP 100; collision radius 16 px. All numeric values from parameters.
"""
from dataclasses import dataclass, field

from src.game.entities.entity import Entity

# Section 4 / parameters: Base HP 100, collision radius 16
BASE_HP = 100
COLLISION_RADIUS = 16
MOVE_SPEED_PX_SEC = 220
DASH_SPEED_MULTIPLIER = 2.2
DASH_DURATION_SEC = 0.18
DASH_COOLDOWN_SEC = 1.0
DASH_TRAIL_FADE_SEC = 0.2


@dataclass
class Player(Entity):
    """Controllable player with HP, dash, and trail."""

    hp: int = BASE_HP
    radius: float = COLLISION_RADIUS
    # Facing for attacks (default right)
    facing_x: float = 1.0
    facing_y: float = 0.0
    # Dash state (deterministic timers)
    dash_remaining: float = 0.0  # sec left in current dash
    dash_cooldown_remaining: float = 0.0  # sec until next dash allowed
    # Attack cooldowns
    short_cooldown_remaining: float = 0.0
    long_cooldown_remaining: float = 0.0
    short_attack_active_remaining: float = 0.0  # visual duration
    # Block/parry: time when L was pressed (for 120 ms parry window)
    parry_press_time: float = -999.0
    parry_flash_remaining: float = 0.0  # brief white flash after parry
    # Trail for visual: list of (x, y, time_added)
    trail: list[tuple[float, float, float]] = field(default_factory=list)
    # Upgrade modifiers (bounded)
    max_hp_bonus_percent: float = 0.0
    move_speed_bonus_percent: float = 0.0
    attack_damage_bonus_percent: float = 0.0
    cooldown_reduction_percent: float = 0.0
    damage_reduction_bonus: float = 0.0

    def __post_init__(self) -> None:
        if self.radius != COLLISION_RADIUS:
            self.radius = COLLISION_RADIUS

    @property
    def max_hp(self) -> int:
        return int(BASE_HP * (1.0 + self.max_hp_bonus_percent))

    def get_move_speed(self) -> float:
        return MOVE_SPEED_PX_SEC * (1.0 + self.move_speed_bonus_percent)

    def is_dashing(self) -> bool:
        return self.dash_remaining > 0.0

    def can_dash(self) -> bool:
        return self.dash_cooldown_remaining <= 0.0 and not self.is_dashing()
