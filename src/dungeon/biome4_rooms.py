# Biome 4 room metadata: spawn specs and patterns. Rooms 24-29 (indices 0-5).
# Phase 1: rooms 24-28 composition; Room 29 (FINAL_BOSS) metadata only, no boss combat.

from dungeon.room import RoomType
from game.config import SPAWN_SLOT_DELAY_SEC

# Biome 4 spawn slot delay = 0.4 s (same as SPAWN_SLOT_DELAY_SEC).
BIOME4_AMBUSH_TELEGRAPH_SEC = 1.5
BIOME4_FINAL_BOSS_SPAWN_DELAY_SEC = 2.0


def get_biome4_spawn_specs(
    room_idx: int,
    room_type: RoomType,
    Swarm,
    Flanker,
    Brute,
    Heavy,
    Ranged,
) -> list[tuple]:
    """
    Return spawn_specs for Biome 4 room. (enemy_cls, elite, start_time_sec, telegraph_sec or None).
    room_idx: 0-5 (maps to campaign rooms 24-29).
    Room 29 (idx 5) FINAL_BOSS: metadata only, no spawns in Phase 1.
    """
    if room_type == RoomType.SAFE:
        return []
    if room_type == RoomType.FINAL_BOSS:
        # Phase 1: reserve metadata only; no boss entity spawned.
        return []

    # Room 24 — Combat: Swarm 0.0, Flanker 0.4, Ranged 0.8, Heavy 1.2
    if room_idx == 0 and room_type == RoomType.COMBAT:
        return [
            (Swarm, False, 0.0, None),
            (Flanker, False, SPAWN_SLOT_DELAY_SEC, None),
            (Ranged, False, SPAWN_SLOT_DELAY_SEC * 2, None),
            (Heavy, False, SPAWN_SLOT_DELAY_SEC * 3, None),
        ]
    # Room 25 — Combat: Brute 0.0, Ranged 0.4, Heavy 0.8
    if room_idx == 1 and room_type == RoomType.COMBAT:
        return [
            (Brute, False, 0.0, None),
            (Ranged, False, SPAWN_SLOT_DELAY_SEC, None),
            (Heavy, False, SPAWN_SLOT_DELAY_SEC * 2, None),
        ]
    # Room 26 — Ambush: Swarm, Flanker, Ranged (telegraph 1.5)
    if room_idx == 2 and room_type == RoomType.AMBUSH:
        return [
            (Swarm, False, 0.0, BIOME4_AMBUSH_TELEGRAPH_SEC),
            (Flanker, False, SPAWN_SLOT_DELAY_SEC, BIOME4_AMBUSH_TELEGRAPH_SEC),
            (Ranged, False, SPAWN_SLOT_DELAY_SEC * 2, BIOME4_AMBUSH_TELEGRAPH_SEC),
        ]
    # Room 27 — Elite: Brute (elite), Heavy (elite), Ranged (triangle, side 200px)
    if room_idx == 3 and room_type == RoomType.ELITE:
        return [
            (Brute, True, 0.0, None),
            (Heavy, True, SPAWN_SLOT_DELAY_SEC, None),
            (Ranged, False, SPAWN_SLOT_DELAY_SEC * 2, None),
        ]

    # Fallback by type (shuffled seed mode)
    if room_type == RoomType.ELITE:
        return [
            (Brute, True, 0.0, None),
            (Heavy, True, SPAWN_SLOT_DELAY_SEC, None),
            (Ranged, False, SPAWN_SLOT_DELAY_SEC * 2, None),
        ]
    if room_type == RoomType.AMBUSH:
        return [
            (Swarm, False, 0.0, BIOME4_AMBUSH_TELEGRAPH_SEC),
            (Flanker, False, SPAWN_SLOT_DELAY_SEC, BIOME4_AMBUSH_TELEGRAPH_SEC),
            (Ranged, False, SPAWN_SLOT_DELAY_SEC * 2, BIOME4_AMBUSH_TELEGRAPH_SEC),
        ]
    if room_type == RoomType.COMBAT:
        return [
            (Swarm, False, 0.0, None),
            (Flanker, False, SPAWN_SLOT_DELAY_SEC, None),
            (Ranged, False, SPAWN_SLOT_DELAY_SEC * 2, None),
            (Heavy, False, SPAWN_SLOT_DELAY_SEC * 3, None),
        ]
    return []


def get_biome4_spawn_pattern(room_type: RoomType):
    """Return spawn pattern: 'spread', 'ambush', 'triangle', 'single', or None (safe/final_boss)."""
    if room_type == RoomType.SAFE or room_type == RoomType.FINAL_BOSS:
        return None
    if room_type == RoomType.ELITE:
        return "triangle"
    if room_type == RoomType.AMBUSH:
        return "ambush"
    return "spread"


# Biome 4 ambush ring radius (px). Other biomes may use different value.
BIOME4_AMBUSH_RADIUS_PX = 160
# Biome 4 Elite triangle: side length 200 px => offset = 200/sqrt(2) ~ 141.
BIOME4_TRIANGLE_OFFSET_PX = 200 / (2 ** 0.5)
