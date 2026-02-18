"""
Adaptive Dungeon — main entry. Run with: python -m src.game.main
"""
import pygame

from src.game import config
from src.game.core.scene_manager import SceneManager


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption(config.TITLE)
    clock = pygame.time.Clock()
    manager = SceneManager(screen)
    running = True

    while running:
        dt = clock.tick(config.FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            manager.handle_event(event)
        if not running:
            break
        if manager.quit_requested():
            running = False
            break
        manager.update(dt)
        manager.render()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
