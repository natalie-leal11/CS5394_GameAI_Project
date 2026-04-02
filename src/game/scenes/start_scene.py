# Title screen (StartScene). Main menu with Play, Controls, Settings, Quit per Requirements_Analysis_Biome1.md §2.

from __future__ import annotations

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


def _window_size_px() -> tuple[int, int]:
    surf = pygame.display.get_surface()
    if surf is None:
        return (LOGICAL_W, LOGICAL_H)
    w, h = surf.get_size()
    return (max(1, w), max(1, h))


def screen_to_logical(pos: tuple[int, int]) -> tuple[int, int]:
    """Map window/screen mouse coordinates to logical buffer (960×640) used for drawing."""
    wx, wy = _window_size_px()
    x, y = pos
    lx = int(x * LOGICAL_W / wx)
    ly = int(y * LOGICAL_H / wy)
    return (lx, ly)


def _fallback_hover_surface(normal: pygame.Surface) -> pygame.Surface:
    """Yellow highlight when no dedicated hover PNG exists; keeps base art."""
    out = normal.copy()
    overlay = pygame.Surface(out.get_size(), pygame.SRCALPHA)
    overlay.fill((255, 220, 0, 100))
    out.blit(overlay, (0, 0))
    return out


class StartScene(BaseScene):
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self._bg = None
        self._font = None
        self._font_small = None
        # bid -> { normal, hover, rect } — single rect for draw + hit-test (logical coords)
        self._menu_buttons: dict[str, dict[str, pygame.Surface | pygame.Rect]] = {}
        self._hover_id: str | None = None
        self._layout_debug_printed: bool = False

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

        total_h = len(BUTTON_ORDER) * BUTTON_H + (len(BUTTON_ORDER) - 1) * BUTTON_SPACING
        start_y = LOGICAL_H // 2 - total_h // 2 + 20

        for i, bid in enumerate(BUTTON_ORDER):
            cx = LOGICAL_W // 2
            cy = start_y + i * (BUTTON_H + BUTTON_SPACING) + BUTTON_H // 2

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

            normal = surfaces.get("normal")
            hover_asset = surfaces.get("hover")
            if hover_asset is not None:
                hover = hover_asset
            elif normal is not None:
                hover = _fallback_hover_surface(normal)
            else:
                hover = None

            if normal is not None:
                rect = normal.get_rect(center=(cx, cy))
            else:
                rect = pygame.Rect(0, 0, BUTTON_W, BUTTON_H)
                rect.center = (cx, cy)

            self._menu_buttons[bid] = {
                "normal": normal,
                "hover": hover,
                "rect": rect,
            }

        if not self._layout_debug_printed:
            self._layout_debug_printed = True
            seen: set[tuple[int, int, int, int]] = set()
            for bid in BUTTON_ORDER:
                r = self._menu_buttons[bid]["rect"]
                t = (r.x, r.y, r.w, r.h)
                print(f"[MENU LAYOUT] button={BUTTON_LABELS.get(bid, bid)} rect={r} size=({r.w}x{r.h})")
                seen.add(t)
            if len(seen) != len(BUTTON_ORDER):
                print("[MENU LAYOUT] warning: duplicate button rects detected")

    def _get_button_at(self, logical_pos: tuple[int, int]) -> str | None:
        for bid in BUTTON_ORDER:
            entry = self._menu_buttons.get(bid)
            if not entry:
                continue
            rect = entry.get("rect")
            if isinstance(rect, pygame.Rect) and rect.collidepoint(logical_pos):
                return bid
        return None

    def update(self, dt: float) -> None:
        self._ensure_loaded(None)
        self._hover_id = None
        logical_pos = screen_to_logical(pygame.mouse.get_pos())
        self._hover_id = self._get_button_at(logical_pos)

    def draw(self, screen: pygame.Surface, camera_offset: tuple[float, float] | None = None) -> None:
        self._ensure_loaded(screen)
        screen.fill(BACKGROUND_COLOR)
        bg = self._bg
        if bg.get_size() != (LOGICAL_W, LOGICAL_H):
            bg = pygame.transform.smoothscale(bg, (LOGICAL_W, LOGICAL_H))
        screen.blit(bg, (0, 0))

        for bid in BUTTON_ORDER:
            entry = self._menu_buttons.get(bid)
            if not entry:
                continue
            rect = entry["rect"]
            is_hover = self._hover_id == bid
            normal = entry.get("normal")
            hover = entry.get("hover")
            surf = hover if (is_hover and hover is not None) else normal
            if surf is not None:
                screen.blit(surf, rect.topleft)
            else:
                color = (80, 120, 160) if is_hover else (60, 80, 100)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (140, 160, 180), rect, 2)

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
            logical_pos = screen_to_logical(event.pos)
            bid = self._get_button_at(logical_pos)
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
