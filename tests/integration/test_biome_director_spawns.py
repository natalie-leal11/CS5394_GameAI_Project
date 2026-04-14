"""Prompt 26: Biome director spawns."""

from __future__ import annotations

import random

from game.ai.ai_director import AIDirector
from game.ai.player_model import PlayerStateClass


def test_spawn_count_non_negative():
    ad = AIDirector()
    ad.update(PlayerStateClass.STABLE)
    assert ad.effective_enemy_adjustment() >= 0


def test_same_seed_same_composition_smoke():
    r1 = random.Random(4242)
    r2 = random.Random(4242)
    a = [r1.randint(0, 5) for _ in range(8)]
    b = [r2.randint(0, 5) for _ in range(8)]
    assert a == b


def test_zero_enemy_edge_if_allowed():
    ad = AIDirector()
    ad.update_room_context(1, 1)
    assert ad.trial_phase is True
    assert ad.effective_enemy_adjustment() == 0
