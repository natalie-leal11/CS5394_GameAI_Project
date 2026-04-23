# Read-only tuning constants for AI Director / Player Model (no mutation during gameplay).
#
# Phase 1: Runtime parameter contract for RL integration — JSON-backed schema (DifficultyParams)
# plus legacy PlayerModelTuningParams used by current gameplay. Gameplay still uses
# PlayerModelTuningParams / DEFAULT_DIFFICULTY_PARAMS until a later integration phase.

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final, Mapping

# Immutable default weights for safe-room offering bias (read-only).
UPGRADE_BIAS_DEFAULT: Final[Mapping[str, float]] = MappingProxyType(
    {"health": 1.0, "speed": 1.0, "attack": 1.0, "defence": 1.0}
)


def _project_root() -> Path:
    """Project root (directory containing config/, assets/)."""
    return Path(__file__).resolve().parent.parent.parent.parent


DEFAULT_DIFFICULTY_JSON_PATH: Final[Path] = _project_root() / "config" / "difficulty_params.json"


# --- JSON contract (mirrors config/difficulty_params.json) ---


@dataclass(frozen=True)
class PlayerModelParams:
    """Player model thresholds (percent / HP-loss bands) for RL contract."""

    struggling_hp_critical_percent: float
    struggling_hp_weak_percent: float
    dominating_hp_min_percent: float
    dominating_avg_hp_loss_max_percent: float


@dataclass(frozen=True)
class DirectorStateFloats:
    """Per-player-state floating knobs (struggling / stable / dominating)."""

    struggling: float
    stable: float
    dominating: float


@dataclass(frozen=True)
class DirectorStateInts:
    """Per-player-state integer knobs."""

    struggling: int
    stable: int
    dominating: int


@dataclass(frozen=True)
class DirectorParams:
    """AI Director numeric contract (not yet wired to AIDirector)."""

    difficulty_modifier: DirectorStateFloats
    enemy_adjustment: DirectorStateInts
    reinforcement_chance: DirectorStateFloats


@dataclass(frozen=True)
class RewardParams:
    """Healing / reward generosity contract."""

    heal_drop_base_chance: float
    safe_room_heal_percent: float
    mini_boss_reward_heal_percent: float


@dataclass(frozen=True)
class MetricsParams:
    """MetricsTracker-related thresholds for RL contract."""

    struggle_hp_loss_percent_threshold: float
    dominating_hp_loss_percent_threshold: float
    spike_damage_threshold: float


@dataclass(frozen=True)
class CombatParams:
    """Combat multipliers contract (elite tuning)."""

    elite_hp_multiplier: float
    elite_damage_multiplier: float


