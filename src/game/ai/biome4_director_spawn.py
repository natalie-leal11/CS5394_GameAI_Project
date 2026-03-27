"""
Biome 4 only: deterministic spawn / pacing from AIDirector + player state.
Final boss uses separate parameter hooks in entities.final_boss (spawned from GameScene).
"""

from __future__ import annotations

import random
from typing import Any, Type

from dungeon.biome4_rooms import BIOME4_AMBUSH_RADIUS_PX, BIOME4_TRIANGLE_OFFSET_PX
from dungeon.room import RoomType
from game.config import BIOME4_START_INDEX, SEED, SPAWN_SLOT_DELAY_SEC

BIOME4_ELIGIBLE = (RoomType.COMBAT, RoomType.AMBUSH, RoomType.ELITE)
BIOME4_MAX_ENEMIES = 6


def biome4_director_spawn_eligible(
    *,
    room_idx: int,
    biome_index: int,
    room_type: RoomType,
    beginner_test_mode: bool,
) -> bool:
    if beginner_test_mode:
        return False
    if biome_index != 4:
        return False
    if room_idx < BIOME4_START_INDEX:
        return False
    # Room 29 = FINAL_BOSS (no normal encounter director)
    if room_idx >= BIOME4_START_INDEX + 5:
        return False
    return room_type in BIOME4_ELIGIBLE


def biome4_pacing_spacing_mult(pacing_bias: str) -> float:
    if pacing_bias == "relaxed":
        return 1.1
    if pacing_bias == "intense":
        return 0.93
    return 1.0


def biome4_spawn_pattern_params(pressure_level: str, pacing_bias: str) -> dict[str, float]:
    out: dict[str, float] = {}
    base_amb = BIOME4_AMBUSH_RADIUS_PX
    base_tri = BIOME4_TRIANGLE_OFFSET_PX
    if pressure_level == "low":
        out["ambush_radius_px"] = base_amb * 1.12
        out["triangle_offset_px"] = base_tri * 1.1
    elif pressure_level == "high":
        out["ambush_radius_px"] = base_amb * 0.88
        out["triangle_offset_px"] = base_tri * 0.9
    pm = biome4_pacing_spacing_mult(pacing_bias)
    if pm != 1.0:
        out["pacing_spacing_mult"] = pm
    return out


def biome4_effective_heal_drop_chance(base_chance: float, player_state_name: str | None) -> float:
    if player_state_name == "STRUGGLING":
        return min(base_chance + 0.14, 0.55)
    if player_state_name == "DOMINATING":
        return max(base_chance - 0.14, 0.08)
    return base_chance


def biome4_safe_room_heal_multiplier(player_state_name: str | None) -> float:
    """Biome 4 safe room (Room 28): defensive tilt + heal tuning."""
    if player_state_name == "STRUGGLING":
        return 1.12
    if player_state_name == "DOMINATING":
        return 0.93
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
    return max(0.2, min(scaled, t * 1.55))


def _apply_pressure_spacing(rows: list[list[Any]], pressure_level: str, pacing_bias: str) -> None:
    mult = {"low": 1.22, "medium": 1.0, "high": 0.78}.get(pressure_level, 1.0)
    mult *= biome4_pacing_spacing_mult(pacing_bias)
    if mult == 1.0:
        return
    for r in rows:
        if float(r[2]) > 0.0:
            r[2] = max(0.18, float(r[2]) * mult)


def _heavy_count(rows: list[list[Any]], Heavy: Type[Any]) -> int:
    return sum(1 for r in rows if r[0] is Heavy)


def _ranged_count(rows: list[list[Any]], Ranged: Type[Any]) -> int:
    return sum(1 for r in rows if r[0] is Ranged)


