import math

import pygame
import pytest

from game import config as game_config
from game.config import (
    PLAYER_SHORT_ATTACK_DAMAGE,
    PLAYER_LONG_ATTACK_DAMAGE,
    PLAYER_SHORT_ATTACK_RANGE_PX,
    PLAYER_LONG_ATTACK_RANGE_PX,
    PLAYER_BLOCK_DAMAGE_FACTOR,
    ENEMY_SWARM_ATTACK_RADIUS,
    ENEMY_SWARM_ATTACK_OFFSET,
)

# Silence proximity / walk-attack trace spam during tests (combat still uses proximity logic).
game_config.DEBUG_PLAYER_ATTACK_PROXIMITY = False
game_config.DEBUG_PLAYER_ATTACK_WALK_TRACE = False
game_config.DEBUG_PLAYER_ATTACK_INPUT_TRACE = False
game_config.DEBUG_PLAYER_SHORT_ATTACK_BUFFER = False
game_config.DEBUG_LIVE_SHORT_ATTACK_TRACE = False
game_config.DEBUG_BLOCK_PARRY_TRACE = False
from entities.player import Player
from systems.combat import apply_player_attacks, apply_enemy_attacks
from systems.vfx import VfxManager


# Initialise pygame once so fonts/VFX can be created safely.
pygame.init()
pygame.display.set_mode((1, 1))


class DummyEnemy:
    def __init__(self, x: float, y: float, enemy_type: str = "swarm", hp: float = 100.0):
        self.world_pos = (x, y)
        self.enemy_type = enemy_type
        self.hp = hp
        self.inactive = False


def _make_player_at_origin_facing_right() -> Player:
    p = Player()
    p.world_pos = (0.0, 0.0)
    p.facing = (1.0, 0.0)
    p.attack_level = 0
    return p


def test_short_attack_buffers_while_attack_short_locked_then_swings_next_opportunity():
    """Clicks during attack_short set _pending_short_attack; next idle frame swings once."""
    p = _make_player_at_origin_facing_right()
    p._ensure_animations_loaded()
    p._set_state("attack_short")
    p.update(
        1 / 60.0,
        set(),
        (False, False, False),
        False,
        False,
        False,
        True,
        False,
    )
    assert p._pending_short_attack is True
    assert p.state == "attack_short"
    # Simulate swing finished: idle, still pending
    p._set_state("idle")
    p.update(
        1 / 60.0,
        set(),
        (False, False, False),
        False,
        False,
        False,
        False,
        False,
    )
    assert p.state == "attack_short"
    assert p._pending_short_attack is False


def test_short_attack_not_swallowed_by_parry_window_while_walking():
    """LMB must reach attack_short even if parry_window_timer is still counting (WASD + click)."""
    p = _make_player_at_origin_facing_right()
    p._ensure_animations_loaded()
    p._set_state("walk")
    p.parry_window_timer = 0.08
    p.update(
        1 / 60.0,
        {pygame.K_w},
        (False, False, False),
        False,
        False,
        False,
        True,
        False,
    )
    assert p.state == "attack_short"


def test_short_attack_hits_enemy_in_front():
    """Short attack deals damage to an enemy directly in front within range during active frames."""
    p = _make_player_at_origin_facing_right()
    p.state = "attack_short"
    # Put timer squarely inside active window.
    p._short_attack_timer = 0.5 * (
        PLAYER_SHORT_ATTACK_RANGE_PX * 0 + 0
    )  # value unused; we'll override below
    # Directly patch timer to mid-active region (windup+half active).
    from game.config import PLAYER_SHORT_ATTACK_WINDUP_SEC, PLAYER_SHORT_ATTACK_ACTIVE_SEC

    p._short_attack_timer = PLAYER_SHORT_ATTACK_WINDUP_SEC + PLAYER_SHORT_ATTACK_ACTIVE_SEC / 2.0

    enemy = DummyEnemy(PLAYER_SHORT_ATTACK_RANGE_PX * 0.8, 0.0, "swarm", hp=50.0)
    events = apply_player_attacks(p, [enemy])

    assert enemy.hp == 50.0 - PLAYER_SHORT_ATTACK_DAMAGE
    assert len(events) == 1
    assert math.isclose(events[0].amount, PLAYER_SHORT_ATTACK_DAMAGE)


