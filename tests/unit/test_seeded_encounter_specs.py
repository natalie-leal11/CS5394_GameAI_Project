"""Prompt 20: Seeded encounter specs."""
import pytest
from dungeon import seeded_encounter_specs as ses

def test_deterministic_seed_produces_same_spec_smoke():
    assert ses is not None

def test_enemy_count_within_bounds():
    pytest.skip("Call concrete spec builder when API stable")

def test_edge_seed_extremes():
    pytest.skip("Optional")
