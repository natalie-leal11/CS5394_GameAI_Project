# Player state classification (Phase 2): deterministic rules from metrics summary + DifficultyParams.

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from game.ai.difficulty_params import DifficultyParams, DEFAULT_DIFFICULTY_PARAMS
from game.ai.metrics_tracker import MetricsTracker, RoomMetrics, RunMetrics


class PlayerStateClass(Enum):
    STRUGGLING = auto()
    STABLE = auto()
    DOMINATING = auto()


PlayerState = PlayerStateClass  # alias


@dataclass(frozen=True)
class PlayerModelSummaryInput:
    """Read-only snapshot of MetricsTracker fields used for classification."""

    hp_percent_current: float
    hp_percent_end_room: float
    hp_lost_in_room: float
    damage_taken_in_room: float
    room_clear_time: float
    rooms_cleared: int
    total_deaths: int
    total_damage_taken: float
    total_healing_received: float
    healing_wasted: float
    reward_collected_flag: bool
    last_3_rooms_hp_loss: tuple[float, ...]
    last_3_rooms_clear_time: tuple[float, ...]
    last_3_rooms_result: tuple[str, ...]
    recent_death_flag: bool
    struggling_rooms_count: int
    dominating_rooms_count: int


@dataclass(frozen=True)
class PlayerClassificationResult:
    """Outcome of PlayerModel.classify (read-only, for HUD / AI Director / debug)."""

    player_state: PlayerStateClass
    reasons: tuple[str, ...] = ()
    score_breakdown: dict[str, float] = field(default_factory=dict)
    struggle_score: float = 0.0
    dominate_score: float = 0.0


def build_player_model_summary(
    run: RunMetrics,
    *,
    hp_percent_current: float | None = None,
) -> PlayerModelSummaryInput:
    """
    Build summary from RunMetrics. Uses the most recently completed room in room_history
    for per-room fields when available; otherwise mirrored run fields.
    """
    hp_cur = float(hp_percent_current) if hp_percent_current is not None else float(run.hp_percent_current)

    end_hp = float(run.hp_percent_end_room)
    hp_lost = float(run.hp_lost_in_room)
    dmg_room = float(run.damage_taken_in_room)
    clear_t = float(run.room_clear_time)
    heal_waste = float(run.total_healing_wasted)
    if run.room_history:
        last: RoomMetrics = run.room_history[-1]
        end_hp = float(last.hp_percent_end_room)
        hp_lost = float(last.hp_lost_in_room)
        dmg_room = float(last.damage_taken_in_room)
        clear_t = float(last.room_clear_time)
        heal_waste = float(last.healing_wasted)

    return PlayerModelSummaryInput(
        hp_percent_current=hp_cur,
        hp_percent_end_room=end_hp,
        hp_lost_in_room=hp_lost,
        damage_taken_in_room=dmg_room,
        room_clear_time=clear_t,
        rooms_cleared=int(run.rooms_cleared),
        total_deaths=int(run.total_deaths),
        total_damage_taken=float(run.total_damage_taken),
        total_healing_received=float(run.total_healing_received),
        healing_wasted=heal_waste,
        reward_collected_flag=bool(run.reward_collected_flag),
        last_3_rooms_hp_loss=tuple(float(x) for x in run.last_3_rooms_hp_loss),
        last_3_rooms_clear_time=tuple(float(x) for x in run.last_3_rooms_clear_time),
        last_3_rooms_result=tuple(str(x) for x in run.last_3_rooms_result),
        recent_death_flag=bool(run.recent_death_flag),
        struggling_rooms_count=int(run.struggling_rooms_count),
        dominating_rooms_count=int(run.dominating_rooms_count),
    )


