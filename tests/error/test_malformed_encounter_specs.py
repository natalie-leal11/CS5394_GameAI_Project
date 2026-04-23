"""
Generated from prompt: test_prompts/error/prompt_malformed_encounter_specs.md

Title: Error — malformed encounter specs

This file is a runnable skeleton. Replace each `pytest.skip` body with a real
assertion per the prompt's acceptance criteria. Do NOT modify src/.
"""
from __future__ import annotations

import pytest

# Gate the whole module on the source module being importable.
_mod = pytest.importorskip("dungeon.seeded_encounter_specs")


def test_module_importable() -> None:
    """Smoke: `dungeon.seeded_encounter_specs` imported successfully."""
    assert _mod is not None


def test_missing_enemy_type_raises() -> None:
    """Pending — see test_prompts/error/prompt_malformed_encounter_specs.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_malformed_encounter_specs.md")


def test_negative_count_raises() -> None:
    """Pending — see test_prompts/error/prompt_malformed_encounter_specs.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_malformed_encounter_specs.md")


def test_unknown_room_id_raises() -> None:
    """Pending — see test_prompts/error/prompt_malformed_encounter_specs.md."""
    pytest.skip("Pending implementation; see test_prompts/error/prompt_malformed_encounter_specs.md")

