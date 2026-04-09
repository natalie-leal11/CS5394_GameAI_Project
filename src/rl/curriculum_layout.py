"""
Deterministic layout helpers for E/F curriculum micro-scenarios (RL-only).

# RL-only path — safe to remove if RL is abandoned
"""

from __future__ import annotations

from dungeon.room import RoomType
from dungeon.srs_biome_order import room_order_biome1_srs


def first_safe_room_index_biome1(seed: int) -> int:
    """Campaign room index of the first SAFE room in biome 1 for this run seed."""
    order = room_order_biome1_srs(int(seed))
    for i, rt in enumerate(order):
        if rt == RoomType.SAFE:
            return i
    return 3