def _apply_composition_b4(
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
        for i, r in enumerate(rows):
            if r[0] is Heavy:
                r[0] = Brute
            elif r[0] is Ranged and i > 0:
                r[0] = Flanker
        if _ranged_count(rows, Ranged) > 1:
            seen = 0
            for r in rows:
                if r[0] is Ranged:
                    seen += 1
                    if seen > 1:
                        r[0] = Swarm

    elif bias == "aggressive":
        has_h = any(r[0] is Heavy for r in rows)
        has_r = any(r[0] is Ranged for r in rows)
        if not has_h and rows:
            rows[-1][0] = Heavy if room_idx % 2 == 0 else Brute
        if not has_r and len(rows) >= 2:
            rows[0][0] = Ranged

    if room_type == RoomType.ELITE:
        if bias == "safe" and len(rows) > 1:
            for i in range(len(rows) - 1, -1, -1):
                if not rows[i][1]:
                    del rows[i]
                    break
            if rows and not any(r[1] for r in rows):
                rows[0][1] = True
        elif bias == "aggressive" and len(rows) < BIOME4_MAX_ENEMIES:
            last_t = max((float(r[2]) for r in rows), default=0.0)
            rows.append([Swarm, False, last_t + SPAWN_SLOT_DELAY_SEC, None])


def _extra_enemy_b4(
    bias: str,
    room_idx: int,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
    Heavy: Type[Any],
    Ranged: Type[Any],
) -> Type[Any]:
    h = (room_idx * 41 + {"safe": 1, "balanced": 2, "aggressive": 3}.get(bias, 2) * 17) & 0xFF
    if bias == "safe":
        return Swarm if h % 2 == 0 else Flanker
    if bias == "aggressive":
        return Ranged if h % 3 != 0 else Heavy
    return [Swarm, Flanker, Brute][h % 3]


def _apply_enemy_count_b4(
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
    elif enemy_adjustment == 1 and len(rows) < BIOME4_MAX_ENEMIES:
        pick = _extra_enemy_b4(bias, room_idx, Swarm, Flanker, Brute, Heavy, Ranged)
        if bias == "safe" and pick in (Heavy, Ranged) and (_heavy_count(rows, Heavy) >= 1 or _ranged_count(rows, Ranged) >= 1):
            pick = Brute
        last_t = max((float(r[2]) for r in rows), default=0.0)
        tele = 1.5 if room_type == RoomType.AMBUSH else None
        rows.append([pick, False, last_t + SPAWN_SLOT_DELAY_SEC, tele])


def _pick_reinf_b4(
    player_state_name: str | None,
    slot_i: int,
    room_idx: int,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
    Ranged: Type[Any],
) -> Type[Any]:
    h = (room_idx * 17 + slot_i * 7) & 0xFF
    if player_state_name == "STRUGGLING":
        return Swarm
    if player_state_name == "DOMINATING":
        opts = [Flanker, Brute, Ranged]
        return opts[h % len(opts)]
    return Swarm if h % 2 == 0 else Flanker


def _apply_reinforcement_b4(
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
    if len(rows) >= BIOME4_MAX_ENEMIES:
        return
    rng = random.Random(SEED + room_idx * 1001 + biome_index)
    if rng.random() >= reinforcement_chance:
        return
    max_n = 2 if player_state_name == "DOMINATING" else 1
    n = max_n
    if max_n == 2:
        n = 1 + ((SEED + room_idx * 1001 + biome_index + 3) & 1)
    for i in range(n):
        if len(rows) >= BIOME4_MAX_ENEMIES:
            break
        cls = _pick_reinf_b4(player_state_name, i, room_idx, Swarm, Flanker, Brute, Ranged)
        last_t = max((float(r[2]) for r in rows), default=0.0)
        delay = 0.45 + 0.55 * float(i)
        if pressure_level == "low":
            delay *= 1.12
        elif pressure_level == "high":
            delay *= 0.88
        rows.append([cls, False, last_t + delay, None])


def adjust_biome4_spawn_specs(
    spawn_specs: list[tuple[Any, bool, float, Any]],
    *,
    room_type: RoomType,
    room_idx: int,
    biome_index: int,
    difficulty_modifier: float,
    enemy_adjustment: int,
    reinforcement_chance_b4: float,
    pressure_level: str,
    composition_bias_b4: str,
    pacing_bias: str,
    player_state_name: str | None,
    hazard_tune_factor: float,
    Swarm: Type[Any],
    Flanker: Type[Any],
    Brute: Type[Any],
    Heavy: Type[Any],
    Ranged: Type[Any],
) -> tuple[list[tuple[Any, bool, float, Any]], dict[str, float]]:
    if not spawn_specs:
        m0 = biome4_spawn_pattern_params(pressure_level, pacing_bias)
        m0["hazard_tune_effective"] = float(hazard_tune_factor)
        return spawn_specs, m0
    rows = _spec_clone(spawn_specs)
    _apply_composition_b4(rows, room_type, composition_bias_b4, room_idx, Swarm, Flanker, Brute, Heavy, Ranged)
    if not rows:
        m0 = biome4_spawn_pattern_params(pressure_level, pacing_bias)
        m0["hazard_tune_effective"] = float(hazard_tune_factor)
        return spawn_specs, m0
    _apply_enemy_count_b4(
        rows, room_type, enemy_adjustment, composition_bias_b4, room_idx, Swarm, Flanker, Brute, Heavy, Ranged
    )
    while len(rows) > BIOME4_MAX_ENEMIES:
        rows.pop()
    for r in rows:
        r[2] = _scale_difficulty_time(float(r[2]), difficulty_modifier)
    _apply_pressure_spacing(rows, pressure_level, pacing_bias)
    _apply_reinforcement_b4(
        rows,
        room_type,
        reinforcement_chance_b4,
        room_idx,
        biome_index,
        player_state_name,
        pressure_level,
        Swarm,
        Flanker,
        Brute,
        Ranged,
    )
    while len(rows) > BIOME4_MAX_ENEMIES:
        rows.pop()
    mods = biome4_spawn_pattern_params(pressure_level, pacing_bias)
    mods["hazard_tune_effective"] = float(hazard_tune_factor)
    return _spec_freeze(rows), mods
