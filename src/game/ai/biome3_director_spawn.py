"""
Biome 3 only: deterministic spawn / pacing from AIDirector + player state.
Does not affect other biomes.
"""

from __future__ import annotations

import math
import random
from typing import Any, Type

from dungeon.room import RoomType
from game.config import (
    AMBUSH_SPAWN_RADIUS_PX,
    BIOME3_START_INDEX,
    BIOME4_START_INDEX,
    SEED,
    SPAWN_SLOT_DELAY_SEC,
    TRIANGLE_OFFSET_PX,
)

BIOME3_ELIGIBLE = (RoomType.COMBAT, RoomType.AMBUSH, RoomType.ELITE)
BIOME3_MAX_ENEMIES = 6


def biome3_director_spawn_eligible(
    *,
    room_idx: int,
    biome_index: int,
    room_type: RoomType,
    beginner_test_mode: bool,
) -> bool:
    if beginner_test_mode:
        return False
    if biome_index != 3:
        return False
    if room_idx < BIOME3_START_INDEX or room_idx >= BIOME4_START_INDEX:
        return False
    return room_type in BIOME3_ELIGIBLE


def biome3_spawn_pattern_params(pressure_level: str, ranged_bias: str) -> dict[str, float]:
    """Wider spread (low pressure / struggling with ranged) vs tighter (high)."""
    out: dict[str, float] = {}
    if pressure_level == "low":
        out["ambush_radius_px"] = AMBUSH_SPAWN_RADIUS_PX * 1.15
        out["triangle_offset_px"] = TRIANGLE_OFFSET_PX * 1.12
    elif pressure_level == "high":
        out["ambush_radius_px"] = AMBUSH_SPAWN_RADIUS_PX * 0.85
        out["triangle_offset_px"] = TRIANGLE_OFFSET_PX * 0.88
    # Ranged pressure: more spacing from player when low, tighter when high
    rm = {"low": 1.12, "medium": 1.0, "high": 0.9}.get(ranged_bias, 1.0)
    out["ranged_spawn_dist_mult"] = rm
    return out


def biome3_effective_heal_drop_chance(base_chance: float, player_state_name: str | None) -> float:
    if player_state_name == "STRUGGLING":
        return min(base_chance + 0.12, 0.55)
    if player_state_name == "DOMINATING":
        return max(base_chance - 0.1, 0.08)
    return base_chance


def biome3_safe_room_heal_multiplier(player_state_name: str | None) -> float:
    if player_state_name == "STRUGGLING":
        return 1.1
    if player_state_name == "DOMINATING":
        return 0.96
    return 1.0


def apply_biome3_ranged_position_offsets(
    positions: list[tuple[float, float]],
    spawn_specs: list[tuple[Any, bool, float, Any]],
    player_center: tuple[float, float],
    ranged_bias: str,
) -> None:
    """Push Ranged spawns farther from player when struggling (low), closer when dominating (high)."""
    px, py = float(player_center[0]), float(player_center[1])
    m = {"low": 1.14, "medium": 1.0, "high": 0.92}.get(ranged_bias, 1.0)
    if m == 1.0:
        return
    for i, spec in enumerate(spawn_specs):
        if i >= len(positions):
            break
        cls = spec[0]
        if getattr(cls, "__name__", "") != "Ranged":
            continue
        x, y = positions[i]
        dx, dy = x - px, y - py
        dist = math.hypot(dx, dy)
        if dist < 1e-3:
            continue
        nd = dist * m
        positions[i] = (px + dx / dist * nd, py + dy / dist * nd)


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


def _ranged_count(rows: list[list[Any]], Ranged: Type[Any]) -> int:
    return sum(1 for r in rows if r[0] is Ranged)


def _heavy_count(rows: list[list[Any]], Heavy: Type[Any]) -> int:
    return sum(1 for r in rows if r[0] is Heavy)


def _apply_composition_b3(
    rows: list[list[Any]],
    room_type: RoomType,
    bias: str,
    room_idx: int,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
    Heavy: Type[Any],
    Ranged: Type[Any],
) -> None:
    if bias == "balanced":
        return

    if bias == "safe":
        # Max 1 Ranged; prefer Swarm + Flanker; trim Heavy pressure
        while _ranged_count(rows, Ranged) > 1:
            for i in range(len(rows) - 1, -1, -1):
                if rows[i][0] is Ranged:
                    rows[i][0] = Swarm if (room_idx + i) % 2 == 0 else Flanker
                    break
        while _heavy_count(rows, Heavy) > 1:
            for i, r in enumerate(rows):
                if r[0] is Heavy:
                    r[0] = Brute
                    break

    elif bias == "aggressive":
        # Ensure ranged pressure: at least one Ranged; aim for two when 4+ slots
        if not any(r[0] is Ranged for r in rows):
            if rows:
                rows[-1][0] = Ranged
        if len(rows) >= 4 and _ranged_count(rows, Ranged) < 2:
            for i, r in enumerate(rows):
                if r[0] in (Swarm, Flanker) and i != len(rows) - 1:
                    r[0] = Ranged
                    break

    if room_type == RoomType.ELITE:
        if bias == "safe" and len(rows) > 1:
            for i in range(len(rows) - 1, -1, -1):
                if not rows[i][1]:
                    del rows[i]
                    break
            if rows and not any(r[1] for r in rows):
                rows[0][1] = True
        elif bias == "aggressive" and len(rows) < BIOME3_MAX_ENEMIES:
            last_t = max((float(r[2]) for r in rows), default=0.0)
            rows.append([Swarm, False, last_t + SPAWN_SLOT_DELAY_SEC, None])


