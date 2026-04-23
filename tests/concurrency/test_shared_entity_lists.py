"""
Generated from prompt: test_prompts/concurrency/prompt_shared_entity_lists.md

Title: Shared entity lists safety

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


def test_projectile_list_mutation_safe() -> None:
    """Pending — see test_prompts/concurrency/prompt_shared_entity_lists.md."""
    pytest.skip("Pending implementation; see test_prompts/concurrency/prompt_shared_entity_lists.md")


def test_enemy_list_mutation_safe() -> None:
    """Pending — see test_prompts/concurrency/prompt_shared_entity_lists.md."""
    pytest.skip("Pending implementation; see test_prompts/concurrency/prompt_shared_entity_lists.md")


def test_vfx_list_mutation_safe() -> None:
    """Pending — see test_prompts/concurrency/prompt_shared_entity_lists.md."""
    pytest.skip("Pending implementation; see test_prompts/concurrency/prompt_shared_entity_lists.md")

