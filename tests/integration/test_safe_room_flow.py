"""Prompt 22: Safe room heal math (no full GameScene)."""

from __future__ import annotations

import pytest

from game.config import SAFE_ROOM_HEAL_PERCENT, SAFE_ROOM_OVERHEAL_CAP_RATIO


def _apply_safe_room_heal(hp: float, max_hp: float) -> tuple[float, int]:
    cap = max_hp * SAFE_ROOM_OVERHEAL_CAP_RATIO
    if hp >= cap - 1e-9:
        return hp, 0
    gain = max_hp * SAFE_ROOM_HEAL_PERCENT
    new_hp = min(hp + gain, cap)
    return new_hp, 1


def test_heal_percent_applied():
    hp, n = _apply_safe_room_heal(50.0, 100.0)
    assert n == 1
    assert hp == pytest.approx(50.0 + 100.0 * SAFE_ROOM_HEAL_PERCENT)


def test_full_hp_heal_noop():
    max_hp = 100.0
    at_cap = max_hp * SAFE_ROOM_OVERHEAL_CAP_RATIO
    hp, presses = _apply_safe_room_heal(at_cap, max_hp)
    assert presses == 0
    assert hp == at_cap


def test_choice_spam_does_not_corrupt_state():
    max_hp = 100.0
    hp = 40.0
    total_presses = 0
    for _ in range(10):
        new_hp, p = _apply_safe_room_heal(hp, max_hp)
        hp = new_hp
        total_presses += p
    cap = max_hp * SAFE_ROOM_OVERHEAL_CAP_RATIO
    assert hp <= cap + 1e-6
    assert total_presses >= 1
    _, p2 = _apply_safe_room_heal(hp, max_hp)
    assert p2 == 0
