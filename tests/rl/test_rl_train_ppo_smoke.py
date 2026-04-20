"""
Generated from prompt: test_prompts/rl/prompt_rl_train_ppo_smoke.md

Title: `rl/train_ppo.py` — smoke (CLI arg parsing + 1-step dry-run)

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("rl.train_ppo")


def test_module_importable() -> None:
    """Smoke: `rl.train_ppo` imported successfully."""
    assert _mod is not None


def test_train_ppo_argparser_parses_defaults() -> None:
    """Pending — see test_prompts/rl/prompt_rl_train_ppo_smoke.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_train_ppo_smoke.md")


def test_train_ppo_argparser_rejects_unknown_args() -> None:
    """Pending — see test_prompts/rl/prompt_rl_train_ppo_smoke.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_train_ppo_smoke.md")


def test_train_ppo_dry_run_creates_output_dir() -> None:
    """Pending — see test_prompts/rl/prompt_rl_train_ppo_smoke.md."""
    pytest.skip("Pending implementation; see test_prompts/rl/prompt_rl_train_ppo_smoke.md")

