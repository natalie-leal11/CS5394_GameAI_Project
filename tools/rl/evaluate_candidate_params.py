#!/usr/bin/env python3
"""
Evaluate offline reward for one or more candidate parameter profiles against
exported room/run datasets (CSV or JSONL).

Does not import gameplay, pygame, or modify config.

Example::

    python tools/rl/evaluate_candidate_params.py \\
        --rooms datasets/rl_export/ai_rl_rooms.jsonl \\
        --runs datasets/rl_export/ai_rl_runs.jsonl \\
        --candidates tools/rl/examples/candidate_default.json

    python tools/rl/evaluate_candidate_params.py -r runs.csv --room-jsonl rooms.jsonl --default
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from game.rl.offline_tuning_spec import (  # noqa: E402
    CandidateEvaluationParams,
    default_candidate,
    schema_summary,
    validate_candidate_dict,
)
from game.rl.reward_eval import InsufficientDataError, RewardBreakdown, evaluate_from_paths  # noqa: E402


def _load_candidates(paths: list[Path]) -> list[tuple[str, CandidateEvaluationParams]]:
    out: list[tuple[str, CandidateEvaluationParams]] = []
    for p in paths:
        raw_text = p.read_text(encoding="utf-8-sig")
        data = json.loads(raw_text)
        if isinstance(data, list):
            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    raise ValueError(f"{p}: list item {i} is not an object")
                out.append((f"{p.name}#{i}", validate_candidate_dict(item)))
        elif isinstance(data, dict):
            out.append((p.name, validate_candidate_dict(data)))
        else:
            raise ValueError(f"{p}: expected object or array, got {type(data).__name__}")
    return out


def _fmt_breakdown(name: str, b: RewardBreakdown) -> str:
    lines = [
        f"=== Candidate: {name} ===",
        f"  overall_reward:                 {b.overall_reward:.4f}",
        f"  win_rate_score:                 {b.win_rate_score:.4f}",
        f"  win_rate_band_applied:          {b.win_rate_band_applied}",
        f"  early_biome_penalty:            {b.early_biome_penalty:.4f}",
        f"  late_game_triviality_penalty:   {b.late_game_triviality_penalty:.4f}",
        f"  difficulty_spike_penalty:       {b.difficulty_spike_penalty:.4f}",
        "",
        "  [data metrics]",
        f"  empirical_win_rate (decisive): {b.empirical_win_rate:.4f}  ({b.wins}/{b.decisive_runs} wins, {b.total_runs} runs total)",
        f"  early_rooms_used:               {b.early_rooms_used}",
        f"  late_rooms_used / trivial:      {b.late_rooms_used} / {b.late_trivial_rooms}",
        f"  spike_transitions / spikes:     {b.spike_transitions} / {b.spike_count}",
        "",
        "  [valid_rows_used_by_metric]",
    ]
    for k, v in sorted(b.valid_rows_used_by_metric.items()):
        lines.append(f"    {k}: {v}")
    lines.append("  [skipped_rows_by_metric]")
    for k, v in sorted(b.skipped_rows_by_metric.items()):
        lines.append(f"    {k}: {v}")
    lines.append("  [triviality_thresholds_used]")
    for k, v in sorted(b.triviality_thresholds_used.items()):
        lines.append(f"    {k}: {v}")
    if b.missing_field_warnings:
        lines.append("  [missing_field_warnings]")
        for w in b.missing_field_warnings:
            lines.append(f"    - {w}")
    if b.notes:
        lines.append("  [notes]")
        for n in b.notes:
            lines.append(f"    - {n}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Offline reward evaluation for exported AI RL datasets.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=schema_summary(),
    )
    ap.add_argument(
        "--rooms",
        "--room",
        dest="rooms",
        type=Path,
        default=None,
        help="Room-level dataset (.csv or .jsonl)",
    )
    ap.add_argument(
        "--runs",
        "--run",
        dest="runs",
        type=Path,
        default=None,
        help="Run-level dataset (.csv or .jsonl)",
    )
    ap.add_argument(
        "--candidates",
        type=Path,
        nargs="*",
        default=(),
        help="One or more JSON files: single object or array of candidate profiles",
    )
    ap.add_argument(
        "--default",
        action="store_true",
        help="Evaluate built-in default candidate (ignores --candidates if both given)",
    )
    args = ap.parse_args()

    if args.rooms is None and args.runs is None:
        print("ERROR: provide at least one of --rooms or --runs", file=sys.stderr)
        return 2

    room_p = args.rooms.resolve() if args.rooms else None
    run_p = args.runs.resolve() if args.runs else None

    candidates: list[tuple[str, CandidateEvaluationParams]] = []
    try:
        if args.default:
            candidates.append(("default", default_candidate()))
        elif args.candidates:
            for p in args.candidates:
                if not p.is_file():
                    print(f"ERROR: candidate file not found: {p}", file=sys.stderr)
                    return 2
            candidates.extend(_load_candidates([p.resolve() for p in args.candidates]))
        else:
            candidates.append(("default", default_candidate()))
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    reports: list[str] = []
    try:
        for name, params in candidates:
            br = evaluate_from_paths(room_p, run_p, params)
            reports.append(_fmt_breakdown(name, br))
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print("\n\n".join(reports))

    # Closing report (human-readable summary)
    print()
    print("---")
    print("Summary")
    print(f"  Files read: rooms={room_p or '—'}, runs={run_p or '—'}")
    print(f"  Candidates evaluated: {len(candidates)}")
    print()
    print("Formulas / policies (see src/game/rl/reward_eval.py):")
    print("  - Missing fields: rows skipped per metric; see skipped_rows_by_metric / warnings.")
    print("  - win_rate_score: band applied only if at least one decisive run; else score 0.")
    print("  - late triviality: fixed caps OR deterministic percentile thresholds on late cohort.")
    print("  - overall_reward: weighted sum of win_rate_score minus weighted penalties")
    print()
    print("Assumptions:")
    print("  - Datasets come from game.rl.dataset_export (same column names).")
    print("  - final_outcome: decisive runs use victory/defeat (case-insensitive).")
    print("  - Candidate params are evaluation-only; runtime config is unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