class PlayerModel:
    """Maps metrics summary + difficulty params → high-level player state (deterministic)."""

    def __init__(self, params: DifficultyParams | None = None) -> None:
        self._params = params or DEFAULT_DIFFICULTY_PARAMS
        self.player_state: PlayerStateClass | None = None

    def classify(self, summary: PlayerModelSummaryInput) -> PlayerClassificationResult:
        """
        Weighted deterministic classification (see difficulty_params PlayerModel v2 + design table).

        - Sums struggle / dominate signal weights from MetricsTracker-backed inputs.
        - First `player_model_early_rooms_stable_count` cleared rooms → STABLE unless
          `recent_death_flag` (obvious struggle).
        - STRUGGLING / DOMINATING use `player_model_weighted_min_score` and
          `player_model_weighted_preference_margin`.
        - DOMINATING also requires `d_performance_gate` (mostly_clean_clear OR
          low_damage_and_loss OR fast_recent_clears).
        """
        p = self._params
        rc = max(0, summary.rooms_cleared)
        denom = max(1, rc)
        heal_denom = max(1.0, float(rc))

        scores: dict[str, float] = {}
        s_labels: list[str] = []
        d_labels: list[str] = []

        th_hp = p.player_model_struggling_hp_percent
        l3 = summary.last_3_rooms_result
        recent_death_signal = summary.recent_death_flag or (len(l3) > 0 and l3[-1] == "death")
        s_recent_death = recent_death_signal
        s_low_hp = (summary.hp_percent_current < th_hp) or (summary.hp_percent_end_room < th_hp)
        bad_nd = sum(1 for r in l3 if r in ("near_death", "death"))
        s_repeated_bad = bad_nd >= p.player_model_repeated_bad_results_min

        if summary.last_3_rooms_hp_loss:
            avg_hp_loss = sum(summary.last_3_rooms_hp_loss) / float(len(summary.last_3_rooms_hp_loss))
        else:
            avg_hp_loss = float(summary.hp_lost_in_room)
        s_high_avg_loss = avg_hp_loss > p.player_model_recent_avg_hp_loss_struggling

        sr_ratio = float(summary.struggling_rooms_count) / float(denom)
        s_struggling_ratio = (
            rc >= p.player_model_min_rooms_for_ratio
            and sr_ratio >= p.player_model_struggling_share_threshold
        )

        heal_per_room = summary.total_healing_received / heal_denom
        s_high_heal = rc >= 1 and heal_per_room > p.player_model_healing_per_room_struggling_threshold

        struggle = 0.0
        if s_recent_death:
            w = p.player_model_w_s_recent_death
            struggle += w
            scores["w_s_recent_death"] = w
            s_labels.append("recent_death")
        if s_low_hp:
            w = p.player_model_w_s_low_hp
            struggle += w
            scores["w_s_low_hp"] = w
            s_labels.append("low_hp")
        if s_repeated_bad:
            w = p.player_model_w_s_repeated_near_death_or_death
            struggle += w
            scores["w_s_repeated_near_death_or_death"] = w
            s_labels.append("repeated_near_death_or_death")
        if s_high_avg_loss:
            w = p.player_model_w_s_high_recent_avg_hp_loss
            struggle += w
            scores["w_s_high_recent_avg_hp_loss"] = w
            s_labels.append("high_recent_avg_hp_loss")
        if s_struggling_ratio:
            w = p.player_model_w_s_struggling_rooms_share
            struggle += w
            scores["w_s_struggling_rooms_share"] = w
            s_labels.append("struggling_rooms_share")
        if s_high_heal:
            w = p.player_model_w_s_high_healing_per_room
            struggle += w
            scores["w_s_high_healing_per_room"] = w
            s_labels.append("high_healing_per_room")

        # --- Dominate signals (meaningful subset) ---
        d_no_recent_death = not recent_death_signal
        hi = p.player_model_high_hp_percent
        d_hp_comfort = (summary.hp_percent_current >= hi) and (summary.hp_percent_end_room >= hi)

        clean_n = sum(1 for r in l3 if r == "clean_clear")
        d_mostly_clean = len(l3) >= 2 and clean_n >= p.player_model_clean_clear_majority_min

        if summary.last_3_rooms_hp_loss:
            avg_loss_d = sum(summary.last_3_rooms_hp_loss) / float(len(summary.last_3_rooms_hp_loss))
        else:
            avg_loss_d = float(summary.hp_lost_in_room)
        low_loss = avg_loss_d <= p.player_model_recent_avg_hp_loss_dominating
        low_dmg = summary.damage_taken_in_room <= p.player_model_damage_taken_low_threshold
        d_low_damage_and_loss = low_dmg and low_loss

        d_fast = False
        if summary.last_3_rooms_clear_time and len(summary.last_3_rooms_clear_time) >= 2:
            avg_ct = sum(summary.last_3_rooms_clear_time) / float(len(summary.last_3_rooms_clear_time))
            d_fast = avg_ct <= p.player_model_fast_clear_avg_seconds

        dr_ratio = float(summary.dominating_rooms_count) / float(denom)
        d_dom_ratio = rc >= p.player_model_min_rooms_for_ratio and dr_ratio >= p.player_model_dominating_share_threshold

        dominate = 0.0
        if d_no_recent_death:
            w = p.player_model_w_d_no_recent_death
            dominate += w
            scores["w_d_no_recent_death"] = w
            d_labels.append("no_recent_death")
        if d_hp_comfort:
            w = p.player_model_w_d_hp_comfortable
            dominate += w
            scores["w_d_hp_comfortable"] = w
            d_labels.append("hp_comfortable")
        if d_mostly_clean:
            w = p.player_model_w_d_mostly_clean_clear
            dominate += w
            scores["w_d_mostly_clean_clear"] = w
            d_labels.append("mostly_clean_clear")
        if d_low_damage_and_loss:
            w = p.player_model_w_d_low_damage_and_loss
            dominate += w
            scores["w_d_low_damage_and_loss"] = w
            d_labels.append("low_damage_and_low_hp_loss")
        if d_fast:
            w = p.player_model_w_d_fast_recent_clears
            dominate += w
            scores["w_d_fast_recent_clears"] = w
            d_labels.append("fast_recent_clears")
        if d_dom_ratio:
            w = p.player_model_w_d_dominating_rooms_share
            dominate += w
            scores["w_d_dominating_rooms_share"] = w
            d_labels.append("dominating_rooms_share")

        scores["struggle_weighted"] = struggle
        scores["dominate_weighted"] = dominate

        # At least one "performance" signal — required for DOMINATING (avoids false positives)
        performance_gate = bool(d_mostly_clean or d_low_damage_and_loss or d_fast)
        scores["d_performance_gate"] = 1.0 if performance_gate else 0.0

        min_score = p.player_model_weighted_min_score
        margin = p.player_model_weighted_preference_margin

        state = PlayerStateClass.STABLE
        decision = "decision:stable"

        early_n = p.player_model_early_rooms_stable_count
        if rc < early_n and not summary.recent_death_flag:
            decision = "decision:stable_early_run"
            compact = ("early_run_protection", decision, f"s={struggle:.2f}", f"d={dominate:.2f}")
        else:
            # STRUGGLING: struggle ≥ min and (dominate < min or struggle − dominate ≥ margin)
            struggle_ok = struggle >= min_score and (
                dominate < min_score or (struggle - dominate) >= margin
            )
            # DOMINATING: dominate ≥ min and performance gate and (struggle < min or dominate − struggle ≥ margin)
            dominate_ok = (
                dominate >= min_score
                and performance_gate
                and (struggle < min_score or (dominate - struggle) >= margin)
            )
            if struggle_ok and dominate_ok:
                state = PlayerStateClass.STABLE
                decision = "decision:stable_mixed_evidence"
                compact = (
                    f"s={struggle:.2f}",
                    f"d={dominate:.2f}",
                    "performance_gate=" + str(performance_gate),
                    decision,
                )
            elif struggle_ok:
                state = PlayerStateClass.STRUGGLING
                decision = "decision:struggling"
                compact = tuple(s_labels[-12:] + [decision])
            elif dominate_ok:
                state = PlayerStateClass.DOMINATING
                decision = "decision:dominating"
                compact = tuple(d_labels[-12:] + [decision])
            else:
                compact = (
                    f"s={struggle:.2f}",
                    f"d={dominate:.2f}",
                    decision,
                )

        result = PlayerClassificationResult(
            player_state=state,
            reasons=compact,
            score_breakdown=dict(scores),
            struggle_score=struggle,
            dominate_score=dominate,
        )
        self.player_state = result.player_state
        return result

    def get_state(self) -> str | None:
        """STRUGGLING / STABLE / DOMINATING, or None before first classify."""
        s = self.player_state
        if s is None:
            return None
        return s.name

    def classify_from_metrics(
        self,
        metrics: MetricsTracker,
        *,
        hp_percent_current: float | None = None,
    ) -> PlayerClassificationResult:
        """Convenience: build summary from tracker and classify."""
        return self.classify(build_player_model_summary(metrics.run, hp_percent_current=hp_percent_current))
