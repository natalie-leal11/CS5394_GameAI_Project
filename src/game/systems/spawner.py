"""
Encounter spawner: spawn enemies per room from directives. Lock until cleared.
Uses only defined archetypes; does not modify base stats. Elite +40% HP, +20% damage.
"""
from typing import List, Tuple, Dict, Any

from src.game import rng
from src.game.entities.enemy_base import Enemy
from src.game.entities.enemies import (
    create_swarm,
    create_flanker,
    create_brute,
    create_heavy,
    create_ranged_suppressor,
)

MAX_ACTIVE_ENEMIES_PER_ROOM = 10
MAX_REINFORCEMENT_WAVES_PER_ROOM = 2

ARCHETYPE_CREATORS = {
    "swarm": create_swarm,
    "flanker": create_flanker,
    "brute": create_brute,
    "heavy": create_heavy,
    "ranged_suppressor": create_ranged_suppressor,
}


def spawn_encounter(
    seed: int,
    room_index: int,
    room_type: str,
    bounds: Tuple[float, float, float, float],
    enemy_count: int,
    archetype_mix: List[str],
    elite_count: int = 0,
    ambush_delay_sec: float = 0.0,
) -> List[Enemy]:
    """
    Spawn enemies for the room. Count and mix from directives (AI Director later).
    Clamps to MAX_ACTIVE_ENEMIES_PER_ROOM. Returns list of enemies.
    ambush_delay_sec: if > 0, spawn can be delayed (caller may spawn later).
    """
    rng.set_seed(seed + room_index * 10000)
    count = min(enemy_count, MAX_ACTIVE_ENEMIES_PER_ROOM)
    if count <= 0 or not archetype_mix:
        return []

    left, top, width, height = bounds
    margin = 40.0
    enemies: List[Enemy] = []
    elite_used = 0

    for i in range(count):
        # Random position within bounds (inset)
        w_avail = max(0, width - 2 * margin)
        h_avail = max(0, height - 2 * margin)
        if w_avail > 1:
            x = left + margin + rng.randint(0, int(w_avail))
        else:
            x = left + width / 2.0 - 20
        if h_avail > 1:
            y = top + margin + rng.randint(0, int(h_avail))
        else:
            y = top + height / 2.0 - 20
        x = float(x)
        y = float(y)

        archetype = rng.choice(archetype_mix)
        creator = ARCHETYPE_CREATORS.get(archetype, create_swarm)
        is_elite = elite_used < elite_count and rng.choice([True, False]) if elite_count > 0 else False
        if is_elite:
            elite_used += 1
        e = creator(x, y, elite=is_elite)
        enemies.append(e)

    return enemies


def clear_encounter(enemies: List[Enemy]) -> None:
    """Remove all enemies (room clear). Caller may replace list reference."""
    enemies.clear()
