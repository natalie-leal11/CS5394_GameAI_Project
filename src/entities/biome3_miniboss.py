# Biome 3 mini boss (96×96). Phase 1: normal attacks; Phase 2 at 50% HP: summon 2 Swarm + 1 Flanker in ring.
# Assets: assets/entities/enemies/biome3_miniboss/ — all frames per prefix (idle_*, move_*, attack1_*, etc.) are loaded.

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
    BIOME3_MINIBOSS_FIREBALL_DAMAGE,
    BIOME3_MINIBOSS_FIREBALL_SPEED,
    BIOME3_MINIBOSS_FIREBALL_LIFETIME_SEC,
    BIOME3_MINIBOSS_FIREBALL_COOLDOWN_SEC,
    ENEMY_MIN_X,
    ENEMY_MIN_Y,
    ENEMY_MAX_X,
    ENEMY_MAX_Y,
)
from game.asset_loader import load_animation_by_prefix
from systems.animation import AnimationState
from entities.projectile import Projectile, BIOME3_MINIBOSS_FIREBALL_IMAGE_PATH, BIOME3_MINIBOSS_FIREBALL_SIZE


# Required animation states; each loads ALL frames matching the file prefix (e.g. idle_1.png, idle_2.png, ...).
BIOME3_MINIBOSS_STATES = (
    "idle", "move", "attack_01", "attack_02", "fireball", "summon", "phase_change", "hit", "death"
)
# File prefixes in folder (state name -> filename prefix). Frames: prefix_1, prefix_2, ... sorted numerically.
# fireball uses summon animation for the cast.
BIOME3_MINIBOSS_PREFIX_MAP = {
    "idle": "idle",
    "move": "move",
    "attack_01": "attack1",
    "attack_02": "attack2",
    "fireball": "summon",
    "summon": "summon",
    "phase_change": "phase_change",
    "hit": "hit",
    "death": "death",
}
BIOME3_MINIBOSS_ASSET_FOLDER = "assets/entities/enemies/biome3_miniboss"
BIOME3_MINIBOSS_STOP_DISTANCE = 70.0
BIOME3_MINIBOSS_PHASE2_HP_RATIO = 0.5  # Phase 2 at 50% HP

# Shared cache so first load (or preload) is reused by all instances; avoids stall when boss spawns.
_BIOME3_MINIBOSS_ANIMATION_CACHE: dict[str, list[pygame.Surface]] | None = None

# AI Director (Biome 3 mini boss): set by GameScene before spawn; reset to neutral after tuning.
_DIRECTOR_FIREBALL_CD_MULT: float = 1.0
_DIRECTOR_FIREBALL_TELEGRAPH_MULT: float = 1.0


def configure_biome3_miniboss_director(
    *,
    fireball_cd_mult: float = 1.0,
    fireball_telegraph_mult: float = 1.0,
) -> None:
    """Deterministic tuning only; does not change attack types or phase logic."""
    global _DIRECTOR_FIREBALL_CD_MULT, _DIRECTOR_FIREBALL_TELEGRAPH_MULT
    _DIRECTOR_FIREBALL_CD_MULT = max(0.5, min(1.5, float(fireball_cd_mult)))
    _DIRECTOR_FIREBALL_TELEGRAPH_MULT = max(0.75, min(1.35, float(fireball_telegraph_mult)))


def preload_biome3_miniboss_animations() -> None:
    """Load all Biome 3 mini boss animation frames into the shared cache. Call before spawning the boss to avoid a stall on first update."""
    global _BIOME3_MINIBOSS_ANIMATION_CACHE
    if _BIOME3_MINIBOSS_ANIMATION_CACHE is not None:
        return
    _BIOME3_MINIBOSS_ANIMATION_CACHE = {}
    idle_frames: list[pygame.Surface] = []
    for state in BIOME3_MINIBOSS_STATES:
        prefix = BIOME3_MINIBOSS_PREFIX_MAP.get(state, state)
        frames = load_animation_by_prefix(
            BIOME3_MINIBOSS_ASSET_FOLDER,
            prefix,
            size=MINI_BOSS_SIZE,
            use_colorkey=True,
            colorkey_color=(255, 255, 255),
            near_white_threshold=0,
            corner_bg_tolerance=40,
            strip_flat_bg=True,
        )
        _BIOME3_MINIBOSS_ANIMATION_CACHE[state] = frames
        if state == "idle" and frames:
            idle_frames = frames
    for state in BIOME3_MINIBOSS_STATES:
        if not _BIOME3_MINIBOSS_ANIMATION_CACHE[state] and idle_frames:
            _BIOME3_MINIBOSS_ANIMATION_CACHE[state] = idle_frames


