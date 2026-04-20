"""Integration tests for GameScene checkpoint progression and respawn behavior."""

from __future__ import annotations

import math

from game.scene_manager import SceneManager


DT = 1.0 / 60.0


def _boot_game_scene():
    """Create a real GameScene via SceneManager and advance one frame to initialize room state."""
    sm = SceneManager()
    sm.init()
    sm.switch_to_game()
    scene = sm.current
    scene.update(DT)
    assert scene._room_controller is not None
    assert scene._player is not None
    return scene


def _spawn_world_pos(scene) -> tuple[float, float]:
    """Expected player spawn world position for the currently loaded room."""
    room = scene._room_controller.current_room
    assert room is not None
    tx, ty = room.spawn_tile
    return room.world_pos_for_tile(tx, ty)


def test_default_checkpoint_starts_at_room0_and_respawn_returns_to_room0():
    scene = _boot_game_scene()

    # New run starts from checkpoint room 0.
    assert scene._checkpoint_room_index == 0
    assert scene._room_controller.current_room_index == 0

    # Move away from room 0 and contaminate transient state, then respawn.
    scene._room_controller.load_room(3)
    scene._player.world_pos = (999.0, 777.0)
    scene._enemies = [object()]
    scene._projectiles = [object()]
    scene._spawned_enemies = True
    scene._spawn_system = object()

    # Simulated life-loss respawn before any mini-boss checkpoint advancement.
    scene._respawn_player_at_checkpoint()

    assert scene._room_controller.current_room_index == 0
    ex, ey = _spawn_world_pos(scene)
    px, py = scene._player.world_pos
    assert math.isclose(px, ex, rel_tol=0.0, abs_tol=1e-6)
    assert math.isclose(py, ey, rel_tol=0.0, abs_tol=1e-6)

    # Transient room state reset.
    assert scene._enemies == []
    assert scene._projectiles == []
    assert scene._spawned_enemies is False
    assert scene._spawn_system is None


def test_checkpoint_advances_after_mini_boss_clears():
    scene = _boot_game_scene()

    assert scene._checkpoint_room_index == 0

    scene._update_checkpoint_from_mini_boss_clear(7)
    assert scene._checkpoint_room_index == 8

    scene._update_checkpoint_from_mini_boss_clear(15)
    assert scene._checkpoint_room_index == 16

    scene._update_checkpoint_from_mini_boss_clear(23)
    assert scene._checkpoint_room_index == 24


def test_respawn_uses_latest_checkpoint_and_clears_transient_room_state():
    scene = _boot_game_scene()

    for cleared_room, checkpoint_room in ((7, 8), (15, 16), (23, 24)):
        # Advance checkpoint through real helper.
        scene._update_checkpoint_from_mini_boss_clear(cleared_room)
        assert scene._checkpoint_room_index == checkpoint_room

        # Move to a different room and dirty transient state to ensure reset is real.
        scene._room_controller.load_room(max(0, checkpoint_room - 1))
        scene._player.world_pos = (1234.5, 678.9)
        scene._enemies = [object(), object()]
        scene._projectiles = [object()]
        scene._spawned_enemies = True
        scene._spawn_system = object()
        scene._room_cleared_flag = True
        scene._doors_unlocked = True
        scene._door_unlock_timer = 1.0
        scene._rewards = [{"kind": "heal_drop"}]
        scene._safe_room_heal_done = True
        scene._final_boss_spawned = True
        scene._meteor_impacts = [{"x": 0}]

        # Simulated life-loss respawn should return to latest checkpoint.
        scene._respawn_player_at_checkpoint()

        assert scene._room_controller.current_room_index == checkpoint_room

        ex, ey = _spawn_world_pos(scene)
        px, py = scene._player.world_pos
        assert math.isclose(px, ex, rel_tol=0.0, abs_tol=1e-6)
        assert math.isclose(py, ey, rel_tol=0.0, abs_tol=1e-6)

        # No stale transient room state survives checkpoint reload.
        assert scene._enemies == []
        assert scene._projectiles == []
        assert scene._spawned_enemies is False
        assert scene._spawn_system is None
        assert scene._room_cleared_flag is False
        assert scene._doors_unlocked is False
        assert scene._door_unlock_timer is None
        assert scene._rewards == []
        assert scene._safe_room_heal_done is False
        assert scene._final_boss_spawned is False
        assert scene._meteor_impacts == []
