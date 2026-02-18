"""
Deterministic AI Director. No random calls. Outputs spawn directives from metrics + difficulty_params.
Does not modify player or enemy base stats.
"""
from typing import Any, Dict, List

from src.game.ai.difficulty_params import DifficultyParams

ARCHETYPE_NAMES = ["swarm", "flanker", "brute", "heavy", "ranged_suppressor"]


def _director_state(hp_percent: float, params: DifficultyParams) -> str:
    """Pure function: struggling / stable / dominating from HP% and params."""
    if hp_percent < params.hp_threshold_struggling:
        return "struggling"
    if hp_percent >= params.hp_threshold_dominating:
        return "dominating"
    return "stable"


def get_directives(
    hp_percent: float,
    death_count: int,
    room_type: str,
    biome_index: int,
    params: DifficultyParams,
) -> Dict[str, Any]:
    """
    Pure function of metrics and params. Returns spawn directives.
    No random calls. Does not modify base stats.
    """
    state = _director_state(hp_percent, params)

    # Enemy count (capped)
    mult = params.enemy_count_multiplier_struggling if state == "struggling" else (
        params.enemy_count_multiplier_dominating if state == "dominating" else 1.0
    )
    count = max(1, min(params.enemy_count_max, int(params.enemy_count_base * mult)))

    # Archetype mix: use weight set by state
    if state == "struggling":
        weights = params.archetype_weights_defense
    elif state == "dominating":
        weights = params.archetype_weights_offense
    else:
        weights = params.archetype_weights_balanced
    archetype_mix = ARCHETYPE_NAMES  # spawner will use weights; we pass full list and elite_bias

    # Elite count (0 to count, biased by state)
    if state == "struggling":
        bias = params.elite_bias_struggling
    elif state == "dominating":
        bias = params.elite_bias_dominating
    else:
        bias = params.elite_bias_stable
    elite_count = max(0, min(count, int(count * bias)))

    # Ambush vs combat: chosen_encounter_type for logging (spawner doesn't change room type)
    if state == "struggling":
        ambush_prob = params.ambush_probability_struggling
    elif state == "dominating":
        ambush_prob = params.ambush_probability_dominating
    else:
        ambush_prob = params.ambush_probability_base
    chosen_encounter_type = "ambush" if room_type == "ambush" else "combat"

    return {
        "enemy_count": count,
        "archetype_mix": archetype_mix,
        "archetype_weights": weights,
        "elite_count": elite_count,
        "director_state": state,
        "chosen_encounter_type": chosen_encounter_type,
        "healing_bias": params.healing_bias_struggling if state == "struggling" else (
            params.healing_bias_dominating if state == "dominating" else params.healing_bias_stable
        ),
    }
