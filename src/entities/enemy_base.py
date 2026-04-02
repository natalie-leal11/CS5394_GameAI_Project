import math
import os
import random
from typing import Tuple

import pygame

from game.config import (
    enemy_movement_size_tuple,
    PROJECT_ROOT,
    HEAVY_UNSTUCK_RETREAT_DURATION_SEC,
    HEAVY_CLEARANCE_CHASE_PADDING_PX,
    HEAVY_CLEARANCE_DESPERATION_MULT,
    HEAVY_REROUTE_CACHE_SEC,
    HEAVY_CLEARANCE_NON_DIRECT_TOWARD_BLEND,
    HEAVY_STUCK_TIME_SEC,
    ENEMY_SWARM_SIZE,
    ENEMY_FLANKER_SIZE,
    ENEMY_BRUTE_SIZE,
    ENEMY_HEAVY_SIZE,
    ENEMY_RANGED_SIZE,
    ENEMY_SWARM_BASE_HP,
    ENEMY_FLANKER_BASE_HP,
    ENEMY_BRUTE_BASE_HP,
    ENEMY_HEAVY_BASE_HP,
    ENEMY_RANGED_BASE_HP,
    ENEMY_SWARM_BASE_DAMAGE,
    ENEMY_FLANKER_BASE_DAMAGE,
    ENEMY_BRUTE_BASE_DAMAGE,
    ENEMY_HEAVY_BASE_DAMAGE,
    ENEMY_RANGED_BASE_DAMAGE,
    ENEMY_SWARM_MOVE_SPEED,
    ENEMY_FLANKER_MOVE_SPEED,
    ENEMY_BRUTE_MOVE_SPEED,
    ENEMY_HEAVY_MOVE_SPEED,
    ENEMY_RANGED_MOVE_SPEED,
    ENEMY_SWARM_STOP_DISTANCE,
    ENEMY_FLANKER_STOP_DISTANCE,
    ENEMY_BRUTE_STOP_DISTANCE,
    ENEMY_HEAVY_STOP_DISTANCE,
    ENEMY_RANGED_STOP_DISTANCE,
    ENEMY_MELEE_ENGAGE_BUFFER_SWARM,
    ENEMY_MELEE_ENGAGE_BUFFER_FLANKER,
    ENEMY_MELEE_ENGAGE_BUFFER_BRUTE,
    ENEMY_MELEE_ENGAGE_BUFFER_HEAVY,
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
    ENEMY_HEAVY_ATTACK_RADIUS,
    ENEMY_HEAVY_ATTACK_OFFSET,
    ENEMY_HEAVY_ATTACK_COOLDOWN_SEC,
    DEBUG_HEAVY_MOVE,
    DEBUG_HEAVY_CLEARANCE,
)
from game.asset_loader import load_animation, load_image
from systems.animation import AnimationState
from systems.collisions import hitbox_overlap

# Anti-stuck: movement < this many px for STUCK_FRAME_COUNT frames in a row = stuck
STUCK_MOVEMENT_THRESHOLD_PX = 3.0
STUCK_FRAME_COUNT = 20
# Heavy: require longer stuck time before retreat (0.5–0.8 s)
STUCK_FRAME_COUNT_HEAVY = max(STUCK_FRAME_COUNT, int(HEAVY_STUCK_TIME_SEC * 60))
# Random steering when stuck: rotate velocity by ± this many degrees to slide along wall
STUCK_STEERING_ANGLE_DEG = 70.0


def _apply_stuck_steering(vx: float, vy: float) -> Tuple[float, float]:
    """Apply a random steering angle to (vx, vy) to help escape obstacles. Keeps same speed."""
    speed = math.hypot(vx, vy)
    if speed < 1e-6:
        return (vx, vy)
    angle_rad = math.atan2(vy, vx)
    deg = random.uniform(-STUCK_STEERING_ANGLE_DEG, STUCK_STEERING_ANGLE_DEG)
    angle_rad += math.radians(deg)
    return (math.cos(angle_rad) * speed, math.sin(angle_rad) * speed)


