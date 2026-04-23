"""RL reward breakdown (mirrors unit coverage; rl/ package location)."""

from __future__ import annotations

import pytest

from rl.reward import (
    R_DAMAGE_HP_RATIO_COEF,
    R_DEFEAT,
    R_FAILED_SPAM_STEP_CAP,
    R_HEAL_PER_STEP_CAP,
    R_ROOM_ENTRY_FORWARD,
    R_STEP_CLIP,
    R_STALL_PENALTY,
    R_STALL_THRESHOLD_STEPS,
    R_VICTORY,
    RewardSnapshot,
    RewardState,
    compute_step_reward,
)


def _snap(**kw):
    d = dict(
        hp=100.0,
        max_hp=100.0,
        lives=3,
        life_index=0,
        room_index=0,
        victory=False,
        death_phase=False,
        alive_combat=0,
        kill_total=0,
        rooms_cleared=0,
        combat_enemy_boss={},
        player_x=0.0,
        player_y=0.0,
        nearest_enemy_dist=float("inf"),
        enemy_hp_sum=0.0,
        door_goal_dist=float("inf"),
        damage_from_hazards=0.0,
        time_in_hazard_tiles=0.0,
        heal_events_count=0,
        total_upgrades_selected=0,
        rl_interact_success_count=0,
        rl_safe_room_heal_success_count=0,
        rl_safe_room_heal_failed_count=0,
        rl_interact_failed_e_count=0,
        rl_reserve_heal_failed_count=0,
    )
    d.update(kw)
    return RewardSnapshot(**d)


def test_components_sum_to_step_reward():
    prev, curr = _snap(), _snap()
    st = RewardState()
    total, br = compute_step_reward(prev, curr, st, terminated=False)
    s = sum(br.values())
    assert abs(s - total) < 1e-2


def test_terminal_reward_paid_once():
    prev = _snap(victory=False)
    curr = _snap(victory=True)
    st = RewardState()
    compute_step_reward(prev, curr, st, terminated=True)
    assert st.paid_victory


def test_stall_penalty_threshold():
    assert R_STALL_THRESHOLD_STEPS > 0


def test_reset_boundary_reward_zero_consistency():
    prev, curr = _snap(), _snap()
    st = RewardState()
    total, _ = compute_step_reward(prev, curr, st, terminated=False)
    assert isinstance(total, float)


def test_damage_hp_loss_negative_contribution() -> None:
    prev = _snap(hp=100.0, max_hp=100.0)
    curr = _snap(hp=70.0, max_hp=100.0)
    st = RewardState()
    _t, b = compute_step_reward(prev, curr, st, terminated=False)
    expected = R_DAMAGE_HP_RATIO_COEF * 0.3
    assert b["damage"] == pytest.approx(expected, rel=1e-5)


def test_heal_hp_gain_positive_capped() -> None:
    prev = _snap(hp=50.0, max_hp=100.0)
    curr = _snap(hp=90.0, max_hp=100.0)
    st = RewardState()
    _t, b = compute_step_reward(prev, curr, st, terminated=False)
    raw = 0.4 * 0.04
    assert b["heal"] == pytest.approx(min(raw, R_HEAL_PER_STEP_CAP), rel=1e-4)


def test_stall_applies_at_stagnation_threshold() -> None:
    st = RewardState()
    st.stagnation_steps = R_STALL_THRESHOLD_STEPS - 1
    prev = _snap()
    curr = _snap()
    _t, b = compute_step_reward(prev, curr, st, terminated=False)
    assert b["stall_timeout"] == pytest.approx(R_STALL_PENALTY)


def test_progress_room_includes_forward_entry() -> None:
    prev = _snap(room_index=0, rooms_cleared=0)
    curr = _snap(room_index=1, rooms_cleared=0, kill_total=0)
    st = RewardState()
    _t, b = compute_step_reward(prev, curr, st, terminated=False)
    assert b["progress_room"] == pytest.approx(R_ROOM_ENTRY_FORWARD, rel=1e-5)


def test_defeat_paid_once() -> None:
    prev = _snap(death_phase=False)
    curr = _snap(death_phase=True)
    st = RewardState()
    _t1, b1 = compute_step_reward(prev, curr, st, terminated=True)
    assert b1["defeat"] == pytest.approx(R_DEFEAT)
    assert st.paid_defeat
    _t2, b2 = compute_step_reward(curr, curr, st, terminated=True)
    assert b2["defeat"] == 0.0


def test_nonterminal_total_clips_to_r_step_clip() -> None:
    """Large kill delta across room change produces raw sum > R_STEP_CLIP, then clip."""
    prev = _snap(room_index=0, kill_total=0, rooms_cleared=0)
    curr = _snap(
        room_index=1,
        kill_total=30,
        rooms_cleared=0,
        combat_enemy_boss={},
    )
    st = RewardState()
    total, b = compute_step_reward(prev, curr, st, terminated=False)
    assert abs(total) <= R_STEP_CLIP + 1e-4
    assert b["kill_normal"] == pytest.approx(30 * 0.12, rel=1e-4)


def test_failed_interact_spam_scaled_when_over_cap() -> None:
    prev = _snap(rl_interact_failed_e_count=0)
    curr = _snap(rl_interact_failed_e_count=20)
    st = RewardState()
    _t, b = compute_step_reward(prev, curr, st, terminated=False)
    assert abs(b["failed_interact"]) <= R_FAILED_SPAM_STEP_CAP + 1e-5


def test_victory_runs_once_only() -> None:
    prev = _snap(victory=False)
    curr = _snap(victory=True)
    st = RewardState()
    _t1, b1 = compute_step_reward(prev, curr, st, terminated=True)
    assert b1["victory"] == pytest.approx(R_VICTORY)
    _t2, b2 = compute_step_reward(curr, curr, st, terminated=True)
    assert b2["victory"] == 0.0
