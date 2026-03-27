# Biome 4 room sequence. Rooms 24-29 (indices 0-5 when USE_BIOME4).

from dungeon.room import RoomType


def room_order_biome4(seed: int) -> list[RoomType]:
    """
    Biome 4 rooms 24-29. SRS §4.1.4 multiset + seed shuffle (Beginner Test Mode = fixed order).
    """
    from dungeon.srs_biome_order import room_order_biome4_srs

    return room_order_biome4_srs(seed)


def total_biome4_rooms() -> int:
    return 6
