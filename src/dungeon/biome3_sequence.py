# Biome 3 room sequence. Rooms 16-23 (indices 0-7 when USE_BIOME3).

import random

from game.config import BEGINNER_TEST_MODE, SEED
from dungeon.room import RoomType


def room_order_biome3(seed: int) -> list[RoomType]:
    """
    Biome 3 rooms 16-23. Fixed order when BEGINNER_TEST_MODE; else shuffle 16-22, 23 always Mini Boss.
    Returns 8 room types.
    """
    if BEGINNER_TEST_MODE:
        return [
            RoomType.COMBAT,     # 16
            RoomType.COMBAT,     # 17
            RoomType.AMBUSH,     # 18
            RoomType.COMBAT,     # 19
            RoomType.ELITE,      # 20
            RoomType.SAFE,       # 21
            RoomType.COMBAT,     # 22
            RoomType.MINI_BOSS,  # 23
        ]
    rng = random.Random(seed)
    mid = [
        RoomType.COMBAT,
        RoomType.COMBAT,
        RoomType.COMBAT,
        RoomType.AMBUSH,
        RoomType.ELITE,
        RoomType.SAFE,
        RoomType.COMBAT,
    ]
    rng.shuffle(mid)
    return mid + [RoomType.MINI_BOSS]


def total_biome3_rooms() -> int:
    return 8
