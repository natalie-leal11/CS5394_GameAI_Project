"""
SRS §4.1.5–4.1.6 — Seed-controlled encounter composition within biome/room-type bounds.

Deterministic: same (seed, campaign_index, room_type) → same specs.
Does not alter boss identity, elite multipliers, or safe-room enemy count (0).
"""

from __future__ import annotations

from typing import Any, Type

from game.rng import derive_seed
from dungeon.room import RoomType
from game.config import SPAWN_SLOT_DELAY_SEC
from dungeon.biome4_rooms import BIOME4_AMBUSH_TELEGRAPH_SEC


def _variant(seed: int) -> int:
    return int(seed) % 3


def _stagger_specs(
    classes: list[Type[Any]],
    elite_flags: list[bool],
    telegraphs: list[float | None] | None = None,
) -> list[tuple[Any, bool, float, Any]]:
    telegraphs = telegraphs or [None] * len(classes)
    time_acc = 0.0
    out: list[tuple[Any, bool, float, Any]] = []
    for i, cls in enumerate(classes):
        tele = telegraphs[i] if i < len(telegraphs) else None
        out.append((cls, elite_flags[i], time_acc, tele))
        time_acc += SPAWN_SLOT_DELAY_SEC
    return out


# --- Biome 1 -----------------------------------------------------------------


def build_biome1_spawn_specs(
    room_idx: int,
    room_type: RoomType,
    campaign_index: int,
    seed: int,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
    MiniBoss: Type[Any],
) -> list[tuple[Any, bool, float, Any]]:
    v = _variant(seed)

    if room_type in (RoomType.START, RoomType.SAFE):
        return []
    if room_type == RoomType.MINI_BOSS:
        return [(MiniBoss, False, 2.0, None)]

    if room_type == RoomType.COMBAT:
        if v == 0:
            classes = [Swarm, Flanker, Brute]
        elif v == 1:
            classes = [Swarm, Flanker]
        else:
            classes = [Swarm, Swarm, Flanker] if (campaign_index % 2 == 0) else [Swarm, Flanker, Brute]
        return _stagger_specs(classes, [False] * len(classes))

    if room_type == RoomType.AMBUSH:
        if v == 0:
            classes = [Swarm, Flanker, Brute]
        elif v == 1:
            classes = [Swarm, Flanker]
        else:
            classes = [Swarm, Swarm] if (campaign_index % 2 == 0) else [Swarm, Flanker, Brute]
        tele = [1.5] * len(classes)
        return _stagger_specs(classes, [False] * len(classes), tele)

    if room_type == RoomType.ELITE:
        if v == 0:
            classes = [Swarm, Flanker, Brute]
            elite_flags = [True, True, True]
        elif v == 1:
            classes = [Brute, Swarm]
            elite_flags = [True, False]
        else:
            if (derive_seed(seed, campaign_index, 0xE1) & 1) == 0:
                classes = [Brute, Swarm]
                elite_flags = [True, False]
            else:
                classes = [Swarm, Flanker, Brute]
                elite_flags = [True, True, True]
        return _stagger_specs(classes, elite_flags)

    return []


# --- Biome 2 -----------------------------------------------------------------


def build_biome2_spawn_specs(
    room_idx: int,
    room_type: RoomType,
    campaign_index: int,
    seed: int,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
    Heavy: Type[Any],
    MiniBoss: Type[Any],
) -> list[tuple[Any, bool, float, Any]]:
    from dungeon.biome2_rooms import _biome2_mini_boss_spawn_specs

    v = _variant(seed)

    if room_type == RoomType.SAFE:
        return []
    if room_type == RoomType.MINI_BOSS:
        return _biome2_mini_boss_spawn_specs(Swarm, Flanker, Brute, Heavy, MiniBoss)

    if room_type == RoomType.COMBAT:
        if v == 0:
            classes = [Swarm, Flanker, Brute]
        elif v == 1:
            classes = [Swarm, Flanker, Heavy, Brute]
        else:
            classes = [Swarm, Swarm, Heavy] if (campaign_index % 2 == 0) else [Flanker, Brute, Heavy]
        return _stagger_specs(classes, [False] * len(classes))

    if room_type == RoomType.AMBUSH:
        if v == 0:
            classes = [Swarm, Flanker, Brute]
        elif v == 1:
            classes = [Swarm, Flanker, Heavy]
        else:
            classes = [Swarm, Flanker, Heavy]
        tele = [1.5] * len(classes)
        return _stagger_specs(classes, [False] * len(classes), tele)

    if room_type == RoomType.ELITE:
        if v == 0:
            classes = [Brute, Swarm]
            elite_flags = [True, False]
        elif v == 1:
            classes = [Heavy, Brute, Swarm]
            elite_flags = [True, True, False]
        else:
            classes = [Brute, Heavy]
            elite_flags = [True, True]
        return _stagger_specs(classes, elite_flags)

    return []


