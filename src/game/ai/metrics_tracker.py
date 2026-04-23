# Deterministic run/room metrics for Player Model / AI Director.
# Attribute names match Metrics_Tracker.md — raw accumulation only (no AI decisions).

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from game.config import DEBUG_ROOM_HP_METRICS_PRINT

from game.ai.difficulty_params import DifficultyParams, load_difficulty_params_json


class RoomResult(str, Enum):
    clean_clear = "clean_clear"
    damaged_clear = "damaged_clear"
    near_death = "near_death"
    death = "death"


@dataclass
class RoomMetrics:
    """Per-room metrics — all room-scoped attributes from Metrics_Tracker.md."""

    current_room_index: int = 0
    current_biome_index: int = 1
    room_start_time: float = 0.0
    room_end_time: float = 0.0
    room_clear_time: float = 0.0
    room_active_flag: bool = False

    hp_percent_start_room: float = 100.0
    hp_percent_end_room: float = 100.0
    hp_lost_in_room: float = 0.0
    hp_gained_in_room: float = 0.0
    max_hp_during_room: float = 0.0
    min_hp_during_room: float = 100.0

    damage_taken_in_room: float = 0.0
    damage_dealt_in_room: float = 0.0
    damage_taken_rate: float = 0.0
    damage_dealt_rate: float = 0.0
    hits_taken_count: int = 0
    hits_given_count: int = 0
    kill_count_room: int = 0
    kill_count_total: int = 0

    enemy_types_in_room: str = ""
    enemy_composition_id: str = ""
    damage_taken_by_enemy_type: dict[str, float] = field(default_factory=dict)
    kills_by_enemy_type: dict[str, int] = field(default_factory=dict)

    room_type: str = ""
    enemies_spawned_count: int = 0
    elite_enemies_count: int = 0
    ambush_flag: bool = False
    spawn_pattern_type: str = ""
    spawn_delay_profile: str = ""
    reinforcement_applied: bool = False

    hazard_tiles_count: int = 0
    time_in_hazard_tiles: float = 0.0
    damage_from_hazards: float = 0.0
    hazard_type_distribution: str = ""

    movement_distance: float = 0.0
    idle_time: float = 0.0
    dash_count: int = 0
    time_near_enemies: float = 0.0
    time_far_from_enemies: float = 0.0

    room_result: RoomResult = RoomResult.clean_clear
    clean_clear_flag: bool = False
    heavy_damage_flag: bool = False
    near_death_flag: bool = False
    death_flag: bool = False
    death_room_index: int = -1
    death_biome_index: int = -1

    reward_dropped_flag: bool = False
    reward_collected_flag: bool = False
    reward_type: str = ""
    reward_value: float = 0.0
    time_to_collect_reward: float = 0.0
    reward_missed_flag: bool = False

    healing_orb_collected_count: int = 0
    healing_amount_collected: float = 0.0
    healing_wasted: float = 0.0

    upgrade_options_count: int = 0
    upgrade_selected_type: str = ""
    upgrade_selected_id: str = ""
    upgrade_power_value: float = 0.0
    upgrade_skipped_flag: bool = False


