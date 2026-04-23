"""Phase 5: Spawn system, telegraphs, spawn portal — config and behaviour."""

import math

import pygame
import pytest

from game.config import (
    TILE_SIZE,
    LOGICAL_W,
    LOGICAL_H,
    SPAWN_TELEGRAPH_DURATION_SEC,
    SPAWN_TELEGRAPH_PULSES,
    SPAWN_SLOT_DELAY_SEC,
    ENEMY_MIN_X,
    ENEMY_MIN_Y,
    ENEMY_MAX_X,
    ENEMY_MAX_Y,
)
from entities.swarm import Swarm
from systems.spawn_system import SpawnSystem, SpawnSlot
from systems.vfx import VfxManager

pygame.init()
pygame.display.set_mode((1, 1))


def test_phase5_config():
    """Phase 5 spawn timing constants are defined per spec."""
    assert math.isclose(SPAWN_TELEGRAPH_DURATION_SEC, 0.5, rel_tol=1e-3)
    assert SPAWN_TELEGRAPH_PULSES == 3
    assert SPAWN_SLOT_DELAY_SEC > 0.0


def test_spawn_system_add_spawn():
    """SpawnSystem.add_spawn creates a slot with correct tile, class, elite, start_time."""
    vfx = VfxManager()
    system = SpawnSystem(vfx)
    system.add_spawn(10, 8, Swarm, False, start_time_sec=0.0)
    assert len(system._slots) == 1
    slot = system._slots[0]
    assert slot.tile_x == 10
    assert slot.tile_y == 8
    assert slot.enemy_cls is Swarm
    assert slot.elite is False
    assert slot.start_time == 0.0
    assert slot.started is False
    assert slot.completed is False


def test_spawn_system_spawns_after_telegraph_duration():
    """Enemy is spawned only after telegraph duration (0.5 s) has elapsed."""
    class MockPlayer:
        world_pos = (LOGICAL_W / 2.0, LOGICAL_H / 2.0)
        def get_hitbox_rect(self):
            return pygame.Rect(self.world_pos[0] - 12, self.world_pos[1] - 20, 24, 40)

    player = MockPlayer()
    vfx = VfxManager()
    system = SpawnSystem(vfx)
    system.add_spawn(5, 5, Swarm, False, start_time_sec=0.0)
    enemies = []

    # First ~0.5 s: telegraph running, no enemy yet (elapsed reaches 0.5 after 30 dt steps from start)
    dt = 1.0 / 60.0
    for _ in range(29):
        system.update(dt, player, enemies)
    assert len(enemies) == 0

    # Run until spawn (telegraph duration 0.5 s; slot starts at t=0, so need 30 dt steps in "started" branch)
    for _ in range(35):
        system.update(dt, player, enemies)
        if len(enemies) >= 1:
            break
    assert len(enemies) == 1
    assert isinstance(enemies[0], Swarm)
    assert enemies[0].enemy_type == "swarm"


def test_spawn_system_tile_to_world_clamped():
    """Spawn positions from tiles are clamped to room bounds."""
    vfx = VfxManager()
    system = SpawnSystem(vfx)
    system.add_spawn(0, 0, Swarm, False, start_time_sec=10.0)  # never start in test
    x, y = system._tile_to_world(0, 0, Swarm, None)
    assert ENEMY_MIN_X <= x <= ENEMY_MAX_X
    assert ENEMY_MIN_Y <= y <= ENEMY_MAX_Y
    # Center of tile (0,0) in world
    assert abs(x - (0.5 * TILE_SIZE)) <= max(0, ENEMY_MIN_X - 0.5 * TILE_SIZE) or x >= ENEMY_MIN_X
    assert abs(y - (0.5 * TILE_SIZE)) <= max(0, ENEMY_MIN_Y - 0.5 * TILE_SIZE) or y >= ENEMY_MIN_Y


def test_spawn_system_slot_delay_prevents_same_frame_spawns():
    """With staggered start_time, enemies do not all spawn on the same frame."""
    class MockPlayer:
        world_pos = (LOGICAL_W / 2.0, LOGICAL_H / 2.0)
        def get_hitbox_rect(self):
            return pygame.Rect(450, 300, 24, 40)

    player = MockPlayer()
    vfx = VfxManager()
    system = SpawnSystem(vfx)
    system.add_spawn(10, 5, Swarm, False, start_time_sec=0.0)
    system.add_spawn(12, 5, Swarm, False, start_time_sec=SPAWN_SLOT_DELAY_SEC)
    enemies = []
    dt = 1.0 / 60.0
    # Run until first spawn (just over 0.5 s)
    for _ in range(35):
        system.update(dt, player, enemies)
    assert len(enemies) == 1
    # Run until second spawn (first at 0.5s, second at 0.5 + 0.4 = 0.9s)
    for _ in range(35):
        system.update(dt, player, enemies)
    assert len(enemies) == 2


def test_vfx_telegraph_has_correct_duration_and_pulses():
    """VfxManager telegraph uses config duration and pulse count."""
    vfx = VfxManager()
    vfx.spawn_telegraph((100.0, 100.0), is_elite=False)
    assert len(vfx._telegraphs) == 1
    t = vfx._telegraphs[0]
    assert math.isclose(t.duration, SPAWN_TELEGRAPH_DURATION_SEC, rel_tol=1e-3)
    assert t.pulses == SPAWN_TELEGRAPH_PULSES


def test_spawn_overlapping_player_pushed_three_tiles():
    """When spawn tile would overlap player, enemy is pushed outward by 3 tiles so no collision."""
    class MockPlayer:
        world_pos = (16.0, 16.0)  # center of tile (0, 0)
        def get_hitbox_rect(self):
            return pygame.Rect(self.world_pos[0] - 12, self.world_pos[1] - 20, 24, 40)

    player = MockPlayer()
    vfx = VfxManager()
    system = SpawnSystem(vfx)
    # Tile (0,0) center = (16, 16) — overlaps player
    system.add_spawn(0, 0, Swarm, False, start_time_sec=0.0)
    enemies = []
    dt = 1.0 / 60.0
    for _ in range(40):
        system.update(dt, player, enemies)
        if len(enemies) >= 1:
            break
    assert len(enemies) == 1
    enemy = enemies[0]
    dist = math.hypot(enemy.world_pos[0] - player.world_pos[0], enemy.world_pos[1] - player.world_pos[1])
    assert dist >= 3 * TILE_SIZE - 2.0  # at least ~3 tiles


def test_spawn_system_room_bounds_clamps_position():
    """With room_bounds set, _tile_to_world clamps to those bounds."""
    vfx = VfxManager()
    room_bounds = (0.0, 0.0, 64.0, 64.0)
    system = SpawnSystem(vfx, room_bounds=room_bounds)
    # Tile (5, 5) would be (5.5*32, 5.5*32) = (176, 176) unclamped
    x, y = system._tile_to_world(5, 5, Swarm, None)
    assert 0 <= x <= 64
    assert 0 <= y <= 64
