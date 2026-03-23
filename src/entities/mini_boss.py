# Phase 6: Mini Boss (96×96). States: idle, move, attack_01, attack_02, dash, windup, phase_change, hit, death.

import math
from typing import Tuple

import pygame

from entities.enemy_base import apply_anti_stuck_velocity, update_stuck_tracking
from game.config import (
    enemy_movement_size_tuple,
    MINI_BOSS_SIZE,
    MINI_BOSS_BASE_HP,
    MINI_BOSS_BASE_DAMAGE,
    MINI_BOSS_MOVE_SPEED,
    MINI_BOSS_ATTACK_RADIUS,
    MINI_BOSS_ATTACK_OFFSET,
    MINI_BOSS_ATTACK_COOLDOWN_SEC,
    ENEMY_MIN_X,
    ENEMY_MIN_Y,
    ENEMY_MAX_X,
    ENEMY_MAX_Y,
)
from game.asset_loader import load_animation
from systems.animation import AnimationState


MINI_BOSS_STATES = (
    "idle", "move", "attack_01", "attack_02", "dash", "windup", "phase_change", "hit", "death"
)
MINI_BOSS_STOP_DISTANCE = 70.0  # px; attack range for melee


class MiniBoss:
    """
    Phase 6 mini boss. 96×96, confined to room. Combat via attack_01/attack_02 (no contact damage).
    """

    def __init__(self, world_pos: Tuple[float, float], elite: bool = False) -> None:
        del elite  # Mini boss has no elite variant
        self.enemy_type = "mini_boss"
        self.world_pos = (float(world_pos[0]), float(world_pos[1]))
        self.state = "idle"
        self.inactive = False

        self.max_hp = float(MINI_BOSS_BASE_HP)
        self.hp = float(MINI_BOSS_BASE_HP)
        self.damage = float(MINI_BOSS_BASE_DAMAGE)
        self.move_speed = float(MINI_BOSS_MOVE_SPEED)
        self.size = MINI_BOSS_SIZE
        self.movement_size = enemy_movement_size_tuple("mini_boss")
        self.velocity_xy = (0.0, 0.0)
        self.facing = (1.0, 0.0)
        self.attack_cooldown_timer = 0.0
        self._player_dead = False
        self._last_world_pos = None
        self._stuck_frames = 0

        self._animations: dict[str, list[pygame.Surface]] = {}
        self._anim_state = AnimationState()
        self._animations_loaded = False
        # Damage feedback: brief red flash when hit.
        self.damage_flash_timer: float = 0.0

    def _ensure_animations_loaded(self) -> None:
        if self._animations_loaded:
            return
        self._animations_loaded = True
        base_path = "assets/entities/enemies/mini_boss_1"
        idle_frames: list[pygame.Surface] = []
        for state in MINI_BOSS_STATES:
            folder = f"{base_path}/{state}"
            frames = load_animation(
                folder,
                size=self.size,
                use_colorkey=True,
                colorkey_color=(255, 255, 255),
                near_white_threshold=0,
                corner_bg_tolerance=40,
                strip_flat_bg=True,
            )
            self._animations[state] = frames
            if state == "idle" and frames:
                idle_frames = frames
        for state in MINI_BOSS_STATES:
            if not self._animations[state] and idle_frames:
                self._animations[state] = idle_frames
        if idle_frames:
            self._anim_state.set_animation(idle_frames, fps=5, loop=True)

    def _set_state(self, new_state: str) -> None:
        if new_state == self.state:
            return
        self.state = new_state
        frames = self._animations.get(new_state) or self._animations.get("idle") or []
        loop = new_state not in ("attack_01", "attack_02", "hit", "death")
        fps = 6
        if new_state == "idle":
            fps = 5
        elif new_state == "move":
            fps = 6
        elif new_state in ("attack_01", "attack_02"):
            fps = 10
        elif new_state == "death":
            fps = 6
            loop = False
        self._anim_state.set_animation(frames, fps, loop)

    def get_hitbox_rect(self) -> pygame.Rect:
        w, h = self.size
        x, y = self.world_pos
        return pygame.Rect(x - w / 2, y - h / 2, w, h)

    def get_movement_hitbox_rect(self) -> pygame.Rect:
        w, h = self.movement_size
        x, y = self.world_pos
        return pygame.Rect(x - w / 2, y - h / 2, w, h)

    def update(self, dt: float, player, room_rect: pygame.Rect | None = None) -> None:
        self._ensure_animations_loaded()
        if self.inactive:
            return
        if self.damage_flash_timer > 0.0:
            self.damage_flash_timer = max(0.0, self.damage_flash_timer - dt)
        if self._player_dead:
            self._set_state("idle")
            self._anim_state.advance(dt)
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

        # Non-looping states: wait until animation finishes then go back to idle/move
        if self.state in ("attack_01", "attack_02", "hit"):
            _, finished = self._anim_state.advance(dt)
            if finished:
                self._set_state("idle")
            return

        px, py = player.world_pos
        x, y = self.world_pos
        start_pos = (x, y)
        dx = px - x
        dy = py - y
        dist = math.hypot(dx, dy)
        vx, vy = 0.0, 0.0

        # Simple facing: if boss center.x < player center.x → face right, else face left. No teleport/snap.
        if px > x:
            self.facing = (1.0, 0.0)
        else:
            self.facing = (-1.0, 0.0)

        if dist > MINI_BOSS_STOP_DISTANCE:
            if dist > 1e-3:
                nx = dx / dist
                ny = dy / dist
                vx = nx * self.move_speed
                vy = ny * self.move_speed
                self._set_state("move")
            else:
                self._set_state("idle")
        else:
            if self.attack_cooldown_timer <= 0.0:
                next_attack = "attack_02" if self.state == "attack_01" else "attack_01"
                self._set_state(next_attack)
                # Do NOT set attack_cooldown_timer here; combat sets it when damage is applied so the boss can actually hit the player.
            else:
                self._set_state("idle")
            vx = vy = 0.0

        vx, vy = apply_anti_stuck_velocity(self, vx, vy)
        self.velocity_xy = (vx, vy)
        x += vx * dt
        y += vy * dt

        min_x = ENEMY_MIN_X
        min_y = ENEMY_MIN_Y
        max_x = ENEMY_MAX_X
        max_y = ENEMY_MAX_Y
        if room_rect is not None:
            min_x = room_rect.left
            min_y = room_rect.top
            max_x = room_rect.right
            max_y = room_rect.bottom
        x = max(min_x, min(max_x, x))
        y = max(min_y, min(max_y, y))
        self.world_pos = (x, y)
        update_stuck_tracking(self, start_pos)
        # No position snap or teleport: movement is velocity-only.

        self._anim_state.advance(dt)

    def on_player_death_start(self, player) -> None:
        if self._player_dead or self.inactive:
            return
        self._player_dead = True
        self._set_state("idle")
        self.velocity_xy = (0.0, 0.0)

    def draw(self, screen: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        self._ensure_animations_loaded()
        if self.inactive:
            return
        surf = self._anim_state.current_surface()
        if surf is None:
            return
        cx, cy = camera_offset
        x = int(self.world_pos[0] - cx - surf.get_width() / 2)
        y = int(self.world_pos[1] - cy - surf.get_height() / 2)
        screen.blit(surf, (x, y))
        if self.damage_flash_timer > 0.0:
            intensity = min(1.0, self.damage_flash_timer / 0.15)
            alpha = int(180 * intensity)
            flash = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            flash.fill((255, 40, 40, alpha))
            screen.blit(flash, (x, y))
