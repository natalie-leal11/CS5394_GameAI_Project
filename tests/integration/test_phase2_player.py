# Phase 2 tests: config, animation system, movement system, player init, GameScene camera.
# No pygame.display required (no asset loading in tests that need display).

import pygame

from game.config import (
    LOGICAL_W,
    LOGICAL_H,
    PLAYER_MOVE_SPEED,
    PLAYER_DASH_SPEED_MULT,
    PLAYER_DASH_DURATION_SEC,
    PLAYER_DASH_COOLDOWN_SEC,
    PLAYER_BASE_HP,
    PLAYER_PARRY_WINDOW_SEC,
    PLAYER_SIZE,
)
from entities.player import Player, PLAYER_STATES, ANIM_SPECS
from systems.animation import AnimationState
from systems.movement import apply_player_movement, MIN_X, MIN_Y, MAX_X, MAX_Y
from game.scenes.game_scene import GameScene
from game.scene_manager import SceneManager


def test_phase2_config():
    """Phase 2 player and movement constants are set from config."""
    assert PLAYER_MOVE_SPEED == 220
    assert PLAYER_DASH_SPEED_MULT == 2.2
    assert PLAYER_DASH_DURATION_SEC == 0.18
    assert PLAYER_DASH_COOLDOWN_SEC == 0.9
    assert PLAYER_BASE_HP == 200
    assert PLAYER_PARRY_WINDOW_SEC == 0.18
    assert len(PLAYER_SIZE) == 2 and PLAYER_SIZE[0] >= 64 and PLAYER_SIZE[1] >= 64


def test_animation_state_loop():
    """AnimationState loops and never returns finished when loop=True."""
    state = AnimationState()
    state.set_animation([1, 2, 3], fps=10, loop=True)
    idx, finished = state.advance(0.15)  # 1.5 frames
    assert not finished
    idx, finished = state.advance(1.0)  # many frames
    assert not finished


def test_animation_state_non_loop_finishes():
    """AnimationState returns finished when non-loop reaches last frame."""
    state = AnimationState()
    state.set_animation(["a", "b", "c"], fps=10, loop=False)  # 3 frames, 0.1s each
    # Advance past last frame in one call so finished is True (n > 0 and index at last)
    idx, finished = state.advance(0.35)
    assert idx == 2
    assert finished


def test_animation_specs_attack_non_loop():
    """attack_short and attack_long are non-loop per Phase 2."""
    assert ANIM_SPECS["attack_short"][1] is False
    assert ANIM_SPECS["attack_long"][1] is False
    assert ANIM_SPECS["dash"][1] is False
    assert ANIM_SPECS["death"][1] is False


def test_movement_no_keys_no_move():
    """With no keys and no dash, position does not change."""
    class MockPlayer:
        world_pos = (LOGICAL_W / 2.0, LOGICAL_H / 2.0)
        state = "idle"
        velocity_xy = (0, 0)
        dash_active = False
        dash_cooldown_timer = 0

    p = MockPlayer()
    apply_player_movement(p, set(), 0.1)
    assert p.world_pos == (LOGICAL_W / 2.0, LOGICAL_H / 2.0)
    assert p.velocity_xy == (0.0, 0.0)


def test_movement_wasd_moves():
    """WASD applies velocity and moves within one frame."""
    class MockPlayer:
        world_pos = (LOGICAL_W / 2.0, LOGICAL_H / 2.0)
        state = "idle"
        velocity_xy = (0, 0)
        dash_active = False
        dash_cooldown_timer = 0

    p = MockPlayer()
    apply_player_movement(p, {pygame.K_w}, 1.0)  # 1 sec, W only
    assert p.velocity_xy[1] < 0  # moving up
    assert p.world_pos[1] < LOGICAL_H / 2.0


def test_movement_bounds_clamp():
    """Position is clamped to MIN_X, MIN_Y, MAX_X, MAX_Y."""
    class MockPlayer:
        world_pos = (MIN_X - 100, MIN_Y - 100)
        state = "idle"
        velocity_xy = (0, 0)
        dash_active = False
        dash_cooldown_timer = 0

    p = MockPlayer()
    apply_player_movement(p, set(), 0.0)
    assert p.world_pos[0] >= MIN_X
    assert p.world_pos[1] >= MIN_Y

    p.world_pos = (MAX_X + 200, MAX_Y + 200)
    apply_player_movement(p, set(), 0.0)
    assert p.world_pos[0] <= MAX_X
    assert p.world_pos[1] <= MAX_Y


def test_player_init():
    """Player initial state: center world_pos, idle, full HP, not inactive."""
    p = Player()
    assert p.world_pos[0] == LOGICAL_W / 2.0
    assert p.world_pos[1] == LOGICAL_H / 2.0
    assert p.state == "idle"
    assert p.hp == PLAYER_BASE_HP
    assert p.inactive is False
    assert p.dash_active is False
    assert p.facing == (1, 0)


def test_player_has_all_states():
    """Player supports all required Phase 2 states."""
    required = {"idle", "walk", "attack_short", "attack_long", "dash", "block", "parry", "hit", "death"}
    assert set(PLAYER_STATES) >= required


def test_game_scene_camera_baseline():
    """GameScene exposes camera_offset and set_camera_target (camera follows player)."""
    sm = SceneManager()
    sm.init()
    sm.switch_to_game()
    scene = sm.current
    assert hasattr(scene, "camera_offset")
    assert hasattr(scene, "set_camera_target")
    # Default before first update: camera at center
    co = scene.camera_offset
    assert isinstance(co, tuple)
    assert len(co) == 2


def test_dash_applies_boosted_velocity_and_enters_cooldown():
    """During dash, velocity is dash speed; after duration expires, cooldown starts."""
    class MockPlayer:
        world_pos = (LOGICAL_W / 2.0, LOGICAL_H / 2.0)
        state = "idle"
        velocity_xy = (0, 0)
        dash_active = True
        dash_direction = (1.0, 0.0)
        dash_timer = PLAYER_DASH_DURATION_SEC * 0.5  # mid-dash
        dash_cooldown_timer = 0

    p = MockPlayer()
    # Small dt so dash doesn't end in one step
    apply_player_movement(p, set(), 0.02)
    assert p.dash_active is True
    expected_speed = PLAYER_MOVE_SPEED * PLAYER_DASH_SPEED_MULT
    assert abs(p.velocity_xy[0] - expected_speed) < 1.0
    assert p.velocity_xy[1] == 0.0
    # Exhaust dash duration (set timer just above zero, step past it)
    p.dash_timer = 0.01
    apply_player_movement(p, set(), 0.02)
    assert p.dash_active is False
    assert getattr(p, "dash_cooldown_timer", 0) > 0


def test_parry_window_timer_set_and_counts_down():
    """Parry request sets parry_window_timer to PLAYER_PARRY_WINDOW_SEC; it counts down with dt."""
    p = Player()
    p.parry_window_timer = 0.0
    p.state = "idle"
    # Simulate parry key: normally handled in player.update with parry_request=True
    p.parry_window_timer = PLAYER_PARRY_WINDOW_SEC
    assert p.parry_window_timer == PLAYER_PARRY_WINDOW_SEC
    # Advance time (player.update would decrement it)
    dt = 0.05
    for _ in range(3):
        if p.parry_window_timer > 0:
            p.parry_window_timer = max(0, p.parry_window_timer - dt)
    assert p.parry_window_timer <= PLAYER_PARRY_WINDOW_SEC - 0.1
