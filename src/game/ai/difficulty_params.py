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

    # --- PlayerModel: reference bands (percent 0–100); optional for other systems ---
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

    # Legacy (pre–v3 PlayerModel); kept for compatibility / external docs
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

    # --- PlayerModel: life-tier visible state (applied after v3 base; see _life_phase_visible_state) ---
    player_model_life1_dominating_min_hp_percent: float = 70.0
    player_model_life1_stable_min_hp_percent: float = 40.0
    player_model_life2_stable_min_hp_percent: float = 70.0

    # --- PlayerModel v3: percentage rules (PlayerModel.classify; single-life run) ---
    # STRUGGLING: HP <= critical OR recent death OR (2+ weak signals among weak HP / bad rooms / high avg loss)
    player_model_struggling_hp_critical_percent: float = 25.0
    player_model_struggling_hp_weak_percent: float = 40.0
    player_model_struggling_bad_rooms_min: int = 2  # near_death or death in last 3 rooms
    player_model_struggling_avg_hp_loss_min: float = 30.0  # average HP% lost across last 3 rooms

    # DOMINATING: baseline HP + no recent death + at least two strong performance signals (clean / low loss / fast)
    player_model_dominating_hp_min_percent: float = 70.0
    player_model_dominating_avg_hp_loss_max_percent: float = 15.0
    player_model_dominating_clean_clears_min: int = 2  # in last 3 rooms
    # Rolling average clear time (seconds) over last 3 — "fast" when len >= 2
    player_model_fast_clear_avg_seconds: float = 55.0

    # Share thresholds (legacy; not used by PlayerModel v3 classify)
    player_model_struggling_share_threshold: float = 0.45
    player_model_dominating_share_threshold: float = 0.40
    # Healing pressure (legacy)
    player_model_healing_per_room_struggling_threshold: float = 45.0


# Default singleton for imports (immutable)
DEFAULT_DIFFICULTY_PARAMS: Final[DifficultyParams] = DifficultyParams()
