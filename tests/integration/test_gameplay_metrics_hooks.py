"""Prompt 14: Gameplay metrics hooks."""

from __future__ import annotations

from game.ai.metrics_tracker import MetricsTracker, RoomResult


def test_kill_increments_metric_once():
    mt = MetricsTracker()
    mt.start_run(42)
    mt.start_room(0, 1, 100.0)
    before = mt.run.kill_count_total
    mt.record_kill("swarm")
    assert mt.run.kill_count_total == before + 1
    assert mt.run.kills_by_enemy_type.get("swarm", 0) >= 1


def test_room_clear_event_fires_once():
    mt = MetricsTracker()
    mt.start_run(1)
    mt.start_room(0, 1, 100.0)
    cleared_before = mt.run.rooms_cleared
    mt.end_room(100.0)
    assert mt.run.rooms_cleared == cleared_before + 1
    assert len(mt.run.room_history) == 1


def test_victory_and_defeat_mutually_exclusive():
    """A room ends with either death result or a non-death clear — not both on the same RoomMetrics row."""
    dead = MetricsTracker()
    dead.start_run(2)
    dead.start_room(0, 1, 100.0)
    dead.record_death()
    dead.end_room(0.0)
    last = dead.run.room_history[-1]
    assert last.room_result == RoomResult.death
    assert last.death_flag is True

    alive = MetricsTracker()
    alive.start_run(3)
    alive.start_room(0, 1, 100.0)
    alive.end_room(100.0)
    last2 = alive.run.room_history[-1]
    assert last2.room_result != RoomResult.death
    assert last2.death_flag is False
