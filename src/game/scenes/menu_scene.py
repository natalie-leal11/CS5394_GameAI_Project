"""
Menu scene: ENTER → Run, ESC → Quit.
"""
import pygame

from src.game import config
from src.game.scenes.base_scene import BaseScene


class MenuScene(BaseScene):
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            self.manager.switch_to("run")
        elif event.key == pygame.K_ESCAPE:
            self.manager.switch_to("quit")

    def update(self, dt: float) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((20, 20, 30))
        font = pygame.font.Font(None, 48)
        title = font.render("Adaptive Dungeon", True, (220, 220, 220))
        rect = title.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 - 40))
        screen.blit(title, rect)
        sub = pygame.font.Font(None, 32).render("ENTER to start  |  ESC to quit", True, (160, 160, 160))
        sub_rect = sub.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 + 20))
        screen.blit(sub, sub_rect)