def test_short_attack_does_not_hit_beyond_radius():
    """Enemies farther than short attack proximity radius take no damage."""
    p = _make_player_at_origin_facing_right()
    p.state = "attack_short"
    from game.config import PLAYER_SHORT_ATTACK_WINDUP_SEC, PLAYER_SHORT_ATTACK_ACTIVE_SEC

    p._short_attack_timer = PLAYER_SHORT_ATTACK_WINDUP_SEC + PLAYER_SHORT_ATTACK_ACTIVE_SEC / 2.0

    # Beyond short radius (account for 32px dummy hurtbox: need center far enough that closest-point dist > R).
    enemy = DummyEnemy(-80.0, 0.0, "swarm", hp=50.0)
    events = apply_player_attacks(p, [enemy])

    assert enemy.hp == 50.0
    assert events == []


def test_short_attack_hits_enemy_behind_within_radius():
    """Proximity short attack can hit an enemy behind the player if within radius."""
    p = _make_player_at_origin_facing_right()
    p.state = "attack_short"
    from game.config import PLAYER_SHORT_ATTACK_WINDUP_SEC, PLAYER_SHORT_ATTACK_ACTIVE_SEC

    p._short_attack_timer = PLAYER_SHORT_ATTACK_WINDUP_SEC + PLAYER_SHORT_ATTACK_ACTIVE_SEC / 2.0

    enemy = DummyEnemy(-PLAYER_SHORT_ATTACK_RANGE_PX * 0.8, 0.0, "swarm", hp=50.0)
    events = apply_player_attacks(p, [enemy])

    assert enemy.hp == 50.0 - PLAYER_SHORT_ATTACK_DAMAGE
    assert len(events) == 1


def test_short_attack_hits_enemy_only_once_per_swing():
    """Short attack does not multi-hit the same enemy during one swing."""
    p = _make_player_at_origin_facing_right()
    p.state = "attack_short"
    from game.config import PLAYER_SHORT_ATTACK_WINDUP_SEC, PLAYER_SHORT_ATTACK_ACTIVE_SEC

    p._short_attack_timer = PLAYER_SHORT_ATTACK_WINDUP_SEC + PLAYER_SHORT_ATTACK_ACTIVE_SEC / 2.0

    enemy = DummyEnemy(PLAYER_SHORT_ATTACK_RANGE_PX * 0.8, 0.0, "swarm", hp=50.0)

    events1 = apply_player_attacks(p, [enemy])
    # Second call while still in same attack should not deal more damage.
    events2 = apply_player_attacks(p, [enemy])

    assert enemy.hp == 50.0 - PLAYER_SHORT_ATTACK_DAMAGE
    assert len(events1) == 1
    assert events2 == []


def test_long_attack_hits_enemies_along_line_once():
    """Long attack damages enemies within long proximity radius once per swing."""
    p = _make_player_at_origin_facing_right()
    p.state = "attack_long"

    # Enemy within long radius (facing irrelevant).
    enemy = DummyEnemy(PLAYER_LONG_ATTACK_RANGE_PX * 0.5, 0.0, "swarm", hp=40.0)
    events1 = apply_player_attacks(p, [enemy])
    events2 = apply_player_attacks(p, [enemy])

    assert enemy.hp == 40.0 - PLAYER_LONG_ATTACK_DAMAGE
    assert len(events1) == 1
    assert events2 == []


def test_long_attack_ignores_enemy_beyond_radius():
    """Long attack does not hit enemies outside the long proximity radius."""
    p = _make_player_at_origin_facing_right()
    p.state = "attack_long"

    enemy = DummyEnemy(PLAYER_LONG_ATTACK_RANGE_PX * 1.2, 0.0, "swarm", hp=40.0)
    events = apply_player_attacks(p, [enemy])

    assert enemy.hp == 40.0
    assert events == []