def _extra_enemy_b3(
    room_type: RoomType,
    bias: str,
    room_idx: int,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
    Heavy: Type[Any],
    Ranged: Type[Any],
) -> Type[Any]:
    h = (room_idx * 37 + {"safe": 1, "balanced": 2, "aggressive": 3}.get(bias, 2) * 11) & 0xFF
    if bias == "safe":
        return Swarm if h % 2 == 0 else Flanker
    if bias == "aggressive":
        return Ranged if h % 2 == 0 else Heavy
    return [Swarm, Flanker, Ranged][h % 3]


def _apply_enemy_count_b3(
    rows: list[list[Any]],
    room_type: RoomType,
    enemy_adjustment: int,
    bias: str,
    room_idx: int,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
    Heavy: Type[Any],
    Ranged: Type[Any],
) -> None:
    if enemy_adjustment == -1 and len(rows) > 1:
        rows.pop()
    elif enemy_adjustment == 1 and len(rows) < BIOME3_MAX_ENEMIES:
        pick = _extra_enemy_b3(room_type, bias, room_idx, Swarm, Flanker, Brute, Heavy, Ranged)
        if bias == "safe" and pick is Ranged and _ranged_count(rows, Ranged) >= 1:
            pick = Flanker
        last_t = max((float(r[2]) for r in rows), default=0.0)
        tele = 1.5 if room_type == RoomType.AMBUSH else None
        rows.append([pick, False, last_t + SPAWN_SLOT_DELAY_SEC, tele])


def _pick_reinf_b3(
    player_state_name: str | None,
    slot_i: int,
    room_idx: int,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
    Ranged: Type[Any],
) -> Type[Any]:
    h = (room_idx * 13 + slot_i * 5) & 0xFF
    if player_state_name == "STRUGGLING":
        return Swarm
    if player_state_name == "DOMINATING":
        if slot_i == 0:
            return Ranged if h % 3 != 0 else Flanker
        return Brute if h % 2 == 0 else Ranged
    return Swarm if h % 2 == 0 else Flanker


def _apply_reinforcement_b3(
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
    Ranged: Type[Any],
) -> None:
    if room_type != RoomType.COMBAT:
        return
    if reinforcement_chance <= 0.0:
        return
    if len(rows) >= BIOME3_MAX_ENEMIES:
        return
    rng = random.Random(SEED + room_idx * 999 + biome_index)
    if rng.random() >= reinforcement_chance:
        return
    max_n = 1
    if player_state_name == "DOMINATING":
        max_n = 2
    elif player_state_name == "STRUGGLING":
        max_n = 1
    n = max_n
    if max_n == 2:
        n = 1 + ((SEED + room_idx * 999 + biome_index + 1) & 1)
    for i in range(n):
        if len(rows) >= BIOME3_MAX_ENEMIES:
            break
        if player_state_name == "STRUGGLING":
            cls = Swarm
        else:
            cls = _pick_reinf_b3(player_state_name, i, room_idx, Swarm, Flanker, Brute, Ranged)
        last_t = max((float(r[2]) for r in rows), default=0.0)
        delay = 0.5 + 0.5 * float(i)
        if pressure_level == "low":
            delay *= 1.15
        elif pressure_level == "high":
            delay *= 0.9
        rows.append([cls, False, last_t + delay, None])


def adjust_biome3_spawn_specs(
    spawn_specs: list[tuple[Any, bool, float, Any]],
    *,
    room_type: RoomType,
    room_idx: int,
    biome_index: int,
    difficulty_modifier: float,
    enemy_adjustment: int,
    reinforcement_chance_b3: float,
    pressure_level: str,
    composition_bias_b3: str,
    ranged_bias_b3: str,
    player_state_name: str | None,
    hazard_tune_factor: float,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
    Heavy: Type[Any],
    Ranged: Type[Any],
) -> tuple[list[tuple[Any, bool, float, Any]], dict[str, float]]:
    """hazard_tune_factor includes director bias × one-room relief after heavy hazard damage."""
    if not spawn_specs:
        m0 = biome3_spawn_pattern_params(pressure_level, ranged_bias_b3)
        m0["hazard_tune_effective"] = float(hazard_tune_factor)
        return spawn_specs, m0
    rows = _spec_clone(spawn_specs)
    _apply_composition_b3(
        rows, room_type, composition_bias_b3, room_idx, Swarm, Flanker, Brute, Heavy, Ranged
    )
    if not rows:
        return spawn_specs, biome3_spawn_pattern_params(pressure_level, ranged_bias_b3)
    _apply_enemy_count_b3(
        rows,
        room_type,
        enemy_adjustment,
        composition_bias_b3,
        room_idx,
        Swarm,
        Flanker,
        Brute,
        Heavy,
        Ranged,
    )
    while len(rows) > BIOME3_MAX_ENEMIES:
        rows.pop()
    for r in rows:
        r[2] = _scale_difficulty_time(float(r[2]), difficulty_modifier)
    _apply_pressure_spacing(rows, pressure_level)
    _apply_reinforcement_b3(
        rows,
        room_type,
        reinforcement_chance_b3,
        room_idx,
        biome_index,
        player_state_name,
        pressure_level,
        Swarm,
        Flanker,
        Brute,
        Ranged,
    )
    while len(rows) > BIOME3_MAX_ENEMIES:
        rows.pop()
    mods = biome3_spawn_pattern_params(pressure_level, ranged_bias_b3)
    mods["hazard_tune_effective"] = float(hazard_tune_factor)
    return _spec_freeze(rows), mods
