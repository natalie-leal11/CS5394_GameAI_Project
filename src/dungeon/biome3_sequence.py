# Biome 3 room sequence. Rooms 16-23 (indices 0-7 when USE_BIOME3).

from dungeon.room import RoomType


def room_order_biome3(seed: int) -> list[RoomType]:
    """
    Biome 3 rooms 16-23. SRS §4.1.4 multiset + seed shuffle (Beginner Test Mode = fixed order).
    """
    from dungeon.srs_biome_order import room_order_biome3_srs

    return room_order_biome3_srs(seed)


def total_biome3_rooms() -> int:
    return 8
