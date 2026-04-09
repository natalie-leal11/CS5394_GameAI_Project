"""
Offline reward evaluation: candidate parameter schema, bounds, and defaults.

This module does **not** load gameplay or change runtime configuration. It only
describes the inputs accepted by :mod:`game.rl.reward_eval`.

Candidate JSON schema (one object per file or array of objects)
----------------------------------------------------------------

.. code-block:: json

   {
     "weights": {
       "win_rate": 1.0,
       "early_penalty": 0.85,
       "late_penalty": 0.75,
       "spike_penalty": 0.8
     },
     "win_band": {"lo": 0.55, "hi": 0.65, "center": 0.6},
     "early_biome_max": 2,
     "early_damage_ref": 40.0,
     "late_biome_min": 3,
     "late_room_index_min": 16,
     "late_trivial_enemy_max": 2,
     "late_trivial_damage_max": 8.0,
     "late_trivial_clear_time_max": 25.0,
     "spike_difficulty_delta": 0.25,
     "spike_enemy_adjust_delta": 3
   }

**weights** combine into ``overall_reward`` (see ``reward_eval`` docstring).

All numeric bounds are enforced by :func:`validate_candidate_dict` /
:class:`CandidateEvaluationParams`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


# --- Bounds (inclusive where noted) ---

WEIGHT_MIN = 0.0
WEIGHT_MAX = 5.0

WIN_BAND_LO_MIN = 0.0
WIN_BAND_LO_MAX = 1.0
WIN_BAND_HI_MIN = 0.0
WIN_BAND_HI_MAX = 1.0
WIN_CENTER_MIN = 0.0
WIN_CENTER_MAX = 1.0

EARLY_BIOME_MAX_MIN = 0
EARLY_BIOME_MAX_MAX = 4

EARLY_DAMAGE_REF_MIN = 1.0
EARLY_DAMAGE_REF_MAX = 200.0

LATE_BIOME_MIN_MIN = 1
LATE_BIOME_MIN_MAX = 6

LATE_ROOM_INDEX_MIN_MIN = 0
LATE_ROOM_INDEX_MIN_MAX = 40

LATE_TRIVIAL_ENEMY_MAX_MIN = 0
LATE_TRIVIAL_ENEMY_MAX_MAX = 20

LATE_TRIVIAL_DAMAGE_MAX_MIN = 0.0
LATE_TRIVIAL_DAMAGE_MAX_MAX = 100.0

LATE_TRIVIAL_CLEAR_TIME_MAX_MIN = 1.0
LATE_TRIVIAL_CLEAR_TIME_MAX_MAX = 300.0

SPIKE_DIFFICULTY_DELTA_MIN = 0.01
SPIKE_DIFFICULTY_DELTA_MAX = 2.0

SPIKE_ENEMY_ADJUST_DELTA_MIN = 1
SPIKE_ENEMY_ADJUST_DELTA_MAX = 20

TRIVIALITY_PERCENTILE_MIN = 0.0
TRIVIALITY_PERCENTILE_MAX = 1.0


@dataclass
class RewardWeights:
    """Linear combination weights for ``overall_reward`` (non-negative)."""

    win_rate: float = 1.0
    early_penalty: float = 0.85
    late_penalty: float = 0.75
    spike_penalty: float = 0.8


@dataclass
class WinBand:
    """Target win-rate band (fraction of decisive runs that end in victory)."""

    lo: float = 0.55
    hi: float = 0.65
    center: float = 0.60


@dataclass
class CandidateEvaluationParams:
    """
    Full evaluation profile: thresholds + weights.

    These parameters define *how* logged runs are scored, not game engine tuning.
    """

    weights: RewardWeights = field(default_factory=RewardWeights)
    win_band: WinBand = field(default_factory=WinBand)

    # Early biome: biome_index <= early_biome_max (typically biomes 1–2)
    early_biome_max: int = 2
    # Scale for normalizing damage_taken in early rooms (HP% units, same as logs)
    early_damage_ref: float = 40.0

    # Late game: biome_index >= late_biome_min AND room_index >= late_room_index_min
    late_biome_min: int = 3
    late_room_index_min: int = 16

    # Trivial late encounter: few enemies, low damage, fast clear
    late_trivial_enemy_max: int = 2
    late_trivial_damage_max: float = 8.0
    late_trivial_clear_time_max: float = 28.0

    # How triviality caps are chosen (see reward_eval module docstring).
    # ``fixed``: use late_trivial_*_max as hard upper bounds.
    # ``percentile``: thresholds = deterministic quantiles of each metric over late rooms
    # that have complete data (same cohort per evaluation).
    late_triviality_mode: Literal["fixed", "percentile"] = "fixed"
    # Quantiles in [0, 1] for enemy_count, damage_taken, room_clear_time (lower = stricter).
    late_trivial_percentile_enemy: float = 0.33
    late_trivial_percentile_damage: float = 0.33
    late_trivial_percentile_clear_time: float = 0.33

    # Spike: consecutive rooms (same run) exceed these deltas
    spike_difficulty_delta: float = 0.25
    spike_enemy_adjust_delta: int = 3


def default_candidate() -> CandidateEvaluationParams:
    """Project default evaluation profile."""
    return CandidateEvaluationParams()


def candidate_from_dict(raw: dict[str, Any]) -> CandidateEvaluationParams:
    """Build :class:`CandidateEvaluationParams` from a JSON-like dict (partial ok)."""
    w = raw.get("weights") or {}
    wb = raw.get("win_band") or {}
    mode_s = str(raw.get("late_triviality_mode", "fixed")).strip().lower()
    if mode_s not in ("fixed", "percentile"):
        raise ValueError(f"late_triviality_mode must be 'fixed' or 'percentile', got {raw.get('late_triviality_mode')!r}")
    params = CandidateEvaluationParams(
        weights=RewardWeights(
            win_rate=float(w.get("win_rate", RewardWeights().win_rate)),
            early_penalty=float(w.get("early_penalty", RewardWeights().early_penalty)),
            late_penalty=float(w.get("late_penalty", RewardWeights().late_penalty)),
            spike_penalty=float(w.get("spike_penalty", RewardWeights().spike_penalty)),
        ),
        win_band=WinBand(
            lo=float(wb.get("lo", WinBand().lo)),
            hi=float(wb.get("hi", WinBand().hi)),
            center=float(wb.get("center", WinBand().center)),
        ),
        early_biome_max=int(raw.get("early_biome_max", 2)),
        early_damage_ref=float(raw.get("early_damage_ref", 40.0)),
        late_biome_min=int(raw.get("late_biome_min", 3)),
        late_room_index_min=int(raw.get("late_room_index_min", 16)),
        late_trivial_enemy_max=int(raw.get("late_trivial_enemy_max", 2)),
        late_trivial_damage_max=float(raw.get("late_trivial_damage_max", 8.0)),
        late_trivial_clear_time_max=float(raw.get("late_trivial_clear_time_max", 28.0)),
        late_triviality_mode=mode_s,  # type: ignore[arg-type]
        late_trivial_percentile_enemy=float(raw.get("late_trivial_percentile_enemy", 0.33)),
        late_trivial_percentile_damage=float(raw.get("late_trivial_percentile_damage", 0.33)),
        late_trivial_percentile_clear_time=float(raw.get("late_trivial_percentile_clear_time", 0.33)),
        spike_difficulty_delta=float(raw.get("spike_difficulty_delta", 0.25)),
        spike_enemy_adjust_delta=int(raw.get("spike_enemy_adjust_delta", 3)),
    )
    validate_candidate_params(params)
    return params


def validate_candidate_params(p: CandidateEvaluationParams) -> None:
    """Raise ``ValueError`` if any field is outside documented bounds."""
    w = p.weights
    for name, val in (
        ("weights.win_rate", w.win_rate),
        ("weights.early_penalty", w.early_penalty),
        ("weights.late_penalty", w.late_penalty),
        ("weights.spike_penalty", w.spike_penalty),
    ):
        if not (WEIGHT_MIN <= val <= WEIGHT_MAX):
            raise ValueError(f"{name} must be in [{WEIGHT_MIN}, {WEIGHT_MAX}], got {val}")

    wb = p.win_band
    if not (WIN_BAND_LO_MIN <= wb.lo <= WIN_BAND_LO_MAX):
        raise ValueError(f"win_band.lo out of bounds: {wb.lo}")
    if not (WIN_BAND_HI_MIN <= wb.hi <= WIN_BAND_HI_MAX):
        raise ValueError(f"win_band.hi out of bounds: {wb.hi}")
    if wb.lo >= wb.hi:
        raise ValueError(f"win_band.lo ({wb.lo}) must be < win_band.hi ({wb.hi})")
    if not (WIN_CENTER_MIN <= wb.center <= WIN_CENTER_MAX):
        raise ValueError(f"win_band.center out of bounds: {wb.center}")
    if not (wb.lo <= wb.center <= wb.hi):
        raise ValueError(
            f"win_band.center ({wb.center}) must lie between lo ({wb.lo}) and hi ({wb.hi})"
        )

    if not (EARLY_BIOME_MAX_MIN <= p.early_biome_max <= EARLY_BIOME_MAX_MAX):
        raise ValueError(f"early_biome_max out of bounds: {p.early_biome_max}")
    if not (EARLY_DAMAGE_REF_MIN <= p.early_damage_ref <= EARLY_DAMAGE_REF_MAX):
        raise ValueError(f"early_damage_ref out of bounds: {p.early_damage_ref}")

    if not (LATE_BIOME_MIN_MIN <= p.late_biome_min <= LATE_BIOME_MIN_MAX):
        raise ValueError(f"late_biome_min out of bounds: {p.late_biome_min}")
    if not (LATE_ROOM_INDEX_MIN_MIN <= p.late_room_index_min <= LATE_ROOM_INDEX_MIN_MAX):
        raise ValueError(f"late_room_index_min out of bounds: {p.late_room_index_min}")

    if not (LATE_TRIVIAL_ENEMY_MAX_MIN <= p.late_trivial_enemy_max <= LATE_TRIVIAL_ENEMY_MAX_MAX):
        raise ValueError(f"late_trivial_enemy_max out of bounds: {p.late_trivial_enemy_max}")
    if not (LATE_TRIVIAL_DAMAGE_MAX_MIN <= p.late_trivial_damage_max <= LATE_TRIVIAL_DAMAGE_MAX_MAX):
        raise ValueError(f"late_trivial_damage_max out of bounds: {p.late_trivial_damage_max}")
    if not (LATE_TRIVIAL_CLEAR_TIME_MAX_MIN <= p.late_trivial_clear_time_max <= LATE_TRIVIAL_CLEAR_TIME_MAX_MAX):
        raise ValueError(f"late_trivial_clear_time_max out of bounds: {p.late_trivial_clear_time_max}")

    if not (SPIKE_DIFFICULTY_DELTA_MIN <= p.spike_difficulty_delta <= SPIKE_DIFFICULTY_DELTA_MAX):
        raise ValueError(f"spike_difficulty_delta out of bounds: {p.spike_difficulty_delta}")
    if not (SPIKE_ENEMY_ADJUST_DELTA_MIN <= p.spike_enemy_adjust_delta <= SPIKE_ENEMY_ADJUST_DELTA_MAX):
        raise ValueError(f"spike_enemy_adjust_delta out of bounds: {p.spike_enemy_adjust_delta}")

    if p.late_triviality_mode not in ("fixed", "percentile"):
        raise ValueError(f"late_triviality_mode must be 'fixed' or 'percentile', got {p.late_triviality_mode!r}")

    for name, pv in (
        ("late_trivial_percentile_enemy", p.late_trivial_percentile_enemy),
        ("late_trivial_percentile_damage", p.late_trivial_percentile_damage),
        ("late_trivial_percentile_clear_time", p.late_trivial_percentile_clear_time),
    ):
        if not (TRIVIALITY_PERCENTILE_MIN <= pv <= TRIVIALITY_PERCENTILE_MAX):
            raise ValueError(f"{name} must be in [0, 1], got {pv}")


def validate_candidate_dict(raw: dict[str, Any]) -> CandidateEvaluationParams:
    """Parse and validate; raises ``ValueError`` on bad schema."""
    return candidate_from_dict(raw)


def schema_summary() -> str:
    """Short human-readable bounds reference for CLI help text."""
    lines = [
        "CandidateEvaluationParams bounds:",
        f"  weights.*: [{WEIGHT_MIN}, {WEIGHT_MAX}]",
        f"  win_band.lo/hi/center: [{WIN_BAND_LO_MIN}, {WIN_BAND_HI_MAX}], lo < hi",
        f"  early_biome_max: [{EARLY_BIOME_MAX_MIN}, {EARLY_BIOME_MAX_MAX}]",
        f"  early_damage_ref: [{EARLY_DAMAGE_REF_MIN}, {EARLY_DAMAGE_REF_MAX}]",
        f"  late_biome_min: [{LATE_BIOME_MIN_MIN}, {LATE_BIOME_MIN_MAX}]",
        f"  late_room_index_min: [{LATE_ROOM_INDEX_MIN_MIN}, {LATE_ROOM_INDEX_MIN_MAX}]",
        f"  late_trivial_*: enemy_max [{LATE_TRIVIAL_ENEMY_MAX_MIN}, {LATE_TRIVIAL_ENEMY_MAX_MAX}],",
        f"    damage_max [{LATE_TRIVIAL_DAMAGE_MAX_MIN}, {LATE_TRIVIAL_DAMAGE_MAX_MAX}],",
        f"    clear_time_max [{LATE_TRIVIAL_CLEAR_TIME_MAX_MIN}, {LATE_TRIVIAL_CLEAR_TIME_MAX_MAX}]",
        f"  spike_difficulty_delta: [{SPIKE_DIFFICULTY_DELTA_MIN}, {SPIKE_DIFFICULTY_DELTA_MAX}]",
        f"  spike_enemy_adjust_delta: [{SPIKE_ENEMY_ADJUST_DELTA_MIN}, {SPIKE_ENEMY_ADJUST_DELTA_MAX}]",
        "  late_triviality_mode: 'fixed' | 'percentile'",
        f"  late_trivial_percentile_*: [{TRIVIALITY_PERCENTILE_MIN}, {TRIVIALITY_PERCENTILE_MAX}]",
    ]
    return "\n".join(lines)
