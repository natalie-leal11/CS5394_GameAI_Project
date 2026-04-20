"""Regression: transient combat state clears when campaign room changes (no stale enemies)."""

from __future__ import annotations

from entities.swarm import Swarm
from game.scene_manager import SceneManager


DT = 1.0 / 60.0


def _scene():
    sm = SceneManager()
    sm.init()
    sm.switch_to_game()
    scene = sm.current
    scene.update(DT)
    return scene


def test_enemy_list_cleared_on_transition():
    scene = _scene()
    rc = scene._room_controller
    assert rc is not None
    scene._enemies = [Swarm((120.0, 200.0))]
    from dungeon.room import total_campaign_rooms

    targ = (rc.current_room_index + 1) % total_campaign_rooms()
    room = rc.load_room(targ)
    scene._apply_transient_reset_after_loading_campaign_room(room)
    assert scene._enemies == []


def test_new_room_enemies_spawn_exactly_once():
    """After transition, spawn flag is reset; no duplicate spawn without new clear."""
    scene = _scene()
    rc = scene._room_controller
    from dungeon.room import total_campaign_rooms

    targ = (rc.current_room_index + 2) % total_campaign_rooms()
    room = rc.load_room(targ)
    scene._apply_transient_reset_after_loading_campaign_room(room)
    assert scene._spawned_enemies is False


def test_no_leftover_enemy_references():
    """Projectiles cleared with enemies on room load reset."""
    scene = _scene()
    rc = scene._room_controller
    from dungeon.room import total_campaign_rooms

    scene._enemies = [object()]
    scene._projectiles = [object()]
    targ = (rc.current_room_index + 1) % total_campaign_rooms()
    room = rc.load_room(targ)
    scene._apply_transient_reset_after_loading_campaign_room(room)
    assert scene._enemies == []
    assert scene._projectiles == []
