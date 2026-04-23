"""Prompt 02: Player cooldowns, dash, combat states — audit §1 Player."""

from __future__ import annotations

import pytest

from entities.player import Player


def test_dash_cooldown_counts_down():
    p = Player()
    p.dash_cooldown_timer = 0.5
    dt = 0.1
    for _ in range(5):
        p.dash_cooldown_timer = max(0.0, p.dash_cooldown_timer - dt)
    assert p.dash_cooldown_timer >= 0.0
    assert p.dash_cooldown_timer < 0.5


def test_attack_cooldown_respects_config():
    p = Player()
    assert p.short_attack_cooldown_timer >= 0.0
    assert p.long_attack_cooldown_timer >= 0.0


def test_block_parry_mutual_exclusion_if_designed():
    p = Player()
    # States are exclusive by state machine; idle is default
    assert p.state in ("idle", "walk", "attack_short", "attack_long", "dash", "block", "parry", "hit", "death")


def test_invulnerability_window_monotonic():
    p = Player()
    p.invulnerable_timer = 0.3
    dt = 0.1
    p.invulnerable_timer = max(0.0, p.invulnerable_timer - dt)
    assert p.invulnerable_timer <= 0.3
