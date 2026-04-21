"""
Generated from prompt: test_prompts/error/prompt_invalid_biome_sequence.md

Title: Error — invalid biome sequence

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("dungeon.biome1_sequence")


def test_module_importable() -> None:
    """Smoke: `dungeon.biome1_sequence` imported successfully."""
    assert _mod is not None


def test_gap_in_sequence_detected() -> None:
    """Pending — see test_prompts/error/prompt_invalid_biome_sequence.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_invalid_biome_sequence.md")


def test_duplicate_room_detected() -> None:
    """Pending — see test_prompts/error/prompt_invalid_biome_sequence.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_invalid_biome_sequence.md")


def test_unknown_room_detected() -> None:
    """Pending — see test_prompts/error/prompt_invalid_biome_sequence.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_invalid_biome_sequence.md")

