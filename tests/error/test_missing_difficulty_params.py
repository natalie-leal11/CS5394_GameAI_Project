"""
Generated from prompt: test_prompts/error/prompt_missing_difficulty_params.md

Title: Error — missing difficulty params file

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


def test_missing_file_returns_defaults() -> None:
    """Pending — see test_prompts/error/prompt_missing_difficulty_params.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_missing_difficulty_params.md")


def test_malformed_file_raises_clear_error() -> None:
    """Pending — see test_prompts/error/prompt_missing_difficulty_params.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_missing_difficulty_params.md")

