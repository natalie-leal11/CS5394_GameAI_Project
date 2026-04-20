"""
Generated from prompt: test_prompts/rl/prompt_rl_best_progress_callback.md

Title: `rl/best_progress_callback.py` — unit-level callback

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("rl.best_progress_callback")


def test_module_importable() -> None:
    """Smoke: `rl.best_progress_callback` imported successfully."""
    assert _mod is not None


def test_callback_saves_on_improvement() -> None:
    """Pending — see test_prompts/rl/prompt_rl_best_progress_callback.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_best_progress_callback.md")


def test_callback_does_not_save_on_regression() -> None:
    """Pending — see test_prompts/rl/prompt_rl_best_progress_callback.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_best_progress_callback.md")


def test_callback_first_call_establishes_baseline() -> None:
    """Pending — see test_prompts/rl/prompt_rl_best_progress_callback.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_best_progress_callback.md")

