"""
Generated from prompt: test_prompts/rl/prompt_rl_observation_schema.md

Title: RL — Observation schema (`rl/obs.py`)

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("rl.obs")


def test_module_importable() -> None:
    """Smoke: `rl.obs` imported successfully."""
    assert _mod is not None


def test_observation_dtype_matches_space() -> None:
    """Pending — see test_prompts/rl/prompt_rl_observation_schema.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_observation_schema.md")


def test_observation_shape_matches_space() -> None:
    """Pending — see test_prompts/rl/prompt_rl_observation_schema.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_observation_schema.md")


def test_observation_no_nan_or_inf() -> None:
    """Pending — see test_prompts/rl/prompt_rl_observation_schema.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_observation_schema.md")