@dataclass(frozen=True)
class DifficultyParams:
    """
    Root runtime difficulty configuration loaded from JSON.

    These parameters are loaded at runtime and must not be modified during gameplay.
    They are tuned offline.
    """

    player_model: PlayerModelParams
    director: DirectorParams
    rewards: RewardParams
    metrics: MetricsParams
    combat: CombatParams

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> DifficultyParams:
        """Build from a decoded JSON object; validates ranges."""
        _require_keys(data, ("player_model", "director", "rewards", "metrics", "combat"), "root")

        pm = data["player_model"]
        _require_keys(
            pm,
            (
                "struggling_hp_critical_percent",
                "struggling_hp_weak_percent",
                "dominating_hp_min_percent",
                "dominating_avg_hp_loss_max_percent",
            ),
            "player_model",
        )
        player_model = PlayerModelParams(
            struggling_hp_critical_percent=float(pm["struggling_hp_critical_percent"]),
            struggling_hp_weak_percent=float(pm["struggling_hp_weak_percent"]),
            dominating_hp_min_percent=float(pm["dominating_hp_min_percent"]),
            dominating_avg_hp_loss_max_percent=float(pm["dominating_avg_hp_loss_max_percent"]),
        )

        dr = data["director"]
        _require_keys(dr, ("difficulty_modifier", "enemy_adjustment", "reinforcement_chance"), "director")
        dm = dr["difficulty_modifier"]
        ea = dr["enemy_adjustment"]
        rc = dr["reinforcement_chance"]
        for label, block in (("difficulty_modifier", dm), ("reinforcement_chance", rc)):
            _require_keys(block, ("struggling", "stable", "dominating"), f"director.{label}")
        _require_keys(ea, ("struggling", "stable", "dominating"), "director.enemy_adjustment")

        director = DirectorParams(
            difficulty_modifier=DirectorStateFloats(
                struggling=float(dm["struggling"]),
                stable=float(dm["stable"]),
                dominating=float(dm["dominating"]),
            ),
            enemy_adjustment=DirectorStateInts(
                struggling=int(ea["struggling"]),
                stable=int(ea["stable"]),
                dominating=int(ea["dominating"]),
            ),
            reinforcement_chance=DirectorStateFloats(
                struggling=float(rc["struggling"]),
                stable=float(rc["stable"]),
                dominating=float(rc["dominating"]),
            ),
        )

        rw = data["rewards"]
        _require_keys(rw, ("heal_drop_base_chance", "safe_room_heal_percent", "mini_boss_reward_heal_percent"), "rewards")
        rewards = RewardParams(
            heal_drop_base_chance=float(rw["heal_drop_base_chance"]),
            safe_room_heal_percent=float(rw["safe_room_heal_percent"]),
            mini_boss_reward_heal_percent=float(rw["mini_boss_reward_heal_percent"]),
        )

        mt = data["metrics"]
        _require_keys(
            mt,
            ("struggle_hp_loss_percent_threshold", "dominating_hp_loss_percent_threshold", "spike_damage_threshold"),
            "metrics",
        )
        metrics = MetricsParams(
            struggle_hp_loss_percent_threshold=float(mt["struggle_hp_loss_percent_threshold"]),
            dominating_hp_loss_percent_threshold=float(mt["dominating_hp_loss_percent_threshold"]),
            spike_damage_threshold=float(mt["spike_damage_threshold"]),
        )

        cb = data["combat"]
        _require_keys(cb, ("elite_hp_multiplier", "elite_damage_multiplier"), "combat")
        combat = CombatParams(
            elite_hp_multiplier=float(cb["elite_hp_multiplier"]),
            elite_damage_multiplier=float(cb["elite_damage_multiplier"]),
        )

        root = cls(
            player_model=player_model,
            director=director,
            rewards=rewards,
            metrics=metrics,
            combat=combat,
        )
        root._validate()
        return root

    def _validate(self) -> None:
        """Basic range checks; raises ValueError on failure."""
        pm = self.player_model
        for name, v in (
            ("player_model.struggling_hp_critical_percent", pm.struggling_hp_critical_percent),
            ("player_model.struggling_hp_weak_percent", pm.struggling_hp_weak_percent),
            ("player_model.dominating_hp_min_percent", pm.dominating_hp_min_percent),
            ("player_model.dominating_avg_hp_loss_max_percent", pm.dominating_avg_hp_loss_max_percent),
        ):
            _percent_0_100(name, v)

        d = self.director
        for label, block in (
            ("director.difficulty_modifier.struggling", d.difficulty_modifier.struggling),
            ("director.difficulty_modifier.stable", d.difficulty_modifier.stable),
            ("director.difficulty_modifier.dominating", d.difficulty_modifier.dominating),
        ):
            if block <= 0.0:
                raise ValueError(f"{label} must be > 0, got {block}")

        for label, p in (
            ("director.reinforcement_chance.struggling", d.reinforcement_chance.struggling),
            ("director.reinforcement_chance.stable", d.reinforcement_chance.stable),
            ("director.reinforcement_chance.dominating", d.reinforcement_chance.dominating),
        ):
            _probability(label, p)

        r = self.rewards
        for label, p in (
            ("rewards.heal_drop_base_chance", r.heal_drop_base_chance),
            ("rewards.safe_room_heal_percent", r.safe_room_heal_percent),
            ("rewards.mini_boss_reward_heal_percent", r.mini_boss_reward_heal_percent),
        ):
            _probability(label, p)

        m = self.metrics
        for name, v in (
            ("metrics.struggle_hp_loss_percent_threshold", m.struggle_hp_loss_percent_threshold),
            ("metrics.dominating_hp_loss_percent_threshold", m.dominating_hp_loss_percent_threshold),
        ):
            _percent_0_100(name, v)
        if m.spike_damage_threshold < 0.0:
            raise ValueError(f"metrics.spike_damage_threshold must be >= 0, got {m.spike_damage_threshold}")

        c = self.combat
        if c.elite_hp_multiplier <= 0.0:
            raise ValueError(f"combat.elite_hp_multiplier must be > 0, got {c.elite_hp_multiplier}")
        if c.elite_damage_multiplier <= 0.0:
            raise ValueError(f"combat.elite_damage_multiplier must be > 0, got {c.elite_damage_multiplier}")


def load_difficulty_params_json(path: Path | None = None) -> DifficultyParams:
    """
    Load and validate ``DifficultyParams`` from a JSON file.

    Defaults to ``config/difficulty_params.json`` under the project root.
    """
    p = path if path is not None else DEFAULT_DIFFICULTY_JSON_PATH
    text = Path(p).read_text(encoding="utf-8")
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("difficulty JSON root must be an object")
    return DifficultyParams.from_dict(data)


def _require_keys(obj: Mapping[str, Any], keys: tuple[str, ...], ctx: str) -> None:
    for k in keys:
        if k not in obj:
            raise KeyError(f"Missing key {k!r} in {ctx}")


def _probability(label: str, v: float) -> None:
    if not (0.0 <= v <= 1.0):
        raise ValueError(f"{label} must be in [0, 1], got {v}")


def _percent_0_100(label: str, v: float) -> None:
    if not (0.0 <= v <= 100.0):
        raise ValueError(f"{label} must be in [0, 100], got {v}")


# --- Legacy PlayerModel tuning (current gameplay; not loaded from JSON in Phase 1) ---


@dataclass(frozen=True)
class PlayerModelTuningParams:
    """
    Frozen snapshot of bounds and thresholds for the live PlayerModel.
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


# Default singleton for imports (immutable) — live PlayerModel tuning (unchanged behavior)
DEFAULT_DIFFICULTY_PARAMS: Final[PlayerModelTuningParams] = PlayerModelTuningParams()
