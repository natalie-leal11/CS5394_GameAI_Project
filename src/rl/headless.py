"""
Pygame bootstrap for headless (no visible window) or hidden-window operation.

# RL-only path — safe to remove if RL is abandoned
"""

from __future__ import annotations

import os
import sys

import pygame

from game.config import LOGICAL_H, LOGICAL_W


def init_pygame_surface(*, human_window: bool) -> pygame.Surface:
    """
    Initialize pygame display subsystem and return a surface to pass to SceneManager.draw.

    - human_window: resizable window scaled like main.py (normal play).
    - not human_window: minimal hidden surface (no flip/update from env); gameplay logic still runs.
    """
    if not pygame.get_init():
        pygame.init()
    if human_window:
        info = pygame.display.Info()
        half_w = max(LOGICAL_W, info.current_w // 2)
        half_h = max(LOGICAL_H, info.current_h // 2)
        try:
            screen = pygame.display.set_mode((half_w, half_h), pygame.RESIZABLE | pygame.DOUBLEBUF)
        except pygame.error:
            screen = pygame.display.set_mode((LOGICAL_W, LOGICAL_H), pygame.RESIZABLE)
        pygame.display.set_caption("Dungeon Geeks (RL human)")
        return screen

    # Headless: avoid requiring a visible desktop; HIDDEN is supported in pygame 2.
    try:
        screen = pygame.display.set_mode((LOGICAL_W, LOGICAL_H), pygame.HIDDEN)
    except (pygame.error, TypeError):
        # Fallback: tiny window (may flash briefly on some systems)
        screen = pygame.display.set_mode((max(1, LOGICAL_W // 8), max(1, LOGICAL_H // 8)))
    pygame.display.set_caption("Dungeon Geeks (RL headless)")
    return screen


def maybe_init_dummy_video_driver() -> None:
    """
    Optional: SDL_VIDEODRIVER=dummy for CI/Linux headless servers (no display).
    Call before pygame.init(). No-op on Windows if dummy is unavailable.
    """
    if os.environ.get("SDL_VIDEODRIVER"):
        return
    if "linux" in sys.platform and os.environ.get("RL_FORCE_DUMMY_VIDEO"):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
