import math
from typing import Tuple

import pygame

from game.config import (
    ENEMY_SWARM_SIZE,
    ENEMY_FLANKER_SIZE,
    ENEMY_BRUTE_SIZE,
    ENEMY_SWARM_BASE_HP,
    ENEMY_FLANKER_BASE_HP,
    ENEMY_BRUTE_BASE_HP,
    ENEMY_SWARM_BASE_DAMAGE,
    ENEMY_FLANKER_BASE_DAMAGE,
    ENEMY_BRUTE_BASE_DAMAGE,
    ENEMY_SWARM_MOVE_SPEED,
    ENEMY_FLANKER_MOVE_SPEED,
    ENEMY_BRUTE_MOVE_SPEED,
    ENEMY_SWARM_STOP_DISTANCE,
    ENEMY_FLANKER_STOP_DISTANCE,
    ENEMY_BRUTE_STOP_DISTANCE,
    ENEMY_CONTACT_DAMAGE_INTERVAL_SEC,
    ENEMY_ELITE_HP_MULT,
    ENEMY_ELITE_DAMAGE_MULT,
    ENEMY_MIN_X,
    ENEMY_MIN_Y,
    ENEMY_MAX_X,
    ENEMY_MAX_Y,
    TILE_SIZE,
    ENEMY_SWARM_ATTACK_RADIUS,
    ENEMY_SWARM_ATTACK_OFFSET,
    ENEMY_SWARM_ATTACK_COOLDOWN_SEC,
    ENEMY_FLANKER_ATTACK_RADIUS,
    ENEMY_FLANKER_ATTACK_OFFSET,
    ENEMY_FLANKER_ATTACK_COOLDOWN_SEC,
    ENEMY_BRUTE_ATTACK_RADIUS,
    ENEMY_BRUTE_ATTACK_OFFSET,
    ENEMY_BRUTE_ATTACK_COOLDOWN_SEC,
)
from game.asset_loader import load_animation, load_image
from systems.animation import AnimationState
from systems.collisions import hitbox_overlap


ENEMY_TYPES = ("swarm", "flanker", "brute")

_TYPE_PRIORITY: dict[str, int] = {
    "swarm": 0,
    "flanker": 1,
    "brute": 2,
    "mini_boss": 3,
}

_SEPARATION_DIST: dict[tuple[str, str], float] = {
    ("swarm", "swarm"): 30.0,
    ("swarm", "flanker"): 35.0,
    ("flanker", "swarm"): 35.0,
    ("swarm", "brute"): 40.0,
    ("brute", "swarm"): 40.0,
    ("flanker", "flanker"): 40.0,
    ("flanker", "brute"): 45.0,
    ("brute", "flanker"): 45.0,
    ("brute", "brute"): 50.0,
    ("swarm", "mini_boss"): 50.0,
    ("mini_boss", "swarm"): 50.0,
    ("flanker", "mini_boss"): 55.0,
    ("mini_boss", "flanker"): 55.0,
    ("brute", "mini_boss"): 60.0,
    ("mini_boss", "brute"): 60.0,
    ("mini_boss", "mini_boss"): 70.0,
}


def enemy_type_priority(enemy_type: str) -> int:
    """Higher value = higher priority for keeping position (Mini Boss would be highest, > Brute)."""
    return _TYPE_PRIORITY.get(enemy_type, 0)


def enemy_min_separation(type_a: str, type_b: str) -> float:
    """Minimum center-to-center separation distance between two enemy types."""
    return _SEPARATION_DIST.get((type_a, type_b), 30.0)

ELITE_OVERLAY_PATH = "assets/entities/enemies/elite/elite_glow_overlay.png"
ELITE_AURA_01_PATH = "assets/entities/enemies/elite/elite_aura_01.png"
ELITE_AURA_02_PATH = "assets/entities/enemies/elite/elite_aura_02.png"


def _enemy_size_for_type(enemy_type: str) -> Tuple[int, int]:
    if enemy_type == "brute":
        return ENEMY_BRUTE_SIZE
    if enemy_type == "flanker":
        return ENEMY_FLANKER_SIZE
    return ENEMY_SWARM_SIZE


