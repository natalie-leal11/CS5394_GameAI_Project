"""Safe-room upgrade persistence across room loads; respawn resets health mult per GameScene."""

from __future__ import annotations

import pytest

from dungeon.room import total_campaign_rooms
from game.scene_manager import SceneManager


DT = 1.0 / 60.0


def _boot():
    sm = SceneManager()
    sm.init()
    sm.switch_to_game()
    scene = sm.current
    scene.update(DT)
    return scene


def test_upgrade_persists_across_2_rooms():
    """Player stat multipliers are not cleared by load_room + transient reset."""
    scene = _boot()
    rc = scene._room_controller
    p = scene._player
    p.move_speed_mult = 1.1
    a = rc.current_room_index
    b = (a + 1) % total_campaign_rooms()
    room = rc.load_room(b)
    scene._apply_transient_reset_after_loading_campaign_room(room)
    assert p.move_speed_mult == pytest.approx(1.1)


def test_upgrades_stack_additively():
    """Attack mult compounds multiplicatively when set twice (simulating two picks)."""
    scene = _boot()
    p = scene._player
    p.attack_damage_mult = 1.0
    p.attack_damage_mult *= 1.12
    p.attack_damage_mult *= 1.12
    assert p.attack_damage_mult == pytest.approx(1.12 * 1.12)


def test_checkpoint_respawn_preserves_upgrades_chosen_so_far():
    """Life-loss respawn resets safe-room health mult (implementation clears upgrade mult on new life)."""
    scene = _boot()
    scene._player._safe_room_health_mult = 1.2  # noqa: SLF001
    scene._respawn_player_at_checkpoint()
    assert scene._player._safe_room_health_mult == pytest.approx(1.0)  # noqa: SLF001
