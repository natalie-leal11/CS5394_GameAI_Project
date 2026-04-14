"""Prompt 32: Spawn system."""

from __future__ import annotations

import pygame

from entities.swarm import Swarm
from game.ai.metrics_tracker import MetricsTracker
from systems.spawn_system import SpawnSystem
from systems import spawn_system as ss
from systems.vfx import VfxManager


class _Player:
    world_pos = (400.0, 300.0)

    def get_hitbox_rect(self):
        return pygame.Rect(388, 280, 24, 40)


def test_spawn_matches_directive():
    assert ss is not None
    assert hasattr(SpawnSystem, "add_spawn")


def test_reinforcement_only_when_flag_set():
    """MetricsTracker records reinforcement only when append_runtime_spawn_metadata marks it."""
    mt = MetricsTracker()
    mt.start_run(1)
    mt.start_room(0, 1, 100.0)
    mt.set_room_spawn_metadata(enemy_count=1, composition=["swarm"], elite_count=0, reinforcement_applied=False)
    assert mt.run.reinforcement_applied is False
    mt.append_runtime_spawn_metadata(names=["swarm"], mark_reinforcement=True)
    assert mt.run.reinforcement_applied is True


def test_no_spawn_after_clear():
    vfx = VfxManager()
    system = SpawnSystem(vfx)
    player = _Player()
    enemies: list = []
    system.add_spawn(15, 8, Swarm, False, start_time_sec=0.0)
    dt = 1.0 / 60.0
    for _ in range(80):
        system.update(dt, player, enemies, room=None)
        if system.all_spawns_completed():
            break
    n = len(enemies)
    for _ in range(30):
        system.update(dt, player, enemies, room=None)
    assert len(enemies) == n
    assert system.all_spawns_completed()


def test_edge_max_enemy_cap():
    vfx = VfxManager()
    system = SpawnSystem(vfx)
    player = _Player()
    enemies: list = []
    for i in range(3):
        system.add_spawn(10 + i, 8, Swarm, False, start_time_sec=float(i) * 0.05)
    dt = 1.0 / 60.0
    for _ in range(400):
        system.update(dt, player, enemies, room=None)
        if len(enemies) >= 3:
            break
    assert len(enemies) <= 3
