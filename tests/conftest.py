"""Shared pytest configuration: put `src` on path and init pygame for tests that need display."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import pytest

try:
    import pygame

    pygame.init()
    pygame.display.set_mode((1, 1))
    _PYGAME_OK = True
except Exception:  # noqa: BLE001
    _PYGAME_OK = False


def _ensure_pygame_display() -> None:
    """Re-init after code paths that call pygame.quit() (e.g. rl.env.DungeonEnv.close)."""
    if not _PYGAME_OK:
        return
    import pygame

    if not pygame.get_init():
        pygame.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1, 1))


@pytest.fixture(autouse=True)
def _pygame_display_for_each_test():
    _ensure_pygame_display()
    yield
    # Optional: leave display up for next test; do not quit here.


@pytest.fixture(scope="session")
def pygame_headless_display():
    """Minimal display surface for asset loading in entity tests."""
    if not _PYGAME_OK:
        pytest.skip("pygame display init failed")
    _ensure_pygame_display()
    return True
