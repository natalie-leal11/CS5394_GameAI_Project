# Enemy projectile (Biome 3 ranged). Deterministic speed/lifetime; integrates with combat.

from typing import Tuple

import pygame

from game.config import (
    RANGED_PROJECTILE_SPEED,
    RANGED_PROJECTILE_DAMAGE,
    RANGED_PROJECTILE_LIFETIME_SEC,
)
from game.asset_loader import load_image

# Default asset (Biome 3 ranged enemy).
PROJECTILE_IMAGE_PATH = "assets/entities/projectiles/enemy_projectile_16x16.png"
PROJECTILE_SIZE = (16, 16)
# Biome 3 mini boss fireball (optional custom asset).
BIOME3_MINIBOSS_FIREBALL_IMAGE_PATH = "assets/entities/projectiles/biome3_miniboss_fireball.png"
BIOME3_MINIBOSS_FIREBALL_SIZE = (24, 24)


class Projectile:
    """
    Enemy-fired projectile. Fixed speed and lifetime; collision via existing hitbox system.
    Supports optional image_path and size for custom projectiles (e.g. Biome 3 mini boss fireball).
    """

    def __init__(
        self,
        world_pos: Tuple[float, float],
        direction: Tuple[float, float],
        damage: float = RANGED_PROJECTILE_DAMAGE,
        speed: float = RANGED_PROJECTILE_SPEED,
        lifetime_sec: float = RANGED_PROJECTILE_LIFETIME_SEC,
        image_path: str | None = None,
        size: Tuple[int, int] | None = None,
        ignore_obstacles: bool = False,
    ):
        self.world_pos = (float(world_pos[0]), float(world_pos[1]))
        dx, dy = direction
        length = (dx * dx + dy * dy) ** 0.5
        if length <= 1e-6:
            dx, dy = 1.0, 0.0
        else:
            dx, dy = dx / length, dy / length
        self.velocity = (dx * speed, dy * speed)
        self.damage = float(damage)
        self.lifetime_sec = float(lifetime_sec)
        self.age_sec = 0.0
        self.inactive = False
        self.ignore_obstacles = bool(ignore_obstacles)  # Boss fireballs: pass through props/hurdles
        self._surf: pygame.Surface | None = None
        self._image_path = image_path if image_path is not None else PROJECTILE_IMAGE_PATH
        self._size = size if size is not None else PROJECTILE_SIZE

    def _ensure_loaded(self) -> pygame.Surface:
        if self._surf is None:
            self._surf = load_image(
                self._image_path,
                size=self._size,
                use_colorkey=True,
                colorkey_color=(255, 255, 255),
                corner_bg_tolerance=40,
            )
        return self._surf

    def get_hitbox_rect(self) -> pygame.Rect:
        w, h = self._size[0], self._size[1]
        x, y = self.world_pos
        return pygame.Rect(int(x - w / 2), int(y - h / 2), w, h)

    def update(self, dt: float) -> None:
        if self.inactive:
            return
        self.age_sec += dt
        if self.age_sec >= self.lifetime_sec:
            self.inactive = True
            return
        vx, vy = self.velocity
        x, y = self.world_pos
        self.world_pos = (x + vx * dt, y + vy * dt)

    def draw(self, screen: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        if self.inactive:
            return
        surf = self._ensure_loaded()
        if surf is None:
            return
        cx, cy = camera_offset
        x = int(self.world_pos[0] - cx - surf.get_width() / 2)
        y = int(self.world_pos[1] - cy - surf.get_height() / 2)
        screen.blit(surf, (x, y))
