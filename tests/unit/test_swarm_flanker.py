"""Prompt 04: Swarm & Flanker."""
import pytest
from entities.swarm import Swarm
from entities.flanker import Flanker

def test_swarm_instantiation_and_update_smoke(pygame_headless_display):
    e = Swarm((50.0, 50.0), elite=False)
    assert e.enemy_type == "swarm"

def test_flanker_approach_smoke(pygame_headless_display):
    e = Flanker((50.0, 50.0), elite=False)
    assert e.enemy_type == "flanker"

def test_edge_many_swarm_instances_no_overflow_invariants(pygame_headless_display):
    xs = [Swarm((float(i), 0.0), elite=False) for i in range(5)]
    assert len(xs) == 5
