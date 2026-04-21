"""
Generated from prompt: test_prompts/error/prompt_invalid_room_surfaces.md

Title: Invalid room / missing pygame surface

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("dungeon.room")


def test_module_importable() -> None:
    """Smoke: `dungeon.room` imported successfully."""
    assert _mod is not None


def test_draw_with_none_surface_raises_clear_error() -> None:
    """Pending — see test_prompts/error/prompt_invalid_room_surfaces.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_invalid_room_surfaces.md")


def test_draw_with_zero_size_surface_is_noop_or_clear_error() -> None:
    """Pending — see test_prompts/error/prompt_invalid_room_surfaces.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_invalid_room_surfaces.md")


def test_draw_with_room_missing_fields_raises_type_error_clearly() -> None:
    """Pending — see test_prompts/error/prompt_invalid_room_surfaces.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_invalid_room_surfaces.md")

