# Settings screen per Requirements_Analysis_Biome1.md §4. Back → Main Menu. Audio/display stubs for MVP.

import pygame

from game.scenes.base_scene import BaseScene
from game.config import LOGICAL_W, LOGICAL_H, BACKGROUND_COLOR
from game.asset_loader import load_image

BACK_BUTTON_ASSET = "assets/ui/buttons/btn_back.png"
SETTINGS_BG = "assets/backgrounds/settings_bg.png"
# Use larger native-style button and make its white background transparent.
BACK_BTN_W = 260
BACK_BTN_H = 80


class SettingsScene(BaseScene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self._bg = None
        self._font = None
        self._back_surf = None
        self._back_rect: pygame.Rect | None = None

    def _ensure_loaded(self):
        if self._bg is not None:
            return
        self._bg = load_image(SETTINGS_BG, size=(LOGICAL_W, LOGICAL_H))
        try:
            self._font = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", 22)
        except (pygame.error, OSError):
            self._font = pygame.font.SysFont("arial", 18)
        self._back_surf = load_image(
            BACK_BUTTON_ASSET,
            size=(BACK_BTN_W, BACK_BTN_H),
            use_colorkey=True,
            colorkey_color=(255, 255, 255),
            near_white_threshold=0,
            corner_bg_tolerance=50,
            exact_size=True,
        )
        self._back_rect = pygame.Rect(LOGICAL_W - BACK_BTN_W - 40, LOGICAL_H - BACK_BTN_H - 40, BACK_BTN_W, BACK_BTN_H)

    def draw(self, screen: pygame.Surface, camera_offset: tuple[float, float] | None = None) -> None:
        self._ensure_loaded()
        screen.fill(BACKGROUND_COLOR)
        bg = self._bg
        if bg.get_size() != (LOGICAL_W, LOGICAL_H):
            bg = pygame.transform.smoothscale(bg, (LOGICAL_W, LOGICAL_H))
        screen.blit(bg, (0, 0))
        title = self._font.render("Settings", True, (240, 240, 240))
        screen.blit(title, (LOGICAL_W // 2 - title.get_width() // 2, 50))
        # §4.2 / 4.3 placeholders for MVP
        stub = self._font.render("Master / Music / SFX volume and display mode (coming soon)", True, (180, 180, 180))
        screen.blit(stub, (80, 120))
        if self._back_rect and self._back_surf:
            screen.blit(self._back_surf, self._back_rect.topleft)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.scene_manager.switch_to_start()
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._ensure_loaded()
            if self._back_rect and self._back_rect.collidepoint(event.pos):
                self.scene_manager.switch_to_start()
                return True
        return False
