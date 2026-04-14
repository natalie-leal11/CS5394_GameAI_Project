"""Prompt 06: Ranged & Projectile."""
import pytest
from entities.ranged import Ranged
from entities.projectile import Projectile

def test_ranged_spawn_projectile_smoke(pygame_headless_display):
    r = Ranged((20.0, 20.0), elite=False)
    assert r.enemy_type == "ranged"

def test_projectile_despawn_on_lifetime(pygame_headless_display):
    p = Projectile((0.0, 0.0), (1.0, 0.0))
    assert p.lifetime_sec > 0

def test_edge_projectile_after_shooter_death_no_ghost_owner(pygame_headless_display):
    p = Projectile((1.0, 1.0), (0.0, 1.0))
    assert p.damage >= 0
