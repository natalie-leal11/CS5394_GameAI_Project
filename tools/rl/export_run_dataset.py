#!/usr/bin/env python3
"""
Export AI Director JSON logs to room-level and run-level offline datasets (CSV / JSONL).

Does not load pygame or gameplay code paths — only reads ``ai_log_*.json`` and writes tables.

Usage (from project root)::

    python tools/rl/export_run_dataset.py --log-dir logs/AI_Director_Logs --out-dir datasets/rl

    python tools/rl/export_run_dataset.py --file logs/AI_Director_Logs/ai_log_123_2026-01-01_00-00-00.json

See ``game.rl.dataset_export`` for schema documentation.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Project root = parent of tools/
_ROOT = Path(__file__).resolve().parent.parent.parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from game.config import PROJECT_ROOT  # noqa: E402
from game.rl.dataset_export import (  # noqa: E402
    AILogParseError,
    AILogSchemaError,
    RUN_LEVEL_FIELDS,
    ROOM_LEVEL_FIELDS,
    emit_warnings,
    export_datasets,
    export_single_file,
)


def main() -> int:
    p = argparse.ArgumentParser(description="Export ai_log_*.json to CSV/JSONL datasets.")
    p.add_argument(
        "--log-dir",
        type=Path,
        default=None,
        help="Directory containing ai_log_*.json (default: <project>/logs/AI_Director_Logs)",
    )
    p.add_argument(
        "--file",
        type=Path,
        default=None,
        help="Single ai_log JSON file (if set, --log-dir batch export is skipped)",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: <project>/datasets/rl_export)",
    )
    p.add_argument(
        "--pattern",
        default="ai_log_*.json",
        help="Glob under log-dir (default: ai_log_*.json)",
    )
    p.add_argument(
        "--prefix",
        default="ai_rl_",
        help="Output filename prefix for batch mode (default: ai_rl_)",
    )
    p.add_argument(
        "--format",
        action="append",
        choices=("csv", "jsonl"),
        dest="formats",
        help="Repeatable; default: both csv and jsonl",
    )
    p.add_argument(
        "--quiet-warnings",
        action="store_true",
        help="Do not print validation warnings to stderr",
    )
    args = p.parse_args()

    out_dir = args.out_dir or (PROJECT_ROOT / "datasets" / "rl_export")
    fmt_tuple: tuple[str, ...]
    if args.formats:
        fmt_tuple = tuple(dict.fromkeys(args.formats))  # preserve order, unique
    else:
        fmt_tuple = ("csv", "jsonl")

    try:
        if args.file is not None:
            fp = args.file.resolve()
            if not fp.is_file():
                print(f"ERROR: file not found: {fp}", file=sys.stderr)
                return 2
            result = export_single_file(fp, out_dir, formats=fmt_tuple)
        else:
            log_dir = args.log_dir or (PROJECT_ROOT / "logs" / "AI_Director_Logs")
            log_dir = log_dir.resolve()
            result = export_datasets(log_dir, out_dir, pattern=args.pattern, formats=fmt_tuple, prefix=args.prefix)
    except (AILogParseError, AILogSchemaError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if result.warnings and not args.quiet_warnings:
        emit_warnings(result.warnings)

    # Summary report (stdout)
    print("Export complete.")
    print(f"  Output directory: {out_dir.resolve()}")
    print("  Files written:")
    for path in sorted(set(result.room_paths + result.run_paths), key=lambda x: str(x)):
        print(f"    - {path}")
    print(f"  Formats: {', '.join(fmt_tuple)}")
    print("  Room-level fields (CSV columns / JSONL keys):")
    print(f"    {', '.join(ROOM_LEVEL_FIELDS)}")
    print("  Run-level fields:")
    print(f"    {', '.join(RUN_LEVEL_FIELDS)}")
    if result.warnings and args.quiet_warnings:
        print(f"  ({len(result.warnings)} warning(s) suppressed; run without --quiet-warnings)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
