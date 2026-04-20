"""GameScene update loop smoke: stable stepping, entity list churn without crash."""

from __future__ import annotations

from entities.swarm import Swarm
from game.scene_manager import SceneManager


DT = 1.0 / 60.0


def test_update_order_stable_over_frames():
    sm = SceneManager()
    sm.init()
    sm.switch_to_game()
    for _ in range(15):
        sm.update(DT)
    assert sm.current is not None


def test_entity_added_mid_frame_does_not_crash():
    sm = SceneManager()
    sm.init()
    sm.switch_to_game()
    scene = sm.current
    scene.update(DT)
    scene._enemies.append(Swarm((150.0, 220.0)))
    scene.update(DT)
    assert len(scene._enemies) >= 1


def test_entity_removed_mid_frame_does_not_crash():
    sm = SceneManager()
    sm.init()
    sm.switch_to_game()
    scene = sm.current
    scene.update(DT)
    e = Swarm((180.0, 240.0))
    scene._enemies.append(e)
    scene.update(DT)
    scene._enemies.clear()
    scene.update(DT)
    assert scene._enemies == []
