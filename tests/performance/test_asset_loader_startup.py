"""
Generated from prompt: test_prompts/performance/prompt_asset_loader_startup.md

Title: Performance — asset loader cold start

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


def test_cold_asset_load_budget() -> None:
    """Pending — see test_prompts/performance/prompt_asset_loader_startup.md."""
    pytest.skip("Pending implementation; see test_prompts/performance/prompt_asset_loader_startup.md")


def test_warm_asset_load_faster_than_cold() -> None:
    """Pending — see test_prompts/performance/prompt_asset_loader_startup.md."""
    pytest.skip("Pending implementation; see test_prompts/performance/prompt_asset_loader_startup.md")

