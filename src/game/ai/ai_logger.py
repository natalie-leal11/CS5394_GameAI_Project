# Passive AI run logging for determinism inspection (no gameplay effects).
#
# =============================================================================
# RL / offline dataset — event schema (append-only JSON array per run file)
# =============================================================================
#
# Each record has an ``event`` string. Typical order: ``run_header`` first, then
# interleaved ``room_end``, healing-related events, ``session_end`` last for a
# complete run.
#
# run_header
#     ``run_id`` (UUID), ``seed`` (int). Written when a file-backed log starts.
#
# room_end
#     Emitted once per *actual* room completion (MetricsTracker.end_room +
#     GameScene._update_player_model_after_room_end). Includes ``room_index``,
#     ``biome_index``, ``room_result``, HP aggregates, director snapshot, etc.
#     ``room_attempt_index``: 1-based completion count for this campaign
#     ``room_index`` *this run* (increments on checkpoint retry of the same room).
#     ``session_room_completion_seq``: 1-based order of ``room_end`` rows this run.
#     ``checkpoint_retry_count``: ``PLAYER_LIVES_INITIAL - lives_remaining``
#     (lives consumed from starting pool; distinguishes checkpoint replays).
#
# session_end
#     Terminal row for the run (at most one per ``run_id`` in normal clients).
#     ``victory_or_defeat`` is one of: ``victory``, ``defeat``, ``aborted``
#     (e.g. pause → main menu, or leave-run safety net), ``quit`` (window close
#     while in game). Also ``total_run_time``, ``rooms_cleared``, ``seed``.
#
# Incomplete / header-only runs
#     If the process exits before ``session_end`` (crash, SIGKILL, power loss),
#     the file may contain only ``run_header`` or ``run_header`` + partial rows.
#     Exporters flag ``header_only_run`` / ``incomplete_run`` (see
#     ``game.rl.dataset_export``). Those cases cannot be distinguished from
#     crash vs. unclean shutdown from JSON alone.
#
# Healing (structured for RL analysis; does not replace room-level
# ``healing_received`` aggregates)
#     ``heal_drop_roll`` / ``heal_drop_skipped``: room-clear heal *evaluation*
#     (RNG and whether a drop was spawned). ``heal_evaluation_complete``: true.
#     ``heal_applied``: one row per heal *consumption* with ``heal_source``,
#     ``hp_percent_before`` / ``hp_percent_after``, ``heal_amount_applied``,
#     ``consumed``: true. Sources include ``room_clear_heal_orb``, ``mini_boss_reward``,
#     ``final_boss_reward``, ``safe_room``, ``reserve_heal``.
#
# Determinism: logging only reads game state; it does not affect RNG or physics.
# =============================================================================

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from game.config import PROJECT_ROOT

AI_DIRECTOR_LOG_SUBDIR = ("logs", "AI_Director_Logs")


class AILogger:
    """
    Collects per-room AI/metrics snapshots in memory; optional print.
    When constructed with a run seed, persists the full log list to a JSON file after each room.
    """

    def __init__(
        self,
        run_seed: int | None = None,
        *,
        run_id: str | None = None,
        verbose: bool = False,
    ) -> None:
        self.logs: list[dict[str, Any]] = []
        self._verbose = verbose
        self.run_seed: int | None = int(run_seed) if run_seed is not None else None
        self.run_id: str | None = str(run_id) if run_id is not None else None
        self.file_path: str | None = None
        if self.run_seed is not None:
            self._init_run_file(self.run_seed)

    def _init_run_file(self, seed: int) -> None:
        """Create log directory, pick a unique file name, write initial empty list."""
        try:
            log_dir = os.path.join(PROJECT_ROOT, *AI_DIRECTOR_LOG_SUBDIR)
            os.makedirs(log_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            base_name = f"ai_log_{int(seed)}_{ts}.json"
            path = os.path.join(log_dir, base_name)
            n = 2
            while os.path.exists(path):
                path = os.path.join(log_dir, f"ai_log_{int(seed)}_{ts}_{n}.json")
                n += 1
            self.file_path = path
            if self.run_id:
                self.logs.append(
                    {
                        "event": "run_header",
                        "run_id": self.run_id,
                        "seed": int(seed),
                    }
                )
            self._persist_to_file()
        except OSError:
            self.file_path = None

    def _persist_to_file(self) -> None:
        if self.file_path is None:
            return
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.logs, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def clear(self) -> None:
        """Clear in-memory logs and rewrite file (if any) as empty array."""
        self.logs.clear()
        self._persist_to_file()

    def log_room(self, data_dict: dict[str, Any]) -> None:
        """Append one room log (values should already be simple / serializable)."""
        entry = dict(data_dict)
        entry.setdefault("event", "room_end")
        self.logs.append(entry)
        self._persist_to_file()
        if self._verbose:
            seed = entry.get("seed", "?")
            ri = entry.get("room_index", "?")
            st = entry.get("player_state", "?")
            adj = entry.get("enemy_adjustment", "?")
            diff = entry.get("difficulty_modifier", "?")
            print(f"[AI LOG] Seed={seed} Room={ri} State={st} Adj={adj} Diff={diff}")

    def log_session_end(self, data_dict: dict[str, Any]) -> None:
        """Run outcome / final totals (offline RL)."""
        entry = dict(data_dict)
        entry.setdefault("event", "session_end")
        self.logs.append(entry)
        self._persist_to_file()

    def log_event(self, event_name: str, data_dict: dict[str, Any]) -> None:
        """Append an arbitrary named event (e.g. heal_drop_roll) for offline analysis."""
        entry = dict(data_dict)
        entry.setdefault("event", str(event_name))
        self.logs.append(entry)
        self._persist_to_file()

    @staticmethod
    def compare_runs(logs_a: list[dict[str, Any]], logs_b: list[dict[str, Any]]) -> bool:
        if len(logs_a) != len(logs_b):
            return False
        return all(a == b for a, b in zip(logs_a, logs_b))

    def export_to_file(self, filename: str) -> None:
        """Write current in-memory logs to an explicit path (manual export)."""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.logs, f, indent=2, ensure_ascii=False)
        except OSError:
            pass
