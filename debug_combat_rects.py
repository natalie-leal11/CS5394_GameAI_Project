import math

from game.config import (
    PLAYER_SHORT_ATTACK_RANGE_PX,
    PLAYER_SHORT_ATTACK_WINDUP_SEC,
    PLAYER_SHORT_ATTACK_ACTIVE_SEC,
    PLAYER_LONG_ATTACK_RANGE_PX,
    PLAYER_SIZE,
)
from entities.player import Player
from systems.combat import apply_player_attacks


class DummyEnemy:
    def __init__(self, x: float, y: float, hp: float = 50.0) -> None:
        self.world_pos = (x, y)
        self.enemy_type = "swarm"
        self.hp = hp
        self.inactive = False


def main() -> None:
    p = Player()
    p.world_pos = (0.0, 0.0)
    p.facing = (1.0, 0.0)
    p.state = "attack_short"
    p._short_attack_timer = (
        PLAYER_SHORT_ATTACK_WINDUP_SEC + PLAYER_SHORT_ATTACK_ACTIVE_SEC / 2.0
    )
    print("is_short_attack_active:", p.is_short_attack_active())

    # Enemy in front
    front = DummyEnemy(PLAYER_SHORT_ATTACK_RANGE_PX * 0.8, 0.0)
    print("front before:", front.world_pos, front.hp)
    events_front = apply_player_attacks(p, [front])
    print("front after:", front.hp, "events:", events_front)

    # Enemy at 120 degrees
    r = PLAYER_SHORT_ATTACK_RANGE_PX * 0.8
    rad = math.radians(120.0)
    side = DummyEnemy(r * math.cos(rad), r * math.sin(rad))
    print("side before:", side.world_pos, side.hp)
    events_side = apply_player_attacks(p, [side])
    print("side after:", side.hp, "events:", events_side)

    # Long attack
    from game.config import PLAYER_LONG_ATTACK_WINDUP_SEC

    p.state = "attack_long"
    p._long_attack_timer = PLAYER_LONG_ATTACK_WINDUP_SEC + 0.01
    print("should_fire_long_attack:", p.should_fire_long_attack())
    long_enemy = DummyEnemy(PLAYER_LONG_ATTACK_RANGE_PX * 0.5, 0.0, hp=40.0)
    print("long before:", long_enemy.world_pos, long_enemy.hp)
    events_long = apply_player_attacks(p, [long_enemy])
    print("long after:", long_enemy.hp, "events:", events_long)


if __name__ == "__main__":
    main()

