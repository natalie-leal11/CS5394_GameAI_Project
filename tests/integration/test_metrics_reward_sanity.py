"""Metrics: kills increment once per record_kill; no phantom double increment without a second call."""

from __future__ import annotations

from game.ai.metrics_tracker import MetricsTracker


def test_kill_increment_once_per_event():
    mt = MetricsTracker()
    mt.start_run(7)
    mt.start_room(0, 1, 100.0)
    base = mt.run.kill_count_total
    mt.record_kill("swarm")
    assert mt.run.kill_count_total == base + 1
    mt.record_kill("flanker")
    assert mt.run.kill_count_total == base + 2


def test_no_double_count_without_duplicate_record():
    mt = MetricsTracker()
    mt.start_run(8)
    mt.start_room(0, 1, 100.0)
    mt.record_kill("brute")
    k = mt.run.kill_count_total
    assert mt.run.kill_count_total == k
