"""
Upgrade definitions and application. Parameter-driven; deterministic.
Safe room: heal 25% max HP, present 3 options, player selects 1.
"""
from typing import List, Tuple, Any

from src.game import rng
from src.game.entities.player import Player, BASE_HP, MOVE_SPEED_PX_SEC

# Upgrade IDs and parameter ranges (from spec)
UPGRADE_MAX_HP = "max_hp"           # +15-25% max HP
UPGRADE_MOVE_SPEED = "move_speed"   # +10% move speed
UPGRADE_ATTACK_DAMAGE = "attack_damage"  # +10-15% attack damage
UPGRADE_COOLDOWN_REDUCTION = "cooldown_reduction"
UPGRADE_DAMAGE_REDUCTION = "damage_reduction"

HEAL_PERCENT_MAX_HP = 0.25  # 25%


def heal_in_safe_room(player: Player) -> None:
    """Restore 25% of max HP. Cap at max_hp."""
    amount = int(player.max_hp * HEAL_PERCENT_MAX_HP)
    player.hp = min(player.max_hp, player.hp + amount)


def generate_three_upgrades(
    seed: int,
    room_index: int,
    director_state: str,
) -> List[Tuple[str, str, Any]]:
    """
    Deterministic: return 3 (id, label, value) options. Biased by director_state.
    struggling -> favor HP/defense; dominating -> offense/speed; stable -> balanced.
    """
    rng.set_seed(seed + room_index * 1000)
    pool = [
        (UPGRADE_MAX_HP, "Max HP +15-25%", rng.randint(15, 25)),
        (UPGRADE_MOVE_SPEED, "Move Speed +10%", 10),
        (UPGRADE_ATTACK_DAMAGE, "Attack Damage +10-15%", rng.randint(10, 15)),
        (UPGRADE_COOLDOWN_REDUCTION, "Cooldown Reduction 8%", 8),
        (UPGRADE_DAMAGE_REDUCTION, "Damage Reduction 5%", 5),
    ]
    if director_state == "struggling":
        order = [0, 4, 3, 1, 2]  # favor HP, damage reduction, cooldown
    elif director_state == "dominating":
        order = [1, 2, 0, 3, 4]  # favor speed, damage
    else:
        order = [0, 1, 2, 3, 4]
    ordered_pool = [pool[i] for i in order]
    rng.shuffle(ordered_pool)
    return ordered_pool[:3]


def apply_upgrade(player: Player, upgrade_id: str, value: Any) -> None:
    """Apply one chosen upgrade. Bounded, parameter-driven."""
    if upgrade_id == UPGRADE_MAX_HP:
        player.max_hp_bonus_percent += value / 100.0
    elif upgrade_id == UPGRADE_MOVE_SPEED:
        player.move_speed_bonus_percent += value / 100.0
    elif upgrade_id == UPGRADE_ATTACK_DAMAGE:
        player.attack_damage_bonus_percent += value / 100.0
    elif upgrade_id == UPGRADE_COOLDOWN_REDUCTION:
        player.cooldown_reduction_percent += value / 100.0
    elif upgrade_id == UPGRADE_DAMAGE_REDUCTION:
        player.damage_reduction_bonus += value / 100.0
