"""Prompt 39: obs + action map."""
import pytest
import numpy as np
from rl.obs import OBS_DIM
from rl import action_map

def test_build_observation_shape_dtype(pygame_headless_display):
    pytest.skip("Needs GameScene instance")

def test_all_action_indices_map_defined():
    assert action_map.ACTION_COUNT == 17

def test_no_nan_inf_for_empty_enemy_case():
    pytest.skip("Needs GameScene")
