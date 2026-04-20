"""
Generated from prompt: test_prompts/unit/prompt_start_scene.md

Title: Start scene (`game/scenes/start_scene.py`) — new unit coverage

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("game.scenes.start_scene")


def test_module_importable() -> None:
    """Smoke: `game.scenes.start_scene` imported successfully."""
    assert _mod is not None


def test_start_scene_initial_menu_index_zero() -> None:
    """Pending — see test_prompts/unit/prompt_start_scene.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_start_scene.md")


def test_menu_navigation_wraps_correctly() -> None:
    """Pending — see test_prompts/unit/prompt_start_scene.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_start_scene.md")


def test_confirm_dispatches_expected_transition() -> None:
    """Pending — see test_prompts/unit/prompt_start_scene.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_start_scene.md")


def test_escape_does_not_exit_without_confirm() -> None:
    """Pending — see test_prompts/unit/prompt_start_scene.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_start_scene.md")

