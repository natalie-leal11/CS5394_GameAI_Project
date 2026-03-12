from typing import Tuple

from entities.enemy_base import EnemyBase


class Heavy(EnemyBase):
    """Biome 2 Heavy enemy (88x88). Heavy armored, slow chaser."""

    def __init__(self, world_pos: Tuple[float, float], elite: bool = False):
        super().__init__("heavy", world_pos, elite=elite)
