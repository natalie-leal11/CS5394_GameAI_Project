"""
Deterministic offline reward evaluation for exported RL datasets.

**Inputs:** CSV or JSONL produced by :mod:`game.rl.dataset_export`. Read-only.

**Missing-data policy**
-----------------------

Rows are **not** coerced to zero. Each metric uses only rows where **all required
fields are present and parseable**. Missing optional fields skip that row for that
metric; counts appear in :attr:`RewardBreakdown.valid_rows_used_by_metric` and
:attr:`RewardBreakdown.skipped_rows_by_metric`. Warnings are appended to
:attr:`RewardBreakdown.missing_field_warnings`.

**Win rate:** requires non-empty ``final_outcome``. Rows with missing/blank outcome
are skipped. Decisive runs are those with ``final_outcome`` in ``{victory, defeat}``
(case-insensitive). If **every** run row lacks a usable outcome but ``run_rows`` is
non-empty, :class:`InsufficientDataError` is raised.

**Early biome penalty:** requires ``biome_index``, ``damage_taken``,
``min_hp_during_room``, ``room_result``. Rows must satisfy ``biome_index <= early_biome_max``.

**Late triviality:** gate requires ``biome_index``, ``room_index``. Classification
requires ``enemy_count``, ``damage_taken``, ``room_clear_time`` on rows that pass
the gate.

**Spike:** each endpoint of a consecutive pair must have ``run_id`` (optional blank
→ ``_unknown``), ``room_index``, ``difficulty_modifier``, ``enemy_adjustment``.
``source_row_index`` defaults to ``0`` if missing for sorting only.

**Win rate score when no decisive runs:** ``win_rate_score`` is **not** computed from
the band; it is set to ``0.0`` and :attr:`RewardBreakdown.win_rate_band_applied` is
``False``.

**Late-game triviality thresholds**
-----------------------------------

- **fixed** (default): a late room is *trivial* iff ``enemy_count <= late_trivial_enemy_max``
  AND ``damage_taken <= late_trivial_damage_max`` AND ``room_clear_time <= late_trivial_clear_time_max``.

- **percentile**: over late rooms with a **complete** triple of metrics, compute
  deterministic quantiles::

      T_e = quantile(sorted(enemy_counts), p_e)
      T_d = quantile(sorted(damages), p_d)
      T_t = quantile(sorted(clear_times), p_t)

  with ``quantile(sorted_v, p) = sorted_v[floor((n-1) * clamp(p,0,1))]`` for ``n >= 1``.
  A room is *trivial* iff ``enemy_count <= T_e`` AND ``damage_taken <= T_d`` AND
  ``room_clear_time <= T_t``.

  If ``late_triviality_mode == "percentile"`` and there is **no** late room with a
  complete triple, :class:`InsufficientDataError` is raised (cannot define thresholds).

Formulas (unchanged where applicable)
-------------------------------------

See previous revision for ``win_rate_score`` (when decisive ≥ 1), early stress blend,
``overall_reward`` linear combination.

Assumptions
-----------

- Column names match :mod:`game.rl.dataset_export`.
- ``final_outcome`` values are as logged by the game.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from game.rl.offline_tuning_spec import CandidateEvaluationParams, default_candidate


class InsufficientDataError(ValueError):
    """Dataset cannot support a required metric (e.g. all outcomes missing; percentile cohort empty)."""


def _is_missing(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and v.strip() == "":
        return True
    return False


def _parse_float_required(v: Any) -> float | None:
    if _is_missing(v):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _parse_int_required(v: Any) -> int | None:
    if _is_missing(v):
        return None
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def _parse_outcome(v: Any) -> str | None:
    if _is_missing(v):
        return None
    return str(v).strip().lower()


def _decisive_outcomes() -> frozenset[str]:
    return frozenset({"victory", "defeat"})


def _deterministic_quantile(sorted_vals: list[float], p: float) -> float:
    """Lower-index quantile on sorted values, deterministic."""
    if not sorted_vals:
        raise ValueError("quantile of empty list")
    p = max(0.0, min(1.0, float(p)))
    n = len(sorted_vals)
    k = int((n - 1) * p)
    return sorted_vals[k]


def _clip(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def win_rate_score_value(w: float, p: CandidateEvaluationParams) -> float:
    a = p.win_band.lo
    b = p.win_band.hi
    if a <= w <= b:
        return 1.0
    if w < a:
        return max(0.0, min(1.0, w / a))
    return max(0.0, min(1.0, (1.0 - w) / max(1e-9, (1.0 - b))))


def load_room_dataset(path: Path) -> list[dict[str, Any]]:
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    suf = path.suffix.lower()
    if suf == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as f:
            r = csv.DictReader(f)
            return [dict(row) for row in r]
    if suf == ".jsonl":
        rows: list[dict[str, Any]] = []
        with path.open(encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))
        return rows
    raise ValueError(f"Unsupported room dataset format: {path} (use .csv or .jsonl)")


def load_run_dataset(path: Path) -> list[dict[str, Any]]:
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    suf = path.suffix.lower()
    if suf == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as f:
            r = csv.DictReader(f)
            return [dict(row) for row in r]
    if suf == ".jsonl":
        rows: list[dict[str, Any]] = []
        with path.open(encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))
        return rows
    raise ValueError(f"Unsupported run dataset format: {path} (use .csv or .jsonl)")


def _metric_win_rate(
    run_rows: list[dict[str, Any]],
) -> tuple[float, int, int, int, int, int, bool]:
    """
    Returns:
        w, wins, decisive, total_runs, valid_outcome_rows, skipped_missing_outcome, band_applicable
    """
    total = len(run_rows)
    skipped = 0
    decisive = 0
    wins = 0
    valid = 0
    for row in run_rows:
        fo = _parse_outcome(row.get("final_outcome"))
        if fo is None:
            skipped += 1
            continue
        valid += 1
        if fo in _decisive_outcomes():
            decisive += 1
            if fo == "victory":
                wins += 1
    if total > 0 and valid == 0:
        raise InsufficientDataError(
            "win_rate: every run row has missing or blank final_outcome; cannot evaluate."
        )
    band_applicable = decisive >= 1
    if not band_applicable:
        return 0.0, wins, decisive, total, valid, skipped, False
    w = wins / decisive
    return w, wins, decisive, total, valid, skipped, True


def _metric_early_biome(
    room_rows: list[dict[str, Any]], p: CandidateEvaluationParams
) -> tuple[float, int, int, int]:
    """Returns penalty, valid_early_rows, skipped_ineligible_biome, skipped_missing_fields."""
    ref = max(p.early_damage_ref, 1e-6)
    vals: list[float] = []
    skip_bio = 0
    skip_missing = 0
    for row in room_rows:
        bio = _parse_int_required(row.get("biome_index"))
        if bio is None:
            skip_missing += 1
            continue
        if bio > p.early_biome_max:
            skip_bio += 1
            continue
        dmg = _parse_float_required(row.get("damage_taken"))
        min_hp = _parse_float_required(row.get("min_hp_during_room"))
        rr_raw = row.get("room_result")
        if dmg is None or min_hp is None or _is_missing(rr_raw):
            skip_missing += 1
            continue
        rr = str(rr_raw).strip().lower()
        dmg_norm = _clip(dmg / ref, 0.0, 1.0)
        hp_stress = _clip((100.0 - min_hp) / 100.0, 0.0, 1.0)
        death = 1.0 if rr == "death" else 0.0
        f = _clip(0.45 * dmg_norm + 0.45 * hp_stress + 0.1 * death, 0.0, 1.0)
        vals.append(f)
    if not vals:
        return 0.0, 0, skip_bio, skip_missing
    return sum(vals) / len(vals), len(vals), skip_bio, skip_missing


def _late_gate_rows(room_rows: list[dict[str, Any]], p: CandidateEvaluationParams) -> tuple[list[dict[str, Any]], int, int]:
    """Late-eligible rows (gate only); returns (rows, skipped_missing_gate_fields)."""
    late: list[dict[str, Any]] = []
    skip = 0
    for row in room_rows:
        bio = _parse_int_required(row.get("biome_index"))
        ri = _parse_int_required(row.get("room_index"))
        if bio is None or ri is None:
            skip += 1
            continue
        if bio >= p.late_biome_min and ri >= p.late_room_index_min:
            late.append(row)
    return late, skip


def _metric_late_triviality(
    room_rows: list[dict[str, Any]], p: CandidateEvaluationParams
) -> tuple[float, int, int, int, int, dict[str, Any]]:
    """
    Returns:
        penalty, late_complete_rows, trivial_count, gate_skip_missing,
        triple_skip_within_late, triviality_thresholds_used
    """
    late, gate_skip = _late_gate_rows(room_rows, p)
    thresholds: dict[str, Any] = {"mode": p.late_triviality_mode}

    complete: list[tuple[dict[str, Any], int, float, float]] = []
    triple_skip = 0
    for row in late:
        ec = _parse_int_required(row.get("enemy_count"))
        dmg = _parse_float_required(row.get("damage_taken"))
        ct = _parse_float_required(row.get("room_clear_time"))
        if ec is None or dmg is None or ct is None:
            triple_skip += 1
            continue
        complete.append((row, ec, dmg, ct))

    if p.late_triviality_mode == "percentile":
        if not complete:
            raise InsufficientDataError(
                "late_triviality (percentile): no late-room rows with complete "
                "enemy_count, damage_taken, and room_clear_time; cannot compute quantile thresholds."
            )
        ecs = sorted(x[1] for x in complete)
        dmgs = sorted(x[2] for x in complete)
        cts = sorted(x[3] for x in complete)
        te = _deterministic_quantile([float(x) for x in ecs], p.late_trivial_percentile_enemy)
        td = _deterministic_quantile(dmgs, p.late_trivial_percentile_damage)
        tt = _deterministic_quantile(cts, p.late_trivial_percentile_clear_time)
        thresholds.update(
            {
                "enemy_threshold": te,
                "damage_threshold": td,
                "clear_time_threshold": tt,
                "percentile_enemy": p.late_trivial_percentile_enemy,
                "percentile_damage": p.late_trivial_percentile_damage,
                "percentile_clear_time": p.late_trivial_percentile_clear_time,
                "cohort_size": len(complete),
            }
        )
        trivial = 0
        for _row, ec, dmg, ct in complete:
            if ec <= te and dmg <= td and ct <= tt:
                trivial += 1
        pen = trivial / len(complete)
        return pen, len(complete), trivial, gate_skip, triple_skip, thresholds

    # fixed
    thresholds.update(
        {
            "enemy_max": p.late_trivial_enemy_max,
            "damage_max": p.late_trivial_damage_max,
            "clear_time_max": p.late_trivial_clear_time_max,
        }
    )
    if not complete:
        return 0.0, 0, 0, gate_skip, triple_skip, thresholds
    trivial = 0
    for _row, ec, dmg, ct in complete:
        if ec <= p.late_trivial_enemy_max and dmg <= p.late_trivial_damage_max and ct <= p.late_trivial_clear_time_max:
            trivial += 1
    pen = trivial / len(complete)
    return pen, len(complete), trivial, gate_skip, triple_skip, thresholds


def _metric_spike(
    room_rows: list[dict[str, Any]], p: CandidateEvaluationParams
) -> tuple[float, int, int, int, int]:
    """Returns penalty, transitions, spikes, skipped_rows_missing_fields, skipped_transitions."""
    by_run: dict[str, list[dict[str, Any]]] = {}
    row_skip = 0
    for row in room_rows:
        rid_raw = row.get("run_id")
        rid = "_unknown" if _is_missing(rid_raw) else str(rid_raw).strip() or "_unknown"
        ri = _parse_int_required(row.get("room_index"))
        dm = _parse_float_required(row.get("difficulty_modifier"))
        adj = _parse_int_required(row.get("enemy_adjustment"))
        if ri is None or dm is None or adj is None:
            row_skip += 1
            continue
        by_run.setdefault(rid, []).append(row)

    transitions = 0
    spikes = 0
    trans_skipped = 0
    dd_thr = p.spike_difficulty_delta
    de_thr = p.spike_enemy_adjust_delta

    for _rid, rows in by_run.items():
        rows.sort(
            key=lambda r: (
                _parse_int_required(r.get("room_index")) or 0,
                _parse_int_required(r.get("source_row_index")) or 0,
            )
        )
        for i in range(len(rows) - 1):
            a, b = rows[i], rows[i + 1]
            a_dm = _parse_float_required(a.get("difficulty_modifier"))
            b_dm = _parse_float_required(b.get("difficulty_modifier"))
            a_adj = _parse_int_required(a.get("enemy_adjustment"))
            b_adj = _parse_int_required(b.get("enemy_adjustment"))
            if a_dm is None or b_dm is None or a_adj is None or b_adj is None:
                trans_skipped += 1
                continue
            transitions += 1
            if abs(b_dm - a_dm) > dd_thr or abs(b_adj - a_adj) > de_thr:
                spikes += 1
    if transitions == 0:
        return 0.0, 0, 0, row_skip, trans_skipped
    return min(1.0, spikes / transitions), transitions, spikes, row_skip, trans_skipped


@dataclass
class RewardBreakdown:
    """All metrics returned by :func:`evaluate_offline_reward`."""

    overall_reward: float
    win_rate_score: float
    early_biome_penalty: float
    late_game_triviality_penalty: float
    difficulty_spike_penalty: float

    empirical_win_rate: float
    decisive_runs: int
    wins: int
    total_runs: int
    win_rate_band_applied: bool

    early_rooms_used: int
    late_rooms_used: int
    late_trivial_rooms: int
    spike_transitions: int
    spike_count: int

    skipped_rows_by_metric: dict[str, int] = field(default_factory=dict)
    valid_rows_used_by_metric: dict[str, int] = field(default_factory=dict)
    missing_field_warnings: list[str] = field(default_factory=list)
    triviality_thresholds_used: dict[str, Any] = field(default_factory=dict)

    notes: list[str] = field(default_factory=list)

    def metrics_dict(self) -> dict[str, Any]:
        d = {
            "overall_reward": self.overall_reward,
            "win_rate_score": self.win_rate_score,
            "early_biome_penalty": self.early_biome_penalty,
            "late_game_triviality_penalty": self.late_game_triviality_penalty,
            "difficulty_spike_penalty": self.difficulty_spike_penalty,
            "empirical_win_rate": self.empirical_win_rate,
            "decisive_runs": self.decisive_runs,
            "wins": self.wins,
            "total_runs": self.total_runs,
            "win_rate_band_applied": self.win_rate_band_applied,
            "early_rooms_used": self.early_rooms_used,
            "late_rooms_used": self.late_rooms_used,
            "late_trivial_rooms": self.late_trivial_rooms,
            "spike_transitions": self.spike_transitions,
            "spike_count": self.spike_count,
            "skipped_rows_by_metric": dict(self.skipped_rows_by_metric),
            "valid_rows_used_by_metric": dict(self.valid_rows_used_by_metric),
            "missing_field_warnings": list(self.missing_field_warnings),
            "triviality_thresholds_used": dict(self.triviality_thresholds_used),
            "notes": list(self.notes),
        }
        return d


def evaluate_offline_reward(
    room_rows: list[dict[str, Any]],
    run_rows: list[dict[str, Any]],
    params: CandidateEvaluationParams | None = None,
) -> RewardBreakdown:
    p = params or default_candidate()
    notes: list[str] = []
    mwarn: list[str] = []
    skipped: dict[str, int] = {}
    valid_used: dict[str, int] = {}

    # Win rate (requires run_rows)
    if not run_rows:
        w = 0.0
        wins = decisive = total = valid = sk_out = 0
        wr_score = 0.0
        band_ok = False
        notes.append("No run-level rows; win_rate metrics are vacuous.")
        skipped["win_rate"] = 0
        valid_used["win_rate"] = 0
    else:
        w, wins, decisive, total, valid, sk_out, band_ok = _metric_win_rate(run_rows)
        skipped["win_rate"] = sk_out
        valid_used["win_rate"] = valid
        if sk_out:
            mwarn.append(f"win_rate: skipped {sk_out} run row(s) with missing/blank final_outcome.")
        if band_ok:
            wr_score = win_rate_score_value(w, p)
        else:
            wr_score = 0.0
            if total > 0:
                mwarn.append(
                    "win_rate: no decisive runs (victory/defeat); win_rate_score set to 0, band not applied."
                )

    if not room_rows:
        notes.append("No room-level rows; early/late/spike penalties are 0.")
        early_pen = 0.0
        early_n = skip_bio = skip_em = 0
        late_pen = 0.0
        late_n = late_triv = gate_sk = trip_sk = 0
        thr_used: dict[str, Any] = {"mode": p.late_triviality_mode}
        spike_pen = 0.0
        spike_tr = spike_c = sp_row = sp_tr = 0
        skipped["early_biome_missing_or_incomplete"] = 0
        skipped["early_biome_ineligible_biome"] = 0
        skipped["late_triviality_gate"] = 0
        skipped["late_triviality_triple"] = 0
        skipped["spike_row"] = 0
        skipped["spike_transition"] = 0
        valid_used["early_biome"] = 0
        valid_used["late_triviality"] = 0
        valid_used["spike_transition"] = 0
    else:
        early_pen, early_n, skip_bio, skip_em = _metric_early_biome(room_rows, p)
        skipped["early_biome_missing_or_incomplete"] = skip_em
        skipped["early_biome_ineligible_biome"] = skip_bio
        valid_used["early_biome"] = early_n
        if skip_em:
            mwarn.append(
                f"early_biome: skipped {skip_em} room row(s) missing biome_index or stress fields."
            )

        late_pen, late_n, late_triv, gate_sk, trip_sk, thr_used = _metric_late_triviality(room_rows, p)
        skipped["late_triviality_gate"] = gate_sk
        skipped["late_triviality_triple"] = trip_sk
        valid_used["late_triviality"] = late_n
        if gate_sk:
            mwarn.append(f"late_triviality: {gate_sk} room row(s) missing biome_index or room_index.")
        if trip_sk:
            mwarn.append(
                f"late_triviality: {trip_sk} late-gate room(s) missing enemy_count, damage_taken, or room_clear_time."
            )

        spike_pen, spike_tr, spike_c, sp_row, sp_tr = _metric_spike(room_rows, p)
        skipped["spike_row"] = sp_row
        skipped["spike_transition"] = sp_tr
        valid_used["spike_transition"] = spike_tr
        if sp_row:
            mwarn.append(f"spike: skipped {sp_row} room row(s) missing room_index, difficulty_modifier, or enemy_adjustment.")
        if sp_tr:
            mwarn.append(f"spike: skipped {sp_tr} transition(s) with incomplete endpoint fields.")

    wg = p.weights
    overall = (
        wg.win_rate * wr_score
        - wg.early_penalty * early_pen
        - wg.late_penalty * late_pen
        - wg.spike_penalty * spike_pen
    )

    return RewardBreakdown(
        overall_reward=overall,
        win_rate_score=wr_score,
        early_biome_penalty=early_pen,
        late_game_triviality_penalty=late_pen,
        difficulty_spike_penalty=spike_pen,
        empirical_win_rate=w,
        decisive_runs=decisive,
        wins=wins,
        total_runs=total if run_rows else 0,
        win_rate_band_applied=band_ok if run_rows else False,
        early_rooms_used=early_n,
        late_rooms_used=late_n,
        late_trivial_rooms=late_triv,
        spike_transitions=spike_tr,
        spike_count=spike_c,
        skipped_rows_by_metric=skipped,
        valid_rows_used_by_metric=valid_used,
        missing_field_warnings=mwarn,
        triviality_thresholds_used=thr_used,
        notes=notes,
    )


def evaluate_from_paths(
    room_path: Path | None,
    run_path: Path | None,
    params: CandidateEvaluationParams | None = None,
) -> RewardBreakdown:
    rooms: list[dict[str, Any]] = []
    runs: list[dict[str, Any]] = []
    if room_path is not None:
        rooms = load_room_dataset(room_path)
    if run_path is not None:
        runs = load_run_dataset(run_path)
    return evaluate_offline_reward(rooms, runs, params)
