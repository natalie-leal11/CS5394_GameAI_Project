"""
Per-step reward computation for DungeonEnv (Step 3 + Step 6 shaping).

# RL-only path — safe to remove if RL is abandoned

Uses snapshot deltas from GameScene / MetricsTracker; does not mutate gameplay.

Step 14 redesign: prioritize room progression and objective travel over local spam (reserve H,
stand-still combat). Stronger progression / E / F / upgrade benefits; reserve-heal misuse penalty;
``progress_room`` / ``progress_travel`` breakdown; stall/timeout slightly stronger.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

from rl.action_map import ACTION_SHORT_ATTACK

# ---------------------------------------------------------------------------
# Tunable reward scales (small, interpretable; clamp total in compute).
# Priority (conceptual): 1) room progression  2) interact/safe benefits  3) heals/upgrades
# 4) combat success  5) anti-spam / stall
# ---------------------------------------------------------------------------
R_VICTORY = 1.5
R_DEFEAT = -1.5
R_LIFE_LOSS_PER = -0.5

R_KILL_NORMAL = 0.12
R_KILL_BOSS = 0.55

# Step 14: stronger dungeon progression than local combat/heal spam.
R_ROOM_CLEAR = 0.58
R_ROOM_ENTRY_FORWARD = 0.24

# Damage: negative proportional to fraction of max HP lost this step.
R_DAMAGE_HP_RATIO_COEF = -0.006
# Healing: small positive; capped so safe-room / orb loops are not exploitable.
R_HEAL_HP_RATIO_COEF = 0.04
R_HEAL_PER_STEP_CAP = 0.02

# Step 6: removed passive alive bonus (was encouraging survive-without-progress).
R_ALIVE_BONUS = 0.0
# Living cost / anti-idle per step.
R_STEP_COST = -0.002

# Stagnation: no macro progress — slightly stronger than pre–Step 14.
R_STALL_THRESHOLD_STEPS = 1800  # ~30 s at 60 FPS
R_STALL_PENALTY = -0.045  # applied once when crossing threshold, then every +600 steps while stuck

# TimeLimit / truncation — applied in TimeoutPenaltyWrapper (see rl.wrappers).
R_TIMEOUT_PENALTY = -0.65  # discourages timeout-only policies

# Step 14: objective-directed travel (merged enemy + door approach; stronger than old coefs).
R_APPROACH_ENEMY_COEF = 0.00034
R_APPROACH_MAX_DELTA_PX = 55.0
R_APPROACH_DOOR_COEF = 0.00048
R_APPROACH_DOOR_MAX_DELTA_PX = 55.0

# Enemy damage reward (combat success tier).
R_ENEMY_DAMAGE_COEF = 0.00012
R_ENEMY_DAMAGE_MAX_PER_STEP = 0.04

# Micro idle — no meaningful movement, no progress, no enemy damage.
MICRO_IDLE_MOVE_THRESHOLD_PX = 1.5
MICRO_IDLE_THRESHOLD_STEPS = 180
MICRO_IDLE_PENALTY_INTERVAL = 60
R_ANTI_IDLE_EXTRA = -0.0012

# Hazard / lava (MetricsTracker run).
R_HAZARD_DAMAGE_COEF = -0.005
R_HAZARD_DAMAGE_STEP_CAP = 0.04
R_HAZARD_TIME_PER_SEC = -0.012
R_HAZARD_TIME_DT_CAP = 0.25
R_HAZARD_COMBINED_STEP_CAP = 0.06

# Discrete heal events (orb, safe-room F, reserve H when applied).
R_BENEFIT_HEAL_EVENT = 0.06
R_BENEFIT_HEAL_STEP_CAP = 0.08
# Safe-room stat choice — stronger than generic heal.
R_BENEFIT_UPGRADE = 0.2

# Successful E / extra on safe-room F (delta on rl_* counters).
R_BENEFIT_INTERACT = 0.2
R_BENEFIT_INTERACT_STEP_CAP = 0.28
R_BENEFIT_SAFE_ROOM_HEAL_EXTRA = 0.16
R_BENEFIT_SAFE_HEAL_STEP_CAP = 0.2

R_FAILED_INTERACT_PER = -0.0035
R_FAILED_SAFE_HEAL_PER = -0.002
R_FAILED_SPAM_STEP_CAP = 0.028  # failed E/F + attack_spam + reserve_heal_spam

# Reserve H misuse (delta on rl_reserve_heal_failed_count; RL-only metrics).
R_RESERVE_HEAL_FAILED_PER = -0.0045

# Anti stationary combat / short-attack spam (Step 13, tuned Step 14).
STATIONARY_COMBAT_MOVE_PX = 2.0
STATIONARY_COMBAT_STEPS_START = 48
STATIONARY_COMBAT_PENALTY_INTERVAL = 12
R_STATIONARY_COMBAT_PENALTY = -0.0012
R_STATIONARY_COMBAT_STEP_CAP = 0.04

COMBAT_MOVE_BONUS_MIN_PX = 3.5
COMBAT_DIST_IMPROVE_MIN_PX = 0.28
R_COMBAT_MOVEMENT_BONUS_COEF = 0.00022
R_COMBAT_MOVEMENT_STEP_CAP = 0.014

SHORT_ATTACK_SPAM_MOVE_PX = 3.0
SHORT_ATTACK_SPAM_STEPS_START = 28
R_SHORT_ATTACK_SPAM_PENALTY = -0.00045
R_ATTACK_SPAM_STEP_CAP = 0.014

# Final safety clamp for non-terminal steps (terminal may use full R_VICTORY / R_DEFEAT).
R_STEP_CLIP = 3.5

# Curriculum E (interact) / F (safe_heal) — replaces generic benefit_interact / benefit_safe_heal for those runs.
CURRICULUM_E_APPROACH_REWARD = 0.02
CURRICULUM_E_INTERACT_BONUS = 1.0
CURRICULUM_E_IDLE_PENALTY = -0.01
CURRICULUM_E_APPROACH_MIN_DELTA_PX = 0.05

CURRICULUM_F_LOW_HP_RATIO = 0.5
CURRICULUM_F_HIGH_HP_RATIO = 0.7
CURRICULUM_F_CORRECT_HEAL = 1.0
CURRICULUM_F_WRONG_HEAL = -0.2
CURRICULUM_F_MISSED_HEAL_PER_STEP = -0.02

_BOSS_CLASS_NAMES = frozenset({"MiniBoss", "MiniBoss2", "Biome3MiniBoss", "FinalBoss"})
# Curriculum interact: movement (1–4), combat, dash, block/parry, interact, heals (1–12).
_CURRICULUM_MEANINGFUL_ACTIONS = frozenset(range(1, 13))


@dataclass(frozen=True)
class RewardSnapshot:
    """Compact state for delta rewards (one line per field in docs)."""

    hp: float
    max_hp: float
    lives: int
    life_index: int
    room_index: int
    victory: bool
    death_phase: bool
    alive_combat: int
    kill_total: int
    rooms_cleared: int
    combat_enemy_boss: dict[int, bool]
    player_x: float
    player_y: float
    nearest_enemy_dist: float
    enemy_hp_sum: float
    door_goal_dist: float
    damage_from_hazards: float
    time_in_hazard_tiles: float
    heal_events_count: int
    total_upgrades_selected: int
    rl_interact_success_count: int
    rl_safe_room_heal_success_count: int
    rl_safe_room_heal_failed_count: int
    rl_interact_failed_e_count: int
    rl_reserve_heal_failed_count: int
    # Curriculum micro-scenarios: goal distance (altar / heal tile) and active scenario label.
    curriculum_scenario: str | None
    curriculum_goal_dist: float


def merge_timeout_penalty_into_breakdown(breakdown: dict[str, float]) -> dict[str, float]:
    """Copy breakdown and add timeout penalty (used by TimeoutPenaltyWrapper)."""
    out = dict(breakdown)
    out["timeout_penalty"] = float(out.get("timeout_penalty", 0.0)) + R_TIMEOUT_PENALTY
    return out


def _is_combat_enemy(e: Any) -> bool:
    if getattr(e, "inactive", False):
        return False
    if getattr(e, "is_training_dummy", False):
        return False
    hp = getattr(e, "hp", None)
    if hp is not None and float(hp) <= 0.0:
        return False
    st = getattr(e, "state", None)
    if st == "death":
        return False
    return True


def _is_boss_enemy(e: Any) -> bool:
    return type(e).__name__ in _BOSS_CLASS_NAMES


def _nearest_enemy_dist_px(enemies: list[Any], px: float, py: float) -> tuple[float, int]:
    best_d = float("inf")
    n = 0
    for e in enemies:
        if not _is_combat_enemy(e):
            continue
        n += 1
        ex, ey = getattr(e, "world_pos", (0.0, 0.0))
        d = math.hypot(float(ex) - px, float(ey) - py)
        if d < best_d:
            best_d = d
    if n == 0:
        return float("inf"), 0
    return best_d, n


def _sum_combat_enemy_hp(enemies: list[Any]) -> float:
    s = 0.0
    for e in enemies:
        if not _is_combat_enemy(e):
            continue
        hp = getattr(e, "hp", None)
        if hp is None:
            continue
        s += max(0.0, float(hp))
    return s


def _forward_open_door_dist_px(game_scene: Any, px: float, py: float) -> float:
    rc = getattr(game_scene, "_room_controller", None)
    if rc is None:
        return float("inf")
    room = rc.current_room
    if room is None:
        return float("inf")
    cur_idx = int(rc.current_room_index)
    doors = list(rc.door_system.doors())
    best = float("inf")
    try:
        from dungeon.door_system import DoorState
    except Exception:
        return float("inf")
    iter_fn = getattr(game_scene, "_iter_doorways", None)
    if iter_fn is None:
        return float("inf")
    for center_x, center_y, target_room_index, state, _ in iter_fn(doors, room):
        if target_room_index <= cur_idx:
            continue
        if state != DoorState.OPEN:
            continue
        d = math.hypot(float(center_x) - px, float(center_y) - py)
        best = min(best, d)
    return best


def build_reward_snapshot(game_scene: Any) -> RewardSnapshot:
    """Read public GameScene / metrics fields only (no gameplay mutation)."""
    gs = game_scene
    p = getattr(gs, "_player", None)
    hp = float(getattr(p, "hp", 0.0)) if p is not None else 0.0
    max_hp = float(getattr(p, "max_hp", 1.0)) if p is not None else 1.0
    lives = int(getattr(p, "lives", 0)) if p is not None else 0
    life_index = int(getattr(p, "life_index", 0)) if p is not None else 0

    px, py = 0.0, 0.0
    if p is not None:
        w = getattr(p, "world_pos", (0.0, 0.0))
        try:
            px, py = float(w[0]), float(w[1])
        except (TypeError, ValueError, IndexError):
            px, py = 0.0, 0.0

    rc = getattr(gs, "_room_controller", None)
    room_idx = int(rc.current_room_index) if rc is not None else -1

    victory = bool(getattr(gs, "_victory_phase", False))
    dp = getattr(gs, "_death_phase", None)
    death_phase = dp is not None

    enemies = list(getattr(gs, "_enemies", []) or [])
    alive_combat = sum(1 for e in enemies if _is_combat_enemy(e))

    id_boss: dict[int, bool] = {}
    for e in enemies:
        if not _is_combat_enemy(e):
            continue
        id_boss[id(e)] = _is_boss_enemy(e)

    d_nearest, _ = _nearest_enemy_dist_px(enemies, px, py)
    hp_sum = _sum_combat_enemy_hp(enemies)
    d_door = _forward_open_door_dist_px(gs, px, py)

    mt = getattr(gs, "_metrics", None)
    kill_total = 0
    rooms_cleared = 0
    haz_dmg = 0.0
    haz_time = 0.0
    heal_ev = 0
    upgrades = 0
    ri_succ = 0
    rssh = 0
    rs_fail = 0
    rife = 0
    rrh_fail = 0
    if mt is not None:
        run = getattr(mt, "run", None)
        if run is not None:
            kill_total = int(getattr(run, "kill_count_total", 0))
            rooms_cleared = int(getattr(run, "rooms_cleared", 0))
            haz_dmg = float(getattr(run, "damage_from_hazards", 0.0))
            haz_time = float(getattr(run, "time_in_hazard_tiles", 0.0))
            heal_ev = int(getattr(run, "healing_orb_collected_count", 0))
            upgrades = int(getattr(run, "total_upgrades_selected", 0))
            ri_succ = int(getattr(run, "rl_interact_success_count", 0))
            rssh = int(getattr(run, "rl_safe_room_heal_success_count", 0))
            rs_fail = int(getattr(run, "rl_safe_room_heal_failed_count", 0))
            rife = int(getattr(run, "rl_interact_failed_e_count", 0))
            rrh_fail = int(getattr(run, "rl_reserve_heal_failed_count", 0))

    c_scen = getattr(gs, "_rl_curriculum_scenario", None)
    c_scen = str(c_scen) if c_scen is not None else None
    cgd = float("inf")
    if c_scen == "interact":
        ap = getattr(gs, "_room0_altar_pos", None)
        if ap is not None and p is not None:
            try:
                cgd = math.hypot(px - float(ap[0]), py - float(ap[1]))
            except (TypeError, ValueError):
                cgd = float("inf")
    elif c_scen == "safe_heal":
        heal_pos = getattr(gs, "_safe_room_heal_pos", None)
        if heal_pos is not None and p is not None:
            try:
                cgd = math.hypot(px - float(heal_pos[0]), py - float(heal_pos[1]))
            except (TypeError, ValueError):
                cgd = float("inf")

    return RewardSnapshot(
        hp=hp,
        max_hp=max(max_hp, 1e-6),
        lives=lives,
        life_index=life_index,
        room_index=room_idx,
        victory=victory,
        death_phase=death_phase,
        alive_combat=alive_combat,
        kill_total=kill_total,
        rooms_cleared=rooms_cleared,
        combat_enemy_boss=id_boss,
        player_x=px,
        player_y=py,
        nearest_enemy_dist=float(d_nearest),
        enemy_hp_sum=float(hp_sum),
        door_goal_dist=float(d_door),
        damage_from_hazards=haz_dmg,
        time_in_hazard_tiles=haz_time,
        heal_events_count=heal_ev,
        total_upgrades_selected=upgrades,
        rl_interact_success_count=ri_succ,
        rl_safe_room_heal_success_count=rssh,
        rl_safe_room_heal_failed_count=rs_fail,
        rl_interact_failed_e_count=rife,
        rl_reserve_heal_failed_count=rrh_fail,
        curriculum_scenario=c_scen,
        curriculum_goal_dist=float(cgd),
    )


@dataclass
class RewardState:
    """One-time bookkeeping across an episode (RL env-owned)."""

    paid_victory: bool = False
    paid_defeat: bool = False
    stagnation_steps: int = 0
    micro_idle_steps: int = 0
    combat_stationary_steps: int = 0
    short_attack_spam_steps: int = 0

    def reset(self) -> None:
        self.paid_victory = False
        self.paid_defeat = False
        self.stagnation_steps = 0
        self.micro_idle_steps = 0
        self.combat_stationary_steps = 0
        self.short_attack_spam_steps = 0


def _killed_enemy_ids(prev: RewardSnapshot, curr: RewardSnapshot) -> set[int]:
    prev_ids = frozenset(prev.combat_enemy_boss.keys())
    curr_ids = frozenset(curr.combat_enemy_boss.keys())
    return set(prev_ids) - set(curr_ids)


def compute_step_reward(
    prev: RewardSnapshot,
    curr: RewardSnapshot,
    state: RewardState,
    *,
    terminated: bool,
    action: int | None = None,
) -> tuple[float, dict[str, float]]:
    """
    Incremental reward from prev -> curr. Terminal flags use one-shot payment via state.

    Returns (total, breakdown) with breakdown values summing to total (within float noise).
    """
    b: dict[str, float] = {
        "victory": 0.0,
        "defeat": 0.0,
        "damage": 0.0,
        "life_loss": 0.0,
        "heal": 0.0,
        "kill_normal": 0.0,
        "kill_boss": 0.0,
        "progress_room": 0.0,
        "progress_travel": 0.0,
        "alive_bonus": 0.0,
        "step_cost": 0.0,
        "stall_timeout": 0.0,
        "timeout_penalty": 0.0,
        "enemy_damage": 0.0,
        "anti_idle": 0.0,
        "hazard": 0.0,
        "benefit_heal": 0.0,
        "benefit_upgrade": 0.0,
        "benefit_interact": 0.0,
        "benefit_safe_heal": 0.0,
        "failed_interact": 0.0,
        "failed_safe_heal": 0.0,
        "reserve_heal_spam": 0.0,
        "stationary_combat": 0.0,
        "combat_movement": 0.0,
        "attack_spam": 0.0,
        "curriculum_e_approach": 0.0,
        "curriculum_e_interact": 0.0,
        "curriculum_e_idle": 0.0,
        "curriculum_f_heal": 0.0,
        "curriculum_f_missed": 0.0,
    }

    scen = prev.curriculum_scenario
    same_room = prev.room_index == curr.room_index and prev.room_index >= 0
    moved = (
        math.hypot(curr.player_x - prev.player_x, curr.player_y - prev.player_y)
        if same_room
        else 0.0
    )
    dhp_same = (
        max(0.0, prev.enemy_hp_sum - curr.enemy_hp_sum) if same_room else 0.0
    )
    prog_step = (
        curr.kill_total > prev.kill_total
        or curr.room_index != prev.room_index
        or curr.rooms_cleared > prev.rooms_cleared
    )

    # --- Terminal (one-shot) ---
    if curr.victory and not state.paid_victory:
        b["victory"] = R_VICTORY
        state.paid_victory = True
    if curr.death_phase and not state.paid_defeat:
        b["defeat"] = R_DEFEAT
        state.paid_defeat = True

    # --- Life loss (per life dropped this step) ---
    if curr.lives < prev.lives:
        lost = prev.lives - curr.lives
        b["life_loss"] = R_LIFE_LOSS_PER * float(max(0, lost))

    # --- HP delta: damage vs heal ---
    mhp = max(prev.max_hp, 1e-6)
    hp_delta = curr.hp - prev.hp
    if curr.lives >= prev.lives:
        if hp_delta < 0.0:
            ratio = (-hp_delta) / mhp
            b["damage"] = R_DAMAGE_HP_RATIO_COEF * float(ratio)
        elif hp_delta > 0.0:
            ratio = hp_delta / mhp
            heal = R_HEAL_HP_RATIO_COEF * float(ratio)
            b["heal"] = float(min(heal, R_HEAL_PER_STEP_CAP))

    # --- Hazard / lava ---
    mhp_h = max(prev.max_hp, 1e-6)
    d_haz_dmg = max(0.0, curr.damage_from_hazards - prev.damage_from_hazards)
    d_haz_time = max(0.0, curr.time_in_hazard_tiles - prev.time_in_hazard_tiles)
    hz = 0.0
    if d_haz_dmg > 0.0:
        hz += float(R_HAZARD_DAMAGE_COEF * (d_haz_dmg / mhp_h))
        hz = float(max(hz, -R_HAZARD_DAMAGE_STEP_CAP))
    if d_haz_time > 0.0:
        hz += float(R_HAZARD_TIME_PER_SEC * min(d_haz_time, R_HAZARD_TIME_DT_CAP))
    if hz < 0.0:
        hz = float(max(hz, -R_HAZARD_COMBINED_STEP_CAP))
    b["hazard"] = hz

    # --- Heals / upgrades (event-based) ---
    d_heal_ev = max(0, curr.heal_events_count - prev.heal_events_count)
    if d_heal_ev > 0:
        b["benefit_heal"] = float(
            min(R_BENEFIT_HEAL_EVENT * float(d_heal_ev), R_BENEFIT_HEAL_STEP_CAP)
        )
    d_upg = max(0, curr.total_upgrades_selected - prev.total_upgrades_selected)
    if d_upg > 0:
        b["benefit_upgrade"] = float(R_BENEFIT_UPGRADE * float(d_upg))

    # --- E / F success + failed E/F ---
    d_ri = max(0, curr.rl_interact_success_count - prev.rl_interact_success_count)
    if d_ri > 0 and scen != "interact":
        b["benefit_interact"] = float(
            min(R_BENEFIT_INTERACT * float(d_ri), R_BENEFIT_INTERACT_STEP_CAP)
        )
    d_ssh = max(0, curr.rl_safe_room_heal_success_count - prev.rl_safe_room_heal_success_count)
    if d_ssh > 0 and scen != "safe_heal":
        b["benefit_safe_heal"] = float(
            min(R_BENEFIT_SAFE_ROOM_HEAL_EXTRA * float(d_ssh), R_BENEFIT_SAFE_HEAL_STEP_CAP)
        )
    d_fail_e = max(0, curr.rl_interact_failed_e_count - prev.rl_interact_failed_e_count)
    d_fail_sf = max(0, curr.rl_safe_room_heal_failed_count - prev.rl_safe_room_heal_failed_count)
    if d_fail_e > 0:
        b["failed_interact"] = float(R_FAILED_INTERACT_PER * float(d_fail_e))
    if d_fail_sf > 0:
        b["failed_safe_heal"] = float(R_FAILED_SAFE_HEAL_PER * float(d_fail_sf))

    d_fail_rh = max(0, curr.rl_reserve_heal_failed_count - prev.rl_reserve_heal_failed_count)
    if d_fail_rh > 0:
        b["reserve_heal_spam"] = float(R_RESERVE_HEAL_FAILED_PER * float(d_fail_rh))

    # --- Stationary combat / combat movement / short-attack spam ---
    if same_room and not terminated and curr.alive_combat > 0:
        stuck = (
            moved < STATIONARY_COMBAT_MOVE_PX
            and not prog_step
            and dhp_same <= 1e-6
        )
        if stuck:
            state.combat_stationary_steps += 1
        else:
            state.combat_stationary_steps = 0
        if state.combat_stationary_steps >= STATIONARY_COMBAT_STEPS_START:
            k = state.combat_stationary_steps - STATIONARY_COMBAT_STEPS_START
            if k % STATIONARY_COMBAT_PENALTY_INTERVAL == 0:
                b["stationary_combat"] = float(
                    max(R_STATIONARY_COMBAT_PENALTY, -R_STATIONARY_COMBAT_STEP_CAP)
                )

        dist_improve = 0.0
        if math.isfinite(prev.nearest_enemy_dist) and math.isfinite(curr.nearest_enemy_dist):
            dist_improve = max(0.0, float(prev.nearest_enemy_dist) - float(curr.nearest_enemy_dist))
        productive = dhp_same > 1e-6 or dist_improve >= COMBAT_DIST_IMPROVE_MIN_PX
        if productive and moved >= COMBAT_MOVE_BONUS_MIN_PX:
            raw_cm = R_COMBAT_MOVEMENT_BONUS_COEF * float(min(moved, 22.0))
            b["combat_movement"] = float(min(raw_cm, R_COMBAT_MOVEMENT_STEP_CAP))
    else:
        state.combat_stationary_steps = 0

    if action is not None and int(action) == ACTION_SHORT_ATTACK:
        low_move = moved < SHORT_ATTACK_SPAM_MOVE_PX
        no_dmg = dhp_same <= 1e-6
        if (
            same_room
            and not terminated
            and curr.alive_combat > 0
            and low_move
            and no_dmg
        ):
            state.short_attack_spam_steps += 1
        else:
            state.short_attack_spam_steps = 0
        if state.short_attack_spam_steps >= SHORT_ATTACK_SPAM_STEPS_START:
            b["attack_spam"] = float(
                max(R_SHORT_ATTACK_SPAM_PENALTY, -R_ATTACK_SPAM_STEP_CAP)
            )
    else:
        state.short_attack_spam_steps = 0

    _spam = (
        abs(b["failed_interact"])
        + abs(b["failed_safe_heal"])
        + abs(b["attack_spam"])
        + abs(b["reserve_heal_spam"])
    )
    if _spam > R_FAILED_SPAM_STEP_CAP and _spam > 1e-9:
        scale = R_FAILED_SPAM_STEP_CAP / _spam
        b["failed_interact"] *= scale
        b["failed_safe_heal"] *= scale
        b["attack_spam"] *= scale
        b["reserve_heal_spam"] *= scale

    # --- Kills ---
    if prev.room_index == curr.room_index:
        killed = _killed_enemy_ids(prev, curr)
        for eid in killed:
            was_boss = prev.combat_enemy_boss.get(eid, False)
            if was_boss:
                b["kill_boss"] += R_KILL_BOSS
            else:
                b["kill_normal"] += R_KILL_NORMAL
    else:
        dk = max(0, curr.kill_total - prev.kill_total)
        if dk:
            b["kill_normal"] += R_KILL_NORMAL * float(dk)

    # --- Room progression (stronger tier) ---
    pr = 0.0
    if curr.rooms_cleared > prev.rooms_cleared:
        delta_rc = curr.rooms_cleared - prev.rooms_cleared
        pr += R_ROOM_CLEAR * float(max(0, delta_rc))
    if curr.room_index > prev.room_index and prev.room_index >= 0:
        pr += R_ROOM_ENTRY_FORWARD * float(curr.room_index - prev.room_index)
    if pr > 0.0:
        b["progress_room"] = float(pr)

    # --- Survival + step cost ---
    if not terminated:
        b["alive_bonus"] = R_ALIVE_BONUS if curr.hp > 0.0 and not curr.death_phase else 0.0
        b["step_cost"] = R_STEP_COST

    # --- Stagnation (macro no-progress) ---
    if prog_step:
        state.stagnation_steps = 0
    else:
        state.stagnation_steps += 1

    if state.stagnation_steps >= R_STALL_THRESHOLD_STEPS:
        s = state.stagnation_steps - R_STALL_THRESHOLD_STEPS
        if s % 600 == 0:
            b["stall_timeout"] = R_STALL_PENALTY

    # --- Objective travel: approach enemy in combat, else approach forward door (no random wander) ---
    if same_room and not terminated:
        dhp = max(0.0, prev.enemy_hp_sum - curr.enemy_hp_sum)
        if dhp > 0.0:
            b["enemy_damage"] = R_ENEMY_DAMAGE_COEF * float(min(dhp, 200.0))
            b["enemy_damage"] = float(min(b["enemy_damage"], R_ENEMY_DAMAGE_MAX_PER_STEP))

        travel = 0.0
        if curr.alive_combat > 0:
            if math.isfinite(prev.nearest_enemy_dist) and math.isfinite(curr.nearest_enemy_dist):
                delta = max(0.0, prev.nearest_enemy_dist - curr.nearest_enemy_dist)
                delta = min(delta, R_APPROACH_MAX_DELTA_PX)
                travel += R_APPROACH_ENEMY_COEF * delta
        else:
            if math.isfinite(prev.door_goal_dist) and math.isfinite(curr.door_goal_dist):
                delta = max(0.0, prev.door_goal_dist - curr.door_goal_dist)
                delta = min(delta, R_APPROACH_DOOR_MAX_DELTA_PX)
                travel += R_APPROACH_DOOR_COEF * delta
        if travel > 0.0:
            b["progress_travel"] = float(travel)

        progress_step_micro = prog_step or (dhp > 1e-6)
        if progress_step_micro or moved >= MICRO_IDLE_MOVE_THRESHOLD_PX:
            state.micro_idle_steps = 0
        else:
            state.micro_idle_steps += 1
        if state.micro_idle_steps >= MICRO_IDLE_THRESHOLD_STEPS:
            k = state.micro_idle_steps - MICRO_IDLE_THRESHOLD_STEPS
            if k % MICRO_IDLE_PENALTY_INTERVAL == 0:
                b["anti_idle"] = R_ANTI_IDLE_EXTRA

    else:
        state.micro_idle_steps = 0

    # --- Curriculum E/F shaping (replaces generic benefit_interact / benefit_safe_heal for those runs) ---
    if scen == "interact":
        if math.isfinite(prev.curriculum_goal_dist) and math.isfinite(curr.curriculum_goal_dist):
            closer = float(prev.curriculum_goal_dist) - float(curr.curriculum_goal_dist)
            if closer > CURRICULUM_E_APPROACH_MIN_DELTA_PX:
                b["curriculum_e_approach"] = CURRICULUM_E_APPROACH_REWARD
        if d_ri > 0:
            b["curriculum_e_interact"] = CURRICULUM_E_INTERACT_BONUS * float(d_ri)
        if not terminated:
            meaningful = moved >= MICRO_IDLE_MOVE_THRESHOLD_PX or (
                action is not None and int(action) in _CURRICULUM_MEANINGFUL_ACTIONS
            )
            if not meaningful:
                b["curriculum_e_idle"] = CURRICULUM_E_IDLE_PENALTY
    elif scen == "safe_heal":
        if d_ssh > 0:
            hp_ratio = float(prev.hp) / float(max(prev.max_hp, 1e-6))
            if hp_ratio < CURRICULUM_F_LOW_HP_RATIO:
                b["curriculum_f_heal"] = CURRICULUM_F_CORRECT_HEAL
            elif hp_ratio > CURRICULUM_F_HIGH_HP_RATIO:
                b["curriculum_f_heal"] = CURRICULUM_F_WRONG_HEAL
        elif not terminated:
            hp_ratio = float(prev.hp) / float(max(prev.max_hp, 1e-6))
            if hp_ratio < CURRICULUM_F_LOW_HP_RATIO:
                b["curriculum_f_missed"] = CURRICULUM_F_MISSED_HEAL_PER_STEP

    total = float(sum(b.values()))
    terminal_big = b["victory"] != 0.0 or b["defeat"] != 0.0
    if not terminal_big:
        total = float(np.clip(total, -R_STEP_CLIP, R_STEP_CLIP))

    return total, b
