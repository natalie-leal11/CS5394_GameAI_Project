# Biome 2 room sequence. Rooms 8-15 (indices 0-7 when USE_BIOME2).

from dungeon.room import RoomType


def room_order_biome2(seed: int) -> list[RoomType]:
    """
    Biome 2 rooms 8-15. SRS §4.1.4 multiset + seed shuffle (Beginner Test Mode = fixed order).
    """
    from dungeon.srs_biome_order import room_order_biome2_srs

    return room_order_biome2_srs(seed)


def total_biome2_rooms() -> int:
    return 8
