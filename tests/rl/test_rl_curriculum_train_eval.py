"""
Generated from prompt: test_prompts/rl/prompt_rl_curriculum_train_eval.md

Title: `rl/train_curriculum_ppo.py` + `rl/eval_curriculum.py` — smoke

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


def test_train_curriculum_ppo_argparser() -> None:
    """Pending — see test_prompts/rl/prompt_rl_curriculum_train_eval.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_curriculum_train_eval.md")


def test_train_curriculum_ppo_dry_run_creates_stage_dirs() -> None:
    """Pending — see test_prompts/rl/prompt_rl_curriculum_train_eval.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_curriculum_train_eval.md")


def test_eval_curriculum_argparser() -> None:
    """Pending — see test_prompts/rl/prompt_rl_curriculum_train_eval.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_curriculum_train_eval.md")


def test_eval_curriculum_missing_stages_raises_clear_error() -> None:
    """Pending — see test_prompts/rl/prompt_rl_curriculum_train_eval.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_curriculum_train_eval.md")