def apply_anti_stuck_velocity(entity, vx: float, vy: float) -> Tuple[float, float]:
    """If entity is stuck (many frames of low movement), apply random steering and return new (vx, vy)."""
    stuck_frames = getattr(entity, "_stuck_frames", 0)
    if stuck_frames >= STUCK_FRAME_COUNT and (vx * vx + vy * vy) > 1e-6:
        entity._stuck_frames = 0
        return _apply_stuck_steering(vx, vy)
    return (vx, vy)


def _get_retreat_direction_away_from_wall(
    world_pos: Tuple[float, float], room_rect: pygame.Rect
) -> Tuple[float, float]:
    """Deterministic unit vector away from the nearest room edge. Used for Heavy unstuck (no random teleport)."""
    x, y = world_pos
    dist_left = x - room_rect.left
    dist_right = room_rect.right - x
    dist_top = y - room_rect.top
    dist_bottom = room_rect.bottom - y
    d_min = min(dist_left, dist_right, dist_top, dist_bottom)
    if d_min <= 0:
        return (1.0, 0.0)
    if d_min == dist_left:
        return (1.0, 0.0)
    if d_min == dist_right:
        return (-1.0, 0.0)
    if d_min == dist_top:
        return (0.0, 1.0)
    return (0.0, -1.0)


def update_stuck_tracking(entity, start_pos: Tuple[float, float]) -> None:
    """Update _stuck_frames and _last_world_pos after movement. Call after setting entity.world_pos.
    Heavy: also count stuck when chasing player but displacement < threshold (e.g. clearance rejected move)."""
    movement_px = math.hypot(
        entity.world_pos[0] - start_pos[0],
        entity.world_pos[1] - start_pos[1],
    )
    vx, vy = getattr(entity, "velocity_xy", (0.0, 0.0))
    has_velocity = (vx * vx + vy * vy) > 1e-6
    # Heavy: stuck if (chasing and displacement < threshold) even when velocity was zeroed by clearance
    is_heavy_chasing = getattr(entity, "_heavy_chasing_this_frame", False)
    if getattr(entity, "enemy_type", None) == "heavy" and is_heavy_chasing and movement_px < STUCK_MOVEMENT_THRESHOLD_PX:
        entity._stuck_frames = getattr(entity, "_stuck_frames", 0) + 1
    elif movement_px < STUCK_MOVEMENT_THRESHOLD_PX and has_velocity:
        entity._stuck_frames = getattr(entity, "_stuck_frames", 0) + 1
    else:
        entity._stuck_frames = 0
    entity._last_world_pos = entity.world_pos


ENEMY_TYPES = ("swarm", "flanker", "brute", "heavy", "ranged")

# Shared animation cache by enemy_type so multiple instances (e.g. Biome 3 boss adds) don't reload.
_ENEMY_ANIMATION_CACHE: dict[str, dict[str, list[pygame.Surface]]] = {}
_ATTACK_FOLDER_BY_TYPE = {"brute": "slam", "heavy": "attack_hit"}


def _load_animations_for_type(enemy_type: str, size: Tuple[int, int]) -> dict[str, list[pygame.Surface]]:
    """Load all animation states for an enemy type. Used by cache and preload."""
    base_path = f"assets/entities/enemies/{enemy_type}"
    animations: dict[str, list[pygame.Surface]] = {}
    for state in ("idle", "walk", "attack", "hit", "death"):
        folder_name = _ATTACK_FOLDER_BY_TYPE.get(enemy_type, state) if state == "attack" else state
        folder = f"{base_path}/{folder_name}"
        frames = load_animation(
            folder,
            size=size,
            use_colorkey=True,
            colorkey_color=(255, 255, 255),
            near_white_threshold=0,
            corner_bg_tolerance=40,
            strip_flat_bg=True,
        )
        animations[state] = frames
    idle_frames = animations["idle"]
    if not idle_frames:
        idle_frames = [pygame.Surface(size)]
    for state in ("walk", "attack", "hit", "death"):
        if not animations.get(state):
            animations[state] = list(idle_frames)
    return animations


