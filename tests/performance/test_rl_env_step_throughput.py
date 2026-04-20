"""
Generated from prompt: test_prompts/performance/prompt_rl_env_step_throughput.md

Title: RL env — step throughput

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


def test_headless_env_throughput_64_steps_under_budget() -> None:
    """Pending — see test_prompts/performance/prompt_rl_env_step_throughput.md."""
    pytest.skip("Pending implementation; see test_prompts/performance/prompt_rl_env_step_throughput.md")


def test_headless_env_reset_under_budget() -> None:
    """Pending — see test_prompts/performance/prompt_rl_env_step_throughput.md."""
    pytest.skip("Pending implementation; see test_prompts/performance/prompt_rl_env_step_throughput.md")

