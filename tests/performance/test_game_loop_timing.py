"""
Generated from prompt: test_prompts/performance/prompt_game_loop_timing.md

Title: Performance — game loop step timing

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("game.scenes.game_scene")


def test_module_importable() -> None:
    """Smoke: `game.scenes.game_scene` imported successfully."""
    assert _mod is not None


def test_update_step_under_budget_small() -> None:
    """Pending — see test_prompts/performance/prompt_game_loop_timing.md."""
    pytest.skip("Pending implementation; see test_prompts/performance/prompt_game_loop_timing.md")


def test_update_step_under_budget_medium() -> None:
    """Pending — see test_prompts/performance/prompt_game_loop_timing.md."""
    pytest.skip("Pending implementation; see test_prompts/performance/prompt_game_loop_timing.md")

