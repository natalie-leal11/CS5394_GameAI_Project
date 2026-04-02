# Player state classification: deterministic percentage rules from MetricsTracker summary + DifficultyParams.

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
    # 3-life run: tier + post-respawn signal (GameScene); life phase caps visible state.
    life_index: int = 0
    recent_life_loss_flag: bool = False


@dataclass(frozen=True)
class PlayerClassificationResult:
    """Outcome of PlayerModel.classify (read-only, for HUD / AI Director / debug)."""

    player_state: PlayerStateClass
    reasons: tuple[str, ...] = ()
    score_breakdown: dict[str, float] = field(default_factory=dict)
    struggle_score: float = 0.0
    dominate_score: float = 0.0


def _avg_hp_loss_last3(summary: PlayerModelSummaryInput) -> float:
    """Average HP percent lost over recorded last-3 rooms; fallback to current room loss if empty."""
    if summary.last_3_rooms_hp_loss:
        xs = summary.last_3_rooms_hp_loss
        return sum(xs) / float(len(xs))
    return float(summary.hp_lost_in_room)


def build_player_model_summary(
    run: RunMetrics,
    *,
    hp_percent_current: float | None = None,
    life_index: int = 0,
    recent_life_loss_flag: bool = False,
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
        life_index=int(life_index),
        recent_life_loss_flag=bool(recent_life_loss_flag),
    )


