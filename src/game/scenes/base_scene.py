# Base interface for all scenes. Update, draw, and event handling.

import pygame


class BaseScene:
    """Base class for StartScene, GameScene, etc. Scene manager delegates to current scene."""

    def __init__(self, scene_manager):
        self.scene_manager = scene_manager

    def update(self, dt: float) -> None:
        """Update scene state. dt in seconds."""
        pass

    def draw(self, screen: pygame.Surface, camera_offset: tuple[float, float] | None = None) -> None:
        """
        Draw scene. camera_offset is (cx, cy) for world-space; use (0,0) for UI-only scenes.
        Screen-space only when camera_offset is None or (0,0) for full-screen UI.
        """
        pass

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle one event. Return True if consumed (e.g. so other systems don't act)."""
        return False
