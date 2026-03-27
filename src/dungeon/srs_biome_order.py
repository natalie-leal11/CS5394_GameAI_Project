"""
seed_determinism.md §2.1–§2.3 room composition rules.
"""

from __future__ import annotations

from game.rng import derive_seed
from dungeon.room import RoomType
from game.config import BEGINNER_TEST_MODE


def _variant(seed: int) -> int:
    return int(seed) % 3


def _safe_mid_for_8(seed: int, biome_id: int) -> int:
    """
    For 8-room biomes, SAFE local index is bounded to {3,4} per document §2.1.
    Variant mapping:
      0 -> 3
      1 -> 4
      2 -> deterministic choice between 3/4
    """
    v = _variant(seed)
    if v == 0:
        return 3
    if v == 1:
        return 4
    mixed = derive_seed(seed, biome_id, 0x53414645)  # SAFE
    return 3 if (mixed & 1) == 0 else 4


def room_order_biome1_srs(seed: int) -> list[RoomType]:
    """Biome 1: fixed START/MINI_BOSS; seed controls SAFE index + flexible ordering."""
    if BEGINNER_TEST_MODE:
        return [
            RoomType.START,
            RoomType.COMBAT,
            RoomType.COMBAT,
            RoomType.SAFE,
            RoomType.COMBAT,
            RoomType.ELITE,
            RoomType.AMBUSH,
            RoomType.MINI_BOSS,
        ]
    v = _variant(seed)
    safe_local = _safe_mid_for_8(seed, 1)
    profile = {
        0: [RoomType.COMBAT, RoomType.COMBAT, RoomType.COMBAT, RoomType.ELITE, RoomType.AMBUSH],
        1: [RoomType.COMBAT, RoomType.ELITE, RoomType.COMBAT, RoomType.AMBUSH, RoomType.COMBAT],
        2: [RoomType.COMBAT, RoomType.COMBAT, RoomType.AMBUSH, RoomType.ELITE, RoomType.COMBAT],
    }[v]
    out = [RoomType.START] + [RoomType.COMBAT] * 6 + [RoomType.MINI_BOSS]
    out[safe_local] = RoomType.SAFE
    flex_indices = [i for i in range(1, 7) if i != safe_local]
    for idx, rt in zip(flex_indices, profile):
        out[idx] = rt
    return out


def room_order_biome2_srs(seed: int) -> list[RoomType]:
    """Biome 2: MINI_BOSS fixed last; SAFE bounded; flexible ordering by 3 variants."""
    if BEGINNER_TEST_MODE:
        return [
            RoomType.COMBAT,
            RoomType.COMBAT,
            RoomType.AMBUSH,
            RoomType.SAFE,
            RoomType.COMBAT,
            RoomType.ELITE,
            RoomType.AMBUSH,
            RoomType.MINI_BOSS,
        ]
    v = _variant(seed)
    safe_local = _safe_mid_for_8(seed, 2)
    # Slots excluding SAFE and terminal boss. Fixed local0 kept COMBAT (entry transition).
    profile = {
        0: [RoomType.COMBAT, RoomType.COMBAT, RoomType.COMBAT, RoomType.ELITE, RoomType.AMBUSH],
        1: [RoomType.COMBAT, RoomType.ELITE, RoomType.COMBAT, RoomType.ELITE, RoomType.AMBUSH],
        2: [RoomType.COMBAT, RoomType.AMBUSH, RoomType.COMBAT, RoomType.ELITE, RoomType.AMBUSH],
    }[v]
    out = [RoomType.COMBAT] * 7 + [RoomType.MINI_BOSS]
    out[safe_local] = RoomType.SAFE
    flex_indices = [i for i in range(1, 7) if i != safe_local]
    for idx, rt in zip(flex_indices, profile):
        out[idx] = rt
    return out


def room_order_biome3_srs(seed: int) -> list[RoomType]:
    """Biome 3: MINI_BOSS fixed last; SAFE bounded; flexible ordering by 3 variants."""
    if BEGINNER_TEST_MODE:
        return [
            RoomType.COMBAT,
            RoomType.COMBAT,
            RoomType.AMBUSH,
            RoomType.COMBAT,
            RoomType.ELITE,
            RoomType.SAFE,
            RoomType.COMBAT,
            RoomType.MINI_BOSS,
        ]
    v = _variant(seed)
    safe_local = _safe_mid_for_8(seed, 3)
    profile = {
        0: [RoomType.COMBAT, RoomType.ELITE, RoomType.COMBAT, RoomType.ELITE, RoomType.AMBUSH],
        1: [RoomType.AMBUSH, RoomType.ELITE, RoomType.COMBAT, RoomType.ELITE, RoomType.AMBUSH],
        2: [RoomType.COMBAT, RoomType.AMBUSH, RoomType.ELITE, RoomType.ELITE, RoomType.COMBAT],
    }[v]
    out = [RoomType.COMBAT] * 7 + [RoomType.MINI_BOSS]
    out[safe_local] = RoomType.SAFE
    flex_indices = [i for i in range(1, 7) if i != safe_local]
    for idx, rt in zip(flex_indices, profile):
        out[idx] = rt
    return out


def room_order_biome4_srs(seed: int) -> list[RoomType]:
    """
    Biome 4 latest intended SAFE rule (from final section examples): SAFE at local index 2
    in the 6-room biome segment, FINAL_BOSS fixed at local 5.
    """
    if BEGINNER_TEST_MODE:
        return [
            RoomType.COMBAT,
            RoomType.COMBAT,
            RoomType.AMBUSH,
            RoomType.ELITE,
            RoomType.SAFE,
            RoomType.FINAL_BOSS,
        ]
    v = _variant(seed)
    # FINAL rule: SAFE at local index 3 or 4 => campaign 27 or 28.
    safe_local = 3 if (int(seed) % 2 == 0) else 4
    # local 0 is non-seed entry transition room, local 5 fixed FINAL_BOSS.
    profile = {
        0: [RoomType.COMBAT, RoomType.ELITE, RoomType.AMBUSH],
        1: [RoomType.ELITE, RoomType.ELITE, RoomType.AMBUSH],
        2: [RoomType.AMBUSH, RoomType.ELITE, RoomType.AMBUSH],
    }[v]
    out = [RoomType.COMBAT, RoomType.COMBAT, RoomType.COMBAT, RoomType.COMBAT, RoomType.COMBAT, RoomType.FINAL_BOSS]
    out[safe_local] = RoomType.SAFE
    flex_indices = [1, 2, 3, 4]
    flex_indices = [i for i in flex_indices if i != safe_local]
    for idx, rt in zip(flex_indices, profile):
        out[idx] = rt
    return out
