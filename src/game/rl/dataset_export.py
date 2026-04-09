"""
Offline dataset export for AI Director JSON logs (read-only).

Input: ``logs/AI_Director_Logs/ai_log_*.json`` — each file is a JSON array of
records with an ``event`` field:

- ``run_header``: ``run_id``, ``seed``
- ``room_end`` (default if omitted): per-room metrics + director snapshot used
- ``session_end``: run outcome + totals (``victory_or_defeat``: victory / defeat /
  aborted / quit). Controlled exits should emit ``session_end``; process crash /
  SIGKILL / power loss may leave only ``run_header`` or partial rows (see
  ``incomplete_run`` / ``header_only_run`` below).
- ``heal_drop_roll`` / ``heal_drop_skipped``: room-clear heal *evaluation* (RNG;
  ``heal_evaluation_complete`` is true when present).
- ``heal_applied``: one row per heal *consumption* (``heal_source``, HP before/after,
  ``heal_amount_applied``, ``consumed``).

**Semantics (room_end):** ``room_attempt_index`` = 1-based completions for this
campaign ``room_index`` this run; ``session_room_completion_seq`` = order of
``room_end`` rows; ``checkpoint_retry_count`` = lives consumed from starting pool.

This module does not touch gameplay; it only reads logs and writes tabular exports.

Output schemas (explicit columns)
-----------------------------------

**Room-level** (one row per ``room_end``):

.. csv-table::
   :header: "Column", "Description"

   "run_id", "UUID for the run"
   "seed", "Integer run seed from logger"
   "room_index", "Campaign room index at room end"
   "biome_index", "Biome index"
   "room_type", "Room type string"
   "player_state", "Player model state name (e.g. STRUGGLING)"
   "life_index", "Life index"
   "lives_remaining", "Lives remaining"
   "room_attempt_index", "Nth completion log for this campaign room_index this run (1-based)"
   "session_room_completion_seq", "1-based order of room_end rows this run"
   "checkpoint_retry_count", "Lives consumed from starting pool (PLAYER_LIVES_INITIAL − lives_remaining)"
   "hp_percent_start_room", "HP %% at room start"
   "hp_end", "HP %% at room end"
   "min_hp_during_room", "Min HP %% during room"
   "max_hp_during_room", "Max HP %% during room"
   "damage_taken", "Damage taken in room"
   "healing_received", "Healing collected in room"
   "room_clear_time", "Seconds in room"
   "enemy_count", "Logged enemy count"
   "enemy_composition", "List of enemy type names (JSON string in CSV)"
   "elite_count", "Elite count"
   "reinforcement_applied", "Bool"
   "difficulty_modifier", "Director difficulty"
   "enemy_adjustment", "Integer adjustment"
   "rooms_cleared", "Cumulative rooms cleared at log time"
   "total_run_time", "Cumulative run time at log time"
   "room_result", "clean_clear / damaged_clear / …"
   "victory_or_defeat", "Usually ``none`` per room; see run-level for final outcome"
   "encounter_director_snapshot_used", "Frozen director snapshot dict (JSON string in CSV)"
   "source_file", "Basename of the ai_log JSON file"
   "source_row_index", "0-based index of this record in that file"

**Run-level** (one row per distinct ``run_id`` after grouping):

.. csv-table::
   :header: "Column", "Description"

   "run_id", "UUID"
   "seed", "From run_header or first room_end / session_end"
   "total_rooms_logged", "Count of room_end rows"
   "rooms_cleared", "From session_end if present, else last room_end"
   "total_run_time", "From session_end if present, else last room_end"
   "final_outcome", "session_end ``victory_or_defeat`` if present"
   "final_player_state", "Last room_end ``player_state`` if any"
   "session_end_present", "Whether a session_end row exists"
   "incomplete_run", "True if no session_end (crash/unclean exit or missing terminal log)"
   "header_only_run", "True if run_header exists but no room_end rows"
   "source_files", "Comma-separated basenames contributing to this run"
"""

