# Room 0 training dummy per Requirements_Analysis_Biome1.md §9.5.
# Does not move, attack, or react; HP resets after damage (practice target).

import pygame

from game.asset_loader import load_image

# Requirements: assets/props/training_dummy.png
TRAINING_DUMMY_ASSET = "assets/props/training_dummy.png"
# Prop size (increased for visibility; hitbox for player attacks)
DUMMY_SIZE = (96, 128)


class TrainingDummy:
    """Non-hostile practice target. Infinite/resetting HP, no AI."""

    def __init__(self, world_pos: tuple[float, float]):
        self.world_pos = world_pos
        self.max_hp = 9999.0
        self.hp = self.max_hp
        self.inactive = False  # Never removed
        self.is_training_dummy = True
        self.enemy_type = "dummy"
        self._surface: pygame.Surface | None = None
        # Damage feedback: brief red flash when hit.
        self.damage_flash_timer: float = 0.0

    def get_hitbox_rect(self) -> pygame.Rect:
        w, h = DUMMY_SIZE
        x, y = self.world_pos
        return pygame.Rect(x - w / 2, y - h / 2, w, h)

    def update(self, dt: float, player, room_rect: pygame.Rect) -> None:
        # Dummy does not move or react. HP reset is done in GameScene after combat.
        if self.damage_flash_timer > 0.0:
            self.damage_flash_timer = max(0.0, self.damage_flash_timer - dt)

    def draw(self, screen: pygame.Surface, camera_offset: tuple[float, float]) -> None:
        if self._surface is None:
            self._surface = load_image(
                TRAINING_DUMMY_ASSET,
                size=DUMMY_SIZE,
                use_colorkey=True,
                colorkey_color=(255, 255, 255),
                corner_bg_tolerance=60,
                strip_flat_bg=True,
                exact_size=True,
            )
        if self._surface is None:
            r = self.get_hitbox_rect()
            cx, cy = camera_offset
            screen.fill((120, 100, 80), (r.x - cx, r.y - cy, r.w, r.h))
            return
        cx, cy = camera_offset
        x, y = self.world_pos
        sx = int(x - self._surface.get_width() / 2 - cx)
        sy = int(y - self._surface.get_height() / 2 - cy)
        screen.blit(self._surface, (sx, sy))
        if self.damage_flash_timer > 0.0:
            intensity = min(1.0, self.damage_flash_timer / 0.15)
            alpha = int(180 * intensity)
            flash = pygame.Surface(self._surface.get_size(), pygame.SRCALPHA)
            flash.fill((255, 40, 40, alpha))
            screen.blit(flash, (sx, sy))
