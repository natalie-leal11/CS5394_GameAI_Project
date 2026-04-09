# Player entity: world_pos, state machine, animations, input (WASD, dash, attack, block/parry).

import os
import pygame

from game.config import (
    LOGICAL_W,
    LOGICAL_H,
    PLAYER_SIZE,
    PLAYER_HITBOX_W,
    PLAYER_HITBOX_H,
    PLAYER_MOVEMENT_HITBOX_W,
    PLAYER_MOVEMENT_HITBOX_H,
    PLAYER_BASE_HP,
    RESERVE_HEAL_POOL_MAX_ENTRIES,
    RESERVE_HEAL_USE_COOLDOWN_SEC,
    PLAYER_PARRY_WINDOW_SEC,
    PLAYER_DASH_DURATION_SEC,
    PLAYER_SHORT_ATTACK_DAMAGE,
    PLAYER_LONG_ATTACK_DAMAGE,
    PLAYER_SHORT_ATTACK_WINDUP_SEC,
    PLAYER_SHORT_ATTACK_ACTIVE_SEC,
    PLAYER_LONG_ATTACK_WINDUP_SEC,
    PLAYER_SHORT_ATTACK_COOLDOWN_SEC,
    PLAYER_LONG_ATTACK_COOLDOWN_SEC,
    PLAYER_SHORT_ATTACK_RANGE_PX,
    PLAYER_LONG_ATTACK_RANGE_PX,
    PLAYER_ATTACK_LEVEL_STEP,
    PLAYER_LIVES_INITIAL,
    PROJECT_ROOT,
    DEBUG_PLAYER_ATTACK_PROXIMITY,
    DEBUG_PLAYER_ATTACK_WALK_TRACE,
    DEBUG_PLAYER_ATTACK_INPUT_TRACE,
    DEBUG_PLAYER_SHORT_ATTACK_BUFFER,
    DEBUG_LIVE_SHORT_ATTACK_TRACE,
    DEBUG_BLOCK_PARRY_TRACE,
    DEBUG_SHORT_ATTACK_INPUT,
)
from game.asset_loader import load_animation
from systems.animation import AnimationState
from systems.movement import apply_player_movement

PLAYER_STATES = (
    "idle",
    "walk",
    "attack_short",
    "attack_long",
    "dash",
    "block",
    "parry",
    "hit",
    "death",
)

# (fps, loop) per state. Short attack stays snappy (10fps); long is slower/heavier (7fps).
ANIM_SPECS = {
    "idle": (10, True),
    "walk": (10, True),
    "attack_short": (10, False),
    "attack_long": (7, False),
    "dash": (12, False),
    "block": (10, True),
    "parry": (10, True),
    "hit": (10, False),
    "death": (10, False),
}

PLAYER_ASSET_BASE = "assets/entities/player"
# Directional animations root (preferred) per new asset layout:
# assets/entities/player/directional/idle, walk_<dir>, attack_<dir>
PLAYER_DIRECTIONAL_BASE = os.path.join(PLAYER_ASSET_BASE, "directional")
FACING_DIRS = ("up", "down", "left", "right")
# One-shot debug after directional attack folders are resolved (see _load_directional_animations).
_DIRECTIONAL_ATTACK_SETS_DEBUG_PRINTED = False
# One-shot: attack FPS + long cooldown enforcement (see _ensure_animations_loaded).
_ATTACK_TIMING_DEBUG_PRINTED = False
# Colorkey: white so sprite background and jagged white outline are transparent
PLAYER_COLORKEY_BG = (255, 255, 255)
# Pixels with R,G,B >= this become transparent (removes antialiased white edges)
PLAYER_NEAR_WHITE_THRESHOLD = 245
# Pixels near the top-left corner color become transparent (removes blue/teal or any solid bg)
PLAYER_CORNER_BG_TOLERANCE = 50

_MOVEMENT_KEYS = frozenset({pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d})


def _player_has_movement_keys(keys_pressed: set[int]) -> bool:
    return bool(keys_pressed & _MOVEMENT_KEYS)