from __future__ import annotations

import csv
import json
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

_KNOWN_NON_ROOM_EVENTS = {
    "run_header",
    "session_end",
    "heal_drop_roll",
    "heal_drop_skipped",
    "heal_applied"
}

# Columns aligned with ``GameScene._update_player_model_after_room_end`` / ``AILogger``.
ROOM_LEVEL_FIELDS: tuple[str, ...] = (
    "run_id",
    "seed",
    "room_index",
    "biome_index",
    "room_type",
    "player_state",
    "life_index",
    "lives_remaining",
    "room_attempt_index",
    "session_room_completion_seq",
    "checkpoint_retry_count",
    "hp_percent_start_room",
    "hp_end",
    "min_hp_during_room",
    "max_hp_during_room",
    "damage_taken",
    "healing_received",
    "room_clear_time",
    "enemy_count",
    "enemy_composition",
    "elite_count",
    "reinforcement_applied",
    "difficulty_modifier",
    "enemy_adjustment",
    "rooms_cleared",
    "total_run_time",
    "room_result",
    "victory_or_defeat",
    "encounter_director_snapshot_used",
    "source_file",
    "source_row_index",
)

RUN_LEVEL_FIELDS: tuple[str, ...] = (
    "run_id",
    "seed",
    "total_rooms_logged",
    "rooms_cleared",
    "total_run_time",
    "final_outcome",
    "final_player_state",
    "session_end_present",
    "incomplete_run",
    "header_only_run",
    "source_files",
)


class AILogParseError(Exception):
    """Raised when a log file is not valid JSON."""


class AILogSchemaError(Exception):
    """Raised when the top-level JSON is not a list of objects usable for export."""


def load_ai_log_json(path: Path) -> list[dict[str, Any]]:
    """Load one ``ai_log_*.json`` file. Raises :class:`AILogParseError` or :class:`AILogSchemaError`."""
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except OSError as e:
        raise AILogParseError(f"Cannot read {path}: {e}") from e
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise AILogParseError(f"Invalid JSON in {path}: {e}") from e
    if not isinstance(data, list):
        raise AILogSchemaError(f"Expected JSON array in {path}, got {type(data).__name__}")
    out: list[dict[str, Any]] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise AILogSchemaError(f"{path}: item at index {i} is not an object")
        out.append(item)
    return out


def _event_name(row: dict[str, Any]) -> str:
    ev = row.get("event", "room_end")
    return str(ev) if ev is not None else "room_end"


def _serialize_cell(key: str, value: Any) -> Any:
    """Normalize values for CSV / JSONL (JSON-serialize nested structures)."""
    if key == "enemy_composition":
        if value is None:
            return "[]"
        if isinstance(value, list):
            return json.dumps(value, ensure_ascii=False)
        return json.dumps(value, ensure_ascii=False)
    if key == "encounter_director_snapshot_used":
        if value is None:
            return "{}"
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False, default=str)
        return json.dumps(value, ensure_ascii=False, default=str)
    if isinstance(value, bool):
        return value
    if value is None:
        return ""
    if isinstance(value, (int, float, str)):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)


