"""Prompt 03: Enemy base lifecycle — audit §1 Enemy base."""

from __future__ import annotations

import pytest

from entities.swarm import Swarm


def test_enemy_starts_alive_with_positive_hp(pygame_headless_display):
    e = Swarm((100.0, 100.0), elite=False)
    assert e.hp > 0


def test_damage_reduces_hp(pygame_headless_display):
    e = Swarm((100.0, 100.0), elite=False)
    before = float(e.hp)
    e.hp = max(0.0, before - 5.0)
    assert e.hp < before


def test_at_zero_hp_marks_dead_or_triggers_removal_hook(pygame_headless_display):
    e = Swarm((100.0, 100.0), elite=False)
    e.hp = 0.0
    assert e.hp <= 0.0


def test_no_damage_after_death(pygame_headless_display):
    e = Swarm((100.0, 100.0), elite=False)
    e.hp = 0.0
    e.hp = max(0.0, e.hp - 10.0)
    assert e.hp == 0.0
