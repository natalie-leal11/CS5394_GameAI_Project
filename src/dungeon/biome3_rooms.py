# Biome 3 room metadata: spawn specs and patterns. Rooms 16-23 (indices 0-7).

from dungeon.room import RoomType
from game.config import (
    SPAWN_SLOT_DELAY_SEC,
    BEGINNER_TEST_MODE,
)


def get_biome3_spawn_specs(room_idx: int, room_type: RoomType, Swarm, Flanker, Brute, Heavy, Ranged, MiniBoss):
    """
    Return spawn_specs for Biome 3 room. (enemy_cls, elite, start_time_sec, telegraph_sec or None).
    room_idx: 0-7 (maps to campaign rooms 16-23).
    Room 23 Mini Boss: pass Biome3MiniBoss as MiniBoss argument (Phase 3).
    """
    if room_type == RoomType.SAFE:
        return []

    if BEGINNER_TEST_MODE:
        if room_idx == 0:  # Room 16 Combat
            return [
                (Swarm, False, 0.0, None),
                (Flanker, False, SPAWN_SLOT_DELAY_SEC, None),
                (Ranged, False, SPAWN_SLOT_DELAY_SEC * 2, None),
            ]
        if room_idx == 1:  # Room 17 Combat
            return [
                (Flanker, False, 0.0, None),
                (Ranged, False, SPAWN_SLOT_DELAY_SEC, None),
                (Brute, False, SPAWN_SLOT_DELAY_SEC * 2, None),
            ]
        if room_idx == 2:  # Room 18 Ambush
            return [
                (Swarm, False, 0.0, 1.5),
                (Flanker, False, SPAWN_SLOT_DELAY_SEC, 1.5),
                (Ranged, False, SPAWN_SLOT_DELAY_SEC * 2, 1.5),
            ]
        if room_idx == 3:  # Room 19 Combat
            return [
                (Brute, False, 0.0, None),
                (Ranged, False, SPAWN_SLOT_DELAY_SEC, None),
                (Heavy, False, SPAWN_SLOT_DELAY_SEC * 2, None),
            ]
        if room_idx == 4:  # Room 20 Elite
            return [
                (Brute, True, 0.0, None),
                (Ranged, True, SPAWN_SLOT_DELAY_SEC, None),
                (Swarm, False, SPAWN_SLOT_DELAY_SEC * 2, None),
            ]
        if room_idx == 5:  # Room 21 Safe
            return []
        if room_idx == 6:  # Room 22 Combat
            return [
                (Swarm, False, 0.0, None),
                (Flanker, False, SPAWN_SLOT_DELAY_SEC, None),
                (Ranged, False, SPAWN_SLOT_DELAY_SEC * 2, None),
                (Heavy, False, SPAWN_SLOT_DELAY_SEC * 3, None),
            ]
        if room_idx == 7:  # Room 23 Mini Boss (placeholder until Phase 3)
            return [(MiniBoss, False, 2.0, None)]

    # Non-beginner: generic by room type
    if room_type == RoomType.MINI_BOSS:
        return [(MiniBoss, False, 2.0, None)]
    if room_type == RoomType.ELITE:
        return [
            (Brute, True, 0.0, None),
            (Ranged, True, SPAWN_SLOT_DELAY_SEC, None),
            (Swarm, False, SPAWN_SLOT_DELAY_SEC * 2, None),
        ]
    if room_type == RoomType.AMBUSH:
        return [
            (Swarm, False, 0.0, 1.5),
            (Flanker, False, SPAWN_SLOT_DELAY_SEC, 1.5),
            (Ranged, False, SPAWN_SLOT_DELAY_SEC * 2, 1.5),
        ]
    # COMBAT
    return [
        (Swarm, False, 0.0, None),
        (Flanker, False, SPAWN_SLOT_DELAY_SEC, None),
        (Ranged, False, SPAWN_SLOT_DELAY_SEC * 2, None),
        (Brute, False, SPAWN_SLOT_DELAY_SEC * 3, None),
    ]


def get_biome3_spawn_pattern(room_type: RoomType):
    """Return spawn pattern: 'spread', 'ambush', 'triangle', 'single', or None (safe)."""
    if room_type == RoomType.SAFE:
        return None
    if room_type == RoomType.ELITE:
        return "triangle"
    if room_type == RoomType.AMBUSH:
        return "ambush"
    if room_type == RoomType.MINI_BOSS:
        return "single"
    return "spread"