def test_attack_multiplier_scales_damage():
    """Attack level increases short and long attack damage by +10% per level."""
    p = _make_player_at_origin_facing_right()
    p.attack_level = 3  # +30%
    mult = p.attack_multiplier
    assert math.isclose(mult, 1.0 + 0.10 * 3)


class DummyPlayerForEnemyDamage:
    def __init__(self, x: float, y: float, hp: float = 100.0, block: bool = False, parry: bool = False):
        self.world_pos = (x, y)
        self.hp = hp
        self._block = block
        self._parry = parry

    def is_blocking(self) -> bool:
        return self._block

    def is_parry_active(self) -> bool:
        return self._parry


class DummyMeleeEnemy:
    def __init__(self, x: float, y: float, damage: float = 10.0, enemy_type: str = "swarm"):
        self.world_pos = (x, y)
        self.enemy_type = enemy_type
        self.damage = damage
        self.state = "attack"
        self.attack_cooldown_timer = 0.0
        self.inactive = False


def _make_enemy_and_player_for_melee(block: bool = False, parry: bool = False):
    # Place enemy so its melee hitbox will overlap the player using swarm params.
    radius = ENEMY_SWARM_ATTACK_RADIUS
    offset = ENEMY_SWARM_ATTACK_OFFSET
    px, py = (0.0, 0.0)
    # Enemy is to the left; its attack hitbox will be centered to the right by `offset`.
    ex = px - offset / 2.0
    ey = py
    player = DummyPlayerForEnemyDamage(px, py, hp=100.0, block=block, parry=parry)
    enemy = DummyMeleeEnemy(ex, ey, damage=20.0, enemy_type="swarm")
    # Sanity: ensure radius is large enough so this setup should hit.
    assert offset / 2.0 < radius
    return player, enemy


def test_enemy_melee_hits_player_and_applies_damage():
    player, enemy = _make_enemy_and_player_for_melee(block=False, parry=False)

    events, parry_n = apply_enemy_attacks(player, [enemy], dt=0.016)
    assert parry_n == 0

    assert len(events) == 1
    event = events[0]
    assert event.is_player is True
    assert event.amount == pytest.approx(enemy.damage)
    assert player.hp == pytest.approx(100.0 - enemy.damage)
    # Enemy should now be on cooldown.
    assert enemy.attack_cooldown_timer > 0.0


def test_enemy_melee_block_reduces_damage():
    player, enemy = _make_enemy_and_player_for_melee(block=True, parry=False)

    events, parry_n = apply_enemy_attacks(player, [enemy], dt=0.016)
    assert parry_n == 0

    assert len(events) == 1
    event = events[0]
    expected = enemy.damage * PLAYER_BLOCK_DAMAGE_FACTOR
    assert event.amount == pytest.approx(expected)
    assert player.hp == pytest.approx(100.0 - expected)


def test_enemy_melee_parry_negates_damage():
    player, enemy = _make_enemy_and_player_for_melee(block=False, parry=True)

    events, parry_n = apply_enemy_attacks(player, [enemy], dt=0.016)
    assert parry_n == 1

    # Parry should prevent any damage events and leave HP unchanged.
    assert events == []
    assert player.hp == pytest.approx(100.0)
    # Cooldown should still start even on parry (swing was attempted).
    assert enemy.attack_cooldown_timer > 0.0


def test_parry_request_overrides_block_while_j_held():
    """K press arms parry even when J is held; player is in parry (not block) for combat."""
    p = Player()
    p.state = "idle"
    dt = 1.0 / 60.0
    p.update(
        dt,
        set(),
        (False, False, False),
        True,  # block_held (J)
        True,  # parry_request (K)
        False,
        False,
        False,
    )
    assert p.state == "parry"
    assert p.is_parry_active()
    assert not p.is_blocking()


