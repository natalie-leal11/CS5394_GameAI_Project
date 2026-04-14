"""Prompt 16: PlayerModel."""
import pytest
from game.ai.player_model import PlayerModel, PlayerStateClass, PlayerModelSummaryInput

def test_same_inputs_same_state_deterministic():
    pm = PlayerModel()
    s = PlayerModelSummaryInput(
        hp_percent_current=50.0, hp_percent_end_room=50.0, hp_lost_in_room=10.0,
        damage_taken_in_room=5.0, room_clear_time=1.0, rooms_cleared=1,
        total_deaths=0, total_damage_taken=5.0, total_healing_received=0.0,
        healing_wasted=0.0, reward_collected_flag=False,
        last_3_rooms_hp_loss=(10.0,), last_3_rooms_clear_time=(1.0,), last_3_rooms_result=("clean_clear",),
        recent_death_flag=False, struggling_rooms_count=0, dominating_rooms_count=0,
    )
    a = pm.classify(s)
    b = pm.classify(s)
    assert a.player_state == b.player_state

def test_boundary_equality_struggling_vs_stable():
    pytest.skip("Tune thresholds with real summary")

def test_spike_damage_single_frame():
    pytest.skip("Needs room history")
