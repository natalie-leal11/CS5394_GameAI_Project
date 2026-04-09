from typing import Tuple

from entities.enemy_base import EnemyBase


class Heavy(EnemyBase):
    """Heavy enemy (88x88). Movement matches Brute (EnemyBase.update): direct chase, wall slide, deterministic sidestep when stalled."""

    def __init__(self, world_pos: Tuple[float, float], elite: bool = False, **kwargs):
        super().__init__("heavy", world_pos, elite=elite, **kwargs)
