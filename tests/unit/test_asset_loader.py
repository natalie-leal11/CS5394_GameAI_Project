"""
Generated from prompt: test_prompts/unit/prompt_asset_loader.md

Title: Asset loader (`game/asset_loader.py`)

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


def test_missing_asset_returns_fallback_or_raises() -> None:
    """Pending — see test_prompts/unit/prompt_asset_loader.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_asset_loader.md")


def test_repeated_load_uses_cache() -> None:
    """Pending — see test_prompts/unit/prompt_asset_loader.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_asset_loader.md")


def test_clear_cache_forces_reload() -> None:
    """Pending — see test_prompts/unit/prompt_asset_loader.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_asset_loader.md")