@dataclass
class RunMetrics:
    """Run-level state, aggregates, mirrors of active room, and history — Metrics_Tracker.md."""

    run_seed: int = 0
    run_start_time: float = 0.0
    run_elapsed_time: float = 0.0
    rooms_cleared: int = 0
    biomes_cleared: int = 0
    total_deaths: int = 0
    total_damage_taken: float = 0.0
    total_damage_dealt: float = 0.0
    total_healing_received: float = 0.0
    total_healing_wasted: float = 0.0
    total_rewards_collected: int = 0
    total_upgrades_selected: int = 0

    # RL reward shaping only (deltas used in rl/reward.py); not mirrored to room snapshots.
    rl_interact_success_count: int = 0
    rl_safe_room_heal_success_count: int = 0
    rl_safe_room_heal_failed_count: int = 0
    rl_interact_failed_e_count: int = 0
    # RL-only: reserve heal (H) — success paired with record_healing; failed = no heal or on cooldown.
    rl_reserve_heal_success_count: int = 0
    rl_reserve_heal_failed_count: int = 0

    hp_percent_current: float = 100.0
    hp_absolute_current: float = 0.0
    low_hp_events_count: int = 0
    near_death_events_count: int = 0
    revive_used_count: int = 0

    current_room_index: int = -1
    current_biome_index: int = 1
    room_start_time: float = 0.0
    room_end_time: float = 0.0
    room_clear_time: float = 0.0
    room_active_flag: bool = False

    hp_percent_start_room: float = 100.0
    hp_percent_end_room: float = 100.0
    hp_lost_in_room: float = 0.0
    hp_gained_in_room: float = 0.0
    max_hp_during_room: float = 0.0
    min_hp_during_room: float = 100.0

    damage_taken_in_room: float = 0.0
    damage_dealt_in_room: float = 0.0
    damage_taken_rate: float = 0.0
    damage_dealt_rate: float = 0.0
    hits_taken_count: int = 0
    hits_given_count: int = 0
    kill_count_room: int = 0
    kill_count_total: int = 0

    enemy_types_in_room: str = ""
    enemy_composition_id: str = ""
    damage_taken_by_enemy_type: dict[str, float] = field(default_factory=dict)
    kills_by_enemy_type: dict[str, int] = field(default_factory=dict)

    room_type: str = ""
    enemies_spawned_count: int = 0
    elite_enemies_count: int = 0
    ambush_flag: bool = False
    spawn_pattern_type: str = ""
    spawn_delay_profile: str = ""
    reinforcement_applied: bool = False

    hazard_tiles_count: int = 0
    time_in_hazard_tiles: float = 0.0
    damage_from_hazards: float = 0.0
    hazard_type_distribution: str = ""

    movement_distance: float = 0.0
    idle_time: float = 0.0
    dash_count: int = 0
    time_near_enemies: float = 0.0
    time_far_from_enemies: float = 0.0

    room_result: RoomResult = RoomResult.clean_clear
    clean_clear_flag: bool = False
    heavy_damage_flag: bool = False
    near_death_flag: bool = False
    death_flag: bool = False
    death_room_index: int = -1
    death_biome_index: int = -1

    reward_dropped_flag: bool = False
    reward_collected_flag: bool = False
    reward_type: str = ""
    reward_value: float = 0.0
    time_to_collect_reward: float = 0.0
    reward_missed_flag: bool = False

    healing_orb_collected_count: int = 0
    healing_amount_collected: float = 0.0
    healing_wasted: float = 0.0

    upgrade_options_count: int = 0
    upgrade_selected_type: str = ""
    upgrade_selected_id: str = ""
    upgrade_power_value: float = 0.0
    upgrade_skipped_flag: bool = False

    last_3_rooms_hp_loss: list[float] = field(default_factory=list)
    last_3_rooms_clear_time: list[float] = field(default_factory=list)
    last_3_rooms_result: list[str] = field(default_factory=list)
    recent_death_flag: bool = False
    recent_struggle_flag: bool = False
    recent_dominating_flag: bool = False

    struggling_rooms_count: int = 0
    dominating_rooms_count: int = 0
    spike_damage_events: int = 0

    biome_start_time: float = 0.0
    biome_end_time: float = 0.0
    biome_clear_time: float = 0.0
    biome_damage_taken: float = 0.0
    biome_deaths: int = 0

    room_history: list[RoomMetrics] = field(default_factory=list)
    biome_history: list[dict[str, Any]] = field(default_factory=list)


_HEAVY_DAMAGE_HP_LOSS_PCT = 20.0


