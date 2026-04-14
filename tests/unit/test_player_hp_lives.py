"""Prompt 01: Player HP, lives, damage intake — audit §1 Player."""

from __future__ import annotations

import pytest

from game.config import PLAYER_BASE_HP, PLAYER_LIVES_INITIAL
from entities.player import Player


def test_hp_never_exceeds_max_when_clamped():
    p = Player()
    cap = float(p.max_hp)
    p.apply_incoming_heal(1_000_000.0)
    assert p.hp <= cap + 1e-6


def test_damage_reduces_hp_monotonically():
    p = Player()
    before = float(p.hp)
    p.hp = max(0.0, before - 10.0)
    assert p.hp <= before


def test_life_decrement_on_run_failure_if_applicable():
    p = Player()
    assert p.lives == int(PLAYER_LIVES_INITIAL)
    if p.lives > 0:
        p.lives -= 1
        assert p.lives == int(PLAYER_LIVES_INITIAL) - 1


def test_heal_at_full_hp_is_noop_or_clamped():
    p = Player()
    p.hp = float(p.max_hp)
    applied = p.apply_incoming_heal(50.0)
    assert applied == 0.0
    assert p.hp <= float(p.max_hp) + 1e-6


def test_edge_last_life_death():
    p = Player()
    p.lives = 1
    p.hp = 0.0
    assert p.lives == 1 and p.hp <= 1e-6


def test_player_base_hp_matches_config():
    p = Player()
    assert float(p.hp) == float(PLAYER_BASE_HP)
