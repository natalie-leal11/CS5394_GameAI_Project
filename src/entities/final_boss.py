# Biome 4 Phase 3: Final Boss (Room 29). 128x128, deterministic attack cycle.
# Assets: assets/entities/enemies/final_boss/ (idle, walk, attack1, attack2, special, summon, phase_change, hit, death)

from __future__ import annotations

import math
from typing import Tuple, Any

import pygame

from game.config import (
    SEED,
    FINAL_BOSS_SIZE,
    FINAL_BOSS_HP,
    FINAL_BOSS_CONTACT_DAMAGE,
    FINAL_BOSS_REVIVE_HP,
    FINAL_BOSS_REVIVE_DELAY_SEC,
    FINAL_BOSS_REVIVE_INVULN_SEC,
    FINAL_BOSS_MOVE_SPEED_REVIVE,
    FINAL_BOSS_ATTACK_COOLDOWN_REVIVE,
    FINAL_BOSS_ATTACK_RECOVERY_REVIVE,
    FINAL_BOSS_FIREBALL_DAMAGE,
    FINAL_BOSS_LAVA_WAVE_DAMAGE,
    FINAL_BOSS_METEOR_DAMAGE,
    FINAL_BOSS_TELEPORT_STRIKE_DAMAGE,
    FINAL_BOSS_ATTACK_COOLDOWN_SEC,
    FINAL_BOSS_ATTACK_COOLDOWN_PHASE2_SEC,
    FINAL_BOSS_MOVE_SPEED,
    FINAL_BOSS_MOVE_SPEED_PHASE2,
    FINAL_BOSS_STOP_DISTANCE,
    FINAL_BOSS_FIREBALL_RANGE_MIN,
    FINAL_BOSS_FIREBALL_RANGE_MAX,
    FINAL_BOSS_WAVE_RANGE_MIN,
    FINAL_BOSS_WAVE_RANGE_MAX,
    FINAL_BOSS_TELEPORT_RANGE_MIN,
    FINAL_BOSS_TELEPORT_RANGE_MAX,
    FINAL_BOSS_TELEPORT_MIN_DIST_PX,
    FINAL_BOSS_FIREBALL_SPEED,
    FINAL_BOSS_FIREBALL_LIFETIME_SEC,
    BOSS_SPAWN_IDLE_DELAY,
    BOSS_ATTACK_RECOVERY,
    BOSS_ATTACK_RECOVERY_PHASE2,
    BOSS_ATTACK_RECOVERY_FIREBALL_PHASE1,
    BOSS_ATTACK_RECOVERY_FIREBALL_PHASE2,
    FINAL_BOSS_ATTACK_RECOVERY_FIREBALL_REVIVE,
    BOSS_PHASE_CHANGE_INVULN_SEC,
    FINAL_BOSS_METEOR_TARGETS,
    FINAL_BOSS_METEOR_SPACING_PX,
    FINAL_BOSS_ATTACK_RADIUS,
    FINAL_BOSS_ATTACK_OFFSET,
    BOSS_TELEGRAPH_FIREBALL_PHASE1,
    BOSS_TELEGRAPH_FIREBALL_PHASE2,
    BOSS_TELEGRAPH_LAVA_PHASE1,
    BOSS_TELEGRAPH_LAVA_PHASE2,
    BOSS_TELEGRAPH_TELEPORT_PHASE1,
    BOSS_TELEGRAPH_TELEPORT_PHASE2,
    BOSS_TELEGRAPH_METEOR_PHASE1,
    BOSS_TELEGRAPH_METEOR_PHASE2,
    TILE_SIZE,
    FINAL_BOSS_HIT_FLINCH_SEC,
    FINAL_BOSS_FIREBALL_CAST_COOLDOWN,
    FINAL_BOSS_TELEPORT_COOLDOWN_SEC,
    FINAL_BOSS_RUSH_SPEED,
    FINAL_BOSS_RUSH_DURATION_SEC,
)
from dungeon.room import TILE_FLOOR, TILE_LAVA, TILE_SLOW
from game.asset_loader import load_animation_by_prefix
from systems.animation import AnimationState
from entities.projectile import Projectile