class Biome3MiniBoss:
    """
    Biome 3 mini boss. 96×96. Phase 1: melee attacks. Phase 2 at 50% HP: plays phase_change
    then sets _pending_adds = True so game_scene spawns 2 Swarm + 1 Flanker in a ring.
    """

    def __init__(self, world_pos: Tuple[float, float], elite: bool = False, **_unused) -> None:
        del elite
        self.enemy_type = "mini_boss_3"
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
        self.fireball_cooldown_timer = 0.0
        self._pending_projectile = None
        self._player_dead = False
        self._last_world_pos = None
        self._stuck_frames = 0

        self._animations: dict[str, list[pygame.Surface]] = {}
        self._anim_state = AnimationState()
        self._animations_loaded = False
        self.damage_flash_timer: float = 0.0

        # Phase 2: at 50% HP we spawn adds once; game_scene reads _pending_adds and spawns 2 Swarm + 1 Flanker in ring
        self._adds_spawned = False
        self._pending_adds = False
        self._phase2_transition_done = False  # True after phase_change anim finished

    def _ensure_animations_loaded(self) -> None:
        global _BIOME3_MINIBOSS_ANIMATION_CACHE
        if self._animations_loaded:
            return
        self._animations_loaded = True
        # Use shared cache if preloaded (avoids stall when boss spawns); otherwise load and fill cache.
        if _BIOME3_MINIBOSS_ANIMATION_CACHE is not None:
            for state in BIOME3_MINIBOSS_STATES:
                self._animations[state] = _BIOME3_MINIBOSS_ANIMATION_CACHE[state]
            idle = self._animations.get("idle") or []
            if idle:
                self._anim_state.set_animation(idle, fps=5, loop=True)
            return
        # Load ALL frames for each state from the flat folder (idle_1..N, move_1..N, attack1_1..N, etc.).
        idle_frames: list[pygame.Surface] = []
        for state in BIOME3_MINIBOSS_STATES:
            prefix = BIOME3_MINIBOSS_PREFIX_MAP.get(state, state)
            frames = load_animation_by_prefix(
                BIOME3_MINIBOSS_ASSET_FOLDER,
                prefix,
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
        for state in BIOME3_MINIBOSS_STATES:
            if not self._animations[state] and idle_frames:
                self._animations[state] = idle_frames
        if idle_frames:
            self._anim_state.set_animation(idle_frames, fps=5, loop=True)
        # Store in shared cache for any future instances (e.g. if preload was not called).
        _BIOME3_MINIBOSS_ANIMATION_CACHE = {s: self._animations[s] for s in BIOME3_MINIBOSS_STATES}

    def _set_state(self, new_state: str) -> None:
        if new_state == self.state:
            return
        self.state = new_state
        frames = self._animations.get(new_state) or self._animations.get("idle") or []
        loop = new_state not in ("attack_01", "attack_02", "fireball", "summon", "phase_change", "hit", "death")
        fps = 6
        if new_state == "idle":
            fps = 5
        elif new_state == "move":
            fps = 6
        elif new_state == "fireball":
            fps = max(4.0, 6.0 / max(0.75, _DIRECTOR_FIREBALL_TELEGRAPH_MULT))
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
        if self.fireball_cooldown_timer > 0.0:
            self.fireball_cooldown_timer = max(0.0, self.fireball_cooldown_timer - dt)

        # Phase 2 transition: at 50% HP play phase_change once, then request adds
        if not self._adds_spawned and self.hp <= self.max_hp * BIOME3_MINIBOSS_PHASE2_HP_RATIO:
            if not self._phase2_transition_done:
                if self.state != "phase_change":
                    self._set_state("phase_change")
                _, finished = self._anim_state.advance(dt)
                if finished:
                    self._phase2_transition_done = True
                    self._adds_spawned = True
                    self._pending_adds = True
                    self._set_state("idle")
                return
            else:
                self._adds_spawned = True
                self._pending_adds = True
            # fall through so boss keeps moving/attacking

        if self.hp <= 0 and self.state != "death":
            self._set_state("death")

        if self.state == "death":
            _, finished = self._anim_state.advance(dt)
            if finished:
                self.inactive = True
            return

        if self.state in ("attack_01", "attack_02", "fireball", "hit"):
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

        if px > x:
            self.facing = (1.0, 0.0)
        else:
            self.facing = (-1.0, 0.0)

        if dist > BIOME3_MINIBOSS_STOP_DISTANCE:
            # Medium/long range: use fireball if cooldown ready, else move toward player.
            if self.fireball_cooldown_timer <= 0.0:
                nx = (dx / dist, dy / dist) if dist > 1e-3 else (1.0, 0.0)
                self._set_state("fireball")
                self._pending_projectile = Projectile(
                    world_pos=(x, y),
                    direction=(nx[0], nx[1]),
                    damage=float(BIOME3_MINIBOSS_FIREBALL_DAMAGE),
                    speed=float(BIOME3_MINIBOSS_FIREBALL_SPEED),
                    lifetime_sec=float(BIOME3_MINIBOSS_FIREBALL_LIFETIME_SEC),
                    image_path=BIOME3_MINIBOSS_FIREBALL_IMAGE_PATH,
                    size=BIOME3_MINIBOSS_FIREBALL_SIZE,
                )
                self.fireball_cooldown_timer = float(BIOME3_MINIBOSS_FIREBALL_COOLDOWN_SEC) * _DIRECTOR_FIREBALL_CD_MULT
                vx = vy = 0.0
            elif dist > 1e-3:
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
                # Do NOT set attack_cooldown_timer here; combat sets it when damage is applied.
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
