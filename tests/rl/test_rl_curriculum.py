"""
Generated from prompt: test_prompts/rl/prompt_rl_curriculum.md

Title: RL — Curriculum wrappers & layout (`rl/curriculum_wrappers.py`, `rl/curriculum_layout.py`)

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("rl.curriculum_wrappers")


def test_module_importable() -> None:
    """Smoke: `rl.curriculum_wrappers` imported successfully."""
    assert _mod is not None


def test_stage_advances_on_success() -> None:
    """Pending — see test_prompts/rl/prompt_rl_curriculum.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_curriculum.md")


def test_stage_does_not_regress() -> None:
    """Pending — see test_prompts/rl/prompt_rl_curriculum.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_curriculum.md")


def test_curriculum_layout_keys_consistent() -> None:
    """Pending — see test_prompts/rl/prompt_rl_curriculum.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_curriculum.md")

