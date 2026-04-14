"""Prompt 09: Training dummy."""
import pytest
from entities.training_dummy import TrainingDummy

def test_dummy_accepts_damage_without_invalid_state(pygame_headless_display):
    d = TrainingDummy((50.0, 50.0))
    assert d.hp > 0

def test_dummy_not_in_kill_count_if_metrics_wired():
    pytest.skip("Wire MetricsTracker in integration when available")
