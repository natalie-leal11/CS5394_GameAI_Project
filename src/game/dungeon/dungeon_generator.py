"""
Deterministic 30-room dungeon plan generator. Same seed -> identical plan.
Uses only src.game.rng for randomness. No layout or hazard logic.
"""
from typing import List

from src.game import rng
from src.game.dungeon.room_types import (
    START,
    CORRIDOR,
    COMBAT,
    AMBUSH,
    SAFE_REST,
    ELITE,
    MINI_BOSS,
    FINAL_BOSS,
    TOTAL_ROOMS,
    START_INDEX,
    MINI_BOSS_INDICES,
    FINAL_BOSS_INDEX,
)
from src.game.dungeon.room_plan import create_empty_plan, set_milestones


def _shuffle_in_place(seq: List[str]) -> None:
    """Fisher-Yates shuffle using rng.randint only."""
    for i in range(len(seq) - 1, 0, -1):
        j = rng.randint(0, i)
        seq[i], seq[j] = seq[j], seq[i]


def _pick_counts(
    combat_range: tuple[int, int],
    ambush_range: tuple[int, int],
    corridor_range: tuple[int, int],
    safe: int,
    elite: int,
    slot_count: int,
) -> tuple[int, int, int]:
    """Pick combat, ambush, corridor counts that sum with safe+elite to slot_count."""
    need = slot_count - safe - elite
    c_lo, c_hi = combat_range
    a_lo, a_hi = ambush_range
    r_lo, r_hi = corridor_range
    # Enumerate valid (c, a, r) with c+a+r=need, c in [c_lo,c_hi], etc.
    options = []
    for c in range(c_lo, c_hi + 1):
        for a in range(a_lo, a_hi + 1):
            r = need - c - a
            if r_lo <= r <= r_hi and r >= 0:
                options.append((c, a, r))
    if not options:
        options = [(c_lo, a_lo, need - c_lo - a_lo)]
    return rng.choice(options)


def _fill_biome_1(plan: List[str]) -> None:
    # Slots 1-6 (6 slots). Combat 3-4, Ambush 0-1, Safe 1, Corridor 0-1, Elite 1
    c, a, r = _pick_counts((3, 4), (0, 1), (0, 1), 1, 1, 6)
    types = [COMBAT] * c + [AMBUSH] * a + [CORRIDOR] * r + [SAFE_REST, ELITE]
    _shuffle_in_place(types)
    for i, t in enumerate(types):
        plan[1 + i] = t


def _fill_biome_2(plan: List[str]) -> None:
    # Slots 8-14 (7 slots). Combat 3-4, Ambush 1-2, Safe 1, Corridor 0-1, Elite 1
    c, a, r = _pick_counts((3, 4), (1, 2), (0, 1), 1, 1, 7)
    types = [COMBAT] * c + [AMBUSH] * a + [CORRIDOR] * r + [SAFE_REST, ELITE]
    _shuffle_in_place(types)
    for i, t in enumerate(types):
        plan[8 + i] = t


def _fill_biome_3(plan: List[str]) -> None:
    # Slots 16-22 (7 slots). Combat 2-4, Ambush 2-3, Safe 1, Corridor 0-1, Elite 1
    c, a, r = _pick_counts((2, 4), (2, 3), (0, 1), 1, 1, 7)
    types = [COMBAT] * c + [AMBUSH] * a + [CORRIDOR] * r + [SAFE_REST, ELITE]
    _shuffle_in_place(types)
    for i, t in enumerate(types):
        plan[16 + i] = t


def _fill_biome_4(plan: List[str]) -> None:
    # Slots 24-28 (5 slots). Combat 2-3, Ambush 1, Safe 1, Corridor 0-1, Elite 1
    c, a, r = _pick_counts((2, 3), (1, 1), (0, 1), 1, 1, 5)
    types = [COMBAT] * c + [AMBUSH] * a + [CORRIDOR] * r + [SAFE_REST, ELITE]
    _shuffle_in_place(types)
    for i, t in enumerate(types):
        plan[24 + i] = t


def generate_dungeon_plan(seed: int) -> List[str]:
    """
    Generate a deterministic 30-room dungeon plan. Same seed -> identical plan.
    Room 0 = Start, 7/15/23 = Mini Boss, 29 = Final Boss. Rest filled within biome bounds.
    """
    rng.set_seed(seed)
    plan = create_empty_plan()
    set_milestones(plan)
    _fill_biome_1(plan)
    _fill_biome_2(plan)
    _fill_biome_3(plan)
    _fill_biome_4(plan)
    return plan
