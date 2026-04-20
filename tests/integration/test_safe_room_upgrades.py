"""Integration tests for biome-specific safe-room upgrade behavior."""

from __future__ import annotations

import math

import pygame

from dungeon.srs_biome_order import (
    room_order_biome1_srs,
    room_order_biome2_srs,
    room_order_biome3_srs,
    room_order_biome4_srs,
)
from dungeon.room import RoomType
from game.config import BIOME2_START_INDEX, BIOME3_START_INDEX, BIOME4_START_INDEX
from game.scene_manager import SceneManager


DT = 1.0 / 60.0


def _boot_scene():
    sm = SceneManager()
    sm.init()
    sm.switch_to_game()
    scene = sm.current
    scene.update(DT)
    assert scene._room_controller is not None
    assert scene._player is not None
    return scene


def _campaign_safe_index(scene, biome_index: int) -> int:
    seed = int(scene._run_seed)
    if biome_index == 1:
        order = room_order_biome1_srs(seed)
        base = 0
    elif biome_index == 2:
        order = room_order_biome2_srs(seed)
        base = BIOME2_START_INDEX
    elif biome_index == 3:
        order = room_order_biome3_srs(seed)
        base = BIOME3_START_INDEX
    elif biome_index == 4:
        order = room_order_biome4_srs(seed)
        base = BIOME4_START_INDEX
    else:
        raise AssertionError(f"unsupported biome: {biome_index}")

    local = next(i for i, rt in enumerate(order) if rt == RoomType.SAFE)
    return base + local


def _load_campaign_room(scene, campaign_index: int) -> None:
    room = scene._room_controller.load_room(campaign_index)
    scene._apply_transient_reset_after_loading_campaign_room(room)
    scene._metrics_pending_room_start = True


def _move_player_to_safe_heal_anchor(scene) -> tuple[float, float]:
    room = scene._room_controller.current_room
    assert room is not None and room.room_type == RoomType.SAFE
    border = room.wall_border()
    tx, ty = border + 2, border + 2
    wx, wy = room.world_pos_for_tile(tx, ty)
    scene._player.world_pos = (wx, wy)
    scene.update(DT)  # refresh near-safe-room proximity flags
    assert scene._safe_room_heal_pos is not None
    hx, hy = scene._safe_room_heal_pos
    px, py = scene._player.world_pos
    assert math.hypot(px - hx, py - hy) <= 70.0
    return wx, wy


def _press_key(scene, key: int) -> None:
    ev = pygame.event.Event(pygame.KEYDOWN, {"key": key})
    scene.handle_event(ev)


def test_biome3_safe_room_upgrade_flow_allows_exactly_one_pick():
    scene = _boot_scene()
    safe_idx = _campaign_safe_index(scene, biome_index=3)
    _load_campaign_room(scene, safe_idx)
    _move_player_to_safe_heal_anchor(scene)

    assert scene._room_controller.current_room.room_type == RoomType.SAFE

    # Entering safe room alone should not auto-open upgrade UI.
    assert scene._safe_room_upgrade_pending is False
    assert scene._safe_room_upgrade_picks_remaining == 0
    assert scene._safe_room_upgrade_chosen_this_room is False

    # Safe-room interaction (F) arms biome 3 upgrade UI with exactly one pick.
    scene._player.hp = scene._player.max_hp * 0.5
    _press_key(scene, pygame.K_f)
    assert scene._safe_room_upgrade_pick_count_for_current_room() == 1
    assert scene._safe_room_upgrade_pending is True
    assert scene._safe_room_upgrade_picks_remaining == 1
    assert scene._safe_room_upgrade_chosen_this_room is False

    # One valid selection completes upgrade flow for biome 3.
    # Health upgrade (1): implementation grants bonus healing via apply_safe_room_health_upgrade and
    # records multiplier on _safe_room_health_mult; it does not raise base_max_hp / max_hp caps.
    old_max_hp = float(scene._player.max_hp)
    old_health_mult = float(getattr(scene._player, "_safe_room_health_mult", 1.0))
    _press_key(scene, pygame.K_1)
    assert scene._safe_room_upgrade_pending is False
    assert scene._safe_room_upgrade_picks_remaining == 0
    assert scene._safe_room_upgrade_chosen_this_room is True
    assert float(scene._player.max_hp) == old_max_hp
    assert float(getattr(scene._player, "_safe_room_health_mult", 1.0)) > old_health_mult

    # Further choices should not apply once room upgrade flow is complete.
    max_hp_after_first = float(scene._player.max_hp)
    _press_key(scene, pygame.K_2)
    assert float(scene._player.max_hp) == max_hp_after_first
    assert scene._safe_room_upgrade_picks_remaining == 0


