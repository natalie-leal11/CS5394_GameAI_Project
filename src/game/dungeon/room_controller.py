"""
Room controller: room entry, completion, and sequential progression. Deterministic.
No layout or enemy spawning; state-driven only.
"""
from typing import List

from src.game.dungeon.room_types import (
    START,
    CORRIDOR,
    SAFE_REST,
    COMBAT,
    AMBUSH,
    ELITE,
    MINI_BOSS,
    FINAL_BOSS,
    TOTAL_ROOMS,
    FINAL_BOSS_INDEX,
)


class RoomController:
    """Tracks current room index and cleared state. Progression is sequential 0..29."""

    def __init__(self, plan: List[str]) -> None:
        assert len(plan) == TOTAL_ROOMS
        self.plan = plan
        self.current_index = 0
        # Start and Corridor are clear on entry; others cleared when combat/rest done
        self._cleared = self._auto_clear_on_entry(self.plan[0])

    def _auto_clear_on_entry(self, room_type: str) -> bool:
        """Start and Corridor clear immediately; others require combat/rest."""
        return room_type in (START, CORRIDOR)

    def get_current_room_type(self) -> str:
        return self.plan[self.current_index]

    def is_current_room_cleared(self) -> bool:
        return self._cleared

    def mark_current_room_cleared(self) -> None:
        self._cleared = True

    def is_clearable_without_combat(self) -> bool:
        """True if room type is Start, Corridor, or Safe (Safe needs rest/upgrade in Prompt 11)."""
        return self.get_current_room_type() in (START, CORRIDOR, SAFE_REST)

    def requires_combat_clear(self) -> bool:
        """True if room clears only when all enemies / boss defeated."""
        return self.get_current_room_type() in (COMBAT, AMBUSH, ELITE, MINI_BOSS, FINAL_BOSS)

    def can_advance(self) -> bool:
        """True when current room is cleared and we are not past the last room."""
        return self._cleared and self.current_index < TOTAL_ROOMS - 1

    def advance(self) -> bool:
        """
        Move to next room. Returns True if advanced. Cannot exceed index 29.
        Start and Corridor are auto-cleared on entry.
        """
        if self.current_index >= TOTAL_ROOMS - 1:
            return False
        if not self._cleared:
            return False
        self.current_index += 1
        self._cleared = self._auto_clear_on_entry(self.get_current_room_type())
        return True

    def at_final_boss(self) -> bool:
        return self.current_index == FINAL_BOSS_INDEX

    def at_start(self) -> bool:
        return self.current_index == 0

    def get_room_index(self) -> int:
        return self.current_index
