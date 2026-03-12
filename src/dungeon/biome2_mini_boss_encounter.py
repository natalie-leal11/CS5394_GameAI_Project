# Biome 2 mini boss encounter: deterministic adds schedule.
# Room 15 (index 7 when USE_BIOME2) only.

from typing import List, Tuple, Type

# Fixed timings (seconds since room entry). Mini boss at 2.0 s; adds at deterministic intervals.
BIOME2_MINI_BOSS_SPAWN_TIME = 2.0
BIOME2_ADD_1_TIME = 8.0   # Swarm
BIOME2_ADD_2_TIME = 12.0  # Flanker
BIOME2_ADD_3_TIME = 16.0  # Brute
BIOME2_ADD_4_TIME = 20.0  # Heavy
BIOME2_ADD_TELEGRAPH_SEC = 0.5


def get_biome2_mini_boss_adds_schedule(Swarm, Flanker, Brute, Heavy) -> List[Tuple[float, Type, bool]]:
    """
    Return deterministic adds schedule for Biome 2 mini boss encounter.
    Each entry: (start_time_sec, enemy_cls, elite).
    """
    return [
        (BIOME2_ADD_1_TIME, Swarm, False),
        (BIOME2_ADD_2_TIME, Flanker, False),
        (BIOME2_ADD_3_TIME, Brute, False),
        (BIOME2_ADD_4_TIME, Heavy, False),
    ]
