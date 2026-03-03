# Hitbox-based collision for combat. Use entity.get_hitbox_rect() so the transparent
# sprite background does not count as hittable (only the body rect matters).

import pygame


def hitbox_overlap(a: pygame.Rect, b: pygame.Rect) -> bool:
    """True if the two hitbox rects overlap. Use for player vs enemy, attack vs body."""
    return a.colliderect(b)
