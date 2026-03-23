"""
Biome 2 only: deterministic spawn / pacing from AIDirector + player state.
Does not affect Biome 1, 3, or 4.
"""

from __future__ import annotations

import random
from typing import Any, Type

from dungeon.room import RoomType
from game.config import AMBUSH_SPAWN_RADIUS_PX, SEED, SPAWN_SLOT_DELAY_SEC, TRIANGLE_OFFSET_PX

BIOME2_CAMPAIGN_START = 8
BIOME3_CAMPAIGN_START = 16
BIOME2_MAX_ENEMIES = 6
BIOME2_ELIGIBLE = (RoomType.COMBAT, RoomType.AMBUSH, RoomType.ELITE)


def biome2_director_spawn_eligible(
    *,
    room_idx: int,
    biome_index: int,
    room_type: RoomType,
    beginner_test_mode: bool,
) -> bool:
    if beginner_test_mode:
        return False
    if biome_index != 2:
        return False
    if room_idx < BIOME2_CAMPAIGN_START or room_idx >= BIOME3_CAMPAIGN_START:
        return False
    return room_type in BIOME2_ELIGIBLE


def biome2_spawn_pattern_params(pressure_level: str) -> dict[str, float]:
    """Wider spread (low pressure) vs tighter (high); no spawn_system rewrite."""
    if pressure_level == "low":
        return {
            "ambush_radius_px": AMBUSH_SPAWN_RADIUS_PX * 1.15,
            "triangle_offset_px": TRIANGLE_OFFSET_PX * 1.12,
        }
    if pressure_level == "high":
        return {
            "ambush_radius_px": AMBUSH_SPAWN_RADIUS_PX * 0.85,
            "triangle_offset_px": TRIANGLE_OFFSET_PX * 0.88,
        }
    return {}


def biome2_effective_heal_drop_chance(base_chance: float, player_state_name: str | None) -> float:
    if player_state_name == "STRUGGLING":
        return min(base_chance + 0.12, 0.55)
    if player_state_name == "DOMINATING":
        return max(base_chance - 0.12, 0.08)
    return base_chance


def biome2_safe_room_heal_multiplier(player_state_name: str | None) -> float:
    if player_state_name == "STRUGGLING":
        return 1.12
    if player_state_name == "DOMINATING":
        return 0.94
    return 1.0


def _spec_clone(specs: list[tuple[Any, bool, float, Any]]) -> list[list[Any]]:
    return [[s[0], s[1], s[2], s[3]] for s in specs]


def _spec_freeze(rows: list[list[Any]]) -> list[tuple[Any, bool, float, Any]]:
    return [(r[0], bool(r[1]), float(r[2]), r[3]) for r in rows]


def _scale_difficulty_time(t: float, difficulty_modifier: float) -> float:
    if t <= 0.0:
        return t
    if difficulty_modifier <= 0:
        return max(0.2, t)
    scaled = t / difficulty_modifier
    return max(0.2, min(scaled, t * 1.5))


def _apply_pressure_spacing(rows: list[list[Any]], pressure_level: str) -> None:
    mult = {"low": 1.2, "medium": 1.0, "high": 0.8}.get(pressure_level, 1.0)
    if mult == 1.0:
        return
    for r in rows:
        if float(r[2]) > 0.0:
            r[2] = max(0.2, float(r[2]) * mult)


def _heavy_count(rows: list[list[Any]], Heavy: Type[Any]) -> int:
    return sum(1 for r in rows if r[0] is Heavy)


def _apply_composition_b2(
    rows: list[list[Any]],
    room_type: RoomType,
    bias: str,
    room_idx: int,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
    Heavy: Type[Any],
) -> None:
    if bias == "balanced":
        return

    early = room_idx < 10

    if room_type != RoomType.ELITE:
        if bias == "lighter":
            for i, r in enumerate(rows):
                if r[0] is Heavy:
                    r[0] = Swarm if (i % 2 == 0) else Flanker

        elif bias == "aggressive":
            has_brute = any(r[0] is Brute for r in rows)
            has_heavy = any(r[0] is Heavy for r in rows)
            if not has_brute and not has_heavy:
                rows[-1][0] = Brute if early else Heavy

        if early and _heavy_count(rows, Heavy) > 1:
            seen = 0
            for r in rows:
                if r[0] is Heavy:
                    seen += 1
                    if seen > 1:
                        r[0] = Brute

    if room_type == RoomType.ELITE:
        if bias == "lighter" and len(rows) > 1:
            for i in range(len(rows) - 1, -1, -1):
                if not rows[i][1]:
                    del rows[i]
                    break
            if rows and not any(r[1] for r in rows):
                rows[0][1] = True
        elif bias == "aggressive" and len(rows) < BIOME2_MAX_ENEMIES:
            last_t = max((float(r[2]) for r in rows), default=0.0)
            rows.append([Swarm, False, last_t + SPAWN_SLOT_DELAY_SEC, None])


