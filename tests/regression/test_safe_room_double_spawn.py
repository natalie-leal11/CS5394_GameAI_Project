"""Regression: SAFE rooms do not run combat spawn pipeline."""

from __future__ import annotations

from dungeon.room import RoomType
from dungeon.srs_biome_order import room_order_biome1_srs
from game.scene_manager import SceneManager


DT = 1.0 / 60.0


def _scene():
    sm = SceneManager()
    sm.init()
    sm.switch_to_game()
    sc = sm.current
    sc.update(DT)
    return sc


def test_safe_room_first_entry_no_spawn():
    scene = _scene()
    rc = scene._room_controller
    seed = int(scene._run_seed)
    order = room_order_biome1_srs(seed)
    safe_local = next(i for i, rt in enumerate(order) if rt == RoomType.SAFE)
    room = rc.load_room(safe_local)
    scene._apply_transient_reset_after_loading_campaign_room(room)
    scene.update(DT)
    assert rc.current_room is not None
    assert rc.current_room.room_type == RoomType.SAFE
    # SAFE rooms may still set spawn flags for dummies; assert no combat enemy types.
    combat = {"swarm", "flanker", "brute", "ranged", "heavy"}
    assert not any(getattr(e, "enemy_type", None) in combat for e in scene._enemies)


def test_safe_room_reentry_no_spawn():
    scene = _scene()
    rc = scene._room_controller
    seed = int(scene._run_seed)
    order = room_order_biome1_srs(seed)
    safe_local = next(i for i, rt in enumerate(order) if rt == RoomType.SAFE)
    rc.load_room(safe_local)
    scene._apply_transient_reset_after_loading_campaign_room(rc.current_room)
    scene.update(DT)
    rc.load_room(safe_local)
    scene._apply_transient_reset_after_loading_campaign_room(rc.current_room)
    scene.update(DT)
    combat = {"swarm", "flanker", "brute", "ranged", "heavy"}
    assert not any(getattr(e, "enemy_type", None) in combat for e in scene._enemies)
