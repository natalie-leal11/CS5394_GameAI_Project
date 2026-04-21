"""
Generated from prompt: test_prompts/error/prompt_scene_manager_unknown_scene.md

Title: Error — SceneManager unknown scene id

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("game.scene_manager")


def test_module_importable() -> None:
    """Smoke: `game.scene_manager` imported successfully."""
    assert _mod is not None


def test_unknown_scene_id_raises() -> None:
    """Pending — see test_prompts/error/prompt_scene_manager_unknown_scene.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_scene_manager_unknown_scene.md")


def test_state_unchanged_on_error() -> None:
    """Pending — see test_prompts/error/prompt_scene_manager_unknown_scene.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_scene_manager_unknown_scene.md")