def _extra_enemy_b2(
    room_type: RoomType,
    bias: str,
    room_idx: int,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
    Heavy: Type[Any],
) -> Type[Any]:
    h = (room_idx * 37 + {"lighter": 1, "balanced": 2, "aggressive": 3}.get(bias, 2) * 11) & 0xFF
    if bias == "lighter":
        return Swarm if h % 2 == 0 else Flanker
    if bias == "aggressive":
        return Heavy if h % 3 != 0 else Brute
    return [Swarm, Flanker, Brute][h % 3]


def _apply_enemy_count_b2(
    rows: list[list[Any]],
    room_type: RoomType,
    enemy_adjustment: int,
    bias: str,
    room_idx: int,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
    Heavy: Type[Any],
) -> None:
    if enemy_adjustment == -1 and len(rows) > 1:
        rows.pop()
    elif enemy_adjustment == 1 and len(rows) < BIOME2_MAX_ENEMIES:
        pick = _extra_enemy_b2(room_type, bias, room_idx, Swarm, Flanker, Brute, Heavy)
        if room_idx < 10 and pick is Heavy and _heavy_count(rows, Heavy) >= 1:
            pick = Brute
        last_t = max((float(r[2]) for r in rows), default=0.0)
        tele = 1.5 if room_type == RoomType.AMBUSH else None
        rows.append([pick, False, last_t + SPAWN_SLOT_DELAY_SEC, tele])


def _pick_reinf(
    pressure_level: str,
    room_idx: int,
    slot_i: int,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
) -> Type[Any]:
    h = (room_idx * 13 + slot_i * 3) & 1
    if pressure_level == "low":
        return Swarm
    if pressure_level == "high":
        return Flanker if h == 0 else Brute
    return Swarm if h == 0 else Flanker


def _apply_reinforcement_b2(
    rows: list[list[Any]],
    room_type: RoomType,
    reinforcement_chance: float,
    room_idx: int,
    biome_index: int,
    player_state_name: str | None,
    pressure_level: str,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
) -> None:
    if room_type != RoomType.COMBAT:
        return
    if reinforcement_chance <= 0.0:
        return
    if len(rows) >= BIOME2_MAX_ENEMIES:
        return
    rng = random.Random(SEED + room_idx * 999 + biome_index)
    if rng.random() >= reinforcement_chance:
        return
    max_n = 2 if player_state_name == "DOMINATING" else 1
    n = max_n
    if max_n == 2:
        n = 1 + ((SEED + room_idx * 999 + biome_index + 1) & 1)
    for i in range(n):
        if len(rows) >= BIOME2_MAX_ENEMIES:
            break
        cls = _pick_reinf(pressure_level, room_idx, i, Swarm, Flanker, Brute)
        last_t = max((float(r[2]) for r in rows), default=0.0)
        rows.append([cls, False, last_t + 0.5 + 0.5 * float(i), None])


def adjust_biome2_spawn_specs(
    spawn_specs: list[tuple[Any, bool, float, Any]],
    *,
    room_type: RoomType,
    room_idx: int,
    biome_index: int,
    difficulty_modifier: float,
    enemy_adjustment: int,
    reinforcement_chance_b2: float,
    pressure_level: str,
    composition_bias_b2: str,
    player_state_name: str | None,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
    Heavy: Type[Any],
) -> tuple[list[tuple[Any, bool, float, Any]], dict[str, float]]:
    if not spawn_specs:
        return spawn_specs, {}
    rows = _spec_clone(spawn_specs)
    _apply_composition_b2(rows, room_type, composition_bias_b2, room_idx, Swarm, Flanker, Brute, Heavy)
    if not rows:
        return spawn_specs, biome2_spawn_pattern_params(pressure_level)
    _apply_enemy_count_b2(
        rows, room_type, enemy_adjustment, composition_bias_b2, room_idx, Swarm, Flanker, Brute, Heavy
    )
    while len(rows) > BIOME2_MAX_ENEMIES:
        rows.pop()
    for r in rows:
        r[2] = _scale_difficulty_time(float(r[2]), difficulty_modifier)
    _apply_pressure_spacing(rows, pressure_level)
    _apply_reinforcement_b2(
        rows,
        room_type,
        reinforcement_chance_b2,
        room_idx,
        biome_index,
        player_state_name,
        pressure_level,
        Swarm,
        Flanker,
        Brute,
    )
    while len(rows) > BIOME2_MAX_ENEMIES:
        rows.pop()
    return _spec_freeze(rows), biome2_spawn_pattern_params(pressure_level)
