"""
Generated from prompt: test_prompts/error/prompt_invalid_config.md

Title: Error — invalid `game/config.py` values

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


def test_negative_hp_rejected() -> None:
    """Pending — see test_prompts/error/prompt_invalid_config.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_invalid_config.md")


def test_nan_value_rejected() -> None:
    """Pending — see test_prompts/error/prompt_invalid_config.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_invalid_config.md")


def test_unknown_key_ignored_or_warns() -> None:
    """Pending — see test_prompts/error/prompt_invalid_config.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_invalid_config.md")

