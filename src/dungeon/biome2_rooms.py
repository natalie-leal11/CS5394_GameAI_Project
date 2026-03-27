# Biome 2 room metadata: spawn specs, patterns, healing rules.
# Rooms 8-15 (indices 0-7 when USE_BIOME2).

from dungeon.room import RoomType
from dungeon.biome2_mini_boss_encounter import (
    BIOME2_MINI_BOSS_SPAWN_TIME,
    BIOME2_ADD_TELEGRAPH_SEC,
    get_biome2_mini_boss_adds_schedule,
)
from game.config import (
    SEED,
    SPAWN_SLOT_DELAY_SEC,
    BEGINNER_TEST_MODE,
    MIN_DISTANCE_FROM_PLAYER_PX,
    MIN_TILES_FROM_WALL,
    MIN_TILES_FROM_DOOR,
    MIN_DISTANCE_BETWEEN_ENEMIES_PX,
    ELITE_EXTRA_SPACING_PX,
    HEAL_DROP_CHANCE,
    SAFE_ROOM_HEAL_PERCENT,
    SAFE_ROOM_OVERHEAL_CAP_RATIO,
    MINI_BOSS_REWARD_HEAL_PERCENT,
    DOOR_UNLOCK_DELAY_SEC,
    MINI_BOSS_DOOR_UNLOCK_DELAY_SEC,
)


def _biome2_mini_boss_spawn_specs(Swarm, Flanker, Brute, Heavy, MiniBoss):
    """Mini boss + deterministic adds for Room 15."""
    specs = [(MiniBoss, False, BIOME2_MINI_BOSS_SPAWN_TIME, None)]
    for t, cls, elite in get_biome2_mini_boss_adds_schedule(Swarm, Flanker, Brute, Heavy):
        specs.append((cls, elite, t, BIOME2_ADD_TELEGRAPH_SEC))
    return specs


# Spawn slot delay = 0.4 s (SPAWN_SLOT_DELAY_SEC)
# Mini Boss spawn at 2.0 s
# Ambush telegraph = 1.5 s
# Elite spacing = MIN_DISTANCE_BETWEEN_ENEMIES_PX + ELITE_EXTRA_SPACING_PX = 150 px


def get_biome2_spawn_specs(
    room_idx: int,
    room_type: RoomType,
    Swarm,
    Flanker,
    Brute,
    Heavy,
    MiniBoss,
    *,
    seed: int | None = None,
):
    """
    Return spawn_specs for Biome 2 room. (enemy_cls, elite, start_time_sec, telegraph_sec or None).
    room_idx: 0-7 (maps to logical rooms 8-15).
    """
    if room_type == RoomType.SAFE:
        return []

    if BEGINNER_TEST_MODE:
        if room_idx == 0:  # Room 8 Combat 1
            return [
                (Swarm, False, 0.0, None),
                (Flanker, False, SPAWN_SLOT_DELAY_SEC, None),
                (Brute, False, SPAWN_SLOT_DELAY_SEC * 2, None),
            ]
        if room_idx == 1:  # Room 9 Combat 2
            return [
                (Flanker, False, 0.0, None),
                (Brute, False, SPAWN_SLOT_DELAY_SEC, None),
                (Heavy, False, SPAWN_SLOT_DELAY_SEC * 2, None),
            ]
        if room_idx == 2:  # Room 10 Ambush 1
            return [
                (Swarm, False, 0.0, 1.5),
                (Flanker, False, SPAWN_SLOT_DELAY_SEC, 1.5),
            ]
        if room_idx == 3:  # Room 11 Safe
            return []
        if room_idx == 4:  # Room 12 Combat 3
            return [
                (Swarm, False, 0.0, None),
                (Brute, False, SPAWN_SLOT_DELAY_SEC, None),
                (Brute, False, SPAWN_SLOT_DELAY_SEC * 2, None),
                (Heavy, False, SPAWN_SLOT_DELAY_SEC * 3, None),
            ]
        if room_idx == 5:  # Room 13 Elite
            return [
                (Brute, True, 0.0, None),
                (Swarm, True, SPAWN_SLOT_DELAY_SEC, None),
                (Swarm, False, SPAWN_SLOT_DELAY_SEC * 2, None),
            ]
        if room_idx == 6:  # Room 14 Ambush 2
            return [
                (Swarm, False, 0.0, 1.5),
                (Flanker, False, SPAWN_SLOT_DELAY_SEC, 1.5),
            ]
        if room_idx == 7:  # Room 15 Mini Boss (with adds)
            return _biome2_mini_boss_spawn_specs(Swarm, Flanker, Brute, Heavy, MiniBoss)

    # Non-beginner: SRS seed-controlled composition
    from dungeon.seeded_encounter_specs import build_biome2_spawn_specs

    s = SEED if seed is None else int(seed)
    campaign_index = 8 + int(room_idx)
    return build_biome2_spawn_specs(
        room_idx, room_type, campaign_index, s, Swarm, Flanker, Brute, Heavy, MiniBoss
    )


def get_biome2_spawn_pattern(room_type: RoomType):
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


def get_biome2_elite_spacing() -> bool:
    """True if room uses elite spacing (150 px)."""
    return True  # Only for ELITE rooms; caller checks room type


# Healing metadata (for later phases)
BIOME2_HEAL_DROP_CHANCE = HEAL_DROP_CHANCE  # 0.25
BIOME2_CLEAR_HEAL_PERCENT = 0.30
BIOME2_CLEAR_HEAL_CAP = 1.0  # 100% base
BIOME2_SAFE_ROOM_HEAL_PERCENT = SAFE_ROOM_HEAL_PERCENT  # 0.30
BIOME2_SAFE_ROOM_OVERHEAL_CAP = SAFE_ROOM_OVERHEAL_CAP_RATIO  # 1.30
BIOME2_MINI_BOSS_REWARD_PERCENT = MINI_BOSS_REWARD_HEAL_PERCENT  # 0.30
