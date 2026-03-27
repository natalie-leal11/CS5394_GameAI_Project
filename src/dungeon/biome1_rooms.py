# Biome 1 spawn metadata (SRS §4.1.5). Rooms 0–7.

from __future__ import annotations

from typing import Any, Type

from dungeon.room import RoomType
from dungeon.seeded_encounter_specs import build_biome1_spawn_specs
from game.config import SEED


def get_biome1_spawn_specs(
    room_idx: int,
    room_type: RoomType,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
    MiniBoss: Type[Any],
    *,
    seed: int | None = None,
    campaign_index: int | None = None,
) -> list[tuple[Any, bool, float, Any]]:
    """
    room_idx: 0–7 (campaign index equals room_idx for Biome 1).
    """
    s = int(SEED if seed is None else seed)
    ci = int(room_idx if campaign_index is None else campaign_index)
    return build_biome1_spawn_specs(room_idx, room_type, ci, s, Swarm, Flanker, Brute, MiniBoss)


def get_biome1_spawn_pattern(room_type: RoomType) -> str | None:
    if room_type in (RoomType.START, RoomType.SAFE):
        return None
    if room_type == RoomType.ELITE:
        return "triangle"
    if room_type == RoomType.AMBUSH:
        return "ambush"
    if room_type == RoomType.MINI_BOSS:
        return "single"
    return "spread"
