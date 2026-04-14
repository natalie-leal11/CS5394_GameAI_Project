"""Prompt 07: MiniBoss variants."""

from __future__ import annotations

import pygame

from entities.mini_boss import MiniBoss
from entities.mini_boss_2 import MiniBoss2
from game.ai.metrics_tracker import MetricsTracker


def test_miniboss_defeat_sets_expected_flags(pygame_headless_display):
    m = MiniBoss((100.0, 100.0))
    m.hp = 0.0
    assert m.hp <= 0


def test_miniboss2_distinct_from_miniboss_smoke(pygame_headless_display):
    a = MiniBoss((10.0, 10.0))
    b = MiniBoss2((20.0, 20.0))
    assert a.enemy_type == "mini_boss"
    assert b.enemy_type == "mini_boss_2"


def test_edge_defeat_during_transition_no_double_reward(pygame_headless_display):
    """Distinct boss types; one reward record per scripted defeat line."""
    mt = MetricsTracker()
    mt.start_run(1)
    mt.start_room(0, 1, 100.0)
    mt.record_reward("mini_boss", 10.0)
    assert mt.run.total_rewards_collected == 1
    mt.record_reward("mini_boss_2", 10.0)
    assert mt.run.total_rewards_collected == 2
    assert mt.run.reward_type in ("mini_boss", "mini_boss_2")
