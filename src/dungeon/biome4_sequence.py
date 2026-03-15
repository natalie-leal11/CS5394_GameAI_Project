# Biome 4 room sequence. Rooms 24-29 (indices 0-5 when USE_BIOME4).

import random

from game.config import BEGINNER_TEST_MODE, SEED
from dungeon.room import RoomType


def room_order_biome4(seed: int) -> list[RoomType]:
    """
    Biome 4 rooms 24-29. Fixed order when BEGINNER_TEST_MODE; else shuffle 24-28, 29 always FINAL_BOSS.
    Returns 6 room types.
    """
    if BEGINNER_TEST_MODE:
        return [
            RoomType.COMBAT,     # 24
            RoomType.COMBAT,     # 25
            RoomType.AMBUSH,     # 26
            RoomType.ELITE,      # 27
            RoomType.SAFE,       # 28
            RoomType.FINAL_BOSS, # 29
        ]
    rng = random.Random(seed)
    mid = [
        RoomType.COMBAT,
        RoomType.COMBAT,
        RoomType.AMBUSH,
        RoomType.ELITE,
        RoomType.SAFE,
    ]
    rng.shuffle(mid)
    return mid + [RoomType.FINAL_BOSS]


def total_biome4_rooms() -> int:
    return 6
