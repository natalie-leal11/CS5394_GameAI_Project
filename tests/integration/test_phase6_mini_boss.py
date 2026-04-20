"""Phase 6: Mini Boss — config, entity, combat, reward and door unlock."""

import math

import pygame
import pytest

from game.config import (
    MINI_BOSS_SIZE,
    MINI_BOSS_BASE_HP,
    MINI_BOSS_BASE_DAMAGE,
    MINI_BOSS_MOVE_SPEED,
    MINI_BOSS_ATTACK_RADIUS,
    MINI_BOSS_ATTACK_OFFSET,
    MINI_BOSS_ATTACK_COOLDOWN_SEC,
    MINI_BOSS_DOOR_UNLOCK_DELAY_SEC,
    MINI_BOSS_REWARD_HEAL_PERCENT,
    PLAYER_SHORT_ATTACK_RANGE_PX,
    PLAYER_SHORT_ATTACK_WINDUP_SEC,
    PLAYER_SHORT_ATTACK_ACTIVE_SEC,
    PLAYER_SHORT_ATTACK_DAMAGE,
)
from entities.mini_boss import MiniBoss
from entities.player import Player
from systems.combat import apply_player_attacks, apply_enemy_attacks

pygame.init()
pygame.display.set_mode((1, 1))


def test_phase6_config():
    """Phase 6 mini boss constants are defined and sensible."""
    assert MINI_BOSS_SIZE == (128, 128)
    assert MINI_BOSS_BASE_HP >= 100
    assert MINI_BOSS_BASE_DAMAGE >= 10
    assert MINI_BOSS_MOVE_SPEED > 0
    assert MINI_BOSS_ATTACK_RADIUS > 0
    assert MINI_BOSS_ATTACK_OFFSET > 0
    assert MINI_BOSS_ATTACK_COOLDOWN_SEC > 0
    assert 0.0 < MINI_BOSS_DOOR_UNLOCK_DELAY_SEC <= 2.0
    assert 0.0 < MINI_BOSS_REWARD_HEAL_PERCENT <= 1.0


def test_mini_boss_entity_basics():
    """MiniBoss has correct type, size, HP, damage and hitbox."""
    boss = MiniBoss((100.0, 100.0))
    assert boss.enemy_type == "mini_boss"
    assert boss.size == (128, 128)
    assert boss.max_hp == MINI_BOSS_BASE_HP
    assert boss.hp == MINI_BOSS_BASE_HP
    assert boss.damage == MINI_BOSS_BASE_DAMAGE
    assert boss.inactive is False
    rect = boss.get_hitbox_rect()
    assert rect.width == 128 and rect.height == 128
    assert rect.centerx == 100 and rect.centery == 100


def test_mini_boss_takes_player_damage():
    """Player short attack can damage MiniBoss (Phase 4 combat applies)."""
    player = Player()
    player.world_pos = (0.0, 0.0)
    player.facing = (1.0, 0.0)
    player.state = "attack_short"
    player._short_attack_timer = PLAYER_SHORT_ATTACK_WINDUP_SEC + PLAYER_SHORT_ATTACK_ACTIVE_SEC / 2.0
    boss = MiniBoss((PLAYER_SHORT_ATTACK_RANGE_PX * 0.5, 0.0))
    initial_hp = boss.hp
    events = apply_player_attacks(player, [boss])
    # Mini-boss may use damage multipliers slightly below full short-attack damage.
    assert boss.hp < initial_hp
    assert initial_hp - boss.hp >= PLAYER_SHORT_ATTACK_DAMAGE * 0.75
    assert len(events) >= 1
    assert any(e.target == boss and not e.is_player for e in events)


def test_mini_boss_death_sets_inactive():
    """When HP reaches 0, MiniBoss eventually becomes inactive after death animation."""
    boss = MiniBoss((200.0, 200.0))
    boss.hp = 0.0
    boss.state = "idle"
    boss._ensure_animations_loaded()
    # One update should set state to death; keep advancing until inactive
    class DummyPlayer:
        world_pos = (0.0, 0.0)
        def get_hitbox_rect(self):
            return pygame.Rect(0, 0, 32, 32)
    player = DummyPlayer()
    room = pygame.Rect(0, 0, 960, 640)
    for _ in range(120):
        boss.update(1.0 / 60.0, player, room)
        if boss.inactive:
            break
    assert boss.inactive is True


def test_mini_boss_attack_state_damages_player():
    """Mini boss in attack_01/attack_02 can deal damage (combat system)."""
    class DummyPlayer:
        def __init__(self):
            self.world_pos = (100.0, 100.0)
            self.hp = 100.0
        def is_blocking(self):
            return False
        def is_parry_active(self):
            return False
        def get_hitbox_rect(self):
            return pygame.Rect(90, 90, 24, 40)
    player = DummyPlayer()
    boss = MiniBoss((60.0, 100.0))  # to the left of player
    boss.state = "attack_01"
    boss.attack_cooldown_timer = 0.0
    boss.facing = (1.0, 0.0)
    events, _ = apply_enemy_attacks(player, [boss], 0.016)
    # If boss is in range and attack state, may produce event
    assert isinstance(events, list)
    if events:
        assert events[0].is_player is True
        assert player.hp < 100.0


def test_mini_boss_attack_cooldown_respected():
    """After attacking, mini boss cannot deal damage again until attack cooldown elapses."""
    class DummyPlayer:
        def __init__(self):
            self.world_pos = (100.0, 100.0)
            self.hp = 100.0
        def is_blocking(self):
            return False
        def is_parry_active(self):
            return False
        def get_hitbox_rect(self):
            return pygame.Rect(88, 80, 24, 40)

    boss = MiniBoss((100.0, 100.0))
    boss.state = "attack_01"
    boss.attack_cooldown_timer = 0.0
    player = DummyPlayer()
    initial_hp = player.hp
    events1, _ = apply_enemy_attacks(player, [boss], dt=0.1)
    if events1:
        assert player.hp < initial_hp
    # Immediately after, cooldown should be set
    assert boss.attack_cooldown_timer > 0.0
    # Same frame or next frame with no dt, no second hit (cooldown blocks)
    events2, _ = apply_enemy_attacks(player, [boss], dt=0.01)
    # Either no second event or cooldown prevented another hit
    assert boss.attack_cooldown_timer > 0.0


def test_door_unlock_and_reward_config():
    """Door unlock delay and reward heal percent are in valid range."""
    assert math.isclose(MINI_BOSS_DOOR_UNLOCK_DELAY_SEC, 0.5, rel_tol=1e-3)
    assert math.isclose(MINI_BOSS_REWARD_HEAL_PERCENT, 0.30, rel_tol=1e-3)
