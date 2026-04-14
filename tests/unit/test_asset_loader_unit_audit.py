"""Prompt 34: Asset loader (audit duplicate name)."""
import pytest
from game.asset_loader import load_image

def test_load_twice_uses_cache_if_implemented(pygame_headless_display):
    a = load_image("assets/ui/buttons/btn_play.png")
    b = load_image("assets/ui/buttons/btn_play.png")
    assert a is not None and b is not None

def test_missing_file_raises_or_placeholder(pygame_headless_display):
    s = load_image("nonexistent/path/x.png")
    assert s.get_size()[0] > 0
