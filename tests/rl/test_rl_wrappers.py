"""
Generated from prompt: test_prompts/rl/prompt_rl_wrappers.md

Title: RL — Env wrappers (`rl/wrappers.py`)

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("rl.wrappers")


def test_module_importable() -> None:
    """Smoke: `rl.wrappers` imported successfully."""
    assert _mod is not None


def test_flatten_wrapper_preserves_info() -> None:
    """Pending — see test_prompts/rl/prompt_rl_wrappers.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_wrappers.md")


def test_normalize_wrapper_stats_update() -> None:
    """Pending — see test_prompts/rl/prompt_rl_wrappers.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_wrappers.md")


def test_framestack_wrapper_shape() -> None:
    """Pending — see test_prompts/rl/prompt_rl_wrappers.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_wrappers.md")

