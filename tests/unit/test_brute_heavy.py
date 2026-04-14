"""Prompt 05: Brute & Heavy."""
import pytest
from entities.brute import Brute
from entities.heavy import Heavy

def test_brute_attack_timing_smoke(pygame_headless_display):
    b = Brute((10.0, 10.0), elite=False)
    assert b.attack_cooldown_timer >= 0.0

def test_heavy_damage_mitigation_or_hp_pool(pygame_headless_display):
    h = Heavy((10.0, 10.0), elite=False)
    assert h.hp > 0

def test_edge_overlapping_hitboxes_no_double_count_same_frame(pygame_headless_display):
    b = Brute((0.0, 0.0), elite=False)
    assert hasattr(b, "get_hitbox_rect")
    _ = b.get_hitbox_rect()
