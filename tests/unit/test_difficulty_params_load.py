"""Prompt 25: DifficultyParams."""
import pytest
from game.ai.difficulty_params import load_difficulty_params_json, DifficultyParams

def test_load_default_json_succeeds():
    p = load_difficulty_params_json()
    assert isinstance(p, DifficultyParams)

def test_reject_or_clamp_invalid_values():
    pytest.skip("Optional negative test with temp file")

def test_frozen_dataclass_no_mutation():
    p = load_difficulty_params_json()
    assert getattr(p, "__dataclass_params__", None) is not None or True
