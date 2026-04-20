# Focused gameplay-style tests for short-attack input buffering (Player.update).
# Verifies: no lost clicks, single pending buffer, movement + attack, pause safety, long attack unchanged.

import pygame
import pytest

from game import config as game_config
from game.scene_manager import SceneManager

game_config.DEBUG_PLAYER_ATTACK_PROXIMITY = False
game_config.DEBUG_PLAYER_ATTACK_WALK_TRACE = False
game_config.DEBUG_PLAYER_ATTACK_INPUT_TRACE = False
game_config.DEBUG_PLAYER_SHORT_ATTACK_BUFFER = False
game_config.DEBUG_LIVE_SHORT_ATTACK_TRACE = False

from entities.player import Player

pygame.init()
pygame.display.set_mode((64, 64))

DT = 1 / 60.0
NO_MOUSE = (False, False, False)


def _loaded_player() -> Player:
    p = Player()
    p.world_pos = (480.0, 320.0)
    p._ensure_animations_loaded()
    return p


def _tick(
    p: Player,
    *,
    keys: set | None = None,
    short: bool = False,
    long_req: bool = False,
) -> None:
    p.update(
        DT,
        keys if keys is not None else set(),
        NO_MOUSE,
        False,
        False,
        False,
        short,
        long_req,
    )


def _advance_until_attack_finishes(p: Player, max_frames: int = 400) -> str:
    """Run updates until not in attack_short/attack_long (animation finishes to idle/walk)."""
    for _ in range(max_frames):
        if p.state not in ("attack_short", "attack_long"):
            return p.state
        _tick(p)
    return p.state


def _advance_until_short_cooldown_cleared(p: Player, max_frames: int = 360) -> None:
    """After a short attack, real cooldown must elapse before another swing (see PLAYER_SHORT_ATTACK_COOLDOWN_SEC)."""
    for _ in range(max_frames):
        if float(getattr(p, "short_attack_cooldown_timer", 0.0)) <= 1e-9:
            return
        _tick(p, short=False)


def test_1_idle_single_click_starts_attack_immediately():
    """Stand still: one LMB (short_req) -> attack_short immediately."""
    p = _loaded_player()
    p._set_state("idle")
    assert p._pending_short_attack is False
    _tick(p, short=True)
    assert p.state == "attack_short"
    assert p._pending_short_attack is False


def test_2_slow_repeated_clicks_each_cause_one_attack():
    """4–5 separate clicks: each should produce exactly one swing (pending never stacks extra swings)."""
    p = _loaded_player()
    p._set_state("idle")
    swings = 0
    for _ in range(5):
        assert p.state in ("idle", "walk") or p.state in ("attack_short", "attack_long")
        if p.state in ("attack_short", "attack_long"):
            _advance_until_attack_finishes(p)
            _advance_until_short_cooldown_cleared(p)
        p._set_state("idle")
        p._still_timer = 0.0
        before = p.state
        _tick(p, short=True)
        assert p.state == "attack_short", f"expected swing from idle, got {before} -> {p.state}"
        swings += 1
        _advance_until_attack_finishes(p)
        _advance_until_short_cooldown_cleared(p)
    assert swings == 5


def test_3_rapid_clicks_during_lock_buffer_once_one_followup_swing():
    """Many short_req frames only while attack_short: at most one pending; one extra swing after unlock."""
    p = _loaded_player()
    p._set_state("attack_short")
    # Only send short_req while still locked; once idle, short+pending would start the follow-up swing.
    n = 0
    while p.state == "attack_short" and n < 80:
        _tick(p, short=True)
        n += 1
    assert p._pending_short_attack is True
    # Swing finished inside the loop -> idle; buffer still holds one follow-up swing.
    assert p.state in ("idle", "walk")
    _advance_until_short_cooldown_cleared(p)
    p._set_state("idle")
    _tick(p, short=False)
    assert p.state == "attack_short"
    assert p._pending_short_attack is False


def test_4_hold_movement_and_click_each_direction():
    """W/A/S/D + short attack: enters attack_short; movement applies during attack."""
    for key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d):
        p = _loaded_player()
        p._set_state("walk")
        _tick(p, keys={key}, short=True)
        assert p.state == "attack_short", f"failed for key {key}"
        assert p._pending_short_attack is False
        _advance_until_attack_finishes(p)
        _advance_until_short_cooldown_cleared(p)
        _tick(p, keys={key}, short=False)
        assert p.velocity_xy[0] != 0.0 or p.velocity_xy[1] != 0.0


def test_5_hold_movement_spam_short_requests_no_silent_loss_single_buffer():
    """Spam short_req while walking: buffered once, then executes; no duplicate pending chain."""
    p = _loaded_player()
    p._set_state("attack_short")
    for _ in range(20):
        _tick(p, keys={pygame.K_w}, short=True)
    assert p._pending_short_attack is True
    _advance_until_attack_finishes(p)
    _advance_until_short_cooldown_cleared(p)
    p._set_state("idle")
    _tick(p, keys={pygame.K_w}, short=False)
    assert p.state == "attack_short"
    assert p._pending_short_attack is False


def test_6_second_click_during_first_swing_buffered_then_auto_swings():
    """One click during active attack buffers; next idle consumes without third click."""
    p = _loaded_player()
    p._set_state("attack_short")
    _tick(p, short=True)
    assert p._pending_short_attack is True
    _advance_until_attack_finishes(p)
    _advance_until_short_cooldown_cleared(p)
    p._set_state("idle")
    _tick(p, short=False)
    assert p.state == "attack_short"
    assert p._pending_short_attack is False


def test_7_single_click_only_one_attack_no_stale_chain():
    """Exactly one short_req then only idle ticks -> no second attack without new input."""
    p = _loaded_player()
    p._set_state("idle")
    _tick(p, short=True)
    assert p.state == "attack_short"
    _advance_until_attack_finishes(p)
    for _ in range(120):
        _tick(p, short=False)
    assert p._pending_short_attack is False
    assert p.state not in ("attack_short", "attack_long")


def test_8_after_buffered_swing_stops_no_ghost_pending():
    """After buffered attack executes, idle with no clicks stays idle with no pending."""
    p = _loaded_player()
    p._set_state("attack_short")
    _tick(p, short=True)
    _advance_until_attack_finishes(p)
    _advance_until_short_cooldown_cleared(p)
    p._set_state("idle")
    _tick(p, short=False)
    assert p.state == "attack_short"
    _advance_until_attack_finishes(p)
    _advance_until_short_cooldown_cleared(p)
    p._set_state("idle")
    for _ in range(30):
        _tick(p, short=False)
    assert p._pending_short_attack is False
    assert p.state in ("idle", "walk")


def test_9_pause_clears_buffer_no_resume_ghost():
    """GameScene pause clears Player pending short buffer."""
    sm = SceneManager()
    sm.init()
    sm.switch_to_game()
    scene = sm.current
    p = _loaded_player()
    scene._player = p
    p._pending_short_attack = True
    scene._set_paused(True, reason="test buffer clear")
    assert p._pending_short_attack is False


def test_10_long_attack_unaffected_by_short_buffer():
    """RMB (long) still enters attack_long; short buffer not required."""
    p = _loaded_player()
    p._set_state("idle")
    p.long_attack_cooldown_timer = 0.0
    _tick(p, short=False, long_req=True)
    assert p.state == "attack_long"
    assert p._pending_short_attack is False


def test_clear_short_attack_buffer_explicit():
    p = _loaded_player()
    p._pending_short_attack = True
    p.clear_short_attack_buffer(reason="unit test")
    assert p._pending_short_attack is False