def _enemy_stats_for_type(enemy_type: str) -> Tuple[float, float, float]:
    if enemy_type == "brute":
        return ENEMY_BRUTE_BASE_HP, ENEMY_BRUTE_BASE_DAMAGE, ENEMY_BRUTE_MOVE_SPEED
    if enemy_type == "flanker":
        return ENEMY_FLANKER_BASE_HP, ENEMY_FLANKER_BASE_DAMAGE, ENEMY_FLANKER_MOVE_SPEED
    return ENEMY_SWARM_BASE_HP, ENEMY_SWARM_BASE_DAMAGE, ENEMY_SWARM_MOVE_SPEED


def _enemy_attack_params(enemy_type: str) -> Tuple[float, float, float]:
    """Return (radius, offset, cooldown_sec) for melee attack."""
    if enemy_type == "brute":
        return ENEMY_BRUTE_ATTACK_RADIUS, ENEMY_BRUTE_ATTACK_OFFSET, ENEMY_BRUTE_ATTACK_COOLDOWN_SEC
    if enemy_type == "flanker":
        return ENEMY_FLANKER_ATTACK_RADIUS, ENEMY_FLANKER_ATTACK_OFFSET, ENEMY_FLANKER_ATTACK_COOLDOWN_SEC
    return ENEMY_SWARM_ATTACK_RADIUS, ENEMY_SWARM_ATTACK_OFFSET, ENEMY_SWARM_ATTACK_COOLDOWN_SEC


def _enemy_stop_distance(enemy_type: str) -> float:
    if enemy_type == "brute":
        return float(ENEMY_BRUTE_STOP_DISTANCE)
    if enemy_type == "flanker":
        return float(ENEMY_FLANKER_STOP_DISTANCE)
    return float(ENEMY_SWARM_STOP_DISTANCE)


