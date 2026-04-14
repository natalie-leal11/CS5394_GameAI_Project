"""Prompt 13: Health."""
import pytest
from entities.player import Player

def test_hp_clamped_to_max():
    p = Player()
    p.apply_incoming_heal(9999.0)
    assert p.hp <= p.max_hp + 1e-6

def test_overheal_rejected_or_clamped():
    p = Player()
    p.apply_incoming_heal(9999.0)
    assert len(p.reserve_heal_pool) <= int(__import__("game.config", fromlist=["RESERVE_HEAL_POOL_MAX_ENTRIES"]).RESERVE_HEAL_POOL_MAX_ENTRIES)

def test_heal_zero_amount_noop():
    p = Player()
    assert p.apply_incoming_heal(0.0) == 0.0
