"""
Generated from prompt: test_prompts/unit/prompt_heavy_behavior.md

Title: Heavy enemy (`entities/heavy.py`)

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("entities.heavy")


def test_module_importable() -> None:
    """Smoke: `entities.heavy` imported successfully."""
    assert _mod is not None


def test_heavy_telegraph_before_attack() -> None:
    """Pending — see test_prompts/unit/prompt_heavy_behavior.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_heavy_behavior.md")


def test_heavy_high_hp_threshold() -> None:
    """Pending — see test_prompts/unit/prompt_heavy_behavior.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_heavy_behavior.md")


def test_heavy_resists_light_knockback() -> None:
    """Pending — see test_prompts/unit/prompt_heavy_behavior.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_heavy_behavior.md")