def _sync_run_from_room(rm: RunMetrics, room: RoomMetrics) -> None:
    for name in (
        "current_room_index",
        "current_biome_index",
        "room_start_time",
        "room_end_time",
        "room_clear_time",
        "room_active_flag",
        "hp_percent_start_room",
        "hp_percent_end_room",
        "hp_lost_in_room",
        "hp_gained_in_room",
        "max_hp_during_room",
        "min_hp_during_room",
        "damage_taken_in_room",
        "damage_dealt_in_room",
        "damage_taken_rate",
        "damage_dealt_rate",
        "hits_taken_count",
        "hits_given_count",
        "kill_count_room",
        "enemy_types_in_room",
        "enemy_composition_id",
        "damage_taken_by_enemy_type",
        "kills_by_enemy_type",
        "room_type",
        "enemies_spawned_count",
        "elite_enemies_count",
        "ambush_flag",
        "spawn_pattern_type",
        "spawn_delay_profile",
        "reinforcement_applied",
        "hazard_tiles_count",
        "time_in_hazard_tiles",
        "damage_from_hazards",
        "hazard_type_distribution",
        "movement_distance",
        "idle_time",
        "dash_count",
        "time_near_enemies",
        "time_far_from_enemies",
        "room_result",
        "clean_clear_flag",
        "heavy_damage_flag",
        "near_death_flag",
        "death_flag",
        "death_room_index",
        "death_biome_index",
        "reward_dropped_flag",
        "reward_collected_flag",
        "reward_type",
        "reward_value",
        "time_to_collect_reward",
        "reward_missed_flag",
        "healing_orb_collected_count",
        "healing_amount_collected",
        "healing_wasted",
        "upgrade_options_count",
        "upgrade_selected_type",
        "upgrade_selected_id",
        "upgrade_power_value",
        "upgrade_skipped_flag",
    ):
        val = getattr(room, name)
        if name in ("damage_taken_by_enemy_type", "kills_by_enemy_type"):
            setattr(rm, name, dict(val))
        else:
            setattr(rm, name, val)


