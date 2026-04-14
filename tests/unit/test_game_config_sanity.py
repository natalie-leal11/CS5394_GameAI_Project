"""Prompt 23: game.config."""
import game.config as cfg

def test_cooldowns_positive():
    assert cfg.PLAYER_DASH_COOLDOWN_SEC > 0

def test_hp_values_positive():
    assert cfg.PLAYER_BASE_HP > 0

def test_edge_no_negative_durations():
    assert cfg.PLAYER_SHORT_ATTACK_COOLDOWN_SEC >= 0