# Meteor: valid tile types for impact (same as spawn; lava/slow allowed)
_METEOR_VALID_TILE_TYPES = (TILE_FLOOR, TILE_LAVA, TILE_SLOW)
METEOR_TARGET_SPACING_PX = 80  # min spacing between meteor targets (fair, dodgeable)

# Animation states and file prefixes (assets/entities/enemies/final_boss/)
FINAL_BOSS_ASSET_FOLDER = "assets/entities/enemies/final_boss"
FINAL_BOSS_PREFIX_MAP = {
    "idle": "idle",
    "walk": "walk",
    "attack1": "attack1",
    "attack2": "attack2",
    "special": "special",
    "summon": "summon",
    "phase_change": "phase_change",
    "hit": "hit",
    "death": "death",
}
FINAL_BOSS_STATES = list(FINAL_BOSS_PREFIX_MAP.keys())

# Deterministic attack cycle: fireball every 2–3 actions; Phase 2 more fireball + teleport
PHASE1_CYCLE = ("fireball", "lava_wave", "fireball", "teleport_strike", "fireball")
PHASE2_CYCLE = ("teleport_strike", "fireball", "meteor_rain", "lava_wave", "fireball")
REVIVE_CYCLE = ("teleport_strike", "fireball", "meteor_rain")  # no lava_wave, meteor + 1 fireball

# Projectile assets (assets/ per solution)
BOSS_FIREBALL_IMAGE = "assets/entities/projectiles/boss_fireball_24x24.png"
BOSS_FIREBALL_SIZE = (24, 24)
BOSS_WAVE_IMAGE = "assets/entities/projectiles/boss_wave_attack_64x64.png"
BOSS_WAVE_SIZE = (64, 64)


# Shared animation cache so preload and real boss instance share the same surfaces (no stall on spawn).
_FINAL_BOSS_ANIMATION_CACHE: dict[str, list] | None = None


def _make_rng(room_index: int, step: int = 0) -> Any:
    import random
    return random.Random(SEED + room_index * 1000 + step)


