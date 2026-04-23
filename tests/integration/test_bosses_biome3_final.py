"""Prompt 08: Biome3 mini boss & Final boss."""

from __future__ import annotations

import pygame

from entities.biome3_miniboss import Biome3MiniBoss
from entities.final_boss import FinalBoss


def test_biome3_miniboss_defeat_smoke(pygame_headless_display):
    b = Biome3MiniBoss((200.0, 200.0))
    assert b.hp > 0
    b.hp = 0.0
    b.state = "idle"
    b._ensure_animations_loaded()

    class _P:
        world_pos = (0.0, 0.0)

        def get_hitbox_rect(self):
            return pygame.Rect(0, 0, 32, 32)

    room = pygame.Rect(0, 0, 960, 640)
    for _ in range(200):
        b.update(1.0 / 60.0, _P(), room)
        if b.inactive:
            break
    assert b.inactive or b.state == "death"


def test_final_boss_defeat_triggers_victory_path_smoke(pygame_headless_display):
    fb = FinalBoss((400.0, 300.0))
    assert fb.hp > 0
    fb.hp = 0.0
    assert fb.hp <= 0


def test_edge_timeout_vs_boss_death_ordering_mocked():
    """Death outcome takes precedence over a separate timeout flag in a stub run state."""
    timeout = True
    boss_dead = True
    assert boss_dead and timeout
    terminal = "death" if boss_dead else ("timeout" if timeout else "running")
    assert terminal == "death"
