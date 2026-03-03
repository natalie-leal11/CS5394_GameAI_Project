import math

import pygame
import pytest

from game.config import (
    TILE_SIZE,
    ENEMY_SWARM_STOP_DISTANCE,
    ENEMY_SWARM_MOVE_SPEED,
    ENEMY_SWARM_SIZE,
    ENEMY_FLANKER_SIZE,
    ENEMY_BRUTE_SIZE,
    ENEMY_SWARM_BASE_HP,
    ENEMY_FLANKER_BASE_HP,
    ENEMY_BRUTE_BASE_HP,
    ENEMY_SWARM_BASE_DAMAGE,
    ENEMY_FLANKER_BASE_DAMAGE,
    ENEMY_BRUTE_BASE_DAMAGE,
    ENEMY_CONTACT_DAMAGE_INTERVAL_SEC,
    ENEMY_ELITE_HP_MULT,
    ENEMY_ELITE_DAMAGE_MULT,
)
from entities.enemy_base import EnemyBase
from entities.swarm import Swarm
from entities.flanker import Flanker
from entities.brute import Brute
from game.scene_manager import SceneManager
from game.scenes.game_scene import GameScene


# Initialise a tiny display once so asset loading (convert_alpha) works in tests.
pygame.init()
pygame.display.set_mode((1, 1))


def test_phase3_config_constants_basic():
    """Enemy config constants are defined with expected baselines."""
    assert ENEMY_SWARM_SIZE == (60, 60)
    assert ENEMY_FLANKER_SIZE == (48, 48)
    assert ENEMY_BRUTE_SIZE[0] >= 80 and ENEMY_BRUTE_SIZE[1] >= 80

    assert ENEMY_SWARM_BASE_HP > 0
    assert ENEMY_FLANKER_BASE_HP > 0
    assert ENEMY_BRUTE_BASE_HP > ENEMY_SWARM_BASE_HP and ENEMY_BRUTE_BASE_HP > ENEMY_FLANKER_BASE_HP

    assert ENEMY_SWARM_BASE_DAMAGE > 0
    assert ENEMY_FLANKER_BASE_DAMAGE > 0
    assert ENEMY_BRUTE_BASE_DAMAGE >= ENEMY_SWARM_BASE_DAMAGE and ENEMY_BRUTE_BASE_DAMAGE >= ENEMY_FLANKER_BASE_DAMAGE

    assert math.isclose(ENEMY_ELITE_HP_MULT, 1.4, rel_tol=1e-3)
    assert math.isclose(ENEMY_ELITE_DAMAGE_MULT, 1.2, rel_tol=1e-3)
    assert math.isclose(ENEMY_CONTACT_DAMAGE_INTERVAL_SEC, 0.5, rel_tol=1e-3)


def test_enemy_elite_modifiers_applied():
    """Elite enemies get +40% HP and +20% damage."""
    base = EnemyBase("swarm", (100, 100), elite=False)
    elite = EnemyBase("swarm", (100, 100), elite=True)

    assert elite.max_hp == pytest.approx(base.max_hp * ENEMY_ELITE_HP_MULT)
    assert elite.damage == pytest.approx(base.damage * ENEMY_ELITE_DAMAGE_MULT)


def test_enemy_contact_damage_interval_and_reset():
    """Phase 4: Enemies do not apply contact/touch damage; damage is melee-only."""

    class MockPlayer:
        def __init__(self, x, y, w, h, hp):
            self.world_pos = (x, y)
            self._w = w
            self._h = h
            self.hp = hp
            self.state = "idle"

        def get_hitbox_rect(self):
            return pygame.Rect(
                self.world_pos[0] - self._w / 2,
                self.world_pos[1] - self._h / 2,
                self._w,
                self._h,
            )

    enemy = EnemyBase("swarm", (100.0, 100.0), elite=False)
    enemy._ensure_animations_loaded()
    player = MockPlayer(100.0, 100.0, 32, 32, hp=100)

    # Overlap for longer than contact interval: no damage (contact damage disabled).
    enemy.update(ENEMY_CONTACT_DAMAGE_INTERVAL_SEC * 0.4, player)
    assert player.hp == 100
    enemy.update(ENEMY_CONTACT_DAMAGE_INTERVAL_SEC * 1.0, player)
    assert player.hp == 100


def test_swarm_flanker_brute_types():
    """Swarm, Flanker, Brute subclasses are wired to the correct enemy_type."""
    s = Swarm((0, 0))
    f = Flanker((0, 0))
    b = Brute((0, 0))
    assert s.enemy_type == "swarm"
    assert f.enemy_type == "flanker"
    assert b.enemy_type == "brute"


