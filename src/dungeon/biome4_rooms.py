# Biome 4 room metadata: spawn specs and patterns. Rooms 24-29 (indices 0-5).
# Phase 1: rooms 24-28 composition; Room 29 (FINAL_BOSS) metadata only, no boss combat.

from dungeon.room import RoomType
from game.config import SEED, SPAWN_SLOT_DELAY_SEC, BIOME4_START_INDEX

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
    *,
    seed: int | None = None,
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

    from dungeon.seeded_encounter_specs import build_biome4_spawn_specs

    s = SEED if seed is None else int(seed)
    campaign_index = BIOME4_START_INDEX + int(room_idx)
    return build_biome4_spawn_specs(
        room_idx, room_type, campaign_index, s, Swarm, Flanker, Brute, Heavy, Ranged
    )


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