def preload_enemy_animations(enemy_type: str) -> None:
    """Load animations for this enemy type into the shared cache. Call before spawning (e.g. Biome 3 boss adds) to avoid stall."""
    if enemy_type in _ENEMY_ANIMATION_CACHE:
        return
    size = _enemy_size_for_type(enemy_type)
    _ENEMY_ANIMATION_CACHE[enemy_type] = _load_animations_for_type(enemy_type, size)


_TYPE_PRIORITY: dict[str, int] = {
    "swarm": 0,
    "flanker": 1,
    "brute": 2,
    "heavy": 3,
    "ranged": 3,
    "mini_boss": 4,
    "mini_boss_2": 4,
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
    ("swarm", "heavy"): 42.0,
    ("heavy", "swarm"): 42.0,
    ("flanker", "heavy"): 48.0,
    ("heavy", "flanker"): 48.0,
    ("brute", "heavy"): 52.0,
    ("heavy", "brute"): 52.0,
    ("heavy", "heavy"): 55.0,
    ("ranged", "ranged"): 45.0,
    ("swarm", "ranged"): 38.0,
    ("ranged", "swarm"): 38.0,
    ("flanker", "ranged"): 42.0,
    ("ranged", "flanker"): 42.0,
    ("brute", "ranged"): 48.0,
    ("ranged", "brute"): 48.0,
    ("heavy", "ranged"): 50.0,
    ("ranged", "heavy"): 50.0,
    ("swarm", "mini_boss"): 50.0,
    ("mini_boss", "swarm"): 50.0,
    ("flanker", "mini_boss"): 55.0,
    ("mini_boss", "flanker"): 55.0,
    ("brute", "mini_boss"): 60.0,
    ("mini_boss", "brute"): 60.0,
    ("heavy", "mini_boss"): 62.0,
    ("mini_boss", "heavy"): 62.0,
    ("mini_boss", "mini_boss"): 70.0,
    ("swarm", "mini_boss_2"): 50.0,
    ("mini_boss_2", "swarm"): 50.0,
    ("flanker", "mini_boss_2"): 55.0,
    ("mini_boss_2", "flanker"): 55.0,
    ("brute", "mini_boss_2"): 60.0,
    ("mini_boss_2", "brute"): 60.0,
    ("heavy", "mini_boss_2"): 62.0,
    ("mini_boss_2", "heavy"): 62.0,
    ("mini_boss", "mini_boss_2"): 70.0,
    ("mini_boss_2", "mini_boss"): 70.0,
    ("mini_boss_2", "mini_boss_2"): 70.0,
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
# Biome 4 Phase 2: red elite aura (assets/effects/elites/). Set by game_scene before drawing.
CURRENT_BIOME_INDEX = 1

# Lazy-loaded Biome 4 elite aura (64x64)
_elite_aura_red_surf = None


def _ensure_elite_aura_red() -> pygame.Surface | None:
    global _elite_aura_red_surf
    if _elite_aura_red_surf is not None:
        return _elite_aura_red_surf
    path = os.path.join(PROJECT_ROOT, "assets", "effects", "elites", "elite_aura_red_64x64.png")
    if not os.path.isfile(path):
        return None
    try:
        _elite_aura_red_surf = load_image("assets/effects/elites/elite_aura_red_64x64.png", size=(64, 64))
        return _elite_aura_red_surf
    except Exception:
        return None


def _enemy_size_for_type(enemy_type: str) -> Tuple[int, int]:
    if enemy_type == "brute":
        return ENEMY_BRUTE_SIZE
    if enemy_type == "flanker":
        return ENEMY_FLANKER_SIZE
    if enemy_type == "heavy":
        return ENEMY_HEAVY_SIZE
    if enemy_type == "ranged":
        return ENEMY_RANGED_SIZE
    return ENEMY_SWARM_SIZE


def _enemy_stats_for_type(enemy_type: str) -> Tuple[float, float, float]:
    if enemy_type == "brute":
        return ENEMY_BRUTE_BASE_HP, ENEMY_BRUTE_BASE_DAMAGE, ENEMY_BRUTE_MOVE_SPEED
    if enemy_type == "flanker":
        return ENEMY_FLANKER_BASE_HP, ENEMY_FLANKER_BASE_DAMAGE, ENEMY_FLANKER_MOVE_SPEED
    if enemy_type == "heavy":
        return ENEMY_HEAVY_BASE_HP, ENEMY_HEAVY_BASE_DAMAGE, ENEMY_HEAVY_MOVE_SPEED
    if enemy_type == "ranged":
        return ENEMY_RANGED_BASE_HP, ENEMY_RANGED_BASE_DAMAGE, ENEMY_RANGED_MOVE_SPEED
    return ENEMY_SWARM_BASE_HP, ENEMY_SWARM_BASE_DAMAGE, ENEMY_SWARM_MOVE_SPEED


def _enemy_attack_params(enemy_type: str) -> Tuple[float, float, float]:
    """Return (radius, offset, cooldown_sec) for melee attack. Ranged uses projectiles."""
    if enemy_type == "ranged":
        return 0.0, 0.0, 999.0
    if enemy_type == "brute":
        return ENEMY_BRUTE_ATTACK_RADIUS, ENEMY_BRUTE_ATTACK_OFFSET, ENEMY_BRUTE_ATTACK_COOLDOWN_SEC
    if enemy_type == "flanker":
        return ENEMY_FLANKER_ATTACK_RADIUS, ENEMY_FLANKER_ATTACK_OFFSET, ENEMY_FLANKER_ATTACK_COOLDOWN_SEC
    if enemy_type == "heavy":
        return ENEMY_HEAVY_ATTACK_RADIUS, ENEMY_HEAVY_ATTACK_OFFSET, ENEMY_HEAVY_ATTACK_COOLDOWN_SEC
    return ENEMY_SWARM_ATTACK_RADIUS, ENEMY_SWARM_ATTACK_OFFSET, ENEMY_SWARM_ATTACK_COOLDOWN_SEC


def _enemy_stop_distance(enemy_type: str) -> float:
    if enemy_type == "brute":
        return float(ENEMY_BRUTE_STOP_DISTANCE)
    if enemy_type == "flanker":
        return float(ENEMY_FLANKER_STOP_DISTANCE)
    if enemy_type == "heavy":
        return float(ENEMY_HEAVY_STOP_DISTANCE)
    if enemy_type == "ranged":
        return float(ENEMY_RANGED_STOP_DISTANCE)
    return float(ENEMY_SWARM_STOP_DISTANCE)


_CLASS_NAME_TO_MOVEMENT_KEY: dict[str, str] = {
    "Swarm": "swarm",
    "Flanker": "flanker",
    "Brute": "brute",
    "Heavy": "heavy",
    "Ranged": "ranged",
    "MiniBoss": "mini_boss",
    "MiniBoss2": "mini_boss_2",
    "Biome3MiniBoss": "mini_boss",
    "FinalBoss": "final_boss",
}


def enemy_type_key_for_class(enemy_cls: type) -> str:
    """Config ENEMY_MOVEMENT_HITBOX key for this enemy class (spawn / movement bounds)."""
    return _CLASS_NAME_TO_MOVEMENT_KEY.get(getattr(enemy_cls, "__name__", ""), "swarm")


def enemy_movement_half_extents_for_class(enemy_cls: type) -> tuple[float, float]:
    """Half extents for SpawnSystem clamp; matches EnemyBase.movement_size for standard enemies."""
    from game.config import enemy_movement_half_extents

    key = enemy_type_key_for_class(enemy_cls)
    return enemy_movement_half_extents(key)


def _enemy_effective_stop_distance(enemy_type: str) -> float:
    """Walk vs attack: base stop + per-type engage buffer (overlap push still uses base stop_dist only)."""
    stop_dist = _enemy_stop_distance(enemy_type)
    if enemy_type == "heavy":
        return stop_dist + float(ENEMY_MELEE_ENGAGE_BUFFER_HEAVY)
    if enemy_type == "brute":
        return stop_dist + float(ENEMY_MELEE_ENGAGE_BUFFER_BRUTE)
    if enemy_type == "flanker":
        return stop_dist + float(ENEMY_MELEE_ENGAGE_BUFFER_FLANKER)
    if enemy_type == "swarm":
        return stop_dist + float(ENEMY_MELEE_ENGAGE_BUFFER_SWARM)
    return stop_dist


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
        self.movement_size = enemy_movement_size_tuple(enemy_type)
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
        # Anti-stuck: wall slide and low-movement detection
        self._last_world_pos: Tuple[float, float] | None = None
        self._stuck_frames: int = 0

    # --- Animations ---------------------------------------------------------

    def _ensure_animations_loaded(self) -> None:
        if self._animations_loaded:
            return
        self._animations_loaded = True
        if self.enemy_type in _ENEMY_ANIMATION_CACHE:
            cached = _ENEMY_ANIMATION_CACHE[self.enemy_type]
            for state in ("idle", "walk", "attack", "hit", "death"):
                self._animations[state] = cached[state]
            idle_frames = self._animations["idle"]
            if idle_frames:
                self._anim_state.set_animation(idle_frames, 6, True)
            return
        loaded = _load_animations_for_type(self.enemy_type, self.size)
        _ENEMY_ANIMATION_CACHE[self.enemy_type] = loaded
        for state in ("idle", "walk", "attack", "hit", "death"):
            self._animations[state] = loaded[state]
        idle_frames = self._animations["idle"] or [pygame.Surface(self.size)]
        self._anim_state.set_animation(idle_frames, 6, True)

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

    def get_movement_hitbox_rect(self) -> pygame.Rect:
        w, h = self.movement_size
        x, y = self.world_pos
        return pygame.Rect(x - w / 2, y - h / 2, w, h)

    # --- Update / AI -------------------------------------------------------

    def update(
        self,
        dt: float,
        player,
        room_rect: pygame.Rect | None = None,
        heavy_clearance_cb=None,
        heavy_retreat_cb=None,
    ) -> None:
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
        engage_dist = _enemy_effective_stop_distance(self.enemy_type)

        # Heavy: record "chasing" for trap detection (low displacement for ~0.6s while chasing = stuck)
        if self.enemy_type == "heavy":
            self._heavy_chasing_this_frame = dist > engage_dist

        if dist > engage_dist:
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

        # Heavy: if in retreat phase (deterministic unstuck), use retreat only when outside attack range
        if (
            self.enemy_type == "heavy"
            and getattr(self, "_unstuck_retreat_timer", 0) > 0
            and room_rect is not None
            and dist > engage_dist
        ):
            dx, dy = getattr(self, "_unstuck_retreat_direction", (1.0, 0.0))
            vx = dx * self.move_speed
            vy = dy * self.move_speed
            self.facing = (dx, dy)
            self._set_state("walk")
        else:
            # Anti-stuck: wall collision = immediate slide; stuck = Heavy retreat or random steering
            wall_collision = getattr(self, "_wall_collision_this_frame", False)
            stuck_frames = getattr(self, "_stuck_frames", 0)
            has_velocity = (vx * vx + vy * vy) > 1e-6
            if wall_collision and has_velocity:
                # Slide along wall (fixed 45° nudge)
                speed = math.hypot(vx, vy)
                cos45 = 0.70710678
                ovx, ovy = vx, vy
                vx = ovx * cos45 - ovy * cos45
                vy = ovx * cos45 + ovy * cos45
                n = math.hypot(vx, vy)
                if n > 1e-6:
                    vx, vy = vx * speed / n, vy * speed / n
                setattr(self, "_wall_collision_this_frame", False)
            elif stuck_frames >= (STUCK_FRAME_COUNT_HEAVY if self.enemy_type == "heavy" else STUCK_FRAME_COUNT) and (has_velocity or self.enemy_type == "heavy"):
                # Heavy: trigger escape even when velocity was zeroed (trap: chasing but can't move)
                if self.enemy_type == "heavy" and (room_rect is not None or heavy_retreat_cb is not None):
                    if getattr(self, "_unstuck_retreat_timer", 0) <= 0:
                        self._unstuck_retreat_timer = HEAVY_UNSTUCK_RETREAT_DURATION_SEC
                        if callable(heavy_retreat_cb):
                            self._unstuck_retreat_direction = heavy_retreat_cb()
                        elif room_rect is not None:
                            self._unstuck_retreat_direction = _get_retreat_direction_away_from_wall(
                                self.world_pos, room_rect
                            )
                        else:
                            self._unstuck_retreat_direction = (1.0, 0.0)
                    vx = self._unstuck_retreat_direction[0] * self.move_speed
                    vy = self._unstuck_retreat_direction[1] * self.move_speed
                else:
                    vx, vy = apply_anti_stuck_velocity(self, vx, vy)

        # Heavy: deterministic obstacle avoidance — try direct, then slide X, slide Y, perpendiculars; cache reroute.
        # Uses HEAVY_CLEARANCE_CHASE_PADDING_PX (tighter than spawn) + desperation passes so we rarely zero velocity while chasing.
        if (
            self.enemy_type == "heavy"
            and callable(heavy_clearance_cb)
            and dist > engage_dist
            and getattr(self, "_unstuck_retreat_timer", 0) <= 0
        ):
            mw, mh = self.movement_size
            padding_chase = float(HEAVY_CLEARANCE_CHASE_PADDING_PX)
            padding_pass2 = max(3.0, padding_chase * float(HEAVY_CLEARANCE_DESPERATION_MULT))

            def _check_pad(ux: float, uy: float, pad_px: float) -> bool:
                next_rect = pygame.Rect(
                    x + ux * self.move_speed * dt - mw / 2,
                    y + uy * self.move_speed * dt - mh / 2,
                    mw,
                    mh,
                )
                return heavy_clearance_cb(next_rect, pad_px)

            # 1) If cached reroute still valid, use it (retry with looser padding if needed)
            reroute_timer = getattr(self, "_heavy_reroute_timer", 0.0)
            reroute_dir = getattr(self, "_heavy_reroute_direction", None)
            if reroute_timer > 0 and reroute_dir is not None:
                ux, uy = reroute_dir
                reroute_ok = False
                for pad_try in (padding_chase, padding_pass2, 0.0):
                    if _check_pad(ux, uy, pad_try):
                        reroute_ok = True
                        break
                if reroute_ok:
                    vx = ux * self.move_speed
                    vy = uy * self.move_speed
                    self.facing = (ux, uy)
                    self._set_state("walk")
                else:
                    self._heavy_reroute_timer = 0.0
                    self._heavy_reroute_direction = None
                    reroute_dir = None

            # 2) If no cached reroute, try candidates in deterministic order at chase → desperation → direct@0
            if reroute_dir is None or reroute_timer <= 0:
                nx_val = dx / dist if dist > 1e-3 else 1.0
                ny_val = dy / dist if dist > 1e-3 else 0.0
                slide_x = (1.0, 0.0) if dx >= 0 else (-1.0, 0.0)
                slide_y = (0.0, 1.0) if dy >= 0 else (0.0, -1.0)
                perp_l = (-ny_val, nx_val)
                perp_r = (ny_val, -nx_val)
                candidates = [
                    (nx_val, ny_val),
                    slide_x,
                    slide_y,
                    perp_l,
                    perp_r,
                ]
                chosen = None
                chosen_pad = padding_chase
                for pad_try in (padding_chase, padding_pass2):
                    for (ux, uy) in candidates:
                        if _check_pad(ux, uy, pad_try):
                            chosen = (ux, uy)
                            chosen_pad = pad_try
                            break
                    if chosen is not None:
                        break
                if chosen is None and _check_pad(nx_val, ny_val, 0.0):
                    chosen = (nx_val, ny_val)
                    chosen_pad = 0.0
                if chosen is not None:
                    ux, uy = chosen
                    chosen_is_direct = abs(ux - nx_val) < 1e-5 and abs(uy - ny_val) < 1e-5
                    if not chosen_is_direct:
                        blend_w = float(HEAVY_CLEARANCE_NON_DIRECT_TOWARD_BLEND)
                        bx = (1.0 - blend_w) * ux + blend_w * nx_val
                        by = (1.0 - blend_w) * uy + blend_w * ny_val
                        bn = math.hypot(bx, by)
                        if bn > 1e-6:
                            bx, by = bx / bn, by / bn
                            blended = False
                            for pad_try in (chosen_pad, padding_pass2, 0.0):
                                if _check_pad(bx, by, pad_try):
                                    ux, uy = bx, by
                                    chosen_pad = pad_try
                                    blended = True
                                    break
                            if not blended:
                                pass
                    vx = ux * self.move_speed
                    vy = uy * self.move_speed
                    self.facing = (ux, uy)
                    self._set_state("walk")
                    if not chosen_is_direct:
                        self._heavy_reroute_timer = HEAVY_REROUTE_CACHE_SEC
                        self._heavy_reroute_direction = (ux, uy)
                else:
                    vx = vy = 0.0
                    if DEBUG_HEAVY_CLEARANCE:
                        print(
                            "[HEAVY CLEARANCE] reject path=main_candidates "
                            f"size=({mw},{mh}) chase_pad={padding_chase}px pass2={padding_pass2:.1f} "
                            f"pos=({x:.1f},{y:.1f}) (all directions blocked at all pads)"
                        )
        else:
            # Heavy during retreat / no multi-candidate pass: single clearance using movement hitbox
            # (same footprint as main Heavy path and _resolve_entity_wall_collision; not sprite size).
            if self.enemy_type == "heavy" and callable(heavy_clearance_cb) and (vx * vx + vy * vy) > 1e-6:
                mw, mh = self.movement_size
                next_rect = pygame.Rect(x + vx * dt - mw / 2, y + vy * dt - mh / 2, mw, mh)
                ok_move = False
                for pad_try in (
                    float(HEAVY_CLEARANCE_CHASE_PADDING_PX),
                    max(3.0, float(HEAVY_CLEARANCE_CHASE_PADDING_PX) * float(HEAVY_CLEARANCE_DESPERATION_MULT)),
                    0.0,
                ):
                    if heavy_clearance_cb(next_rect, pad_try):
                        ok_move = True
                        break
                if not ok_move:
                    if DEBUG_HEAVY_CLEARANCE:
                        print(
                            "[HEAVY CLEARANCE] reject path=fallback "
                            f"size=({mw},{mh}) pad_tried up to chase/desperation/0 "
                            f"pos=({x:.1f},{y:.1f}) vel=({vx:.1f},{vy:.1f})"
                        )
                    vx = vy = 0.0

        self.velocity_xy = (vx, vy)

        start_pos = (x, y)
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
        # Skip during player dash so enemies are not displaced by dash (player-only movement).
        if not getattr(player, "dash_active", False):
            enemy_rect = self.get_movement_hitbox_rect()
            player_rect = (
                player.get_movement_hitbox_rect()
                if hasattr(player, "get_movement_hitbox_rect")
                else player.get_hitbox_rect()
            )
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

        update_stuck_tracking(self, start_pos)

        if self.enemy_type == "heavy" and DEBUG_HEAVY_MOVE:
            sx, sy = self.world_pos
            print(
                f"[MOVE DEBUG] enemy=heavy stuck={getattr(self, '_stuck_frames', 0)} "
                f"pos=({sx:.1f},{sy:.1f})"
            )

        # Heavy: tick down retreat timer and reroute cache (deterministic unstuck / obstacle avoid)
        if self.enemy_type == "heavy":
            if getattr(self, "_unstuck_retreat_timer", 0) > 0:
                self._unstuck_retreat_timer = max(0.0, self._unstuck_retreat_timer - dt)
            if getattr(self, "_heavy_reroute_timer", 0) > 0:
                self._heavy_reroute_timer = max(0.0, self._heavy_reroute_timer - dt)

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
        # Biome 4 Phase 2: red elite aura for Biome 4 elite encounters only.
        if self.elite and CURRENT_BIOME_INDEX == 4:
            aura = _ensure_elite_aura_red()
            if aura is not None:
                ax = int(self.world_pos[0] - cx - aura.get_width() / 2)
                ay = int(self.world_pos[1] - cy - aura.get_height() / 2)
                screen.blit(aura, (ax, ay))
        screen.blit(surf, (x, y))
        if self.damage_flash_timer > 0.0:
            intensity = min(1.0, self.damage_flash_timer / 0.15)
            alpha = int(180 * intensity)
            flash = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            flash.fill((255, 40, 40, alpha))
            screen.blit(flash, (x, y))