class MetricsTracker:
    """Accumulates run-level and per-room metrics (Metrics_Tracker.md)."""

    def __init__(self, difficulty_params: DifficultyParams | None = None) -> None:
        self._dp: DifficultyParams = difficulty_params or load_difficulty_params_json()
        self.run: RunMetrics = RunMetrics()
        self._room: RoomMetrics | None = None
        self._room_t0: float = 0.0
        self._last_biome: int = -1
        # Game loop sets these so update(dt) can split idle / hazard / proximity time.
        self.player_idle: bool = False
        self.in_hazard: bool = False
        self.near_enemy: bool = False

    def start_run(self, seed: int) -> None:
        self.run = RunMetrics()
        self.run.run_seed = int(seed)
        self.run.run_start_time = 0.0
        self.run.run_elapsed_time = 0.0
        self._room = None
        self._last_biome = -1
        self._room_t0 = 0.0

    def start_room(
        self, room_index: int, biome_index: int, hp_percent: float, *, room_type: str = ""
    ) -> None:
        now = self.run.run_elapsed_time
        if self._room is not None and self._room.room_active_flag:
            self.end_room(hp_percent)

        if biome_index != self._last_biome:
            if self._last_biome >= 0:
                self._flush_biome_segment(now)
            self._last_biome = biome_index
            self.run.biome_start_time = now
            self.run.biome_damage_taken = 0.0
            self.run.biome_deaths = 0
            self.run.biome_end_time = 0.0
            self.run.biome_clear_time = 0.0

        self._room = RoomMetrics()
        r = self._room
        r.current_room_index = int(room_index)
        r.current_biome_index = int(biome_index)
        r.room_type = str(room_type)
        r.room_start_time = now
        r.room_active_flag = True
        r.hp_percent_start_room = float(hp_percent)
        r.hp_percent_end_room = float(hp_percent)
        r.max_hp_during_room = float(hp_percent)
        r.min_hp_during_room = float(hp_percent)
        self._room_t0 = now

        self.run.current_room_index = int(room_index)
        self.run.current_biome_index = int(biome_index)
        self.run.room_active_flag = True
        self.run.room_start_time = now
        self.run.kill_count_room = 0
        self.run.hp_percent_start_room = float(hp_percent)
        self.run.hp_percent_end_room = float(hp_percent)
        self.run.max_hp_during_room = float(hp_percent)
        self.run.min_hp_during_room = float(hp_percent)
        _sync_run_from_room(self.run, r)

    def set_room_spawn_metadata(
        self,
        *,
        enemy_count: int,
        composition: list[str],
        elite_count: int,
        reinforcement_applied: bool,
    ) -> None:
        """After spawn specs are finalized for the current room (no gameplay effect)."""
        if self._room is None or not self._room.room_active_flag:
            return
        self._room.enemies_spawned_count = int(enemy_count)
        self._room.elite_enemies_count = int(elite_count)
        self._room.enemy_types_in_room = ",".join(composition)
        self._room.enemy_composition_id = "|".join(sorted(composition))
        self._room.reinforcement_applied = bool(reinforcement_applied)
        _sync_run_from_room(self.run, self._room)

    def append_runtime_spawn_metadata(
        self,
        *,
        names: list[str],
        elite_flags: list[bool] | None = None,
        mark_reinforcement: bool = True,
    ) -> None:
        """Hostiles spawned outside initial spawn_specs (logging only; does not affect gameplay)."""
        if self._room is None or not self._room.room_active_flag or not names:
            return
        flags = elite_flags if elite_flags is not None else [False] * len(names)
        if len(flags) != len(names):
            return
        r = self._room
        existing = [x for x in str(r.enemy_types_in_room).split(",") if x]
        combined = existing + list(names)
        r.enemies_spawned_count = int(r.enemies_spawned_count) + len(names)
        r.elite_enemies_count = int(r.elite_enemies_count) + sum(1 for e in flags if e)
        r.enemy_types_in_room = ",".join(combined)
        r.enemy_composition_id = "|".join(sorted(combined))
        if mark_reinforcement:
            r.reinforcement_applied = True
        _sync_run_from_room(self.run, r)

    def record_player_hp_percent(self, hp_percent: float) -> None:
        """
        Call each frame (or after discrete HP changes) while a room is active.
        Maintains min/max HP % during the room so end_room hp_lost_in_room and room_result are correct.
        """
        if self._room is None or not self._room.room_active_flag:
            return
        hp = float(hp_percent)
        if hp < self._room.min_hp_during_room:
            self._room.min_hp_during_room = hp
        if hp > self._room.max_hp_during_room:
            self._room.max_hp_during_room = hp
        _sync_run_from_room(self.run, self._room)

    def end_room(self, hp_percent: float) -> None:
        if self._room is None or not self._room.room_active_flag:
            return

        now = self.run.run_elapsed_time
        room = self._room
        # Fold exit HP into extrema so end_room is correct even if called in the same frame before record_player_hp_percent.
        hp_end = float(hp_percent)
        room.min_hp_during_room = min(room.min_hp_during_room, hp_end)
        room.max_hp_during_room = max(room.max_hp_during_room, hp_end)
        _sync_run_from_room(self.run, room)

        room.room_end_time = now
        dur = max(now - self._room_t0, 1e-9)
        room.room_clear_time = dur
        room.hp_percent_end_room = hp_end
        room.hp_lost_in_room = max(0.0, room.hp_percent_start_room - room.min_hp_during_room)
        room.hp_gained_in_room = room.healing_amount_collected
        room.damage_taken_rate = room.damage_taken_in_room / dur
        room.damage_dealt_rate = room.damage_dealt_in_room / dur

        hp_loss_pct = room.hp_lost_in_room
        if room.death_flag:
            room.room_result = RoomResult.death
        elif room.min_hp_during_room < 15.0:
            room.room_result = RoomResult.near_death
        elif hp_loss_pct > self._dp.metrics.struggle_hp_loss_percent_threshold:
            room.room_result = RoomResult.damaged_clear
        else:
            room.room_result = RoomResult.clean_clear

        room.clean_clear_flag = room.room_result == RoomResult.clean_clear
        room.heavy_damage_flag = hp_loss_pct >= _HEAVY_DAMAGE_HP_LOSS_PCT
        room.near_death_flag = room.room_result == RoomResult.near_death or room.min_hp_during_room < 15.0
        room.death_flag = room.room_result == RoomResult.death

        room.kill_count_total = self.run.kill_count_total

        self.run.rooms_cleared += 1
        self.run.biome_clear_time = now - self.run.biome_start_time

        self._push_last_3(hp_loss_pct, dur, room.room_result.value)
        lst = self.run.last_3_rooms_result
        self.run.recent_death_flag = len(lst) > 0 and lst[-1] == RoomResult.death.value
        self.run.recent_struggle_flag = len(lst) > 0 and lst[-1] in (
            RoomResult.damaged_clear.value,
            RoomResult.near_death.value,
        )
        dom_thr = float(self._dp.metrics.dominating_hp_loss_percent_threshold)
        self.run.recent_dominating_flag = len(lst) > 0 and lst[-1] == RoomResult.clean_clear.value and hp_loss_pct < dom_thr

        if hp_loss_pct > self._dp.metrics.struggle_hp_loss_percent_threshold:
            self.run.struggling_rooms_count += 1
        elif hp_loss_pct < dom_thr and not room.death_flag:
            self.run.dominating_rooms_count += 1

        # Room is complete; must be False before archive + final sync so run.room_active_flag is not
        # overwritten True by _sync_run_from_room (fixes duplicate room_end logs on door exit).
        room.room_active_flag = False
        archived = copy.deepcopy(room)
        self.run.room_history.append(archived)

        if DEBUG_ROOM_HP_METRICS_PRINT:
            print(
                "[ROOM HP METRICS] "
                f"room_idx={room.current_room_index} "
                f"hp_start={room.hp_percent_start_room:.2f} "
                f"min={room.min_hp_during_room:.2f} max={room.max_hp_during_room:.2f} "
                f"hp_end={room.hp_percent_end_room:.2f} "
                f"hp_lost={room.hp_lost_in_room:.2f} "
                f"result={room.room_result.value}"
            )

        self.run.room_end_time = now
        self.run.room_clear_time = dur
        self.run.hp_percent_end_room = float(hp_percent)
        _sync_run_from_room(self.run, room)
        self._room = None

    def record_damage_taken(self, amount: float, enemy_type: str) -> None:
        if amount <= 0:
            return
        et = str(enemy_type)
        self.run.total_damage_taken += amount
        self.run.biome_damage_taken += amount
        if amount >= float(self._dp.metrics.spike_damage_threshold):
            self.run.spike_damage_events += 1
        self.run.damage_taken_in_room += amount
        self.run.hits_taken_count += 1
        rd = self.run.damage_taken_by_enemy_type
        rd[et] = rd.get(et, 0.0) + amount
        if self._room is not None:
            self._room.damage_taken_in_room += amount
            self._room.hits_taken_count += 1
            d = self._room.damage_taken_by_enemy_type
            d[et] = d.get(et, 0.0) + amount
            if "hazard" in et:
                self._room.damage_from_hazards += float(amount)
                self.run.damage_from_hazards += float(amount)
            _sync_run_from_room(self.run, self._room)

    def record_damage_dealt(self, amount: float) -> None:
        if amount <= 0:
            return
        self.run.total_damage_dealt += amount
        self.run.damage_dealt_in_room += amount
        self.run.hits_given_count += 1
        if self._room is not None:
            self._room.damage_dealt_in_room += amount
            self._room.hits_given_count += 1
            _sync_run_from_room(self.run, self._room)

    def record_kill(self, enemy_type: str) -> None:
        et = str(enemy_type)
        self.run.kill_count_total += 1
        kr = self.run.kills_by_enemy_type
        kr[et] = kr.get(et, 0) + 1
        if self._room is not None:
            self._room.kill_count_room += 1
            k = self._room.kills_by_enemy_type
            k[et] = k.get(et, 0) + 1
            _sync_run_from_room(self.run, self._room)

    def record_healing(self, amount: float) -> None:
        if amount <= 0:
            return
        self.run.total_healing_received += amount
        self.run.healing_amount_collected += amount
        self.run.healing_orb_collected_count += 1
        if self._room is not None:
            self._room.healing_amount_collected += amount
            self._room.healing_orb_collected_count += 1
            _sync_run_from_room(self.run, self._room)

    def record_reward(self, type: str, value: float) -> None:
        self.run.total_rewards_collected += 1
        self.run.reward_type = str(type)
        self.run.reward_value = float(value)
        self.run.reward_collected_flag = True
        if self._room is not None:
            self._room.reward_type = str(type)
            self._room.reward_value = float(value)
            self._room.reward_collected_flag = True
            _sync_run_from_room(self.run, self._room)

    def record_upgrade(self, type: str, id: str) -> None:
        self.run.total_upgrades_selected += 1
        self.run.upgrade_selected_type = str(type)
        self.run.upgrade_selected_id = str(id)
        if self._room is not None:
            self._room.upgrade_selected_type = str(type)
            self._room.upgrade_selected_id = str(id)
            _sync_run_from_room(self.run, self._room)

    def record_rl_interact_success(self) -> None:
        """Room 0 altar open or story close via E (gameplay event; used by RL reward only)."""
        self.run.rl_interact_success_count += 1

    def record_rl_safe_room_heal_success(self) -> None:
        """Safe-room F heal applied with HP gain (paired with record_healing)."""
        self.run.rl_safe_room_heal_success_count += 1

    def record_rl_safe_room_heal_failed(self) -> None:
        """Safe-room F pressed in valid context but no HP applied (e.g. already full)."""
        self.run.rl_safe_room_heal_failed_count += 1

    def record_rl_interact_failed_e(self) -> None:
        """RL dispatched E but no interact success this frame (anti-spam; RL path only)."""
        self.run.rl_interact_failed_e_count += 1

    def record_rl_reserve_heal_success(self) -> None:
        """RL path: reserve H consumed with HP gain (paired with record_healing)."""
        self.run.rl_reserve_heal_success_count += 1

    def record_rl_reserve_heal_failed(self) -> None:
        """RL path: H pressed but no heal (empty pool, full HP, or on cooldown)."""
        self.run.rl_reserve_heal_failed_count += 1

    def record_death(self) -> None:
        self.run.total_deaths += 1
        self.run.biome_deaths += 1
        self.run.death_flag = True
        self.run.death_room_index = self.run.current_room_index
        self.run.death_biome_index = self.run.current_biome_index
        if self._room is not None:
            self._room.death_flag = True
            self._room.death_room_index = self._room.current_room_index
            self._room.death_biome_index = self._room.current_biome_index
            _sync_run_from_room(self.run, self._room)

    def update(self, dt: float) -> None:
        if dt <= 0:
            return
        self.run.run_elapsed_time += dt
        if self._room is not None and self._room.room_active_flag:
            if self.player_idle:
                self._room.idle_time += dt
                self.run.idle_time += dt
            if self.in_hazard:
                self._room.time_in_hazard_tiles += dt
                self.run.time_in_hazard_tiles += dt
            if self.near_enemy:
                self._room.time_near_enemies += dt
                self.run.time_near_enemies += dt
            else:
                self._room.time_far_from_enemies += dt
                self.run.time_far_from_enemies += dt
            _sync_run_from_room(self.run, self._room)

    def _flush_biome_segment(self, now: float) -> None:
        self.run.biome_end_time = now
        self.run.biome_clear_time = max(0.0, now - self.run.biome_start_time)
        self.run.biome_history.append(
            {
                "biome_start_time": self.run.biome_start_time,
                "biome_end_time": self.run.biome_end_time,
                "biome_clear_time": self.run.biome_clear_time,
                "biome_damage_taken": self.run.biome_damage_taken,
                "biome_deaths": self.run.biome_deaths,
            }
        )
        self.run.biomes_cleared += 1

    def _push_last_3(self, hp_loss: float, clear_t: float, result: str) -> None:
        a = self.run.last_3_rooms_hp_loss
        b = self.run.last_3_rooms_clear_time
        c = self.run.last_3_rooms_result
        a.append(hp_loss)
        b.append(clear_t)
        c.append(result)
        while len(a) > 3:
            a.pop(0)
        while len(b) > 3:
            b.pop(0)
        while len(c) > 3:
            c.pop(0)
