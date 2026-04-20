"""
Generated from prompt: test_prompts/unit/prompt_debug_overlay.md

Title: Debug overlay (`game/debug/debug_overlay.py`) — new unit coverage

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("game.debug.debug_overlay")


def test_module_importable() -> None:
    """Smoke: `game.debug.debug_overlay` imported successfully."""
    assert _mod is not None


def test_overlay_off_by_default() -> None:
    """Pending — see test_prompts/unit/prompt_debug_overlay.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_debug_overlay.md")


def test_toggle_enables_overlay() -> None:
    """Pending — see test_prompts/unit/prompt_debug_overlay.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_debug_overlay.md")


def test_lines_include_expected_keys_when_enabled() -> None:
    """Pending — see test_prompts/unit/prompt_debug_overlay.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_debug_overlay.md")


def test_fps_line_updates_on_tick() -> None:
    """Pending — see test_prompts/unit/prompt_debug_overlay.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_debug_overlay.md")

