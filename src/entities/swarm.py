from typing import Tuple

from entities.enemy_base import EnemyBase


class Swarm(EnemyBase):
    """Melee swarm enemy. Simple chaser using EnemyBase behaviour."""

    def __init__(self, world_pos: Tuple[float, float], elite: bool = False, **kwargs):
        super().__init__("swarm", world_pos, elite=elite, **kwargs)

