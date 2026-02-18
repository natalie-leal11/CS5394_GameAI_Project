"""
Base scene interface. All scenes implement handle_event, update, render.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from src.game.core.scene_manager import SceneManager


class BaseScene(ABC):
    """Base class for Menu, Run, and End scenes."""

    def __init__(self, manager: "SceneManager") -> None:
        self.manager = manager

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Process one pygame event."""
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update scene state. dt in seconds."""
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """Draw the scene to screen."""
        pass
