"""
Base entity: position, collision radius. Used by player and enemies.
"""
from dataclasses import dataclass


@dataclass
class Entity:
    """Position and collision radius. Subclass for HP, velocity, etc."""

    x: float
    y: float
    radius: float

    @property
    def center(self) -> tuple[float, float]:
        return (self.x, self.y)
