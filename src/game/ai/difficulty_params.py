"""
Difficulty parameters for AI Director. All thresholds and multipliers here.
RL may tune these offline; no hard-coded values in ai_director.py.
"""
from dataclasses import dataclass
from typing import List


@dataclass
class DifficultyParams:
    """External parameters for director decisions. Loaded at runtime."""

    # HP thresholds (fraction 0-1). Director state: struggling / stable / dominating
    hp_threshold_struggling: float = 0.40  # below = struggling
    hp_threshold_dominating: float = 0.75   # above = dominating

    # Enemy count: base per room type, multiplier when struggling (reduce count)
    enemy_count_base: int = 2
    enemy_count_max: int = 6
    enemy_count_multiplier_struggling: float = 0.6  # reduce when low HP
    enemy_count_multiplier_dominating: float = 1.2  # increase when dominating

    # Archetype mix weights (order: swarm, flanker, brute, heavy, ranged_suppressor)
    archetype_weights_balanced: List[float] = None
    archetype_weights_defense: List[float] = None   # when struggling: more swarm, less brute
    archetype_weights_offense: List[float] = None  # when dominating: more flanker/brute

    # Elite
    elite_bias_struggling: float = 0.0   # fewer elites when struggling
    elite_bias_stable: float = 0.2
    elite_bias_dominating: float = 0.4

    # Ambush probability (0-1) - director can suggest ambush vs combat
    ambush_probability_base: float = 0.2
    ambush_probability_struggling: float = 0.1  # less ambush when struggling
    ambush_probability_dominating: float = 0.35

    # Healing bias (for safe rooms / drops) 0-1
    healing_bias_struggling: float = 0.8
    healing_bias_stable: float = 0.5
    healing_bias_dominating: float = 0.2

    def __post_init__(self) -> None:
        if self.archetype_weights_balanced is None:
            self.archetype_weights_balanced = [0.3, 0.25, 0.2, 0.15, 0.1]
        if self.archetype_weights_defense is None:
            self.archetype_weights_defense = [0.4, 0.2, 0.15, 0.15, 0.1]
        if self.archetype_weights_offense is None:
            self.archetype_weights_offense = [0.2, 0.3, 0.25, 0.15, 0.1]


def get_default_difficulty_params() -> DifficultyParams:
    """Return default params. RL may load from file instead."""
    return DifficultyParams()