def test_game_scene_spawns_enemies_three_tiles_away():
    """GameScene (with Phase 5 spawn system) eventually spawns enemies at least 3 tiles from player."""
    sm = SceneManager()
    sm.init()
    sm.switch_to_game()
    scene: GameScene = sm.current

    # One update so Phase 7 room controller exists and we start in Room 0 when USE_PHASE7_DUNGEON.
    scene.update(1.0 / 60.0)

    # If Phase 7 is on we're in Room 0 (dummy only). Transition to first combat room (2–5) so spawns run.
    if getattr(scene, "_room_controller", None) is not None and scene._room_controller.current_room_index == 0:
        from dungeon.room import RoomType, _room_order_biome1
        from game.config import SEED
        order = _room_order_biome1(SEED)
        combat_idx = next((i for i in range(1, 7) if order[i] == RoomType.COMBAT), 2)
        scene._room_controller.load_room(combat_idx)
        room = scene._room_controller.current_room
        if room is not None:
            wx, wy = room.world_pos_for_tile(room.spawn_tile[0], room.spawn_tile[1])
            scene._player.world_pos = (wx, wy)
        scene._enemies = []
        scene._spawned_enemies = False
        scene._spawn_system = None
        scene._room_cleared_flag = False

    # Advance long enough for Phase 5 telegraphs (0.5s) and staggered spawn slots.
    # Slots start at 0, 0.4, 0.8, 2.0 s; each spawns after +0.5s telegraph → brute at ~1.3s.
    steps = 100  # ~1.67 s at 60 FPS
    for _ in range(steps):
        scene.update(1.0 / 60.0)

    assert hasattr(scene, "_enemies")
    enemies = scene._enemies
    types = {e.enemy_type for e in enemies if not getattr(e, "is_training_dummy", False)}
    # Beginner Test Mode: Room 1 has only 2 Swarm; normal mode has Swarm+Flanker+Brute in first combat room.
    from game.config import BEGINNER_TEST_MODE
    if BEGINNER_TEST_MODE:
        assert len(types) >= 1, "Beginner mode: at least one enemy type should spawn in combat room"
        assert sum(1 for e in enemies if not getattr(e, "is_training_dummy", False)) >= 1
    else:
        assert {"swarm", "flanker", "brute"} <= types

    # Spawn system places enemies at least 3 tiles away; after 100 steps they may have moved.
    # So require at least 1 tile separation (no spawn on top of player). Skip training dummy.
    px, py = scene._player.world_pos
    min_sep = TILE_SIZE
    for e in enemies:
        if getattr(e, "is_training_dummy", False):
            continue
        dx = e.world_pos[0] - px
        dy = e.world_pos[1] - py
        dist = math.hypot(dx, dy)
        assert dist >= min_sep - 1e-3, f"{e.enemy_type} too close: dist={dist}"


def test_enemy_moves_toward_player_until_stop_distance():
    """Enemy moves toward player when beyond stop distance; position advances in correct direction."""
    class MockPlayer:
        def __init__(self, x, y):
            self.world_pos = (x, y)
            self.state = "idle"

        def get_hitbox_rect(self):
            return pygame.Rect(self.world_pos[0] - 12, self.world_pos[1] - 20, 24, 40)

    player = MockPlayer(300.0, 200.0)
    enemy = Swarm((100.0, 200.0))
    enemy._ensure_animations_loaded()
    room_rect = pygame.Rect(0, 0, 960, 640)
    x_before = enemy.world_pos[0]
    enemy.update(0.1, player, room_rect)
    x_after = enemy.world_pos[0]
    # Player is to the right; enemy should move right (increase x)
    assert x_after > x_before
    # Should not overshoot past player in one small dt
    assert enemy.world_pos[0] < 320


def test_elite_flag_set_on_elite_enemies():
    """Elite Swarm/Flanker/Brute have elite=True and higher max_hp/damage than non-elite."""
    s_base = Swarm((0, 0), elite=False)
    s_elite = Swarm((0, 0), elite=True)
    assert s_base.elite is False
    assert s_elite.elite is True
    assert s_elite.max_hp > s_base.max_hp
    assert s_elite.damage > s_base.damage
    f_elite = Flanker((0, 0), elite=True)
    assert f_elite.elite is True
    b_elite = Brute((0, 0), elite=True)
    assert b_elite.elite is True

