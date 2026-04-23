"""
Generated from prompt: test_prompts/rl/prompt_rl_compare_models.md

Title: `rl/compare_ppo_models.py` — smoke

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("rl.compare_ppo_models")


def test_module_importable() -> None:
    """Smoke: `rl.compare_ppo_models` imported successfully."""
    assert _mod is not None


def test_compare_models_aggregates_mean_and_std() -> None:
    """Pending — see test_prompts/rl/prompt_rl_compare_models.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_compare_models.md")


def test_compare_models_handles_single_model() -> None:
    """Pending — see test_prompts/rl/prompt_rl_compare_models.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_compare_models.md")


def test_compare_models_empty_input_raises_or_empty_summary() -> None:
    """Pending — see test_prompts/rl/prompt_rl_compare_models.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_compare_models.md")