class EnemyBase:
    """
    Shared enemy logic for Phase 3.

    - world_pos: float (x, y) in world space.
    - states: idle, walk, attack, hit, death.
    - animations loaded from assets/entities/enemies/<type>/<state>/.
    - elite flag applies HP/damage multipliers and draws overlay/aura.
    - contact damage every ENEMY_CONTACT_DAMAGE_INTERVAL_SEC while overlapping player.
    - enemies clamped to simple play area rectangle.
    """

    def __init__(self, enemy_type: str, world_pos: Tuple[float, float], elite: bool = False):
        assert enemy_type in ENEMY_TYPES
        self.enemy_type = enemy_type
        self.world_pos = (float(world_pos[0]), float(world_pos[1]))
        self.state = "idle"
        self.inactive = False

        base_hp, base_damage, move_speed = _enemy_stats_for_type(enemy_type)
        if elite:
            base_hp *= ENEMY_ELITE_HP_MULT
            base_damage *= ENEMY_ELITE_DAMAGE_MULT
        self.max_hp = float(base_hp)
        self.hp = float(base_hp)
        self.damage = float(base_damage)
        self.move_speed = float(move_speed)

        self.elite = elite
        self.contact_timer = 0.0

        self.size = _enemy_size_for_type(enemy_type)
        self.velocity_xy = (0.0, 0.0)
        self.facing = (1.0, 0.0)
        self.attack_cooldown_timer = 0.0

        self._animations: dict[str, list[pygame.Surface]] = {}
        self._anim_state = AnimationState()
        self._animations_loaded = False

        # Player-death behaviour
        self._player_dead = False
        # Damage feedback: brief red flash when hit.
        self.damage_flash_timer: float = 0.0

    # --- Animations ---------------------------------------------------------

    def _ensure_animations_loaded(self) -> None:
        if self._animations_loaded:
            return
        self._animations_loaded = True
        base_path = f"assets/entities/enemies/{self.enemy_type}"
        for state in ("idle", "walk", "attack", "hit", "death"):
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
        idle_frames = self._animations["idle"]
        fps = 6
        loop = True
        self._anim_state.set_animation(idle_frames, fps, loop)

    def _set_state(self, new_state: str) -> None:
        if new_state == self.state:
            return
        self.state = new_state
        frames = self._animations.get(new_state) or self._animations.get("idle") or []
        loop = new_state not in ("attack", "hit", "death")
        fps = 10 if new_state in ("walk", "attack") else 8
        if new_state == "death":
            loop = False
        self._anim_state.set_animation(frames, fps, loop)

    # --- Geometry / hitboxes -----------------------------------------------

    def get_hitbox_rect(self) -> pygame.Rect:
        w, h = self.size
        x, y = self.world_pos
        return pygame.Rect(x - w / 2, y - h / 2, w, h)

    # --- Update / AI -------------------------------------------------------

    def update(self, dt: float, player, room_rect: pygame.Rect | None = None) -> None:
        self._ensure_animations_loaded()
        if self.inactive:
            return
        if self.damage_flash_timer > 0.0:
            self.damage_flash_timer = max(0.0, self.damage_flash_timer - dt)
        if self._player_dead:
            # When player is dead, normal AI is paused; only idle animation is advanced.
            self._idle_during_player_death(dt)
            return

        # Tick attack cooldown
        if self.attack_cooldown_timer > 0.0:
            self.attack_cooldown_timer = max(0.0, self.attack_cooldown_timer - dt)

        if self.hp <= 0 and self.state != "death":
            self._set_state("death")

        if self.state == "death":
            _, finished = self._anim_state.advance(dt)
            if finished:
                self.inactive = True
            return

        # Simple chase AI towards player with separation / attack distance
        px, py = player.world_pos
        x, y = self.world_pos
        dx = px - x
        dy = py - y
        dist = math.hypot(dx, dy)
        vx, vy = 0.0, 0.0
        stop_dist = _enemy_stop_distance(self.enemy_type)

        if dist > stop_dist:
            if dist > 1e-3:
                nx = dx / dist
                ny = dy / dist
                vx = nx * self.move_speed
                vy = ny * self.move_speed
                self.facing = (nx, ny)
                self._set_state("walk")
            else:
                self._set_state("idle")
        else:
            # Inside attack radius: stop moving and switch to attack/windup.
            vx = vy = 0.0
            self._set_state("attack")

        self.velocity_xy = (vx, vy)

        # Integrate position
        x += vx * dt
        y += vy * dt

        # Clamp to room bounds (Phase 3: simple rectangle)
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

        # Collision resolution: if overlapping player, keep enemy on its current side
        # and push it outward so its center is ~stop_dist away from the player.
        enemy_rect = self.get_hitbox_rect()
        player_rect = player.get_hitbox_rect()
        if enemy_rect.colliderect(player_rect):
            # Use direction from player to enemy so we never "teleport" through
            # the player to the opposite side.
            nx, ny = 1.0, 0.0
            if dist > 1e-3:
                nx = (x - px) / dist
                ny = (y - py) / dist
            # Push back to the configured stop distance so melee radius/offset
            # still line up with attack logic.
            target_dist = stop_dist
            x = px + nx * target_dist
            y = py + ny * target_dist
            self.world_pos = (x, y)

        # Contact damage removed per Phase 4 decision: damage will come only from
        # explicit attack hitboxes/projectiles (no touch damage).

        self._anim_state.advance(dt)

    def _update_contact_damage(self, dt: float, player, stop_dist: float) -> None:
        # Phase 4 decision: enemies never deal damage via touch/contact.
        # All enemy→player damage will be applied via explicit melee/projectile
        # hitboxes in the combat system. Keep timer zeroed for determinism.
        self.contact_timer = 0.0

    # --- Player death behaviour --------------------------------------------

    def on_player_death_start(self, player) -> None:
        """Called once when player HP reaches 0. Enemies step back and stop attacking."""
        if self._player_dead or self.inactive:
            return
        self._player_dead = True
        px, py = player.world_pos
        x, y = self.world_pos
        dx = x - px
        dy = y - py
        dist = math.hypot(dx, dy)
        stop_dist = _enemy_stop_distance(self.enemy_type)
        retreat_extra = 20.0
        if dist > 1e-3:
            nx = dx / dist
            ny = dy / dist
        else:
            nx, ny = 1.0, 0.0
        target_dist = stop_dist + retreat_extra
        x = px + nx * target_dist
        y = py + ny * target_dist
        # Clamp to bounds
        x = max(ENEMY_MIN_X, min(ENEMY_MAX_X, x))
        y = max(ENEMY_MIN_Y, min(ENEMY_MAX_Y, y))
        self.world_pos = (x, y)
        self.velocity_xy = (0.0, 0.0)
        self._set_state("idle")
        self.contact_timer = 0.0

    def _idle_during_player_death(self, dt: float) -> None:
        """Advance idle animation while player death sequence plays."""
        if self.inactive:
            return
        if self.state != "idle":
            self._set_state("idle")
        self._anim_state.advance(dt)

    # --- Draw --------------------------------------------------------------

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