def test_short_attack_same_frame_as_parry_request_prioritizes_short_attack():
    """LMB + K same frame: short attack is handled before K-tap parry (reliable melee input)."""
    p = Player()
    p.state = "block"
    dt = 1.0 / 60.0
    p.update(
        dt,
        set(),
        (True, False, False),  # LMB held -> often used with left_edge in GameScene
        True,  # block_held
        True,  # parry_request (K same frame as attack request)
        False,
        True,  # attack_short_request
        False,
    )
    assert p.state == "attack_short"


def test_damage_numbers_spawn_and_expire():
    mgr = VfxManager()
    assert getattr(mgr, "_damage_numbers") == []

    mgr.spawn_damage_number(12.7, (100.0, 100.0), is_player=False)
    numbers = getattr(mgr, "_damage_numbers")
    assert len(numbers) == 1
    n = numbers[0]
    # Value rounded to nearest int text.
    assert n.text == "13"
    # Enemy damage → red color.
    assert n.color == (255, 60, 60)

    # After less than lifetime (0.6s), it should still be alive.
    mgr.update(0.3)
    assert len(getattr(mgr, "_damage_numbers")) == 1

    # After enough additional time, it should be gone.
    mgr.update(0.25)
    mgr.update(0.1)
    assert len(getattr(mgr, "_damage_numbers")) == 0


def test_damage_numbers_color_for_player_damage():
    mgr = VfxManager()
    mgr.spawn_damage_number(5.0, (0.0, 0.0), is_player=True)
    numbers = getattr(mgr, "_damage_numbers")
    assert len(numbers) == 1
    # Player damage → yellow-ish color.
    assert numbers[0].color == (255, 230, 80)


def test_parry_negation_feedback_spawns_spark_and_label():
    mgr = VfxManager()
    mgr.spawn_parry_negation_feedback((100.0, 100.0))
    nums = getattr(mgr, "_damage_numbers")
    assert len(nums) == 1
    assert nums[0].text == "PARRY!"
    assert nums[0].color == (120, 230, 255)
    assert len(getattr(mgr, "_instances")) >= 1


def test_parry_inactive_allows_damage():
    """When parry is not active (e.g. window expired), enemy melee applies full damage."""
    player, enemy = _make_enemy_and_player_for_melee(block=False, parry=False)
    events, _ = apply_enemy_attacks(player, [enemy], dt=0.016)
    assert len(events) >= 1
    assert player.hp < 100.0


def test_multiple_enemies_each_produce_damage_events():
    """Two enemies hitting player in same frame produce two damage events."""
    player = DummyPlayerForEnemyDamage(0.0, 0.0, hp=100.0, block=False, parry=False)
    radius, offset = ENEMY_SWARM_ATTACK_RADIUS, ENEMY_SWARM_ATTACK_OFFSET
    e1 = DummyMeleeEnemy(-offset / 2.0, 0.0, damage=10.0)
    e2 = DummyMeleeEnemy(-offset / 2.0, 20.0, damage=15.0)
    events, _ = apply_enemy_attacks(player, [e1, e2], dt=0.016)
    assert len(events) == 2
    amounts = {e.amount for e in events}
    assert 10.0 in amounts and 15.0 in amounts
    assert player.hp == pytest.approx(100.0 - 10.0 - 15.0)


def test_damage_numbers_multiple_spawn_and_both_expire():
    """Multiple damage numbers can be active; each expires after lifetime."""
    mgr = VfxManager()
    mgr.spawn_damage_number(10, (50.0, 50.0), is_player=False)
    mgr.spawn_damage_number(20, (150.0, 50.0), is_player=True)
    numbers = getattr(mgr, "_damage_numbers")
    assert len(numbers) == 2
    colors = [n.color for n in numbers]
    assert (255, 60, 60) in colors
    assert (255, 230, 80) in colors
    mgr.update(0.7)
    assert len(getattr(mgr, "_damage_numbers")) == 0

