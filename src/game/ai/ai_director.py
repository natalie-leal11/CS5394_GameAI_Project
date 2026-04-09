# Phase 3: deterministic difficulty decisions from PlayerModel state (no gameplay side effects here).

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from game.ai.difficulty_params import UPGRADE_BIAS_DEFAULT, DifficultyParams, load_difficulty_params_json
from game.ai.player_model import PlayerStateClass


@dataclass(frozen=True)
class EncounterDirective:
    """Bounded knobs for encounter composition (applied only by future wiring)."""

    enemy_count_offset: int = 0
    spawn_delay_profile: str = "default"
    reinforcement_enabled: bool = False
    elite_bias: float = 0.0
    ambush_bias: float = 0.0


@dataclass(frozen=True)
class SafeRoomDirective:
    """Bounded safe-room tuning (does not replace player choice)."""

    safe_room_heal_bias: float = 0.0
    upgrade_bias_profile: Mapping[str, float] = UPGRADE_BIAS_DEFAULT


@dataclass(frozen=True)
class VariationDirective:
    """Aggregate seed-controlled variation intent for future encounter / safe-room wiring."""

    encounter: EncounterDirective = field(default_factory=EncounterDirective)
    safe_room: SafeRoomDirective = field(default_factory=SafeRoomDirective)


@dataclass(frozen=True)
class EncounterDirectorSnapshot:
    """
    Immutable copy of director outputs used when building spawns for a room.
    Updated only after a room-end classification (next room uses this; current room is frozen).
    """

    difficulty_modifier: float = 1.0
    enemy_adjustment: int = 0
    reinforcement_chance: float = 0.1
    composition_bias: str = "normal"
    last_player_state_name: str | None = "STABLE"
    pressure_level: str = "medium"
    composition_bias_b2: str = "balanced"
    reinforcement_chance_b2: float = 0.15
    hazard_tune_factor_b2: float = 1.0
    composition_bias_b3: str = "balanced"
    ranged_bias_b3: str = "medium"
    reinforcement_chance_b3: float = 0.15
    hazard_tune_factor_b3: float = 1.0
    composition_bias_b4: str = "balanced"
    boss_pressure: str = "medium"
    pacing_bias: str = "normal"
    reinforcement_chance_b4: float = 0.15
    hazard_tune_factor_b4: float = 1.0

    @classmethod
    def neutral_default(cls) -> EncounterDirectorSnapshot:
        """STABLE-equivalent before any room-end classification."""
        return cls()


