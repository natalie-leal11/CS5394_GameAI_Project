"""
Generated from prompt: test_prompts/error/prompt_asset_loader_missing.md

Title: Error — asset loader missing files

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("game.asset_loader")


def test_module_importable() -> None:
    """Smoke: `game.asset_loader` imported successfully."""
    assert _mod is not None


def test_missing_texture_clear_error_or_fallback() -> None:
    """Pending — see test_prompts/error/prompt_asset_loader_missing.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_asset_loader_missing.md")


def test_missing_sound_does_not_crash_game() -> None:
    """Pending — see test_prompts/error/prompt_asset_loader_missing.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_asset_loader_missing.md")

