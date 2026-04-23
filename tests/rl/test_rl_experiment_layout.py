"""
Generated from prompt: test_prompts/rl/prompt_rl_experiment_layout.md

Title: RL — Experiment layout (`rl/experiment_layout.py`)

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("rl.experiment_layout")


def test_module_importable() -> None:
    """Smoke: `rl.experiment_layout` imported successfully."""
    assert _mod is not None


def test_run_id_unique_per_config() -> None:
    """Pending — see test_prompts/rl/prompt_rl_experiment_layout.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_experiment_layout.md")


def test_output_dir_parts_stable() -> None:
    """Pending — see test_prompts/rl/prompt_rl_experiment_layout.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_experiment_layout.md")


def test_layout_is_pure_function_of_config() -> None:
    """Pending — see test_prompts/rl/prompt_rl_experiment_layout.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_experiment_layout.md")

