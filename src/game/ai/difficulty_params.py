# Read-only tuning constants for AI Director / Player Model (no mutation during gameplay).

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Mapping

# Immutable default weights for safe-room offering bias (read-only).
UPGRADE_BIAS_DEFAULT: Final[Mapping[str, float]] = MappingProxyType(
    {"health": 1.0, "speed": 1.0, "attack": 1.0, "defence": 1.0}
)


@dataclass(frozen=True)
class DifficultyParams:
    """
    Frozen snapshot of bounds and thresholds.
    Loaded once; gameplay code must not modify instances.
    """

    # --- Legacy / AI Director (unchanged defaults) ---
    struggling_hp_ratio: float = 0.35
    dominating_hp_ratio: float = 0.85
    stable_damage_taken_window: int = 5

    enemy_count_offset_min: int = -1
    enemy_count_offset_max: int = 1

    reinforcement_enabled_bias: float = 0.0
    elite_bias_min: float = -0.2
    elite_bias_max: float = 0.2
    ambush_bias_min: float = -0.2
    ambush_bias_max: float = 0.2

    safe_room_heal_bias_min: float = -0.1
    safe_room_heal_bias_max: float = 0.1

    # --- PlayerModel Phase 2: HP bands (percent 0–100) ---
    player_model_low_hp_percent: float = 30.0
    player_model_near_death_hp_percent: float = 15.0
    player_model_high_hp_percent: float = 75.0

    # Room-level HP loss considered "heavy" (percent points lost in a room)
    player_model_heavy_room_hp_loss: float = 28.0

    # Raw damage taken in the last completed room (HP points) — heavy hit
    player_model_heavy_room_damage_taken: float = 80.0

    # Room clear duration (seconds): above this rolling average => "slow" clears (legacy / other use)
    player_model_slow_clear_time_sec: float = 90.0

    # Ratios use rooms_cleared as denominator; min rooms before ratio is trusted
    player_model_min_rooms_for_ratio: int = 2

    # Legacy (pre–weighted PlayerModel); kept for compatibility
    player_model_score_margin: float = 12.0
    player_model_struggling_score_threshold: float = 52.0
    player_model_dominating_score_threshold: float = 48.0

    # Recent death / bad outcomes in last_3 room results
    player_model_recent_death_struggle_weight: float = 38.0
    player_model_bad_result_count_weight: float = 14.0  # per near_death or death in last_3

    # Healing dependency: total_healing_received / max(total_damage_taken, eps)
    player_model_healing_dependency_high: float = 0.42

    # reward_collected_flag as a weak positive for "engaged" play (not dominating alone)
    player_model_reward_collected_bonus: float = 6.0

    # --- PlayerModel v2: global thresholds (see PlayerModel rules table) ---
    # HP/struggle vs dominate bands (0–100 scale; doc "0.30" means 30%)
    player_model_struggling_hp_percent: float = 30.0
    # Average HP loss across last_3 above this (percent points) => high_recent_avg_hp_loss signal
    player_model_recent_avg_hp_loss_struggling: float = 22.0
    # Average HP loss across last_3 at or below this (percent points) => part of low_damage_and_loss
    player_model_recent_avg_hp_loss_dominating: float = 8.0
    # Damage taken in last completed room (HP points) — "low" for dominate signal
    player_model_damage_taken_low_threshold: float = 45.0
    # Rolling average clear time (seconds) — "fast" for dominate signal
    player_model_fast_clear_avg_seconds: float = 55.0
    # Share thresholds (with rooms_cleared denominator; min_rooms_for_ratio gates use)
    player_model_struggling_share_threshold: float = 0.45
    player_model_dominating_share_threshold: float = 0.40
    # Healing pressure: total_healing_received / rooms_cleared above this => struggle signal
    player_model_healing_per_room_struggling_threshold: float = 45.0
    # Minimum weighted sum on an axis to qualify STRUGGLING / DOMINATING (before margins / gates)
    player_model_weighted_min_score: float = 2.0
    # When both axes could apply, winner must exceed the other by at least this (else STABLE)
    player_model_weighted_preference_margin: float = 0.35
    # First N cleared rooms: default STABLE unless recent_death_flag (obvious struggle)
    player_model_early_rooms_stable_count: int = 2

    # Repeated bad results: need at least this many near_death or death in last_3
    player_model_repeated_bad_results_min: int = 2
    # Dominate: need at least this many clean_clear in last_3 (requires len >= 2)
    player_model_clean_clear_majority_min: int = 2

    # Per-signal weights (struggle axis)
    player_model_w_s_recent_death: float = 1.15
    player_model_w_s_low_hp: float = 1.0
    player_model_w_s_repeated_near_death_or_death: float = 1.2
    player_model_w_s_high_recent_avg_hp_loss: float = 1.0
    player_model_w_s_struggling_rooms_share: float = 1.05
    player_model_w_s_high_healing_per_room: float = 0.70

    # Per-signal weights (dominate axis)
    player_model_w_d_no_recent_death: float = 0.80
    player_model_w_d_hp_comfortable: float = 1.10
    player_model_w_d_mostly_clean_clear: float = 1.15
    player_model_w_d_low_damage_and_loss: float = 1.10
    player_model_w_d_fast_recent_clears: float = 1.00
    player_model_w_d_dominating_rooms_share: float = 1.05


# Default singleton for imports (immutable)
DEFAULT_DIFFICULTY_PARAMS: Final[DifficultyParams] = DifficultyParams()
