"""Prompt 24: AIDirector."""
import pytest
from game.ai.ai_director import AIDirector, EncounterDirectorSnapshot
from game.ai.player_model import PlayerStateClass

def test_fixed_input_fixed_output():
    ad = AIDirector()
    ad.update(PlayerStateClass.STABLE)
    m1 = float(ad.difficulty_modifier)
    ad.update(PlayerStateClass.STABLE)
    m2 = float(ad.difficulty_modifier)
    assert m1 == m2

def test_snapshot_fields_within_expected_ranges():
    s = EncounterDirectorSnapshot.neutral_default()
    assert 0.0 <= s.reinforcement_chance <= 1.0

def test_neutral_default_snapshot():
    s = EncounterDirectorSnapshot.neutral_default()
    assert s.last_player_state_name in (None, "STABLE")
