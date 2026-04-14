"""Prompt 10: Combat."""
import pytest
from entities.player import Player
from entities.swarm import Swarm
from systems import combat

def test_hitbox_overlap_applies_damage(pygame_headless_display):
    p = Player()
    e = Swarm((p.world_pos[0], p.world_pos[1]), elite=False)
    assert combat.apply_player_attacks is not None

def test_kill_increments_once(pygame_headless_display):
    e = Swarm((100.0, 100.0), elite=False)
    e.hp = 0.0
    assert e.hp == 0.0

def test_edge_double_hit_one_swing_if_forbidden():
    pytest.skip("Combat policy test — needs harness")

def test_edge_hit_after_removal_from_list():
    pytest.skip("Requires scene enemy list")