class FinalBoss:
    """
    Final Boss for Room 29. Deterministic attack cycle; phase change at 50% HP;
    summons 2 Swarm + 1 Flanker in ring. Contact damage 18; no grab/claw.
    """

    def __init__(self, world_pos: Tuple[float, float], room_index: int = 29) -> None:
        self.enemy_type = "final_boss"
        self.world_pos = (float(world_pos[0]), float(world_pos[1]))
        self.room_index = room_index
        self.state = "spawn_idle"
        self.inactive = False

        self.max_hp = float(FINAL_BOSS_HP)
        self.hp = float(FINAL_BOSS_HP)
        self.damage = float(FINAL_BOSS_TELEPORT_STRIKE_DAMAGE)
        self.move_speed = float(FINAL_BOSS_MOVE_SPEED)
        self.size = FINAL_BOSS_SIZE
        self.velocity_xy = (0.0, 0.0)
        self.facing = (1.0, 0.0)
        self.attack_cooldown_timer = 0.0
        self._player_dead = False
        self.damage_flash_timer: float = 0.0

        self._animations: dict[str, list] = {}
        self._anim_state = AnimationState()
        self._animations_loaded = False

        self._spawn_idle_timer = BOSS_SPAWN_IDLE_DELAY
        self._phase2 = False
        self._phase_change_invuln_timer = 0.0
        self._adds_spawned = False
        self._pending_adds = False
        self._cycle_index = 0
        self._attack_recovery_timer = 0.0
        self._last_attack_start_time = 0.0
        self._time = 0.0

        # Teleport state (one-frame signal for game_scene to draw teleport FX)
        self._teleport_telegraph_timer = 0.0
        self._teleport_dest: Tuple[float, float] | None = None
        self._teleport_strike_damage_frame = False
        self._teleport_fx_frame: Tuple[Tuple[float, float], Tuple[float, float]] | None = None  # (old_pos, new_pos)

        # Fireball / wave: telegraph then projectile (no chain with no recovery gap)
        self._pending_projectile = None
        self._attack_telegraph_timer: float = 0.0
        self._pending_fireball_dir: Tuple[float, float] | None = None
        self._pending_lava_wave_dir: Tuple[float, float] | None = None
        # Meteor: list of {x, y, damage, trigger_time, telegraph_sec?, radius} for game_scene
        self.pending_meteor_impacts: list = []
        # Phase 2: Meteor Rain + 1 Fireball during telegraph (only one fireball per meteor sequence)
        self._meteor_fireball_timer: float = 0.0
        self._meteor_fireball_fired: bool = False
        # Revive phase: first death -> wait 2s -> revive at center with 50 HP; second death is permanent.
        self._revived: bool = False
        self._revive_used: bool = False  # one-time guard: True once we have entered revive_wait
        self._final_death: bool = False
        self._revive_timer: float = 0.0
        self._revive_invuln_timer: float = 0.0
        # Hit state: short flinch only; never reset attack cycle or cooldowns (stagger resistance).
        self._hit_state_timer: float = 0.0
        # Teleport: separate cooldown so reposition can happen every 4–5 s.
        self._teleport_cooldown_timer: float = 0.0
        # Rush: short burst of high speed toward player after teleport or lava wave.
        self._rush_timer: float = 0.0

    def _ensure_animations_loaded(self) -> None:
        if self._animations_loaded:
            return
        self._animations_loaded = True
        global _FINAL_BOSS_ANIMATION_CACHE
        if _FINAL_BOSS_ANIMATION_CACHE is not None:
            for state, frames in _FINAL_BOSS_ANIMATION_CACHE.items():
                self._animations[state] = frames
        else:
            _FINAL_BOSS_ANIMATION_CACHE = {}
            for state, prefix in FINAL_BOSS_PREFIX_MAP.items():
                frames = load_animation_by_prefix(
                    FINAL_BOSS_ASSET_FOLDER,
                    prefix,
                    size=self.size,
                    use_colorkey=True,
                    colorkey_color=(255, 255, 255),
                    near_white_threshold=248,
                    corner_bg_tolerance=25,
                    strip_flat_bg=False,
                )
                self._animations[state] = frames
                _FINAL_BOSS_ANIMATION_CACHE[state] = frames
        idle = self._animations.get("idle") or []
        if idle:
            self._anim_state.set_animation(idle, fps=5, loop=True)

    def _set_state(self, new_state: str) -> None:
        if new_state == self.state:
            return
        # Stagger resistance: do not leave attack/telegraph for "hit"; keep casting/attacking.
        if new_state == "hit" and self.state in ("attack1", "attack2", "special", "summon", "teleport_telegraph"):
            return
        if new_state == "hit":
            self._hit_state_timer = float(FINAL_BOSS_HIT_FLINCH_SEC)
        elif self.state == "hit":
            self._hit_state_timer = 0.0
        self.state = new_state
        frames = self._animations.get(new_state) or self._animations.get("idle") or []
        loop = new_state not in ("attack1", "attack2", "special", "summon", "phase_change", "hit", "death")
        fps = 6
        if new_state == "death":
            fps = 6
            loop = False
        elif new_state in ("attack1", "attack2", "special", "summon"):
            fps = 10
        self._anim_state.set_animation(frames, fps, loop)

    def get_hitbox_rect(self) -> pygame.Rect:
        w, h = self.size
        x, y = self.world_pos
        return pygame.Rect(int(x - w / 2), int(y - h / 2), w, h)

    def get_hurtbox_rect(self) -> pygame.Rect:
        return self.get_hitbox_rect()

    def _current_cycle(self) -> tuple:
        if self._revived:
            return REVIVE_CYCLE
        return PHASE2_CYCLE if self._phase2 else PHASE1_CYCLE

    def _cooldown_sec(self) -> float:
        if self._revived:
            return FINAL_BOSS_ATTACK_COOLDOWN_REVIVE
        return FINAL_BOSS_ATTACK_COOLDOWN_PHASE2_SEC if self._phase2 else FINAL_BOSS_ATTACK_COOLDOWN_SEC

    def _telegraph_fireball_sec(self) -> float:
        return BOSS_TELEGRAPH_FIREBALL_PHASE2 if self._phase2 else BOSS_TELEGRAPH_FIREBALL_PHASE1

    def _telegraph_lava_sec(self) -> float:
        return BOSS_TELEGRAPH_LAVA_PHASE2 if self._phase2 else BOSS_TELEGRAPH_LAVA_PHASE1

    def _telegraph_teleport_sec(self) -> float:
        return BOSS_TELEGRAPH_TELEPORT_PHASE2 if self._phase2 else BOSS_TELEGRAPH_TELEPORT_PHASE1

    def _telegraph_meteor_sec(self) -> float:
        if self._revived:
            return BOSS_TELEGRAPH_METEOR_PHASE2
        return BOSS_TELEGRAPH_METEOR_PHASE2 if self._phase2 else BOSS_TELEGRAPH_METEOR_PHASE1

    def _recovery_sec(self) -> float:
        if self._revived:
            return FINAL_BOSS_ATTACK_RECOVERY_REVIVE
        return BOSS_ATTACK_RECOVERY_PHASE2 if self._phase2 else BOSS_ATTACK_RECOVERY

    def _recovery_fireball_sec(self) -> float:
        """Shorter recovery after fireball so next action starts sooner."""
        if self._revived:
            return FINAL_BOSS_ATTACK_RECOVERY_FIREBALL_REVIVE
        return BOSS_ATTACK_RECOVERY_FIREBALL_PHASE2 if self._phase2 else BOSS_ATTACK_RECOVERY_FIREBALL_PHASE1

    def update(
        self,
        dt: float,
        player: Any,
        room_rect: pygame.Rect | None = None,
        room: Any = None,
        block_check: Any = None,
    ) -> None:
        self._ensure_animations_loaded()
        if self.inactive:
            return
        self._time += dt
        if self.damage_flash_timer > 0.0:
            self.damage_flash_timer = max(0.0, self.damage_flash_timer - dt)
        if self._player_dead:
            self._set_state("idle")
            self._anim_state.advance(dt)
            return

        # Invulnerable during phase change
        if self._phase_change_invuln_timer > 0.0:
            self._phase_change_invuln_timer -= dt
            _, finished = self._anim_state.advance(dt)
            if finished and self._phase_change_invuln_timer <= 0.0:
                self._set_state("idle")
            return

        if self.attack_cooldown_timer > 0.0:
            self.attack_cooldown_timer = max(0.0, self.attack_cooldown_timer - dt)
        if self._attack_recovery_timer > 0.0:
            self._attack_recovery_timer = max(0.0, self._attack_recovery_timer - dt)
        if self._teleport_cooldown_timer > 0.0:
            self._teleport_cooldown_timer = max(0.0, self._teleport_cooldown_timer - dt)
        if self._rush_timer > 0.0:
            self._rush_timer = max(0.0, self._rush_timer - dt)

        # Phase change at 50% HP (once); skip if already in revive phase
        if not self._revived and not self._phase2 and self.hp <= self.max_hp * 0.5:
            self._phase2 = True
            self.move_speed = float(FINAL_BOSS_MOVE_SPEED_PHASE2)
            self._set_state("phase_change")
            self._phase_change_invuln_timer = BOSS_PHASE_CHANGE_INVULN_SEC
            self._adds_spawned = True
            self._pending_adds = True
            self._cycle_index = 0
            return

        # First death: start death anim, then revive_wait; final death (after revive): go inactive
        if self.hp <= 0 and self.state != "death" and self.state != "revive_wait":
            self._set_state("death")
            if self._revived:
                self._final_death = True

        if self.state == "death":
            _, finished = self._anim_state.advance(dt)
            if finished:
                if self._final_death or self._revive_used:
                    self.inactive = True
                else:
                    self.state = "revive_wait"
                    self._revive_used = True
                    self._revive_timer = FINAL_BOSS_REVIVE_DELAY_SEC
            return

        # Revive wait: count down 2s then revive at room center
        if self.state == "revive_wait":
            self._revive_timer -= dt
            if self._revive_timer <= 0.0 and room_rect is not None:
                cx = (room_rect.left + room_rect.right) / 2.0
                cy = (room_rect.top + room_rect.bottom) / 2.0
                self.world_pos = (cx, cy)
                self.max_hp = float(FINAL_BOSS_REVIVE_HP)
                self.hp = float(FINAL_BOSS_REVIVE_HP)
                self.move_speed = float(FINAL_BOSS_MOVE_SPEED_REVIVE)
                self._revived = True
                self._revive_invuln_timer = FINAL_BOSS_REVIVE_INVULN_SEC
                self._cycle_index = 0
                self.state = "idle"
                self._set_state("idle")
                self.attack_cooldown_timer = 0.0
                self._attack_recovery_timer = 0.0
            return

        # Revive invulnerability tick
        if self._revive_invuln_timer > 0.0:
            self._revive_invuln_timer = max(0.0, self._revive_invuln_timer - dt)

        # Spawn idle: wait 0.75s before entering cycle
        if self.state == "spawn_idle":
            self._spawn_idle_timer -= dt
            self._set_state("idle")
            self._anim_state.advance(dt)
            if self._spawn_idle_timer <= 0.0:
                self.state = "idle"
            return

        # Teleport strike: telegraph -> teleport -> attack2 -> damage on frame
        if self.state == "teleport_telegraph":
            self._teleport_telegraph_timer -= dt
            if self._teleport_telegraph_timer <= 0.0 and self._teleport_dest is not None:
                old_pos = (float(self.world_pos[0]), float(self.world_pos[1]))
                self.world_pos = self._teleport_dest
                self._teleport_fx_frame = (old_pos, (float(self.world_pos[0]), float(self.world_pos[1])))
                self._teleport_dest = None
                self._set_state("attack2")
                self._teleport_strike_damage_frame = True
            self._anim_state.advance(dt)
            return

        # Attack2 (lava wave or teleport strike): telegraph then projectile for lava; teleport has its own telegraph
        if self.state == "attack2":
            if self._pending_lava_wave_dir is not None and self._attack_telegraph_timer > 0.0:
                self._attack_telegraph_timer -= dt
                if self._attack_telegraph_timer <= 0.0:
                    dx, dy = self._pending_lava_wave_dir
                    self._pending_lava_wave_dir = None
                    x, y = self.world_pos
                    self._pending_projectile = Projectile(
                        world_pos=(x, y),
                        direction=(dx, dy),
                        damage=float(FINAL_BOSS_LAVA_WAVE_DAMAGE),
                        speed=280.0,
                        lifetime_sec=2.0,
                        image_path=BOSS_WAVE_IMAGE,
                        size=BOSS_WAVE_SIZE,
                    )
            _, finished = self._anim_state.advance(dt)
            if self._teleport_strike_damage_frame:
                self.attack_cooldown_timer = self._cooldown_sec()
                self._attack_recovery_timer = self._recovery_sec()
            if finished:
                if not self._teleport_strike_damage_frame:
                    self._attack_recovery_timer = self._recovery_sec()
                self._set_state("idle")
                self._advance_cycle()
            return

        # Attack1 (fireball): telegraph then projectile; Phase 2 may move during/after release (Fireball + Movement)
        if self.state == "attack1":
            if self._pending_fireball_dir is not None and self._attack_telegraph_timer > 0.0:
                self._attack_telegraph_timer -= dt
                if self._attack_telegraph_timer <= 0.0:
                    self._pending_fireball_dir = None
                    # Aim at player at cast/release time: direction = normalize(player_pos - fireball_spawn_pos)
                    fireball_spawn_x, fireball_spawn_y = self.world_pos
                    px, py = player.world_pos
                    dx = px - fireball_spawn_x
                    dy = py - fireball_spawn_y
                    length = math.hypot(dx, dy)
                    if length < 1e-6:
                        dx, dy = 1.0, 0.0
                    else:
                        dx, dy = dx / length, dy / length
                    # Boss facing from same aim direction
                    self.facing = (1.0, 0.0) if dx >= 0 else (-1.0, 0.0)
                    self._pending_projectile = Projectile(
                        world_pos=(fireball_spawn_x, fireball_spawn_y),
                        direction=(dx, dy),
                        damage=float(FINAL_BOSS_FIREBALL_DAMAGE),
                        speed=float(FINAL_BOSS_FIREBALL_SPEED),
                        lifetime_sec=float(FINAL_BOSS_FIREBALL_LIFETIME_SEC),
                        image_path=BOSS_FIREBALL_IMAGE,
                        size=BOSS_FIREBALL_SIZE,
                        ignore_obstacles=True,
                    )
            # Phase 2: continue moving toward player during fireball pressure (Fireball + Movement)
            if self._phase2 and self._pending_fireball_dir is None and room_rect is not None:
                px, py = player.world_pos
                x, y = self.world_pos
                dx = px - x
                dy = py - y
                dist = math.hypot(dx, dy)
                if dist > 1e-3 and dist > FINAL_BOSS_STOP_DISTANCE:
                    nx, ny = dx / dist, dy / dist
                    vx = nx * self.move_speed * dt
                    vy = ny * self.move_speed * dt
                    x = max(room_rect.left + 64, min(room_rect.right - 64, x + vx))
                    y = max(room_rect.top + 64, min(room_rect.bottom - 64, y + vy))
                    self.world_pos = (x, y)
            _, finished = self._anim_state.advance(dt)
            if finished:
                self._attack_recovery_timer = self._recovery_fireball_sec()
                self._set_state("idle")
                self._advance_cycle()
            return

        # Non-looping attack anims: special (meteor), summon — Phase 2 may cast 1 Fireball during meteor telegraph
        if self.state in ("special", "summon"):
            if self.state == "special" and self._phase2 and self._meteor_fireball_timer > 0.0:
                self._meteor_fireball_timer -= dt
                if self._meteor_fireball_timer <= 0.0 and not self._meteor_fireball_fired:
                    self._meteor_fireball_fired = True
                    px, py = player.world_pos
                    x, y = self.world_pos
                    dx = px - x
                    dy = py - y
                    length = math.hypot(dx, dy)
                    if length < 1e-6:
                        dx, dy = 1.0, 0.0
                    else:
                        dx, dy = dx / length, dy / length
                    self._pending_projectile = Projectile(
                        world_pos=(x, y),
                        direction=(dx, dy),
                        damage=float(FINAL_BOSS_FIREBALL_DAMAGE),
                        speed=float(FINAL_BOSS_FIREBALL_SPEED),
                        lifetime_sec=float(FINAL_BOSS_FIREBALL_LIFETIME_SEC),
                        image_path=BOSS_FIREBALL_IMAGE,
                        size=BOSS_FIREBALL_SIZE,
                        ignore_obstacles=True,
                    )
            _, finished = self._anim_state.advance(dt)
            if finished:
                self._meteor_fireball_timer = 0.0
                self._meteor_fireball_fired = False
                self._attack_recovery_timer = self._recovery_sec()
                self._set_state("idle")
                self._advance_cycle()
            return

        # Hit: brief flinch only; do not reset attack cycle or cooldowns (stagger resistance).
        if self.state == "hit":
            self._hit_state_timer = max(0.0, self._hit_state_timer - dt)
            _, finished = self._anim_state.advance(dt)
            if self._hit_state_timer <= 0.0 or finished:
                self._hit_state_timer = 0.0
                self._set_state("idle")
            return

        # Idle / choosing next attack
        px, py = player.world_pos
        x, y = self.world_pos
        dx = px - x
        dy = py - y
        dist = math.hypot(dx, dy)

        if px > x:
            self.facing = (1.0, 0.0)
        else:
            self.facing = (-1.0, 0.0)

        # Can we start next attack? (cooldown and recovery both satisfied)
        if self._attack_recovery_timer <= 0.0 and self.attack_cooldown_timer <= 0.0:
            cycle = self._current_cycle()
            attack = cycle[self._cycle_index % len(cycle)]
            if attack == "teleport_strike" and self._teleport_cooldown_timer > 0.0:
                self._advance_cycle()
            else:
                if attack == "fireball" and dist >= FINAL_BOSS_STOP_DISTANCE:
                    self._start_fireball(px, py, x, y)
                    return
                if attack == "lava_wave" and FINAL_BOSS_WAVE_RANGE_MIN <= dist <= FINAL_BOSS_WAVE_RANGE_MAX:
                    self._start_lava_wave(px, py, x, y)
                    return
                if attack == "teleport_strike" and FINAL_BOSS_TELEPORT_RANGE_MIN <= dist <= FINAL_BOSS_TELEPORT_RANGE_MAX:
                    self._start_teleport_strike(player, room_rect, room, block_check=block_check)
                    return
                if attack == "meteor_rain":
                    self._start_meteor_rain(room, room_rect, player)
                    return
                # Current attack not valid (range); try next next frame
                self._advance_cycle()

        # Move toward player when not attacking (rush speed during _rush_timer)
        move_speed = float(FINAL_BOSS_RUSH_SPEED) if self._rush_timer > 0.0 else self.move_speed
        if dist > FINAL_BOSS_STOP_DISTANCE and self._attack_recovery_timer <= 0.0:
            if dist > 1e-3:
                nx, ny = dx / dist, dy / dist
                vx = nx * move_speed
                vy = ny * move_speed
                self._set_state("walk")
            else:
                vx = vy = 0.0
                self._set_state("idle")
        else:
            vx = vy = 0.0
            self._set_state("idle")

        x += vx * dt
        y += vy * dt
        if room_rect is not None:
            x = max(room_rect.left, min(room_rect.right, x))
            y = max(room_rect.top, min(room_rect.bottom, y))
        self.world_pos = (x, y)
        self._anim_state.advance(dt)

    def _advance_cycle(self) -> None:
        self._cycle_index += 1

    def _start_fireball(self, px: float, py: float, x: float, y: float) -> None:
        dx = px - x
        dy = py - y
        length = math.hypot(dx, dy)
        if length < 1e-6:
            dx, dy = 1.0, 0.0
        else:
            dx, dy = dx / length, dy / length
        self._set_state("attack1")
        self._attack_telegraph_timer = self._telegraph_fireball_sec()
        self._pending_fireball_dir = (dx, dy)
        self.attack_cooldown_timer = float(FINAL_BOSS_FIREBALL_CAST_COOLDOWN)

    def _start_lava_wave(self, px: float, py: float, x: float, y: float) -> None:
        dx = px - x
        dy = py - y
        length = math.hypot(dx, dy)
        if length < 1e-6:
            dx, dy = 1.0, 0.0
        else:
            dx, dy = dx / length, dy / length
        self._set_state("attack2")
        self._attack_telegraph_timer = self._telegraph_lava_sec()
        self._pending_lava_wave_dir = (dx, dy)
        self.attack_cooldown_timer = self._cooldown_sec()

    def _start_teleport_strike(
        self,
        player: Any,
        room_rect: pygame.Rect | None,
        room: Any,
        block_check: Any = None,
    ) -> None:
        if room_rect is None or room is None:
            self._advance_cycle()
            return
        px, py = player.world_pos
        min_dist = float(FINAL_BOSS_TELEPORT_MIN_DIST_PX)
        rng = _make_rng(self.room_index, int(self._time * 10))
        # Prefer appearing behind or flanking the player (threatening angle)
        facing = getattr(player, "facing", (1, 0))
        fx, fy = float(facing[0]), float(facing[1])
        player_angle = math.atan2(fy, fx)
        use_behind = rng.random() < 0.6
        tx, ty = None, None
        for attempt in range(12):
            if use_behind:
                angle = player_angle + math.pi + rng.uniform(-0.55, 0.55)
                radius = rng.uniform(min_dist, min_dist + 80.0)
            else:
                angle = rng.uniform(0, 2 * math.pi)
                radius = rng.uniform(min_dist, min_dist + 120.0)
            tx = px + radius * math.cos(angle)
            ty = py + radius * math.sin(angle)
            tx = max(room_rect.left + 80, min(room_rect.right - 80, tx))
            ty = max(room_rect.top + 80, min(room_rect.bottom - 80, ty))
            dx, dy = tx - px, ty - py
            dist = math.hypot(dx, dy)
            if dist < min_dist and dist > 1e-6:
                scale = min_dist / dist
                tx, ty = px + dx * scale, py + dy * scale
            elif dist < 1e-6:
                tx, ty = px + min_dist, py
            if block_check is not None and room is not None:
                txi = int(tx // TILE_SIZE)
                tyi = int(ty // TILE_SIZE)
                if block_check(room, txi, tyi):
                    continue
            break
        self._teleport_dest = (tx, ty)
        self._teleport_telegraph_timer = self._telegraph_teleport_sec()
        self.state = "teleport_telegraph"
        self.attack_cooldown_timer = self._cooldown_sec()
        self._teleport_cooldown_timer = float(FINAL_BOSS_TELEPORT_COOLDOWN_SEC)

    def _start_meteor_rain(self, room: Any, room_rect: pygame.Rect | None, player: Any) -> None:
        self._set_state("special")
        self._meteor_fireball_fired = False
        self._meteor_fireball_timer = 0.0
        if room_rect is None:
            self.attack_cooldown_timer = self._cooldown_sec()
            return
        telegraph_sec = self._telegraph_meteor_sec()
        # Phase 2 or Revive: cast 1 Fireball during meteor telegraph (at 0.35s into 1.0s window)
        if self._phase2 or self._revived:
            self._meteor_fireball_timer = 0.35
        # 3 targets at or near player position (deterministic pattern, fair and dodgeable)
        px, py = player.world_pos
        min_x = room_rect.left + 48
        max_x = room_rect.right - 48
        min_y = room_rect.top + 48
        max_y = room_rect.bottom - 48
        # Deterministic offsets from player: one on player, two nearby with fixed spacing (>= METEOR_TARGET_SPACING_PX)
        step = int(self._time * 10) % 100
        rng = _make_rng(self.room_index, step)
        # Pattern: center on player, then two at (dx1, dy1) and (dx2, dy2) with spacing >= 80px
        offsets = [(0.0, 0.0), (METEOR_TARGET_SPACING_PX, 0.0), (-METEOR_TARGET_SPACING_PX * 0.6, METEOR_TARGET_SPACING_PX * 0.8)]
        # Rotate pattern slightly by deterministic angle so it's not always axis-aligned
        angle = (step % 7) * 0.45
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        positions = []
        for (dx, dy) in offsets:
            rx = dx * cos_a - dy * sin_a
            ry = dx * sin_a + dy * cos_a
            x = px + rx
            y = py + ry
            x = max(min_x, min(max_x, x))
            y = max(min_y, min(max_y, y))
            # Snap to valid tile if possible (no walls/blocked)
            tx = int(x // TILE_SIZE)
            ty = int(y // TILE_SIZE)
            if room is not None and (tx < 0 or ty < 0 or tx >= room.width or ty >= room.height or room.is_tile_in_wall_band(tx, ty) or room.get_tile_type(tx, ty) not in _METEOR_VALID_TILE_TYPES):
                # Find nearest valid tile (expand in rings)
                found = False
                for d in range(0, 8):
                    for otx in range(tx - d, tx + d + 1):
                        for oty in range(ty - d, ty + d + 1):
                            if 0 <= otx < room.width and 0 <= oty < room.height and not room.is_tile_in_wall_band(otx, oty) and room.get_tile_type(otx, oty) in _METEOR_VALID_TILE_TYPES:
                                x = (otx + 0.5) * TILE_SIZE
                                y = (oty + 0.5) * TILE_SIZE
                                x = max(min_x, min(max_x, x))
                                y = max(min_y, min(max_y, y))
                                found = True
                                break
                        if found:
                            break
                    if found:
                        break
            positions.append((x, y))
        trigger_time = self._time + telegraph_sec
        for (mx, my) in positions:
            self.pending_meteor_impacts.append({
                "x": mx, "y": my, "damage": float(FINAL_BOSS_METEOR_DAMAGE),
                "trigger_time": trigger_time, "radius": 64.0,
                "telegraph_sec": telegraph_sec,
            })
        self.attack_cooldown_timer = self._cooldown_sec()

    def on_player_death_start(self, player: Any) -> None:
        if self._player_dead or self.inactive:
            return
        self._player_dead = True
        self._set_state("idle")
        self.velocity_xy = (0.0, 0.0)

    def draw(self, screen: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        self._ensure_animations_loaded()
        if self.inactive:
            return
        if self.state == "revive_wait":
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


def preload_final_boss_animations() -> None:
    """Load Final Boss animations into shared cache; call when entering Room 29 so spawn does not stall."""
    global _FINAL_BOSS_ANIMATION_CACHE
    if _FINAL_BOSS_ANIMATION_CACHE is not None:
        return
    b = FinalBoss((0, 0), room_index=29)
    b._ensure_animations_loaded()
