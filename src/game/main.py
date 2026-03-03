# Entry point. Initialize display BEFORE any convert_alpha(); StartScene first; clear every frame.
# Logical buffer (960x640) is scaled to the window (half screen by default).

import random
import pygame

from game.config import SEED, LOGICAL_W, LOGICAL_H, FPS, BACKGROUND_COLOR
from game.scene_manager import SceneManager


def main():
    random.seed(SEED)
    pygame.init()
    # Half screen: window is 50% of display width and height.
    info = pygame.display.Info()
    half_w = info.current_w // 2
    half_h = info.current_h // 2
    try:
        screen = pygame.display.set_mode((half_w, half_h), pygame.RESIZABLE | pygame.DOUBLEBUF)
    except pygame.error:
        screen = pygame.display.set_mode((LOGICAL_W, LOGICAL_H), pygame.RESIZABLE)
    pygame.display.set_caption("Dungeon Geeks")
    clock = pygame.time.Clock()
    scene_manager = SceneManager()
    scene_manager.init()

    # Logical buffer: always 960x640; scaled to window each frame.
    logical_surface = pygame.Surface((LOGICAL_W, LOGICAL_H))

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            scene_manager.handle_event(event)

        if not running:
            break
        logical_surface.fill(BACKGROUND_COLOR)
        co = getattr(scene_manager.current, "camera_offset", (0, 0))
        scene_manager.update(dt)
        scene_manager.draw(logical_surface, co)

        # Scale logical buffer to fill the window.
        win_w, win_h = screen.get_size()
        scaled = pygame.transform.smoothscale(logical_surface, (win_w, win_h))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
