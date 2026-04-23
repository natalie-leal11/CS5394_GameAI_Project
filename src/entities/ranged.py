# Biome 3 ranged enemy: maintains distance, shoots projectiles.

import math
from typing import Tuple

import pygame

from game.config import (
    ENEMY_RANGED_ATTACK_COOLDOWN_SEC,
    RANGED_PROJECTILE_SPEED,
    RANGED_PROJECTILE_LIFETIME_SEC,
    RANGED_KITE_CLOSE_THRESHOLD,
    RANGED_KITE_FAR_THRESHOLD,
    RANGED_PLAYER_OVERLAP_PUSH_PX,
    RANGED_STRAFE_SPEED_FACTOR,
    RANGED_ATTACK_STRAFE_SPEED_FACTOR,
    ENEMY_MIN_X,
    ENEMY_MIN_Y,
    ENEMY_MAX_X,
    ENEMY_MAX_Y,
)
from game.asset_loader import load_animation_by_prefix
from entities.enemy_base import EnemyBase, apply_anti_stuck_velocity, update_stuck_tracking
from entities.projectile import Projectile

# Flat folder: idle_1.png, walk_1.png, shoot_1.png, hit_1.png, death_1.png, etc.
RANGED_ASSET_BASE = "assets/entities/enemies/biome3/ranged"


class Ranged(EnemyBase):
    """
    Ranged enemy: maintains distance from player, shoots projectiles.
    Reuses existing enemy update pipeline and hitbox/combat systems.
    """

    def __init__(self, world_pos: Tuple[float, float], elite: bool = False, **kwargs):
        super().__init__("ranged", world_pos, elite=elite, **kwargs)
        self._pending_projectile = None

    def _ensure_animations_loaded(self) -> None:
        if self._animations_loaded:
            return
        self._animations_loaded = True
        load_kw = dict(
            folder_path=RANGED_ASSET_BASE,
            size=self.size,
            use_colorkey=True,
            colorkey_color=(255, 255, 255),
            near_white_threshold=0,
            corner_bg_tolerance=40,
            strip_flat_bg=True,
        )
        for state, prefix in (
            ("idle", "idle"),
            ("walk", "walk"),
            ("attack", "shoot"),
            ("hit", "hit"),
            ("death", "death"),
        ):
            frames = load_animation_by_prefix(file_prefix=prefix, **load_kw)
            self._animations[state] = frames
        idle_frames = self._animations.get("idle") or []
        if not idle_frames:
            idle_frames = [pygame.Surface(self.size)]
        self._anim_state.set_animation(idle_frames, 6, True)

    def update(self, dt: float, player, room_rect: pygame.Rect | None = None) -> None:
        self._ensure_animations_loaded()
        if self.inactive:
            return
        if self.damage_flash_timer > 0.0:
            self.damage_flash_timer = max(0.0, self.damage_flash_timer - dt)
        if self._player_dead:
            self._idle_during_player_death(dt)
            return

        if self.attack_cooldown_timer > 0.0:
            self.attack_cooldown_timer = max(0.0, self.attack_cooldown_timer - dt)

        if self.hp <= 0 and self.state != "death":
            self._set_state("death")

        if self.state == "death":
            _, finished = self._anim_state.advance(dt)
            if finished:
                self.inactive = True
            return

        px, py = player.world_pos
        x, y = self.world_pos
        start_pos = (x, y)
        dx = px - x
        dy = py - y
        dist = math.hypot(dx, dy)

        if dist > 1e-3:
            nx, ny = dx / dist, dy / dist
            self.facing = (nx, ny)
        else:
            nx, ny = 1.0, 0.0

        # Kiting: back away if too close, approach if too far, strafe in ideal band (never stand still).
        vx, vy = 0.0, 0.0

        if dist < RANGED_KITE_CLOSE_THRESHOLD:
            # Too close: move away from player (slower than approach/strafe base for controlled retreat feel)
            retreat_speed = self.move_speed * 0.42
            vx = -nx * retreat_speed
            vy = -ny * retreat_speed
            self._set_state("walk")
        elif dist > RANGED_KITE_FAR_THRESHOLD:
            # Too far: move toward player
            vx = nx * self.move_speed
            vy = ny * self.move_speed
            self._set_state("walk")
        else:
            # Ideal band: strafe sideways; keep moving slowly when attacking
            perp_x = -ny
            perp_y = nx
            if self.attack_cooldown_timer <= 0.0:
                self._set_state("attack")
                self.attack_cooldown_timer = ENEMY_RANGED_ATTACK_COOLDOWN_SEC
                self._pending_projectile = Projectile(
                    world_pos=(x, y),
                    direction=(nx, ny),
                    damage=self.damage,
                    speed=RANGED_PROJECTILE_SPEED,
                    lifetime_sec=RANGED_PROJECTILE_LIFETIME_SEC,
                )
                strafe_factor = RANGED_ATTACK_STRAFE_SPEED_FACTOR
            else:
                self._set_state("walk")
                strafe_factor = RANGED_STRAFE_SPEED_FACTOR
            speed = self.move_speed * strafe_factor
            vx = perp_x * speed
            vy = perp_y * speed

        vx, vy = apply_anti_stuck_velocity(self, vx, vy)
        self.velocity_xy = (vx, vy)
        x += vx * dt
        y += vy * dt

        min_x, min_y = ENEMY_MIN_X, ENEMY_MIN_Y
        max_x, max_y = ENEMY_MAX_X, ENEMY_MAX_Y
        if room_rect is not None:
            min_x, min_y = room_rect.left, room_rect.top
            max_x, max_y = room_rect.right, room_rect.bottom
        x = max(min_x, min(max_x, x))
        y = max(min_y, min(max_y, y))
        self.world_pos = (x, y)

        # Don't push enemy when player is dashing (player-only movement)
        if not getattr(player, "dash_active", False):
            enemy_rect = self.get_hitbox_rect()
            player_rect = player.get_hitbox_rect()
            if enemy_rect.colliderect(player_rect) and dist > 1e-3:
                push = float(RANGED_PLAYER_OVERLAP_PUSH_PX)
                x -= nx * push
                y -= ny * push
                x = max(min_x, min(max_x, x))
                y = max(min_y, min(max_y, y))
                self.world_pos = (x, y)

        update_stuck_tracking(self, start_pos)
        self._anim_state.advance(dt)
