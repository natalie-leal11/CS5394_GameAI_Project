# Controls screen per Requirements_Analysis_Biome1.md §3. Back → Main Menu.

import pygame

from game.scenes.base_scene import BaseScene
from game.config import LOGICAL_W, LOGICAL_H, BACKGROUND_COLOR
from game.asset_loader import load_image

BACK_BUTTON_ASSET = "assets/ui/buttons/btn_back.png"
CONTROLS_BG = "assets/backgrounds/controls_bg.png"
# Use larger native-style button and make its white background transparent.
BACK_BTN_W = 260
BACK_BTN_H = 80


def _window_size_px() -> tuple[int, int]:
    surf = pygame.display.get_surface()
    if surf is None:
        return (LOGICAL_W, LOGICAL_H)
    w, h = surf.get_size()
    return (max(1, w), max(1, h))


def screen_to_logical(pos: tuple[int, int]) -> tuple[int, int]:
    """Window mouse coords → logical buffer (same as main menu)."""
    wx, wy = _window_size_px()
    x, y = pos
    return (int(x * LOGICAL_W / wx), int(y * LOGICAL_H / wy))


def _fallback_hover_surface(normal: pygame.Surface) -> pygame.Surface:
    out = normal.copy()
    overlay = pygame.Surface(out.get_size(), pygame.SRCALPHA)
    overlay.fill((255, 220, 0, 100))
    out.blit(overlay, (0, 0))
    return out


class ControlsScene(BaseScene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self._bg = None
        self._font = None
        self._back_surf: pygame.Surface | None = None
        self._back_hover_surf: pygame.Surface | None = None
        self._back_rect: pygame.Rect | None = None
        self._back_hovered = False
        self._back_hover_prev = False

    def prepare_enter(self) -> None:
        """Called when navigating to this scene; safe to call multiple times."""
        self._ensure_loaded()
        self._back_hover_prev = False
        print(f"[CONTROLS] entered Back rect={self._back_rect}")

    def _ensure_loaded(self):
        if self._bg is not None:
            return
        self._bg = load_image(CONTROLS_BG, size=(LOGICAL_W, LOGICAL_H))
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
        self._back_hover_surf = _fallback_hover_surface(self._back_surf)
        # Single rect: from final image, bottom-right margin (matches prior layout)
        self._back_rect = self._back_surf.get_rect(bottomright=(LOGICAL_W - 40, LOGICAL_H - 40))

    def update(self, dt: float) -> None:
        self._ensure_loaded()
        if self._back_rect is None:
            return
        logical = screen_to_logical(pygame.mouse.get_pos())
        self._back_hovered = self._back_rect.collidepoint(logical)
        if self._back_hovered and not self._back_hover_prev:
            print("[CONTROLS] Back button hovered")
        self._back_hover_prev = self._back_hovered

    def draw(self, screen: pygame.Surface, camera_offset: tuple[float, float] | None = None) -> None:
        self._ensure_loaded()
        screen.fill(BACKGROUND_COLOR)
        bg = self._bg
        if bg.get_size() != (LOGICAL_W, LOGICAL_H):
            bg = pygame.transform.smoothscale(bg, (LOGICAL_W, LOGICAL_H))
        screen.blit(bg, (0, 0))
        # §3.2 Control mapping
        lines = [
            "Movement: W / A / S / D",
            "Short Attack: Left Mouse Click",
            "Long Attack: Right Mouse Click",
            "Dash: Space",
            "Block: J   Parry: K",
            "Pause / Menu: Esc",
        ]
        y = 120
        for line in lines:
            surf = self._font.render(line, True, (220, 220, 220))
            screen.blit(surf, (80, y))
            y += 36
        # Back button: one rect for draw + hit-test
        if self._back_rect and self._back_surf:
            surf = (
                self._back_hover_surf
                if (self._back_hovered and self._back_hover_surf is not None)
                else self._back_surf
            )
            screen.blit(surf, self._back_rect.topleft)
        title = self._font.render("Controls", True, (240, 240, 240))
        screen.blit(title, (LOGICAL_W // 2 - title.get_width() // 2, 50))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            print("[CONTROLS] Esc -> Main Menu (switch_to_start)")
            self.scene_manager.switch_to_start()
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._ensure_loaded()
            if self._back_rect is not None:
                logical_pos = screen_to_logical(event.pos)
                if self._back_rect.collidepoint(logical_pos):
                    print("[CONTROLS] Back clicked -> Main Menu (switch_to_start)")
                    self.scene_manager.switch_to_start()
                    return True
        return False
