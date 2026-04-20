"""
Generated from prompt: test_prompts/error/prompt_rl_env_bad_inputs.md

Title: Error — RL env bad inputs

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("rl.env")


def test_module_importable() -> None:
    """Smoke: `rl.env` imported successfully."""
    assert _mod is not None


def test_step_bad_action_shape_raises() -> None:
    """Pending — see test_prompts/error/prompt_rl_env_bad_inputs.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_rl_env_bad_inputs.md")


def test_step_action_out_of_range_clamped_or_raises() -> None:
    """Pending — see test_prompts/error/prompt_rl_env_bad_inputs.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_rl_env_bad_inputs.md")


def test_reset_with_bad_seed_handled() -> None:
    """Pending — see test_prompts/error/prompt_rl_env_bad_inputs.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_rl_env_bad_inputs.md")