class Player:
    def __init__(self):
        self.world_pos = (LOGICAL_W / 2.0, LOGICAL_H / 2.0)
        self.state = "idle"
        self.facing = (1, 0)
        self.hp = float(PLAYER_BASE_HP)
        self.base_max_hp = float(PLAYER_BASE_HP)  # Reference for HUD / %-heals; unchanged by Safe Room health pick
        self.max_hp = float(PLAYER_BASE_HP)       # Current max HP (cap for overheal)
        self.lives = int(PLAYER_LIVES_INITIAL)
        self.life_index = 0
        self.invulnerable_timer: float = 0.0
        # Banked heals: FIFO list of exact leftover HP from overheal; H consumes from front (see try_consume_reserve_heal).
        self.reserve_heal_pool: list[float] = []
        self.reserve_heal_cooldown_timer: float = 0.0
        self.inactive = False
        self.velocity_xy = (0.0, 0.0)
        # Attack stats / scaling
        self.attack_level = 0  # increases later via pickups
        # Biome 3/4 Safe Room upgrade multipliers (1.0 = no upgrade)
        self.move_speed_mult = 1.0   # +10% from Speed Boost
        self.attack_damage_mult = 1.0  # +12% from Attack Boost
        self.damage_taken_mult = 1.0   # Defense: -12% incoming = 0.88
        # Health upgrade: Safe Room pick records mult; benefit is heal + overflow (not base_max_hp scaling).
        self._safe_room_health_mult = 1.0
        # Dash
        self.dash_active = False
        self.dash_timer = 0.0
        self.dash_cooldown_timer = 0.0
        self.dash_direction = (1, 0)
        # Parry (K key): PLAYER_PARRY_WINDOW_SEC window when K is pressed
        self.parry_window_timer = 0.0
        # Avoid idle/walk flicker: only switch to idle after still for this long (sec)
        self._still_timer = 0.0
        self._IDLE_DELAY = 0.1
        # Animations: state -> list of surfaces (loaded lazily after display init)
        self._animations: dict[str, list] = {}
        self._anim_state = AnimationState()
        self._animations_loaded = False
        # Attack timing helpers for hitboxes
        self._short_attack_timer = 0.0
        self._short_attack_hit_ids: set[int] = set()
        self._long_attack_timer = 0.0
        self._long_attack_fired = False
        # Real gameplay cooldown for long attack (independent of animation length).
        self.long_attack_cooldown_timer = 0.0
        # Min gap between short-attack starts (keyboard/mouse and RL use the same Player path).
        self.short_attack_cooldown_timer = 0.0
        # One visible frame for idle (Requirements: player visible when idle at all times).
        self._idle_surface: pygame.Surface | None = None
        # Directional animations (per facing dir); populated if directional assets exist.
        self._dir_animations: dict[str, dict[str, list[pygame.Surface]]] = {}
        self._use_directional = False
        self._facing_dir = "down"
        self._current_anim_key: tuple[str, str | None] | None = None
        # Damage feedback: brief red flash when hit.
        self.damage_flash_timer: float = 0.0
        # Buffered short attack: click while locked (attack_short/dash/hit/death) is held until we can swing once.
        self._pending_short_attack: bool = False

    def apply_safe_room_health_upgrade(self, mult: float) -> None:
        """
        Safe Room health upgrade: grant (mult - 1) * base_max_hp as healing via apply_incoming_heal
        (fills HP up to max_hp; remainder goes to reserve_heal_pool). Does not change base_max_hp or max_hp.
        """
        m = float(mult)
        if m <= 1.0:
            return
        base = float(self.base_max_hp)
        bonus = base * (m - 1.0)
        if bonus > 0.0:
            self.apply_incoming_heal(bonus)
        self._safe_room_health_mult = m

    def clear_reserve_heals(self) -> None:
        """Called on death / when banked heals must reset."""
        self.reserve_heal_pool.clear()
        self.reserve_heal_cooldown_timer = 0.0

    def apply_incoming_heal(self, amount: float) -> float:
        """
        Heal up to max_hp; leftover amount is appended to reserve_heal_pool (FIFO, max entries; if full, discard new).
        Returns HP actually restored to HP bar.
        """
        if amount <= 0.0:
            return 0.0
        cap = float(self.max_hp)
        before = float(self.hp)
        room = max(0.0, cap - before)
        applied = min(float(amount), room)
        self.hp = before + applied
        leftover = float(amount) - applied
        if leftover > 0.0 and len(self.reserve_heal_pool) < int(RESERVE_HEAL_POOL_MAX_ENTRIES):
            self.reserve_heal_pool.append(leftover)
        return applied

    def try_consume_reserve_heal(self) -> float:
        """
        Pop front of reserve_heal_pool (FIFO), heal up to max_hp. Unused portion of that entry is put back at front.
        Returns HP restored this press, or 0 if pool empty or already full.
        """
        if not self.reserve_heal_pool:
            return 0.0
        cap = float(self.max_hp)
        if self.hp >= cap - 1e-9:
            return 0.0
        first = float(self.reserve_heal_pool.pop(0))
        room = cap - float(self.hp)
        applied = min(first, room)
        self.hp += applied
        remainder = first - applied
        if remainder > 1e-9:
            self.reserve_heal_pool.insert(0, remainder)
        return applied

    def get_hitbox_rect(self) -> pygame.Rect:
        """World-space rect for combat/collision (body only). Use this instead of full sprite rect so the transparent background doesn't count as hittable."""
        x, y = self.world_pos[0], self.world_pos[1]
        return pygame.Rect(
            x - PLAYER_HITBOX_W / 2,
            y - PLAYER_HITBOX_H / 2,
            PLAYER_HITBOX_W,
            PLAYER_HITBOX_H,
        )

    def get_movement_hitbox_rect(self) -> pygame.Rect:
        """Tighter body for room clamp, wall collision, and spawn overlap checks (same center as world_pos)."""
        x, y = self.world_pos[0], self.world_pos[1]
        return pygame.Rect(
            x - PLAYER_MOVEMENT_HITBOX_W / 2,
            y - PLAYER_MOVEMENT_HITBOX_H / 2,
            PLAYER_MOVEMENT_HITBOX_W,
            PLAYER_MOVEMENT_HITBOX_H,
        )

    def _ensure_animations_loaded(self) -> None:
        """Load animations once; call only after pygame.display.set_mode() has been used."""
        if self._animations_loaded:
            return
        self._animations_loaded = True
        # 1) Load non-directional animations as fallback (legacy folders).
        for s in PLAYER_STATES:
            folder = os.path.join(PLAYER_ASSET_BASE, s)
            if not os.path.isdir(folder):
                folder = PLAYER_ASSET_BASE + "/" + s
            self._animations[s] = load_animation(
                folder,
                size=PLAYER_SIZE,
                use_colorkey=True,
                colorkey_color=PLAYER_COLORKEY_BG,
                near_white_threshold=PLAYER_NEAR_WHITE_THRESHOLD,
                corner_bg_tolerance=PLAYER_CORNER_BG_TOLERANCE,
            )
        # 2) Load directional animations (preferred) if the new folder root exists.
        self._load_directional_animations()
        # 3) Build one visible idle frame, preferring directional idle if available.
        idle_frames: list[pygame.Surface] = []
        if self._use_directional:
            idle_map = self._dir_animations.get("idle", {})
            idle_frames = idle_map.get("center") or idle_map.get("down") or []
        if not idle_frames:
            idle_frames = self._animations.get("idle", [])
        idle_single = [idle_frames[0]] if idle_frames else []
        if not idle_single:
            for key in ("walk", "attack_short", "attack_long"):
                other = self._animations.get(key)
                if other:
                    idle_single = [other[0]]
                    break
        if not idle_single:
            placeholder = pygame.Surface(PLAYER_SIZE)
            placeholder.fill((70, 90, 110))
            placeholder = placeholder.convert_alpha()
            idle_single = [placeholder]
        self._anim_state.set_animation(idle_single, 1, True)
        if idle_single:
            s = idle_single[0]
            self._idle_surface = s.convert_alpha().copy()
        else:
            self._idle_surface = None
        # Initial facing/animation key.
        self._facing_dir = getattr(self, "_facing_dir", "down")
        self._current_anim_key = ("idle", None)

        global _ATTACK_TIMING_DEBUG_PRINTED
        if not _ATTACK_TIMING_DEBUG_PRINTED:
            _ATTACK_TIMING_DEBUG_PRINTED = True
            s_fps, _ = ANIM_SPECS["attack_short"]
            l_fps, _ = ANIM_SPECS["attack_long"]
            print(f"[PLAYER] Attack animation FPS: attack_short={s_fps}, attack_long={l_fps}")
            print(
                f"[PLAYER] Short attack cooldown enforced at {PLAYER_SHORT_ATTACK_COOLDOWN_SEC}s "
                "(real timer; independent of animation lock)."
            )
            print(
                f"[PLAYER] Long attack cooldown enforced at {PLAYER_LONG_ATTACK_COOLDOWN_SEC}s "
                "(real timer; independent of animation lock)."
            )

    def _load_directional_animations(self) -> None:
        """Populate directional animations dict if assets/entities/player/directional exists."""
        self._dir_animations = {}
        base_rel = PLAYER_DIRECTIONAL_BASE
        base_fs = os.path.join(PROJECT_ROOT, base_rel)
        if not os.path.isdir(base_fs):
            self._use_directional = False
            return
        self._use_directional = True

        def _subdir_exists(name: str) -> bool:
            return os.path.isdir(os.path.join(base_fs, name))

        # Idle (single folder).
        if _subdir_exists("idle"):
            idle_frames = load_animation(
                os.path.join(base_rel, "idle"),
                size=PLAYER_SIZE,
                use_colorkey=True,
                colorkey_color=PLAYER_COLORKEY_BG,
                near_white_threshold=PLAYER_NEAR_WHITE_THRESHOLD,
                corner_bg_tolerance=PLAYER_CORNER_BG_TOLERANCE,
            )
            if idle_frames:
                self._dir_animations["idle"] = {"center": idle_frames}

        # walk_<dir>
        for dir_name in ("up", "down", "left", "right"):
            sub = f"walk_{dir_name}"
            if not _subdir_exists(sub):
                continue
            frames = load_animation(
                os.path.join(base_rel, sub),
                size=PLAYER_SIZE,
                use_colorkey=True,
                colorkey_color=PLAYER_COLORKEY_BG,
                near_white_threshold=PLAYER_NEAR_WHITE_THRESHOLD,
                corner_bg_tolerance=PLAYER_CORNER_BG_TOLERANCE,
            )
            if frames:
                self._dir_animations.setdefault("walk", {})[dir_name] = frames

        # attack_<dir> → attack_short only (short slash animations).
        for dir_name in ("up", "down", "left", "right"):
            sub = f"attack_{dir_name}"
            if not _subdir_exists(sub):
                continue
            frames = load_animation(
                os.path.join(base_rel, sub),
                size=PLAYER_SIZE,
                use_colorkey=True,
                colorkey_color=PLAYER_COLORKEY_BG,
                near_white_threshold=PLAYER_NEAR_WHITE_THRESHOLD,
                corner_bg_tolerance=PLAYER_CORNER_BG_TOLERANCE,
            )
            if frames:
                self._dir_animations.setdefault("attack_short", {})[dir_name] = frames

        # attack_long_<dir> → attack_long; per-direction fallback to attack_<dir> if missing/empty.
        long_used_fallback_for_any_dir = False
        for dir_name in ("up", "down", "left", "right"):
            sub_long = f"attack_long_{dir_name}"
            sub_short = f"attack_{dir_name}"
            frames = []
            if _subdir_exists(sub_long):
                frames = load_animation(
                    os.path.join(base_rel, sub_long),
                    size=PLAYER_SIZE,
                    use_colorkey=True,
                    colorkey_color=PLAYER_COLORKEY_BG,
                    near_white_threshold=PLAYER_NEAR_WHITE_THRESHOLD,
                    corner_bg_tolerance=PLAYER_CORNER_BG_TOLERANCE,
                )
            if not frames and _subdir_exists(sub_short):
                long_used_fallback_for_any_dir = True
                frames = load_animation(
                    os.path.join(base_rel, sub_short),
                    size=PLAYER_SIZE,
                    use_colorkey=True,
                    colorkey_color=PLAYER_COLORKEY_BG,
                    near_white_threshold=PLAYER_NEAR_WHITE_THRESHOLD,
                    corner_bg_tolerance=PLAYER_CORNER_BG_TOLERANCE,
                )
            if frames:
                self._dir_animations.setdefault("attack_long", {})[dir_name] = frames

        global _DIRECTIONAL_ATTACK_SETS_DEBUG_PRINTED
        if not _DIRECTIONAL_ATTACK_SETS_DEBUG_PRINTED:
            _DIRECTIONAL_ATTACK_SETS_DEBUG_PRINTED = True
            print(
                "[PLAYER] Directional short attack: "
                "directional/attack_up|attack_down|attack_left|attack_right/"
            )
            long_msg = (
                "directional/attack_long_up|attack_long_down|attack_long_left|attack_long_right/"
            )
            if long_used_fallback_for_any_dir:
                long_msg += (
                    " (one or more dirs fell back to directional/attack_<dir>/ — "
                    "missing or empty attack_long_* folder)"
                )
            print(f"[PLAYER] Directional long attack: {long_msg}")

    def _dir_from_vector(self, dx: float, dy: float) -> str:
        if dx == 0 and dy == 0:
            return getattr(self, "_facing_dir", "down")
        if abs(dx) >= abs(dy):
            return "right" if dx > 0 else "left"
        return "down" if dy > 0 else "up"

    def _set_facing_from_velocity(self, vx: float, vy: float) -> None:
        if vx == 0 and vy == 0:
            return
        self.facing = (vx, vy)
        self._facing_dir = self._dir_from_vector(vx, vy)

    def _select_frames_for_state(
        self,
        state: str,
        dir_tag: str | None,
        fps: int,
        loop: bool,
    ) -> list[pygame.Surface]:
        """Pick animation frames for state, preferring directional sets when available."""
        frames = self._animations.get(state, self._animations.get("idle", []))
        if self._use_directional and state in ("walk", "attack_short", "attack_long"):
            dir_map = self._dir_animations.get(state)
            if state == "attack_long" and not dir_map:
                dir_map = self._dir_animations.get("attack_short")
            if dir_map:
                use_dir = dir_tag or getattr(self, "_facing_dir", "down")
                if use_dir not in dir_map and "down" in dir_map:
                    use_dir = "down"
                if use_dir in dir_map:
                    frames = dir_map[use_dir]
                elif state == "attack_long":
                    short_map = self._dir_animations.get("attack_short")
                    if short_map and use_dir in short_map:
                        frames = short_map[use_dir]
        if not frames:
            frames = self._animations.get("idle", [])
        return frames

    def _set_state(self, new_state: str) -> None:
        dir_tag: str | None = None
        if new_state in ("walk", "attack_short", "attack_long"):
            dir_tag = getattr(self, "_facing_dir", "down")
        anim_key = (new_state, dir_tag)
        old_key = getattr(self, "_current_anim_key", None)
        # Only skip when state AND key are unchanged (walk→attack_short always differs in first tuple slot).
        if anim_key == old_key and new_state == self.state:
            return
        old_state = self.state
        if DEBUG_LIVE_SHORT_ATTACK_TRACE and {old_state, new_state} & {
            "walk",
            "idle",
            "attack_short",
            "attack_long",
        }:
            print(f"[LIVE_TRACE] Player._set_state {old_state!r} -> {new_state!r} anim_key={anim_key!r}")
        if DEBUG_BLOCK_PARRY_TRACE and {old_state, new_state} & {"block", "parry", "idle", "walk"}:
            print(
                f"[BLOCK_PARRY_TRACE] Player._set_state {old_state!r} -> {new_state!r} "
                f"anim_key={anim_key!r} parry_timer={getattr(self, 'parry_window_timer', 0.0):.4f}"
            )
        if DEBUG_PLAYER_ATTACK_WALK_TRACE and new_state in ("attack_short", "attack_long"):
            print(
                f"[PLAYER] _set_state apply: {self.state!r} -> {new_state!r} anim_key={anim_key} was_key={old_key}"
            )
        self.state = new_state
        self._current_anim_key = anim_key
        fps, loop = ANIM_SPECS.get(new_state, (10, True))
        # Idle uses the precomputed single-frame idle surface.
        if new_state == "idle":
            if self._idle_surface is not None:
                frames = [self._idle_surface]
            else:
                frames = self._animations.get("idle", []) or self._animations.get("walk", [])
            fps, loop = 1, True
        else:
            frames = self._select_frames_for_state(new_state, dir_tag, fps, loop)
        if new_state == "attack_short":
            self._short_attack_timer = 0.0
            self._short_attack_hit_ids.clear()
            self.short_attack_cooldown_timer = float(PLAYER_SHORT_ATTACK_COOLDOWN_SEC)
        if new_state == "attack_long":
            self._long_attack_timer = 0.0
            self._long_attack_fired = False
            self.long_attack_cooldown_timer = float(PLAYER_LONG_ATTACK_COOLDOWN_SEC)
        self._anim_state.set_animation(frames, fps, loop)

    def update(
        self,
        dt: float,
        keys_pressed: set[int],
        mouse_buttons: tuple[bool, bool, bool],
        block_held: bool,
        parry_request: bool,
        dash_request: bool,
        attack_short_request: bool,
        attack_long_request: bool,
    ) -> None:
        self._ensure_animations_loaded()
        if self.inactive:
            return
        state_at_update_entry = self.state
        try:
            self._run_update_body(
                dt,
                keys_pressed,
                mouse_buttons,
                block_held,
                parry_request,
                dash_request,
                attack_short_request,
                attack_long_request,
                state_at_update_entry,
            )
        finally:
            if DEBUG_LIVE_SHORT_ATTACK_TRACE and (
                attack_short_request
                or self._pending_short_attack
                or state_at_update_entry == "attack_short"
                or self.state == "attack_short"
            ):
                fi = getattr(self._anim_state, "current_frame_index", -1)
                print(
                    f"[LIVE_TRACE] Player.update end state={self.state!r} pending={self._pending_short_attack} "
                    f"frame_idx={fi} short_req_was={attack_short_request}"
                )
            if DEBUG_PLAYER_ATTACK_WALK_TRACE and (
                attack_short_request
                or state_at_update_entry == "attack_short"
                or self.state == "attack_short"
            ):
                fi = getattr(self._anim_state, "current_frame_index", -1)
                print(
                    f"[PLAYER] update end: state={self.state!r} began={state_at_update_entry!r} "
                    f"frame_idx={fi} anim_key={self._current_anim_key}"
                )

    def _run_update_body(
        self,
        dt: float,
        keys_pressed: set[int],
        mouse_buttons: tuple[bool, bool, bool],
        block_held: bool,
        parry_request: bool,
        dash_request: bool,
        attack_short_request: bool,
        attack_long_request: bool,
        state_at_update_entry: str,
    ) -> None:
        if DEBUG_PLAYER_ATTACK_WALK_TRACE and attack_short_request:
            print(
                f"[PLAYER] update begin: state={self.state!r} short_req={attack_short_request} "
                f"keys_WASD={bool(keys_pressed & _MOVEMENT_KEYS)}"
            )
        if self.long_attack_cooldown_timer > 0.0:
            self.long_attack_cooldown_timer = max(0.0, self.long_attack_cooldown_timer - dt)
        if self.short_attack_cooldown_timer > 0.0:
            self.short_attack_cooldown_timer = max(0.0, self.short_attack_cooldown_timer - dt)
        if self.damage_flash_timer > 0.0:
            self.damage_flash_timer = max(0.0, self.damage_flash_timer - dt)
        if self.invulnerable_timer > 0.0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)
        self._consumed_dash_request = False
        locking = {"attack_short", "attack_long", "dash", "hit", "death"}
        can_accept_input = self.state not in locking
        # Dash can interrupt attack/block/parry so Space feels instant (no delay)
        can_dash = self.state not in ("dash", "hit", "death")

        if DEBUG_LIVE_SHORT_ATTACK_TRACE:
            print(
                f"[LIVE_TRACE] _run_update_body state={self.state!r} can_accept_input={can_accept_input} "
                f"attack_short_request={attack_short_request} _pending_short_attack={self._pending_short_attack}"
            )

        # Buffer short-attack clicks before any state branch returns early (e.g. during attack_short).
        if attack_short_request and not can_accept_input:
            self._pending_short_attack = True
            if DEBUG_PLAYER_SHORT_ATTACK_BUFFER or DEBUG_PLAYER_ATTACK_INPUT_TRACE:
                print(
                    f"[BUFFER] short attack buffered (will swing when unlocked) "
                    f"state={self.state!r} can_accept_input={can_accept_input}"
                )

        # Death
        if self.hp <= 0 and self.state != "death":
            self._set_state("death")
            apply_player_movement(self, set(), dt)
            self._anim_state.advance(dt)
            return

        if self.state == "death":
            _, finished = self._anim_state.advance(dt)
            if finished:
                self.inactive = True
            return

        # Dash (active): can't be interrupted
        if self.state == "dash":
            apply_player_movement(self, keys_pressed, dt)
            if not self.dash_active:
                self._set_state("idle")
            self._anim_state.advance(dt)
            return

        # Hit (stub: one-shot then idle)
        if self.state == "hit":
            _, finished = self._anim_state.advance(dt)
            if finished:
                self._set_state("idle")
            apply_player_movement(self, set(), dt)
            return

        # Attack: allow movement while attacking so strikes can be made on the move.
        if self.state in ("attack_short", "attack_long"):
            if self.state == "attack_short":
                self._short_attack_timer += dt
            elif self.state == "attack_long":
                self._long_attack_timer += dt
            _, finished = self._anim_state.advance(dt)
            if finished:
                self._set_state("idle")
            # Use current input so the player can keep moving during attacks.
            apply_player_movement(self, keys_pressed, dt)
            return

        # Drop guard visuals once block/parry window is over (before melee so LMB works right after releasing J).
        if self.parry_window_timer <= 0 and not block_held:
            if self.state in ("block", "parry"):
                self._set_state("idle")

        # Short attack BEFORE K-tap parry: key-repeat KEYDOWN on K can share a frame with LMB and previously
        # stole the whole update (walk+LMB felt like multi-click). Ongoing parry (timer, no new K) stays below.
        if attack_short_request and DEBUG_PLAYER_ATTACK_PROXIMITY:
            print(
                f"[PLAYER] update sees attack_short_request=True state={self.state} "
                f"can_accept_input={can_accept_input}"
            )
        if DEBUG_SHORT_ATTACK_INPUT and attack_short_request:
            print(
                f"[SHORT_ATK_IN] Player.update receives attack_short_request=True "
                f"state={state_at_update_entry!r} can_accept_input={can_accept_input} "
                f"wasd={bool(keys_pressed & _MOVEMENT_KEYS)}"
            )
        # Short attack: pending was set above when locked; execute when unlocked.
        # Cooldown (config): cannot start a new short attack until timer elapses; keep buffer.
        want_short = can_accept_input and (attack_short_request or self._pending_short_attack)
        if want_short and self.short_attack_cooldown_timer > 0.0:
            self._pending_short_attack = True
        elif want_short:
            had_pending = self._pending_short_attack
            from_buffer_only = had_pending and not attack_short_request
            if DEBUG_PLAYER_SHORT_ATTACK_BUFFER or DEBUG_PLAYER_ATTACK_INPUT_TRACE:
                if from_buffer_only:
                    print(
                        f"[BUFFER] buffered short attack EXECUTED (consumed pending) "
                        f"state={self.state!r} can_accept_input={can_accept_input}"
                    )
                elif attack_short_request:
                    print(
                        f"[BUFFER] short attack IMMEDIATE (no pending) "
                        f"state={state_at_update_entry!r} can_accept_input={can_accept_input}"
                    )
            self._pending_short_attack = False
            if (DEBUG_PLAYER_SHORT_ATTACK_BUFFER or DEBUG_PLAYER_ATTACK_INPUT_TRACE) and had_pending:
                print(f"[BUFFER] pending buffer cleared state={self.state!r}")
            self.parry_window_timer = 0.0
            if DEBUG_PLAYER_ATTACK_PROXIMITY and _player_has_movement_keys(keys_pressed):
                print("[PLAYER] Short attack triggered while moving (WASD held)")
            prev_state = self.state
            self._set_state("attack_short")
            if DEBUG_SHORT_ATTACK_INPUT:
                print(
                    f"[SHORT_ATK_IN] attack_short state ENTERED from={prev_state!r} "
                    f"anim_key={getattr(self, '_current_anim_key', None)!r}"
                )
            if DEBUG_PLAYER_ATTACK_WALK_TRACE:
                if self.state != "attack_short":
                    print(
                        f"[PLAYER] ERROR: after _set_state(attack_short) state is {self.state!r} "
                        f"anim_key={self._current_anim_key} (desync / early-return bug)"
                    )
                else:
                    print(
                        f"[PLAYER] after short attack trigger: state={self.state!r} "
                        f"from={prev_state!r} anim_key={self._current_anim_key}"
                    )
            if DEBUG_PLAYER_ATTACK_PROXIMITY and prev_state == "walk":
                print(f"[PLAYER] walk -> attack_short (short attack priority over walk/dash)")
            apply_player_movement(self, keys_pressed, dt)
            self._anim_state.advance(dt)
            return

        # K pressed THIS frame: parry after short melee so K repeat + LMB still swings short (LMB wins same frame).
        if DEBUG_BLOCK_PARRY_TRACE:
            print(
                f"[BLOCK_PARRY_TRACE] Player._run_update_body pre-parry "
                f"state={self.state!r} block_held={block_held} parry_request={parry_request} "
                f"parry_window_timer(before)={self.parry_window_timer:.4f} "
                f"attack_short_request={attack_short_request}"
            )
        if parry_request:
            self.parry_window_timer = PLAYER_PARRY_WINDOW_SEC
        if parry_request and self.parry_window_timer > 0:
            self.parry_window_timer -= dt
            self._set_state("parry")
            self._anim_state.advance(dt)
            apply_player_movement(self, set(), dt)
            if DEBUG_BLOCK_PARRY_TRACE:
                print(
                    f"[BLOCK_PARRY_TRACE] Player parry (K this frame) -> state={self.state!r} "
                    f"parry_timer(after)={self.parry_window_timer:.4f} is_parry_active={self.is_parry_active()}"
                )
            return
        if can_accept_input and attack_long_request:
            if self.long_attack_cooldown_timer > 0.0:
                print(
                    f"[PLAYER] Long attack blocked by cooldown "
                    f"({self.long_attack_cooldown_timer:.2f}s remaining / "
                    f"{PLAYER_LONG_ATTACK_COOLDOWN_SEC}s configured)"
                )
            else:
                self.parry_window_timer = 0.0
                if DEBUG_PLAYER_ATTACK_PROXIMITY and _player_has_movement_keys(keys_pressed):
                    print("[PLAYER] Long attack triggered while moving (WASD held)")
                self._set_state("attack_long")
                apply_player_movement(self, keys_pressed, dt)
                self._anim_state.advance(dt)
                return

        # Ongoing parry window without a new K press: lower priority than short attack (handled above).
        if self.parry_window_timer > 0:
            self.parry_window_timer -= dt
            self._set_state("parry")
            self._anim_state.advance(dt)
            apply_player_movement(self, set(), dt)
            if DEBUG_BLOCK_PARRY_TRACE:
                print(
                    f"[BLOCK_PARRY_TRACE] Player parry (ongoing timer) -> state={self.state!r} "
                    f"parry_timer(after)={self.parry_window_timer:.4f} is_parry_active={self.is_parry_active()}"
                )
            return

        # Block (J): K-tap parry and ongoing parry handled above.
        if block_held:
            self._set_state("block")
            self._anim_state.advance(dt)
            apply_player_movement(self, set(), dt)
            return

        # Dash request (Space) — after melee so click + Space prioritizes attack
        if can_dash and dash_request:
            if not self.dash_active and getattr(self, "dash_cooldown_timer", 0) <= 0:
                dx, dy = self.velocity_xy[0], self.velocity_xy[1]
                if dx == 0 and dy == 0:
                    dx, dy = self.facing[0], self.facing[1]
                if dx == 0 and dy == 0:
                    dx = 1
                length = (dx * dx + dy * dy) ** 0.5
                self.dash_direction = (dx / length, dy / length)
                self.dash_active = True
                self.dash_timer = PLAYER_DASH_DURATION_SEC
                self._consumed_dash_request = True
                self._set_state("dash")
                apply_player_movement(self, keys_pressed, dt)
                self._anim_state.advance(dt)
                return

        # Normal movement
        apply_player_movement(self, keys_pressed, dt)
        vx, vy = self.velocity_xy[0], self.velocity_xy[1]
        if vx != 0 or vy != 0:
            self._set_facing_from_velocity(vx, vy)
            self._still_timer = 0.0
            self._set_state("walk")
        else:
            self._still_timer += dt
            # Only switch to idle after still for a short time to avoid blink/flicker
            if self._still_timer >= self._IDLE_DELAY:
                self._set_state("idle")
            # else stay in current state (e.g. walk) so animation doesn't reset every frame
        self._anim_state.advance(dt)

    def clear_short_attack_buffer(self, *, reason: str = "") -> None:
        """Clear pending short-attack buffer (e.g. on pause so no swing fires after resume)."""
        if not self._pending_short_attack:
            return
        self._pending_short_attack = False
        if DEBUG_LIVE_SHORT_ATTACK_TRACE:
            print(f"[LIVE_TRACE] clear_short_attack_buffer reason={reason!r} state={self.state!r}")
        if DEBUG_PLAYER_SHORT_ATTACK_BUFFER or DEBUG_PLAYER_ATTACK_INPUT_TRACE:
            msg = f"[BUFFER] pending cleared ({reason})" if reason else "[BUFFER] pending cleared"
            print(f"{msg} state={self.state!r}")

    # --- Combat helpers used by systems.combat --------------------------------

    @property
    def attack_multiplier(self) -> float:
        level_mult = 1.0 + PLAYER_ATTACK_LEVEL_STEP * max(0, int(self.attack_level))
        return level_mult * getattr(self, "attack_damage_mult", 1.0)

    def is_short_attack_active(self) -> bool:
        """True when short attack is in its active frames (for hitbox checks)."""
        if self.state != "attack_short":
            return False
        t = self._short_attack_timer
        return PLAYER_SHORT_ATTACK_WINDUP_SEC <= t <= PLAYER_SHORT_ATTACK_WINDUP_SEC + PLAYER_SHORT_ATTACK_ACTIVE_SEC

    def can_hit_enemy_with_short(self, enemy) -> bool:
        return id(enemy) not in self._short_attack_hit_ids

    def register_short_attack_hit(self, enemy) -> None:
        self._short_attack_hit_ids.add(id(enemy))

    def should_fire_long_attack(self) -> bool:
        """Fire long-attack hitbox once per attack_long state.

        In gameplay we want this to be very reliable, so as soon as the player
        enters the ``attack_long`` state we allow one long-strike hit. Tests
        may still choose to advance timers, but the timer is no longer required
        for the strike to occur in-game.
        """
        if self.state != "attack_long":
            return False
        if self._long_attack_fired:
            return False
        self._long_attack_fired = True
        return True

    def is_blocking(self) -> bool:
        return self.state == "block"

    def is_parry_active(self) -> bool:
        return self.parry_window_timer > 0.0

    def draw(self, screen: pygame.Surface, camera_offset: tuple[float, float]) -> None:
        self._ensure_animations_loaded()
        if self.inactive:
            return
        if DEBUG_LIVE_SHORT_ATTACK_TRACE:
            prev_live = getattr(self, "_debug_live_draw_prev", None)
            if prev_live != self.state:
                fi = getattr(self._anim_state, "current_frame_index", -1)
                print(
                    f"[LIVE_TRACE] draw render state={self.state!r} anim_key={self._current_anim_key} "
                    f"frame_idx={fi}"
                )
            self._debug_live_draw_prev = self.state
        if DEBUG_BLOCK_PARRY_TRACE and self.state in ("block", "parry"):
            prev_bp = getattr(self, "_debug_block_parry_draw_prev", None)
            if prev_bp != self.state:
                fi = getattr(self._anim_state, "current_frame_index", -1)
                print(
                    f"[BLOCK_PARRY_TRACE] draw state={self.state!r} anim_key={self._current_anim_key} "
                    f"frame_idx={fi} parry_timer={self.parry_window_timer:.4f} is_parry_active={self.is_parry_active()}"
                )
            self._debug_block_parry_draw_prev = self.state
        if DEBUG_PLAYER_ATTACK_WALK_TRACE:
            prev = getattr(self, "_debug_prev_draw_state", None)
            if prev != self.state and (
                self.state in ("attack_short", "attack_long")
                or prev in ("attack_short", "attack_long")
            ):
                fi = getattr(self._anim_state, "current_frame_index", -1)
                print(
                    f"[PLAYER] draw: state {prev!r} -> {self.state!r} "
                    f"frame_idx={fi} anim_key={self._current_anim_key}"
                )
            self._debug_prev_draw_state = self.state
        dx = self.world_pos[0] - camera_offset[0]
        dy = self.world_pos[1] - camera_offset[1]
        # Idle: always use the single visible idle frame (no blue background, no flicker).
        if self.state == "idle" and self._idle_surface is not None:
            x = int(dx) - self._idle_surface.get_width() // 2
            y = int(dy) - self._idle_surface.get_height() // 2
            screen.blit(self._idle_surface, (x, y))
            if self.damage_flash_timer > 0.0:
                intensity = min(1.0, self.damage_flash_timer / 0.15)
                alpha = int(180 * intensity)
                flash = pygame.Surface(self._idle_surface.get_size(), pygame.SRCALPHA)
                flash.fill((255, 40, 40, alpha))
                screen.blit(flash, (x, y))
            return
        surf = self._anim_state.current_surface()
        if surf is None or surf.get_width() == 0 or surf.get_height() == 0:
            # Only fallback when non-idle and no frame (use idle surface if available).
            if self._idle_surface is not None:
                x = int(dx) - self._idle_surface.get_width() // 2
                y = int(dy) - self._idle_surface.get_height() // 2
                screen.blit(self._idle_surface, (x, y))
                if self.damage_flash_timer > 0.0:
                    intensity = min(1.0, self.damage_flash_timer / 0.15)
                    alpha = int(180 * intensity)
                    flash = pygame.Surface(self._idle_surface.get_size(), pygame.SRCALPHA)
                    flash.fill((255, 40, 40, alpha))
                    screen.blit(flash, (x, y))
            return
        if self.state == "death":
            w, h = surf.get_size()
            scale = 0.6
            new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
            if new_size != (w, h):
                surf = pygame.transform.smoothscale(surf, new_size)
        x = int(dx) - surf.get_width() // 2
        y = int(dy) - surf.get_height() // 2
        screen.blit(surf, (x, y))
        if self.damage_flash_timer > 0.0:
            intensity = min(1.0, self.damage_flash_timer / 0.15)
            alpha = int(180 * intensity)
            flash = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            flash.fill((255, 40, 40, alpha))
            screen.blit(flash, (x, y))

    def trigger_hit(self) -> None:
        """Stub for Phase 4: switch to hit state and play hit animation."""
        if self.state in ("hit", "death") or self.inactive:
            return
        self._pending_short_attack = False
        self._set_state("hit")