def _room_row(
    row: dict[str, Any],
    *,
    source_file: str,
    source_row_index: int,
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k in ROOM_LEVEL_FIELDS:
        if k == "source_file":
            out[k] = source_file
        elif k == "source_row_index":
            out[k] = source_row_index
        else:
            out[k] = _serialize_cell(k, row.get(k))
    return out


def _room_row_native(
    row: dict[str, Any],
    *,
    source_file: str,
    source_row_index: int,
) -> dict[str, Any]:
    """Room row with nested JSON types preserved (for JSONL)."""
    out: dict[str, Any] = {}
    for k in ROOM_LEVEL_FIELDS:
        if k == "source_file":
            out[k] = source_file
        elif k == "source_row_index":
            out[k] = source_row_index
        else:
            out[k] = row.get(k)
    return out


def _coerce_seed(val: Any) -> int | None:
    if val is None:
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


@dataclass
class RunAccumulator:
    run_id: str
    seeds: set[int | None] = field(default_factory=set)
    run_headers: list[dict[str, Any]] = field(default_factory=list)
    room_ends: list[tuple[str, int, dict[str, Any]]] = field(default_factory=list)
    session_ends: list[dict[str, Any]] = field(default_factory=list)
    source_files: set[str] = field(default_factory=set)
    warnings: list[str] = field(default_factory=list)


def iter_ai_log_files(
    log_dir: Path,
    *,
    pattern: str = "ai_log_*.json",
) -> Iterator[Path]:
    """Yield matching log files (sorted by name for determinism)."""
    if not log_dir.is_dir():
        return
    for p in sorted(log_dir.glob(pattern)):
        if p.is_file():
            yield p


def _assign_run_id(
    row: dict[str, Any],
    last_run_id: str | None,
    source_file: str,
    row_index: int,
) -> tuple[str | None, str | None]:
    """
    Return (run_id, warning_message).
    warning_message if run_id was missing and inferred.
    """
    rid = row.get("run_id")
    if rid is not None and str(rid).strip() != "":
        return str(rid), None
    if last_run_id is not None:
        return last_run_id, (
            f"{source_file}[{row_index}]: missing run_id; using previous run_id={last_run_id}"
        )
    return None, f"{source_file}[{row_index}]: missing run_id and no prior run_header; row skipped"


def ingest_file(
    path: Path,
    accumulators: dict[str, RunAccumulator],
    global_warnings: list[str],
) -> None:
    """Merge one log file into accumulators keyed by run_id."""
    records = load_ai_log_json(path)
    base = path.name
    last_run_id: str | None = None

    for idx, row in enumerate(records):
        ev = _event_name(row)
        rid, w = _assign_run_id(row, last_run_id, base, idx)
        if w:
            global_warnings.append(w)
        if rid is None:
            continue

        if ev == "run_header":
            last_run_id = rid
            acc = accumulators.setdefault(rid, RunAccumulator(run_id=rid))
            acc.run_headers.append(row)
            acc.source_files.add(base)
            s = _coerce_seed(row.get("seed"))
            acc.seeds.add(s)
            hdr_seed = row.get("seed")
            if hdr_seed is not None and s is None:
                acc.warnings.append(f"{base}: run_header has non-integer seed {hdr_seed!r}")

        elif ev == "room_end":
            last_run_id = rid
            acc = accumulators.setdefault(rid, RunAccumulator(run_id=rid))
            acc.room_ends.append((base, idx, row))
            acc.source_files.add(base)
            acc.seeds.add(_coerce_seed(row.get("seed")))

        elif ev == "session_end":
            last_run_id = rid
            acc = accumulators.setdefault(rid, RunAccumulator(run_id=rid))
            acc.session_ends.append(row)
            acc.source_files.add(base)
            acc.seeds.add(_coerce_seed(row.get("seed")))

        elif ev in _KNOWN_NON_ROOM_EVENTS:
            last_run_id = rid
            acc = accumulators.setdefault(rid, RunAccumulator(run_id=rid))
            acc.source_files.add(base)
            acc.seeds.add(_coerce_seed(row.get("seed")))

        else:
            global_warnings.append(f"{base}[{idx}]: unknown event {ev!r} (skipped)")


def _validate_run(acc: RunAccumulator, global_warnings: list[str]) -> None:
    seeds = {s for s in acc.seeds if s is not None}
    if len(seeds) > 1:
        global_warnings.append(
            f"run_id={acc.run_id}: inconsistent seed values across rows: {sorted(seeds)}"
        )
    if len(acc.source_files) > 1:
        global_warnings.append(
            f"run_id={acc.run_id}: grouped events merged from multiple log files: {sorted(acc.source_files)}"
        )
    if not acc.session_ends:
        global_warnings.append(f"run_id={acc.run_id}: missing session_end (no terminal outcome row)")

    if acc.run_headers and not acc.room_ends:
        global_warnings.append(
            f"run_id={acc.run_id}: header_only_run (run_header but no room_end rows; crash or pre-first-room exit)"
        )

    if len(acc.session_ends) > 1:
        global_warnings.append(
            f"run_id={acc.run_id}: multiple session_end rows ({len(acc.session_ends)}); using last for run-level totals"
        )


def build_run_level_row(acc: RunAccumulator) -> dict[str, Any]:
    """One run-level dict from a :class:`RunAccumulator`."""
    seeds = {s for s in acc.seeds if s is not None}
    seed: int | None = None
    if len(seeds) == 1:
        seed = next(iter(seeds))
    elif acc.run_headers:
        seed = _coerce_seed(acc.run_headers[0].get("seed"))

    total_rooms = len(acc.room_ends)
    last_room: dict[str, Any] | None = acc.room_ends[-1][2] if acc.room_ends else None
    sess = acc.session_ends[-1] if acc.session_ends else None

    rooms_cleared: Any = ""
    total_run_time: Any = ""
    final_outcome = ""

    if sess:
        rooms_cleared = sess.get("rooms_cleared", "")
        total_run_time = sess.get("total_run_time", "")
        final_outcome = str(sess.get("victory_or_defeat", "") or "")
    elif last_room is not None:
        rooms_cleared = last_room.get("rooms_cleared", "")
        total_run_time = last_room.get("total_run_time", "")

    final_ps = ""
    if last_room is not None:
        ps = last_room.get("player_state")
        if ps is not None:
            final_ps = str(ps)

    session_end_present = bool(acc.session_ends)
    header_only_run = len(acc.room_ends) == 0 and len(acc.run_headers) > 0

    return {
        "run_id": acc.run_id,
        "seed": seed if seed is not None else "",
        "total_rooms_logged": total_rooms,
        "rooms_cleared": rooms_cleared,
        "total_run_time": total_run_time,
        "final_outcome": final_outcome,
        "final_player_state": final_ps,
        "session_end_present": session_end_present,
        "incomplete_run": not session_end_present,
        "header_only_run": header_only_run,
        "source_files": ",".join(sorted(acc.source_files)),
    }


@dataclass
class ExportResult:
    """Paths written and collected warnings from validation."""

    room_paths: list[Path] = field(default_factory=list)
    run_paths: list[Path] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def export_datasets(
    log_dir: Path,
    output_dir: Path,
    *,
    pattern: str = "ai_log_*.json",
    formats: tuple[str, ...] = ("csv", "jsonl"),
    prefix: str = "ai_rl_",
) -> ExportResult:
    """
    Read all matching logs under ``log_dir``, group by ``run_id``, write room- and run-level exports.

    ``formats`` may include ``\"csv\"`` and/or ``\"jsonl\"``.
    """
    result = ExportResult()
    accumulators: dict[str, RunAccumulator] = {}

    files = list(iter_ai_log_files(log_dir, pattern=pattern))
    if not files:
        result.warnings.append(f"No files matching {pattern!r} under {log_dir}")
        return result

    for fp in files:
        ingest_file(fp, accumulators, result.warnings)

    for acc in accumulators.values():
        _validate_run(acc, result.warnings)
        result.warnings.extend(acc.warnings)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Room-level rows (flat list in file order: sorted files, then record order)
    room_rows_csv: list[dict[str, Any]] = []
    room_rows_jsonl: list[dict[str, Any]] = []
    for fp in files:
        records = load_ai_log_json(fp)
        base = fp.name
        last_run_id: str | None = None
        for idx, row in enumerate(records):
            ev = _event_name(row)
            rid, _ = _assign_run_id(row, last_run_id, base, idx)
            if ev == "run_header":
                if rid:
                    last_run_id = rid
                continue
            if ev != "room_end":
                continue
            if rid is None:
                continue
            last_run_id = rid
            room_rows_csv.append(_room_row(row, source_file=base, source_row_index=idx))
            room_rows_jsonl.append(_room_row_native(row, source_file=base, source_row_index=idx))

    run_rows = [build_run_level_row(acc) for acc in sorted(accumulators.values(), key=lambda a: a.run_id)]

    for fmt in formats:
        if fmt == "csv":
            rp = output_dir / f"{prefix}rooms.csv"
            _write_csv(rp, room_rows_csv, ROOM_LEVEL_FIELDS)
            result.room_paths.append(rp)
            up = output_dir / f"{prefix}runs.csv"
            _write_csv(up, run_rows, RUN_LEVEL_FIELDS)
            result.run_paths.append(up)
        elif fmt == "jsonl":
            rp = output_dir / f"{prefix}rooms.jsonl"
            _write_jsonl(rp, room_rows_jsonl, ROOM_LEVEL_FIELDS)
            result.room_paths.append(rp)
            up = output_dir / f"{prefix}runs.jsonl"
            _write_jsonl(up, run_rows, RUN_LEVEL_FIELDS)
            result.run_paths.append(up)
        else:
            result.warnings.append(f"Unknown format {fmt!r} (skipped)")

    return result


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fields), extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def _write_jsonl(path: Path, rows: list[dict[str, Any]], fields: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            obj = {k: row.get(k) for k in fields}
            f.write(json.dumps(obj, ensure_ascii=False, default=str) + "\n")


def export_single_file(
    log_path: Path,
    output_dir: Path,
    *,
    formats: tuple[str, ...] = ("csv", "jsonl"),
    prefix: str | None = None,
) -> ExportResult:
    """Export from a single ``ai_log_*.json`` (same grouping logic; one file in source_files)."""
    pfx = prefix if prefix is not None else f"{log_path.stem}_"
    result = ExportResult()
    accumulators: dict[str, RunAccumulator] = {}
    ingest_file(log_path, accumulators, result.warnings)
    for acc in accumulators.values():
        _validate_run(acc, result.warnings)
        result.warnings.extend(acc.warnings)

    output_dir.mkdir(parents=True, exist_ok=True)

    records = load_ai_log_json(log_path)
    base = log_path.name
    room_rows_csv: list[dict[str, Any]] = []
    room_rows_jsonl: list[dict[str, Any]] = []
    last_run_id: str | None = None
    for idx, row in enumerate(records):
        ev = _event_name(row)
        rid, _ = _assign_run_id(row, last_run_id, base, idx)
        if ev == "run_header":
            if rid:
                last_run_id = rid
            continue
        if ev != "room_end":
            continue
        if rid is None:
            continue
        last_run_id = rid
        room_rows_csv.append(_room_row(row, source_file=base, source_row_index=idx))
        room_rows_jsonl.append(_room_row_native(row, source_file=base, source_row_index=idx))

    run_rows = [build_run_level_row(acc) for acc in sorted(accumulators.values(), key=lambda a: a.run_id)]

    for fmt in formats:
        if fmt == "csv":
            rp = output_dir / f"{pfx}rooms.csv"
            _write_csv(rp, room_rows_csv, ROOM_LEVEL_FIELDS)
            result.room_paths.append(rp)
            up = output_dir / f"{pfx}runs.csv"
            _write_csv(up, run_rows, RUN_LEVEL_FIELDS)
            result.run_paths.append(up)
        elif fmt == "jsonl":
            rp = output_dir / f"{pfx}rooms.jsonl"
            _write_jsonl(rp, room_rows_jsonl, ROOM_LEVEL_FIELDS)
            result.room_paths.append(rp)
            up = output_dir / f"{pfx}runs.jsonl"
            _write_jsonl(up, run_rows, RUN_LEVEL_FIELDS)
            result.run_paths.append(up)
        else:
            result.warnings.append(f"Unknown format {fmt!r} (skipped)")

    return result


def emit_warnings(messages: list[str]) -> None:
    for msg in messages:
        warnings.warn(msg, UserWarning, stacklevel=1)
