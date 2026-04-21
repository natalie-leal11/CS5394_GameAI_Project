"""Regression: phase index tracks HP thresholds monotonically (no skipped bands when damage is sequential)."""

from __future__ import annotations


def _phase(hp: float) -> int:
    """Toy 4-phase model: full / high / mid / low."""
    if hp > 75.0:
        return 0
    if hp > 50.0:
        return 1
    if hp > 25.0:
        return 2
    return 3


def test_burst_damage_triggers_all_phases():
    """Sequential chunks cross 75 / 50 / 25 so every band is visited."""
    hp = 100.0
    seen = set()
    for dmg in (5.0, 10.0, 20.0, 20.0, 20.0, 15.0, 15.0):
        hp -= dmg
        seen.add(_phase(hp))
    assert seen == {0, 1, 2, 3}


def test_phase_events_emitted_in_order():
    """Phase index never decreases while HP only drops."""
    hp = 100.0
    seq: list[int] = []
    for dmg in (10.0, 10.0, 20.0, 25.0, 20.0, 20.0):
        hp -= dmg
        seq.append(_phase(hp))
    for a, b in zip(seq, seq[1:]):
        assert b >= a
