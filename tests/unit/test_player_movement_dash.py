"""
Generated from prompt: test_prompts/unit/prompt_player_movement_dash.md

Title: Player — Movement, dash cooldown, dash i-frames

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("entities.player")


def test_module_importable() -> None:
    """Smoke: `entities.player` imported successfully."""
    assert _mod is not None


def test_movement_velocity_applied_per_frame() -> None:
    """Pending — see test_prompts/unit/prompt_player_movement_dash.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_player_movement_dash.md")


def test_dash_triggers_on_input() -> None:
    """Pending — see test_prompts/unit/prompt_player_movement_dash.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_player_movement_dash.md")


def test_dash_cooldown_blocks_re_trigger() -> None:
    """Pending — see test_prompts/unit/prompt_player_movement_dash.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_player_movement_dash.md")


def test_dash_cooldown_expires() -> None:
    """Pending — see test_prompts/unit/prompt_player_movement_dash.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_player_movement_dash.md")


def test_dash_grants_iframes() -> None:
    """Pending — see test_prompts/unit/prompt_player_movement_dash.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_player_movement_dash.md")

