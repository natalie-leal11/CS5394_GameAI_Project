# Title screen (StartScene). Main menu with Play, Controls, Settings, Quit per Requirements_Analysis_Biome1.md §2.

import pygame

from game.scenes.base_scene import BaseScene
from game.config import LOGICAL_W, LOGICAL_H, BACKGROUND_COLOR
from game.asset_loader import load_image


# Button IDs for main menu (per §2.1)
BTN_PLAY = "play"
BTN_CONTROLS = "controls"
BTN_SETTINGS = "settings"
BTN_QUIT = "quit"

BUTTON_ORDER = [BTN_PLAY, BTN_CONTROLS, BTN_SETTINGS, BTN_QUIT]
BUTTON_LABELS = {
    BTN_PLAY: "Play",
    BTN_CONTROLS: "Controls",
    BTN_SETTINGS: "Settings",
    BTN_QUIT: "Quit",
}
# Optional image assets (§2.2). We also honor hover/pressed variants when present.
BUTTON_ASSETS = {
    BTN_PLAY: {
        "normal": "assets/ui/buttons/btn_play.png",
        "hover": "assets/ui/buttons/btn_play_hover.png",
        "pressed": "assets/ui/buttons/btn_play_pressed.png",
    },
    BTN_CONTROLS: {
        "normal": "assets/ui/buttons/btn_controls.png",
    },
    BTN_SETTINGS: {
        "normal": "assets/ui/buttons/btn_settings.png",
    },
    BTN_QUIT: {
        "normal": "assets/ui/buttons/btn_quit.png",
    },
}

BUTTON_W = 320
BUTTON_H = 96
BUTTON_SPACING = 16


class StartScene(BaseScene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self._bg = None
        self._font = None
        self._font_small = None
        self._button_rects: dict[str, pygame.Rect] = {}
        # id -> {"normal": surf, "hover": surf?, "pressed": surf?}
        self._button_surfaces: dict[str, dict[str, pygame.Surface | None]] = {}
        self._hover_id: str | None = None

    def _ensure_loaded(self, screen: pygame.Surface | None = None):
        """Load assets once. Called from draw; display is already set_mode'd by main."""
        if self._bg is not None:
            return
        self._bg = load_image("assets/backgrounds/main_menu_bg.png", size=(LOGICAL_W, LOGICAL_H))
        try:
            self._font = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", 28)
            self._font_small = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", 22)
        except (pygame.error, OSError):
            self._font = pygame.font.SysFont("arial", 24)
            self._font_small = pygame.font.SysFont("arial", 18)
        # Preload button images from assets/ui/buttons (paths resolved from project root)
        for bid in BUTTON_ORDER:
            surfaces: dict[str, pygame.Surface | None] = {}
            asset_info = BUTTON_ASSETS.get(bid, {})
            if isinstance(asset_info, dict):
                for state, path in asset_info.items():
                    if path:
                        surfaces[state] = load_image(
                            path,
                            size=(BUTTON_W, BUTTON_H),
                            use_colorkey=True,
                            colorkey_color=(255, 255, 255),
                            near_white_threshold=0,
                            corner_bg_tolerance=50,
                            exact_size=True,
                        )
            else:
                surfaces["normal"] = load_image(
                    asset_info, size=(BUTTON_W, BUTTON_H), exact_size=True
                )
            self._button_surfaces[bid] = surfaces
        # Layout: vertical list centered
        total_h = len(BUTTON_ORDER) * BUTTON_H + (len(BUTTON_ORDER) - 1) * BUTTON_SPACING
        start_y = LOGICAL_H // 2 - total_h // 2 + 20
        for i, bid in enumerate(BUTTON_ORDER):
            x = LOGICAL_W // 2 - BUTTON_W // 2
            y = start_y + i * (BUTTON_H + BUTTON_SPACING)
            self._button_rects[bid] = pygame.Rect(x, y, BUTTON_W, BUTTON_H)

    def _get_button_at(self, pos: tuple[int, int]) -> str | None:
        for bid in BUTTON_ORDER:
            if self._button_rects.get(bid) and self._button_rects[bid].collidepoint(pos):
                return bid
        return None

    def update(self, dt: float) -> None:
        self._ensure_loaded(None)
        self._hover_id = None
        pos = pygame.mouse.get_pos()
        self._hover_id = self._get_button_at(pos)

    def draw(self, screen: pygame.Surface, camera_offset: tuple[float, float] | None = None) -> None:
        self._ensure_loaded(screen)
        screen.fill(BACKGROUND_COLOR)
        bg = self._bg
        if bg.get_size() != (LOGICAL_W, LOGICAL_H):
            bg = pygame.transform.smoothscale(bg, (LOGICAL_W, LOGICAL_H))
        screen.blit(bg, (0, 0))
        # Buttons
        for bid in BUTTON_ORDER:
            rect = self._button_rects.get(bid)
            if rect is None:
                continue
            is_hover = self._hover_id == bid
            surfaces = self._button_surfaces.get(bid, {})
            # Prefer explicit hover asset; fall back to normal
            surf = None
            if is_hover and surfaces.get("hover") is not None:
                surf = surfaces.get("hover")
            else:
                surf = surfaces.get("normal")
            if surf is not None:
                screen.blit(surf, rect.topleft)
            else:
                color = (80, 120, 160) if is_hover else (60, 80, 100)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (140, 160, 180), rect, 2)
        # Keyboard hint
        hint = self._font_small.render("Enter = Play  |  Esc = Quit", True, (140, 140, 140))
        hw, _ = hint.get_size()
        screen.blit(hint, (LOGICAL_W // 2 - hw // 2, LOGICAL_H - 40))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.scene_manager.switch_to_game()
                return True
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._ensure_loaded(None)
            bid = self._get_button_at(event.pos)
            if bid == BTN_PLAY:
                self.scene_manager.switch_to_game()
                return True
            if bid == BTN_CONTROLS:
                self.scene_manager.switch_to_controls()
                return True
            if bid == BTN_SETTINGS:
                self.scene_manager.switch_to_settings()
                return True
            if bid == BTN_QUIT:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return True
        return False
