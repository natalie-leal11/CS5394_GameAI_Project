"""
HUD: rest room upgrade selection. Exactly 3 options, player selects 1.
"""
from typing import List, Tuple

import pygame

from src.game import config


def draw_rest_room_hud(
    screen: pygame.Surface,
    options: List[Tuple[str, str, object]],
    healing_amount: int,
) -> None:
    """
    Draw safe room: heal amount and 3 upgrade options. Keys 1, 2, 3 to select.
    """
    font = pygame.font.Font(None, 32)
    title = font.render("Safe Room — Rest & Upgrade", True, (220, 220, 200))
    screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, 40))
    heal_text = font.render(f"Healed +{healing_amount} HP (25% max)", True, (120, 255, 120))
    screen.blit(heal_text, (config.WIDTH // 2 - heal_text.get_width() // 2, 80))
    prompt = font.render("Choose one upgrade (1, 2, or 3):", True, (200, 200, 200))
    screen.blit(prompt, (config.WIDTH // 2 - prompt.get_width() // 2, 120))
    for i, (uid, label, value) in enumerate(options):
        line = font.render(f"  [{i + 1}] {label}", True, (180, 180, 220))
        screen.blit(line, (config.WIDTH // 2 - 150, 160 + i * 36))
