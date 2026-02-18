"""
End scene: R → Menu.
"""
import pygame

from src.game import config
from src.game.scenes.base_scene import BaseScene


class EndScene(BaseScene):
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_r:
            self.manager.switch_to("menu")

    def update(self, dt: float) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((25, 20, 35))
        font = pygame.font.Font(None, 48)
        if getattr(self.manager, "run_result", None) is True:
            title = font.render("You Win!", True, (120, 255, 150))
        elif getattr(self.manager, "run_result", None) is False:
            title = font.render("You Died", True, (220, 100, 100))
        else:
            title = font.render("Game Over", True, (200, 180, 220))
        rect = title.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 - 30))
        screen.blit(title, rect)
        sub = pygame.font.Font(None, 32).render("R to return to menu", True, (160, 150, 180))
        sub_rect = sub.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 + 20))
        screen.blit(sub, sub_rect)
