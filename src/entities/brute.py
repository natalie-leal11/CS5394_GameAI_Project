from typing import Tuple

from entities.enemy_base import EnemyBase


class Brute(EnemyBase):
    """Brute enemy (80x80). Phase 3: slow chaser with higher HP/damage."""

    def __init__(self, world_pos: Tuple[float, float], elite: bool = False, **kwargs):
        super().__init__("brute", world_pos, elite=elite, **kwargs)