class PlayerModel:
    """Maps metrics summary + difficulty params → high-level player state (deterministic, v3 percentage rules)."""

    def __init__(self, params: DifficultyParams | None = None) -> None:
        self._params = params or DEFAULT_DIFFICULTY_PARAMS
        self.player_state: PlayerStateClass | None = None

    def classify(self, summary: PlayerModelSummaryInput) -> PlayerClassificationResult:
        """
        Percentage-based deterministic classification (single-life run).

        Priority (first match wins):
        1) STRUGGLING if:
           (hp_percent_current <= struggling_hp_critical) OR (recent death in last room)
           OR (at least 2 of: hp <= struggling_hp_weak, bad rooms in last 3 >= min,
               average HP loss last 3 rooms >= struggling_avg_hp_loss_min).
           Bad room = near_death or death.

        2) Else DOMINATING if:
           (hp_percent_current >= dominating_hp_min AND no recent death)
           AND (at least two of: clean_clear count in last 3 >= min,
                average HP loss last 3 <= dominating_avg_hp_loss_max,
                fast recent clears: rolling avg clear time <= fast_clear_avg_seconds when len >= 2).

        3) Else STABLE.
        """
        p = self._params
        l3 = summary.last_3_rooms_result
        recent_death = bool(summary.recent_death_flag) or (len(l3) > 0 and l3[-1] == "death")

        hp_cur = float(summary.hp_percent_current)
        avg_hp_loss = _avg_hp_loss_last3(summary)

        bad_count = sum(1 for r in l3 if r in ("near_death", "death"))
        weak_hp = hp_cur <= p.player_model_struggling_hp_weak_percent
        weak_bad_rooms = bad_count >= p.player_model_struggling_bad_rooms_min
        weak_avg_loss = avg_hp_loss >= p.player_model_struggling_avg_hp_loss_min
        weak_signal_count = int(weak_hp) + int(weak_bad_rooms) + int(weak_avg_loss)

        struggle_critical = hp_cur <= p.player_model_struggling_hp_critical_percent
        struggle_from_two_weak = weak_signal_count >= 2
        struggling = bool(struggle_critical or recent_death or struggle_from_two_weak)

        clean_n = sum(1 for r in l3 if r == "clean_clear")
        strong_clean = clean_n >= p.player_model_dominating_clean_clears_min
        strong_low_avg_loss = avg_hp_loss <= p.player_model_dominating_avg_hp_loss_max_percent

        fast_recent = False
        ct = summary.last_3_rooms_clear_time
        if ct and len(ct) >= 2:
            avg_ct = sum(ct) / float(len(ct))
            fast_recent = avg_ct <= p.player_model_fast_clear_avg_seconds

        strong_signals: list[bool] = [strong_clean, strong_low_avg_loss, fast_recent]
        strong_signal_count = int(sum(1 for s in strong_signals if s))
        strong_performance_met = strong_signal_count >= 2
        baseline_dom = (hp_cur >= p.player_model_dominating_hp_min_percent) and (not recent_death)
        dominating = bool((not struggling) and baseline_dom and strong_performance_met)

        if struggling:
            state = PlayerStateClass.STRUGGLING
            decision = "decision:struggling"
        elif dominating:
            state = PlayerStateClass.DOMINATING
            decision = "decision:dominating"
        else:
            state = PlayerStateClass.STABLE
            decision = "decision:stable"

        reasons: list[str] = [decision]
        if struggling:
            if struggle_critical:
                reasons.append("hp<=critical")
            if recent_death:
                reasons.append("recent_death")
            if struggle_from_two_weak:
                reasons.append(f"weak_signals_{weak_signal_count}")
        elif dominating:
            if strong_clean:
                reasons.append("clean_clears")
            if strong_low_avg_loss:
                reasons.append("low_avg_hp_loss")
            if fast_recent:
                reasons.append("fast_recent_clears")

        scores: dict[str, float] = {
            "struggle_critical": 1.0 if struggle_critical else 0.0,
            "recent_death": 1.0 if recent_death else 0.0,
            "weak_hp": 1.0 if weak_hp else 0.0,
            "weak_bad_rooms": 1.0 if weak_bad_rooms else 0.0,
            "weak_avg_loss": 1.0 if weak_avg_loss else 0.0,
            "weak_signal_count": float(weak_signal_count),
            "struggle_from_two_weak": 1.0 if struggle_from_two_weak else 0.0,
            "avg_hp_loss_last3": avg_hp_loss,
            "baseline_dom_hp": 1.0 if (hp_cur >= p.player_model_dominating_hp_min_percent) else 0.0,
            "strong_clean": 1.0 if strong_clean else 0.0,
            "strong_low_avg_loss": 1.0 if strong_low_avg_loss else 0.0,
            "fast_recent_clears": 1.0 if fast_recent else 0.0,
            "strong_signal_count": float(strong_signal_count),
            "strong_performance_met": 1.0 if strong_performance_met else 0.0,
        }

        final_state = self._life_phase_visible_state(summary)
        scores["base_v3_state"] = float(
            {"STRUGGLING": 0.0, "STABLE": 1.0, "DOMINATING": 2.0}.get(state.name, -1.0)
        )
        scores["life_phase_state"] = float(
            {"STRUGGLING": 0.0, "STABLE": 1.0, "DOMINATING": 2.0}.get(final_state.name, -1.0)
        )
        if final_state != state:
            reasons.append(f"life_phase_override:{final_state.name}(base_v3={state.name})")
        else:
            reasons.append(f"life_phase:{final_state.name}")

        result = PlayerClassificationResult(
            player_state=final_state,
            reasons=tuple(reasons),
            score_breakdown=scores,
            struggle_score=1.0 if final_state == PlayerStateClass.STRUGGLING else 0.0,
            dominate_score=1.0 if final_state == PlayerStateClass.DOMINATING else 0.0,
        )
        self.player_state = result.player_state
        return result

    def _life_phase_visible_state(self, summary: PlayerModelSummaryInput) -> PlayerStateClass:
        """
        Final visible state from life_index + HP (+ post-life-loss flag on Life 2).
        Overrides base v3 classification for HUD / AI Director. life_index: 0 = first life, 1 = second, 2 = last.
        """
        p = self._params
        hp = float(summary.hp_percent_current)
        li = int(summary.life_index)
        if li >= 2:
            return PlayerStateClass.STRUGGLING
        if li == 1:
            if summary.recent_life_loss_flag:
                return PlayerStateClass.STRUGGLING
            if hp >= p.player_model_life2_stable_min_hp_percent:
                return PlayerStateClass.STABLE
            return PlayerStateClass.STRUGGLING
        if hp >= p.player_model_life1_dominating_min_hp_percent:
            return PlayerStateClass.DOMINATING
        if hp >= p.player_model_life1_stable_min_hp_percent:
            return PlayerStateClass.STABLE
        return PlayerStateClass.STRUGGLING

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