class AIDirector:
    """
    Reads PlayerModel state and stores deterministic difficulty-related outputs.
    No randomness, smoothing, or gameplay mutations.
    """

    def __init__(self, params: DifficultyParams | None = None) -> None:
        self._params: DifficultyParams = params or load_difficulty_params_json()
        self.difficulty_modifier: float = 1.0
        self.enemy_adjustment: int = 0
        self.reinforcement_chance: float = 0.0
        self.reward_bias: str = "normal"
        self.hazard_bias: str = "normal"
        self.composition_bias: str = "normal"
        self.last_player_state_name: str | None = None
        # Biome 2 (parallel tuning; Biome 1 uses reinforcement_chance + composition_bias above)
        self.pressure_level: str = "medium"
        self.composition_bias_b2: str = "balanced"
        self.reinforcement_chance_b2: float = 0.15
        # Intent factor for hazard tuning (grid not mutated at runtime; for debug / future wiring)
        self.hazard_tune_factor_b2: float = 1.0
        # Biome 3 (parallel; prompts use safe/balanced/aggressive + ranged + hazard intent)
        self.composition_bias_b3: str = "balanced"
        self.ranged_bias_b3: str = "medium"
        self.reinforcement_chance_b3: float = 0.15
        self.hazard_tune_factor_b3: float = 1.0
        # Biome 4 (final biome + boss pressure + pacing)
        self.composition_bias_b4: str = "balanced"
        self.boss_pressure: str = "medium"
        self.pacing_bias: str = "normal"
        self.reinforcement_chance_b4: float = 0.15
        self.hazard_tune_factor_b4: float = 1.0
        # Set each frame from GameScene (current campaign room) for overlay / effective adjustment
        self._ctx_room_idx: int | None = None
        self._ctx_biome_idx: int | None = None

    @staticmethod
    def _reinforcement_biome234(r1: float) -> float:
        """Biomes 2–4: +0.05 vs Biome 1 reinforcement for the same player state (legacy curve)."""
        return round(min(1.0, float(r1) + 0.05), 12)

    def update_room_context(self, room_idx: int | None, biome_index: int | None) -> None:
        """Room index + biome for trial-phase and debug (no gameplay side effects by itself)."""
        self._ctx_room_idx = int(room_idx) if room_idx is not None else None
        self._ctx_biome_idx = int(biome_index) if biome_index is not None else None

    @property
    def trial_phase(self) -> bool:
        """Biome 1 campaign rooms 1–4: onboarding; spawn tuning uses neutral adjustment."""
        if self._ctx_room_idx is None or self._ctx_biome_idx is None:
            return False
        return self._ctx_biome_idx == 1 and 1 <= self._ctx_room_idx <= 4

    def effective_enemy_adjustment(self) -> int:
        if self.trial_phase:
            return 0
        return int(self.enemy_adjustment)

    def update(self, player_state: PlayerStateClass | None) -> None:
        dr = self._params.director
        if player_state == PlayerStateClass.STRUGGLING:
            self.difficulty_modifier = float(dr.difficulty_modifier.struggling)
            self.enemy_adjustment = int(dr.enemy_adjustment.struggling)
            self.reinforcement_chance = float(dr.reinforcement_chance.struggling)
            self.reward_bias = "more_help"
            self.hazard_bias = "lower"
            self.composition_bias = "lighter"
            self.last_player_state_name = "STRUGGLING"
            self.pressure_level = "low"
            self.composition_bias_b2 = "lighter"
            r1 = self.reinforcement_chance
            self.reinforcement_chance_b2 = self._reinforcement_biome234(r1)
            self.hazard_tune_factor_b2 = 0.88
            self.composition_bias_b3 = "safe"
            self.ranged_bias_b3 = "low"
            self.reinforcement_chance_b3 = self._reinforcement_biome234(r1)
            self.hazard_tune_factor_b3 = 0.85
            self.composition_bias_b4 = "safe"
            self.boss_pressure = "low"
            self.pacing_bias = "relaxed"
            self.reinforcement_chance_b4 = self._reinforcement_biome234(r1)
            self.hazard_tune_factor_b4 = 0.85
        elif player_state == PlayerStateClass.DOMINATING:
            self.difficulty_modifier = float(dr.difficulty_modifier.dominating)
            self.enemy_adjustment = int(dr.enemy_adjustment.dominating)
            self.reinforcement_chance = float(dr.reinforcement_chance.dominating)
            self.reward_bias = "lower_help"
            self.hazard_bias = "higher"
            self.composition_bias = "harder"
            self.last_player_state_name = "DOMINATING"
            self.pressure_level = "high"
            self.composition_bias_b2 = "aggressive"
            r1 = self.reinforcement_chance
            self.reinforcement_chance_b2 = self._reinforcement_biome234(r1)
            self.hazard_tune_factor_b2 = 1.12
            self.composition_bias_b3 = "aggressive"
            self.ranged_bias_b3 = "high"
            self.reinforcement_chance_b3 = self._reinforcement_biome234(r1)
            self.hazard_tune_factor_b3 = 1.15
            self.composition_bias_b4 = "aggressive"
            self.boss_pressure = "high"
            self.pacing_bias = "intense"
            self.reinforcement_chance_b4 = self._reinforcement_biome234(r1)
            self.hazard_tune_factor_b4 = 1.15
        else:
            # STABLE or unknown / None
            self.difficulty_modifier = float(dr.difficulty_modifier.stable)
            self.enemy_adjustment = int(dr.enemy_adjustment.stable)
            self.reinforcement_chance = float(dr.reinforcement_chance.stable)
            self.reward_bias = "normal"
            self.hazard_bias = "normal"
            self.composition_bias = "normal"
            self.last_player_state_name = "STABLE" if player_state == PlayerStateClass.STABLE else None
            self.pressure_level = "medium"
            self.composition_bias_b2 = "balanced"
            r1 = self.reinforcement_chance
            self.reinforcement_chance_b2 = self._reinforcement_biome234(r1)
            self.hazard_tune_factor_b2 = 1.0
            self.composition_bias_b3 = "balanced"
            self.ranged_bias_b3 = "medium"
            self.reinforcement_chance_b3 = self._reinforcement_biome234(r1)
            self.hazard_tune_factor_b3 = 1.0
            self.composition_bias_b4 = "balanced"
            self.boss_pressure = "medium"
            self.pacing_bias = "normal"
            self.reinforcement_chance_b4 = self._reinforcement_biome234(r1)
            self.hazard_tune_factor_b4 = 1.0

    def capture_encounter_snapshot(self) -> EncounterDirectorSnapshot:
        """Copy current outputs for encounter spawn (call after room-end classify only)."""
        return EncounterDirectorSnapshot(
            difficulty_modifier=float(self.difficulty_modifier),
            enemy_adjustment=int(self.enemy_adjustment),
            reinforcement_chance=float(self.reinforcement_chance),
            composition_bias=str(self.composition_bias),
            last_player_state_name=self.last_player_state_name,
            pressure_level=str(self.pressure_level),
            composition_bias_b2=str(self.composition_bias_b2),
            reinforcement_chance_b2=float(self.reinforcement_chance_b2),
            hazard_tune_factor_b2=float(self.hazard_tune_factor_b2),
            composition_bias_b3=str(self.composition_bias_b3),
            ranged_bias_b3=str(self.ranged_bias_b3),
            reinforcement_chance_b3=float(self.reinforcement_chance_b3),
            hazard_tune_factor_b3=float(self.hazard_tune_factor_b3),
            composition_bias_b4=str(self.composition_bias_b4),
            boss_pressure=str(self.boss_pressure),
            pacing_bias=str(self.pacing_bias),
            reinforcement_chance_b4=float(self.reinforcement_chance_b4),
            hazard_tune_factor_b4=float(self.hazard_tune_factor_b4),
        )

    def get_debug_state(self) -> dict[str, Any]:
        return {
            "difficulty": self.difficulty_modifier,
            "enemy_adjustment": self.enemy_adjustment,
            "enemy_adjustment_effective": self.effective_enemy_adjustment(),
            "trial_phase": self.trial_phase,
            "reinforcement_chance": self.reinforcement_chance,
            "reward_bias": self.reward_bias,
            "hazard_bias": self.hazard_bias,
            "composition_bias": self.composition_bias,
            "player_state": self.last_player_state_name,
            "pressure_level": self.pressure_level,
            "composition_bias_b2": self.composition_bias_b2,
            "reinforcement_chance_b2": self.reinforcement_chance_b2,
            "hazard_tune_factor_b2": self.hazard_tune_factor_b2,
        }

    def get_biome1_debug(self) -> dict[str, Any]:
        """Compact Biome 1 AI Director inspection (prompt §10)."""
        return {
            "player_state": self.last_player_state_name,
            "difficulty_modifier": self.difficulty_modifier,
            "enemy_adjustment": self.enemy_adjustment,
            "reinforcement_chance": self.reinforcement_chance,
            "composition_bias": self.composition_bias,
            "reward_bias": self.reward_bias,
            "hazard_bias": self.hazard_bias,
        }

    def get_biome2_debug(self) -> dict[str, Any]:
        return {
            "player_state": self.last_player_state_name,
            "difficulty_modifier": self.difficulty_modifier,
            "enemy_adjustment": self.enemy_adjustment,
            "reinforcement_chance": self.reinforcement_chance_b2,
            "pressure_level": self.pressure_level,
            "composition_bias": self.composition_bias_b2,
            "hazard_tune_factor_b2": self.hazard_tune_factor_b2,
        }

    def get_biome3_debug(self) -> dict[str, Any]:
        return {
            "player_state": self.last_player_state_name,
            "difficulty_modifier": self.difficulty_modifier,
            "enemy_adjustment": self.enemy_adjustment,
            "reinforcement_chance": self.reinforcement_chance_b3,
            "pressure_level": self.pressure_level,
            "composition_bias": self.composition_bias_b3,
            "ranged_bias": self.ranged_bias_b3,
            "hazard_bias": self.hazard_tune_factor_b3,
        }

    def get_biome4_debug(self) -> dict[str, Any]:
        return {
            "player_state": self.last_player_state_name,
            "difficulty_modifier": self.difficulty_modifier,
            "enemy_adjustment": self.enemy_adjustment,
            "reinforcement_chance": self.reinforcement_chance_b4,
            "pressure_level": self.pressure_level,
            "composition_bias": self.composition_bias_b4,
            "boss_pressure": self.boss_pressure,
            "pacing_bias": self.pacing_bias,
            "hazard_tune_factor_b4": self.hazard_tune_factor_b4,
        }
