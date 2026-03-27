"""
Biome 1 only: deterministic spawn adjustments from AIDirector outputs.
Does not affect other biomes or MiniBoss / START / SAFE.
"""

from __future__ import annotations

import random
from typing import Any, Type

from dungeon.room import RoomType
from game.config import SEED, SPAWN_SLOT_DELAY_SEC

BIOME1_COMBAT_MAX = 4
BIOME1_ELIGIBLE = (RoomType.COMBAT, RoomType.AMBUSH, RoomType.ELITE)
# Trial / onboarding: campaign rooms 1–4 in Biome 1 — no AI Director enemy count or composition swings
BIOME1_TRIAL_ROOM_MIN = 1
BIOME1_TRIAL_ROOM_MAX = 4


def biome1_trial_phase_active(room_idx: int, biome_index: int) -> bool:
    return biome_index == 1 and BIOME1_TRIAL_ROOM_MIN <= room_idx <= BIOME1_TRIAL_ROOM_MAX


def biome1_director_spawn_eligible(
    *,
    room_idx: int,
    biome_index: int,
    room_type: RoomType,
    beginner_test_mode: bool,
) -> bool:
    if beginner_test_mode:
        return False
    if biome_index != 1:
        return False
    if room_idx >= 8:
        return False
    return room_type in BIOME1_ELIGIBLE


def _scale_start_time(t: float, difficulty_modifier: float) -> float:
    if t <= 0.0:
        return t
    if difficulty_modifier <= 0:
        return max(0.2, t)
    scaled = t / difficulty_modifier
    return max(0.2, min(scaled, t * 1.5))


def _spec_clone(specs: list[tuple[Any, bool, float, Any]]) -> list[list[Any]]:
    return [[s[0], s[1], s[2], s[3]] for s in specs]


def _spec_freeze(rows: list[list[Any]]) -> list[tuple[Any, bool, float, Any]]:
    return [(r[0], bool(r[1]), float(r[2]), r[3]) for r in rows]


def _apply_composition_bias(
    rows: list[list[Any]],
    room_type: RoomType,
    composition_bias: str,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
) -> None:
    if composition_bias == "normal":
        return

    def _has_brute() -> bool:
        return any(r[0] is Brute for r in rows)

    if room_type == RoomType.COMBAT:
        if composition_bias == "lighter":
            for i in range(len(rows) - 1, -1, -1):
                if rows[i][0] is Brute:
                    rows[i][0] = Swarm if (i % 2 == 0) else Flanker
        elif composition_bias == "harder":
            if not _has_brute():
                rows[-1][0] = Brute

    elif room_type == RoomType.AMBUSH:
        if composition_bias == "lighter":
            for i, r in enumerate(rows):
                if r[0] is Brute:
                    r[0] = Swarm
                elif r[0] is Flanker and i == len(rows) - 1 and len(rows) > 1:
                    r[0] = Swarm
        elif composition_bias == "harder":
            if not _has_brute():
                rows[-1][0] = Brute

    elif room_type == RoomType.ELITE:
        if composition_bias == "lighter" and len(rows) > 1:
            removed = False
            for i in range(len(rows) - 1, -1, -1):
                if not rows[i][1]:
                    del rows[i]
                    removed = True
                    break
            if not removed and len(rows) > 1:
                del rows[-1]
            if rows and not any(r[1] for r in rows):
                rows[0][1] = True
        elif composition_bias == "harder" and len(rows) < BIOME1_COMBAT_MAX:
            last_t = max((float(r[2]) for r in rows), default=0.0)
            rows.append([Swarm, False, last_t + SPAWN_SLOT_DELAY_SEC, None])


def _apply_enemy_count(
    rows: list[list[Any]],
    room_type: RoomType,
    enemy_adjustment: int,
    composition_bias: str,
    room_idx: int,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
) -> None:
    if enemy_adjustment == -1 and len(rows) > 1:
        rows.pop()
    elif enemy_adjustment == 1 and len(rows) < BIOME1_COMBAT_MAX:
        pick = _extra_enemy_class(room_type, composition_bias, room_idx, Swarm, Flanker, Brute)
        last_t = max((float(r[2]) for r in rows), default=0.0)
        tele = 1.5 if room_type == RoomType.AMBUSH else None
        rows.append([pick, False, last_t + SPAWN_SLOT_DELAY_SEC, tele])


def _bias_key(composition_bias: str) -> int:
    return {"lighter": 0, "normal": 1, "harder": 2}.get(composition_bias, 1)


def _extra_enemy_class(
    room_type: RoomType,
    composition_bias: str,
    room_idx: int,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
) -> Type[Any]:
    h = (room_idx * 31 + _bias_key(composition_bias) * 7) & 0xFFFFFFFF
    if room_type == RoomType.COMBAT:
        if composition_bias == "harder":
            return Brute if (h % 3) != 0 else Swarm
        return Swarm if (h % 2) == 0 else Flanker
    if room_type == RoomType.AMBUSH:
        if composition_bias == "harder":
            return Brute
        return Swarm
    # ELITE
    return Swarm


def _apply_delay_scale(rows: list[list[Any]], difficulty_modifier: float) -> None:
    for r in rows:
        r[2] = _scale_start_time(float(r[2]), difficulty_modifier)


def _apply_reinforcement(
    rows: list[list[Any]],
    room_type: RoomType,
    reinforcement_chance: float,
    room_idx: int,
    biome_index: int,
    Swarm: Type[Any],
) -> None:
    if room_type != RoomType.COMBAT:
        return
    if reinforcement_chance <= 0.0:
        return
    if len(rows) >= BIOME1_COMBAT_MAX:
        return
    rng = random.Random(SEED + room_idx * 999 + biome_index)
    if rng.random() >= reinforcement_chance:
        return
    last_t = max((float(r[2]) for r in rows), default=0.0)
    rows.append([Swarm, False, last_t + 0.5, None])


def adjust_biome1_spawn_specs(
    spawn_specs: list[tuple[Any, bool, float, Any]],
    *,
    room_type: RoomType,
    room_idx: int,
    biome_index: int,
    difficulty_modifier: float,
    enemy_adjustment: int,
    reinforcement_chance: float,
    composition_bias: str,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
) -> list[tuple[Any, bool, float, Any]]:
    if not spawn_specs:
        return spawn_specs
    rows = _spec_clone(spawn_specs)
    _apply_composition_bias(rows, room_type, composition_bias, Swarm, Flanker, Brute)
    if not rows:
        return spawn_specs
    _apply_enemy_count(rows, room_type, enemy_adjustment, composition_bias, room_idx, Swarm, Flanker, Brute)
    while len(rows) > BIOME1_COMBAT_MAX:
        rows.pop()
    _apply_delay_scale(rows, difficulty_modifier)
    _apply_reinforcement(rows, room_type, reinforcement_chance, room_idx, biome_index, Swarm)
    while len(rows) > BIOME1_COMBAT_MAX:
        rows.pop()
    return _spec_freeze(rows)


def biome1_effective_heal_drop_chance(
    base_chance: float,
    player_state_name: str | None,
) -> float:
    if player_state_name == "STRUGGLING":
        return min(base_chance + 0.10, 0.50)
    if player_state_name == "DOMINATING":
        return max(base_chance - 0.10, 0.10)
    return base_chance
