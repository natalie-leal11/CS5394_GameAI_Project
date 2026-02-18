"""
Metrics tracker: player HP%, death count, room clear time, combat performance.
Logs per-room and run summary to logs/runs/ (JSON). Logging does not influence gameplay.
"""
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict
from datetime import datetime


@dataclass
class RoomMetrics:
    """Per-room metrics logged once on room completion."""
    run_id: str = ""
    seed: int = 0
    biome_index: int = 0
    room_index: int = 0
    room_type: str = ""
    chosen_encounter_type: str = ""
    enemy_count: int = 0
    elite_count: int = 0
    player_hp_start: int = 0
    player_hp_end: int = 0
    damage_taken: int = 0
    clear_time: float = 0.0
    director_state: str = "stable"


@dataclass
class RunSummary:
    """End-of-run summary."""
    run_id: str = ""
    seed: int = 0
    win_or_loss: str = "loss"
    rooms_cleared: int = 0
    total_damage_taken: int = 0
    total_run_time: float = 0.0


class MetricsTracker:
    """Tracks metrics; logs on room complete and run end. No per-frame logging."""

    def __init__(self, run_id: str = "", seed: int = 0) -> None:
        self.run_id = run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.seed = seed
        self.death_count: int = 0
        self.room_clear_times: list[float] = []
        self.total_damage_taken: int = 0
        self.run_start_time: float = 0.0
        self._current_room_hp_start: int = 0
        self._current_room_start_time: float = 0.0
        self._rooms_cleared: int = 0

    def hp_percent(self, current_hp: int, max_hp: int) -> float:
        if max_hp <= 0:
            return 1.0
        return current_hp / max_hp

    def start_room(self, player_hp: int, room_start_time: float) -> None:
        self._current_room_hp_start = player_hp
        self._current_room_start_time = room_start_time

    def record_room_complete(
        self,
        room_index: int,
        room_type: str,
        biome_index: int,
        chosen_encounter_type: str,
        enemy_count: int,
        elite_count: int,
        player_hp_end: int,
        clear_time: float,
        director_state: str,
    ) -> None:
        """Call once when room is cleared. Logs to disk."""
        damage_taken = max(0, self._current_room_hp_start - player_hp_end)
        self.total_damage_taken += damage_taken
        self._rooms_cleared += 1
        rm = RoomMetrics(
            run_id=self.run_id,
            seed=self.seed,
            biome_index=biome_index,
            room_index=room_index,
            room_type=room_type,
            chosen_encounter_type=chosen_encounter_type,
            enemy_count=enemy_count,
            elite_count=elite_count,
            player_hp_start=self._current_room_hp_start,
            player_hp_end=player_hp_end,
            damage_taken=damage_taken,
            clear_time=clear_time,
            director_state=director_state,
        )
        self._log_room(rm)

    def _log_room(self, rm: RoomMetrics) -> None:
        """Write room log to logs/runs/. JSON format."""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "logs", "runs")
        os.makedirs(log_dir, exist_ok=True)
        path = os.path.join(log_dir, f"{self.run_id}_room_{rm.room_index}.json")
        with open(path, "w") as f:
            json.dump(
                {
                    "run_id": rm.run_id,
                    "seed": rm.seed,
                    "biome_index": rm.biome_index,
                    "room_index": rm.room_index,
                    "room_type": rm.room_type,
                    "chosen_encounter_type": rm.chosen_encounter_type,
                    "enemy_count": rm.enemy_count,
                    "elite_count": rm.elite_count,
                    "player_hp_start": rm.player_hp_start,
                    "player_hp_end": rm.player_hp_end,
                    "damage_taken": rm.damage_taken,
                    "clear_time": rm.clear_time,
                    "director_state": rm.director_state,
                },
                f,
                indent=0,
            )

    def record_run_end(self, win: bool, total_run_time: float) -> None:
        """Call once at run end. Logs summary."""
        summary = RunSummary(
            run_id=self.run_id,
            seed=self.seed,
            win_or_loss="win" if win else "loss",
            rooms_cleared=self._rooms_cleared,
            total_damage_taken=self.total_damage_taken,
            total_run_time=total_run_time,
        )
        self._log_run_summary(summary)

    def _log_run_summary(self, summary: RunSummary) -> None:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "logs", "runs")
        os.makedirs(log_dir, exist_ok=True)
        path = os.path.join(log_dir, f"{self.run_id}_summary.json")
        with open(path, "w") as f:
            json.dump(
                {
                    "run_id": summary.run_id,
                    "seed": summary.seed,
                    "win_or_loss": summary.win_or_loss,
                    "rooms_cleared": summary.rooms_cleared,
                    "total_damage_taken": summary.total_damage_taken,
                    "total_run_time": summary.total_run_time,
                },
                f,
                indent=0,
            )
        # Append to logs/summary.json for offline analysis
        summary_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "logs", "summary.json")
        os.makedirs(os.path.dirname(summary_path), exist_ok=True)
        line = json.dumps({
            "seed": summary.seed,
            "win_or_loss": summary.win_or_loss,
            "total_rooms_cleared": summary.rooms_cleared,
            "total_time": summary.total_run_time,
            "total_damage_taken": summary.total_damage_taken,
        }) + "\n"
        with open(summary_path, "a") as f:
            f.write(line)
