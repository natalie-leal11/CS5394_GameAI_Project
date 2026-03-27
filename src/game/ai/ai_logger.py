# Passive AI run logging for determinism inspection (no gameplay effects).

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

    def __init__(self, run_seed: int | None = None, *, verbose: bool = False) -> None:
        self.logs: list[dict[str, Any]] = []
        self._verbose = verbose
        self.run_seed: int | None = int(run_seed) if run_seed is not None else None
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
        self.logs.append(entry)
        self._persist_to_file()
        if self._verbose:
            seed = entry.get("seed", "?")
            ri = entry.get("room_index", "?")
            st = entry.get("player_state", "?")
            adj = entry.get("enemy_adjustment", "?")
            diff = entry.get("difficulty_modifier", "?")
            print(f"[AI LOG] Seed={seed} Room={ri} State={st} Adj={adj} Diff={diff}")

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