# --- Biome 3 -----------------------------------------------------------------


def build_biome3_spawn_specs(
    room_idx: int,
    room_type: RoomType,
    campaign_index: int,
    seed: int,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
    Heavy: Type[Any],
    Ranged: Type[Any],
    MiniBoss: Type[Any],
) -> list[tuple[Any, bool, float, Any]]:
    v = _variant(seed)

    if room_type == RoomType.SAFE:
        return []
    if room_type == RoomType.MINI_BOSS:
        return [(MiniBoss, False, 2.0, None)]

    if room_type == RoomType.COMBAT:
        if v == 0:
            classes = [Swarm, Flanker, Ranged, Brute]
        elif v == 1:
            classes = [Flanker, Ranged, Brute, Heavy]
        else:
            classes = [Brute, Ranged, Heavy] if (campaign_index % 2 == 0) else [Swarm, Ranged, Heavy, Flanker]
        return _stagger_specs(classes, [False] * len(classes))

    if room_type == RoomType.AMBUSH:
        if v == 0:
            classes = [Swarm, Flanker, Ranged]
        elif v == 1:
            classes = [Swarm, Flanker, Ranged, Heavy]
        else:
            classes = [Swarm, Ranged, Heavy] if (campaign_index % 2 == 0) else [Flanker, Ranged, Heavy]
        tele = [1.5] * len(classes)
        return _stagger_specs(classes, [False] * len(classes), tele)

    if room_type == RoomType.ELITE:
        if v == 0:
            classes = [Brute, Ranged, Swarm]
            elite_flags = [True, True, False]
        elif v == 1:
            classes = [Brute, Ranged, Heavy]
            elite_flags = [True, True, False]
        else:
            classes = [Brute, Heavy, Ranged]
            elite_flags = [True, True, False]
        return _stagger_specs(classes, elite_flags)

    return []


# --- Biome 4 -----------------------------------------------------------------


def build_biome4_spawn_specs(
    room_idx: int,
    room_type: RoomType,
    campaign_index: int,
    seed: int,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
    Heavy: Type[Any],
    Ranged: Type[Any],
) -> list[tuple[Any, bool, float, Any]]:
    v = _variant(seed)

    if room_type in (RoomType.SAFE, RoomType.FINAL_BOSS):
        return []

    if room_type == RoomType.COMBAT:
        if v == 0:
            classes = [Swarm, Flanker, Ranged]
        elif v == 1:
            classes = [Swarm, Brute, Heavy, Ranged]
        else:
            classes = [Swarm, Ranged, Heavy]
        return _stagger_specs(classes, [False] * len(classes))

    if room_type == RoomType.AMBUSH:
        if v == 0:
            classes = [Swarm, Flanker, Ranged]
        elif v == 1:
            classes = [Swarm, Flanker, Ranged, Heavy]
        else:
            classes = [Swarm, Flanker, Ranged, Heavy]
        tele = [BIOME4_AMBUSH_TELEGRAPH_SEC] * len(classes)
        return _stagger_specs(classes, [False] * len(classes), tele)

    if room_type == RoomType.ELITE:
        if v == 0:
            classes = [Brute, Ranged]
            elite_flags = [True, True]
        elif v == 1:
            classes = [Brute, Heavy, Ranged]
            elite_flags = [True, True, True]
        else:
            classes = [Brute, Heavy, Ranged]
            elite_flags = [True, True, False]
        return _stagger_specs(classes, elite_flags)

    return []
