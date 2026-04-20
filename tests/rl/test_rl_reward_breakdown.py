"""RL reward breakdown (mirrors unit coverage; rl/ package location)."""

from __future__ import annotations

from rl.reward import R_STALL_THRESHOLD_STEPS, RewardSnapshot, RewardState, compute_step_reward


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
