from typing import Tuple

from entities.enemy_base import EnemyBase


class Flanker(EnemyBase):
    """Fast flanker enemy. For Phase 3, simple chase using EnemyBase movement."""

    def __init__(self, world_pos: Tuple[float, float], elite: bool = False):
        super().__init__("flanker", world_pos, elite=elite)

