"""
Generated from prompt: test_prompts/error/prompt_dataset_export_errors.md

Title: Dataset export — error paths

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("game.rl.dataset_export")


def test_module_importable() -> None:
    """Smoke: `game.rl.dataset_export` imported successfully."""
    assert _mod is not None


def test_export_to_unwritable_path_raises() -> None:
    """Pending — see test_prompts/error/prompt_dataset_export_errors.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_dataset_export_errors.md")


def test_export_with_mismatched_schema_raises() -> None:
    """Pending — see test_prompts/error/prompt_dataset_export_errors.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_dataset_export_errors.md")


def test_export_empty_trajectory_returns_empty_or_raises_clearly() -> None:
    """Pending — see test_prompts/error/prompt_dataset_export_errors.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_dataset_export_errors.md")

