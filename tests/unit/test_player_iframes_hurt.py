"""
Generated from prompt: test_prompts/unit/prompt_player_iframes_hurt.md

Title: Player — Hurt state and i-frames

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("entities.player")


def test_module_importable() -> None:
    """Smoke: `entities.player` imported successfully."""
    assert _mod is not None


def test_iframes_block_second_hit_same_frame() -> None:
    """Pending — see test_prompts/unit/prompt_player_iframes_hurt.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_player_iframes_hurt.md")


def test_iframes_decay_over_time() -> None:
    """Pending — see test_prompts/unit/prompt_player_iframes_hurt.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_player_iframes_hurt.md")


def test_hurt_state_clears_after_duration() -> None:
    """Pending — see test_prompts/unit/prompt_player_iframes_hurt.md."""
    pytest.skip("Pending implementation; see test_prompts/unit/prompt_player_iframes_hurt.md")

