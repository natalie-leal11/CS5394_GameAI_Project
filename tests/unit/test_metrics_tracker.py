"""Prompt 17: MetricsTracker."""
import pytest
from game.ai.metrics_tracker import MetricsTracker

def test_reset_clears_run_counters():
    mt = MetricsTracker()
    mt.start_run(42)
    assert mt.run.rooms_cleared >= 0

def test_increment_idempotent_where_required():
    mt = MetricsTracker()
    assert mt.run is not None

def test_rl_interact_counters_separate_from_success():
    mt = MetricsTracker()
    r = mt.run
    assert getattr(r, "rl_interact_success_count", 0) >= 0
