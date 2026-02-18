"""
Dungeon plan: list of 30 room types. Pure data, no rendering or combat.
"""
from typing import List

from src.game.dungeon.room_types import (
    TOTAL_ROOMS,
    START,
    FINAL_BOSS,
    MINI_BOSS,
    START_INDEX,
    MINI_BOSS_INDICES,
    FINAL_BOSS_INDEX,
)


def create_empty_plan() -> List[str]:
    """Return a list of 30 placeholder room types (to be filled by generator)."""
    return [""] * TOTAL_ROOMS


def set_milestones(plan: List[str]) -> None:
    """Enforce fixed milestone room types. Mutates plan in place."""
    assert len(plan) == TOTAL_ROOMS
    plan[START_INDEX] = START
    for i in MINI_BOSS_INDICES:
        plan[i] = MINI_BOSS
    plan[FINAL_BOSS_INDEX] = FINAL_BOSS


def validate_plan(plan: List[str]) -> bool:
    """Return True if plan has exactly 30 rooms and correct milestones."""
    if len(plan) != TOTAL_ROOMS:
        return False
    if plan[START_INDEX] != START:
        return False
    for i in MINI_BOSS_INDICES:
        if plan[i] != MINI_BOSS:
            return False
    if plan[FINAL_BOSS_INDEX] != FINAL_BOSS:
        return False
    return True
