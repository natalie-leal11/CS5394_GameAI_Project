"""
Generated from prompt: test_prompts/unit/prompt_game_config.md

Title: Game config sanity (`game/config.py`)

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("game.config")


def test_module_importable() -> None:
    """Smoke: `game.config` imported successfully."""
    assert _mod is not None


def test_required_keys_present() -> None:
    """Pending — see test_prompts/unit/prompt_game_config.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_game_config.md")


def test_numeric_ranges_sane() -> None:
    """Pending — see test_prompts/unit/prompt_game_config.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_game_config.md")


def test_no_nan_or_none_defaults() -> None:
    """Pending — see test_prompts/unit/prompt_game_config.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_game_config.md")

