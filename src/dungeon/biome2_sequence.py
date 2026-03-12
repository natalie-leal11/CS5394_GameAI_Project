# Biome 2 room sequence. Rooms 8-15 (indices 0-7 when USE_BIOME2).

import random

from game.config import BEGINNER_TEST_MODE, SEED
from dungeon.room import RoomType


def room_order_biome2(seed: int) -> list[RoomType]:
    """
    Biome 2 rooms 8-15. Fixed order when BEGINNER_TEST_MODE; else shuffled.
    Returns 8 room types: Combat1, Combat2, Ambush1, Safe, Combat3, Elite, Ambush2, MiniBoss.
    """
    if BEGINNER_TEST_MODE:
        return [
            RoomType.COMBAT,    # 8 Combat 1
            RoomType.COMBAT,    # 9 Combat 2
            RoomType.AMBUSH,   # 10 Ambush 1
            RoomType.SAFE,     # 11 Safe
            RoomType.COMBAT,    # 12 Combat 3
            RoomType.ELITE,    # 13 Elite
            RoomType.AMBUSH,   # 14 Ambush 2
            RoomType.MINI_BOSS,  # 15 Mini Boss
        ]
    rng = random.Random(seed)
    mid = [
        RoomType.COMBAT, RoomType.COMBAT, RoomType.COMBAT,
        RoomType.AMBUSH, RoomType.AMBUSH,
        RoomType.SAFE,
        RoomType.ELITE,
    ]
    rng.shuffle(mid)
    return mid + [RoomType.MINI_BOSS]


def total_biome2_rooms() -> int:
    return 8