def test_biome4_safe_room_upgrade_flow_requires_two_distinct_picks():
    scene = _boot_scene()
    safe_idx = _campaign_safe_index(scene, biome_index=4)
    _load_campaign_room(scene, safe_idx)
    _move_player_to_safe_heal_anchor(scene)

    # Entering safe room alone should not auto-open upgrade UI.
    assert scene._safe_room_upgrade_pending is False
    assert scene._safe_room_upgrade_picks_remaining == 0
    assert scene._safe_room_upgrade_chosen_this_room is False

    # Safe-room interaction (F) arms biome 4 upgrade UI with exactly two picks.
    scene._player.hp = scene._player.max_hp * 0.5
    _press_key(scene, pygame.K_f)
    assert scene._safe_room_upgrade_pick_count_for_current_room() == 2
    assert scene._safe_room_upgrade_pending is True
    assert scene._safe_room_upgrade_picks_remaining == 2
    assert scene._safe_room_biome4_chosen == set()

    # First valid selection accepted.
    _press_key(scene, pygame.K_1)
    assert scene._safe_room_upgrade_pending is True
    assert scene._safe_room_upgrade_picks_remaining == 1
    assert scene._safe_room_upgrade_chosen_this_room is False
    assert scene._safe_room_biome4_chosen == {1}

    # Duplicate selection should be ignored (still one pick left, no extra chosen options).
    _press_key(scene, pygame.K_1)
    assert scene._safe_room_upgrade_picks_remaining == 1
    assert scene._safe_room_biome4_chosen == {1}
    assert scene._safe_room_upgrade_chosen_this_room is False

    # Second distinct valid selection completes flow.
    _press_key(scene, pygame.K_2)
    assert scene._safe_room_upgrade_pending is False
    assert scene._safe_room_upgrade_picks_remaining == 0
    assert scene._safe_room_upgrade_chosen_this_room is True
    assert scene._safe_room_biome4_chosen == {1, 2}


def test_biome1_and_biome2_safe_rooms_do_not_expose_upgrade_selection_flow():
    scene = _boot_scene()

    for biome in (1, 2):
        safe_idx = _campaign_safe_index(scene, biome_index=biome)
        _load_campaign_room(scene, safe_idx)
        _move_player_to_safe_heal_anchor(scene)

        assert scene._room_controller.current_room.room_type == RoomType.SAFE
        assert scene._safe_room_upgrade_pick_count_for_current_room() == 0

        # F heal may mark pending internally, but no upgrade picks should be exposed for biome 1/2.
        scene._player.hp = scene._player.max_hp * 0.5
        _press_key(scene, pygame.K_f)
        assert scene._safe_room_upgrade_picks_remaining == 0
        assert scene._safe_room_upgrade_chosen_this_room is False

        # Number-key selection should not create a completed upgrade selection for non-upgrade biomes.
        _press_key(scene, pygame.K_1)
        _press_key(scene, pygame.K_2)
        assert scene._safe_room_upgrade_pick_count_for_current_room() == 0
        assert scene._safe_room_upgrade_picks_remaining == 0
        assert scene._safe_room_upgrade_chosen_this_room is False
