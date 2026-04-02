# GameScene: player, camera follow, input (WASD, dash, attacks, block/parry).

import math
import os
import random
import pygame

from game.scenes.base_scene import BaseScene
from game.config import (
    LOGICAL_W,
    LOGICAL_H,
    BACKGROUND_COLOR,
    TILE_SIZE,
    PROJECT_ROOT,
    ENEMY_MIN_X,
    ENEMY_MIN_Y,
    ENEMY_MAX_X,
    ENEMY_MAX_Y,
    ENEMY_SWARM_STOP_DISTANCE,
    ENEMY_FLANKER_STOP_DISTANCE,
    ENEMY_BRUTE_STOP_DISTANCE,
    ENEMY_HIT_ZONE_RADIUS,
    DEBUG_COMBAT_HITS,
    DEBUG_DOOR_TRIGGER,
    DEBUG_DRAW_ATTACK_RANGE,
    SPAWN_SLOT_DELAY_SEC,
    MINI_BOSS_DOOR_UNLOCK_DELAY_SEC,
    MINI_BOSS_REWARD_HEAL_PERCENT,
    SEED,
    LAVA_DAMAGE_PER_SECOND,
    SLOW_TILE_SPEED_FACTOR,
    USE_PHASE7_DUNGEON,
    BIOME3_START_INDEX,
    BIOME4_START_INDEX,
    START_ROOM_INDEX,
    SAFE_ROOM_HEAL_PERCENT,
    SAFE_ROOM_OVERHEAL_CAP_RATIO,
    HEAL_DROP_CHANCE,
    AMBUSH_SPAWN_RADIUS_PX,
    TRIANGLE_OFFSET_PX,
    BEGINNER_TEST_MODE,
    PLAYER_BASE_HP,
    PLAYER_LIVES_INITIAL,
    PLAYER_MAX_HP_BY_LIFE,
    PLAYER_RESPAWN_INVULN_SEC,
    LIFE_LOSS_TRANSITION_SEC,
    LIFE_LOSS_FADE_IN_SEC,
    BIOME4_BOSS_UI_ANCHOR_X,
    BIOME4_BOSS_UI_ANCHOR_Y,
    BIOME4_BOSS_UI_ANCHOR_W,
    BIOME4_BOSS_UI_ANCHOR_H,
    FINAL_BOSS_REWARD_HEAL_PERCENT,
    RESERVE_HEAL_USE_COOLDOWN_SEC,
    FINAL_BOSS_CONTACT_DAMAGE,
    FINAL_BOSS_CONTACT_DAMAGE_REVIVE,
    BIOME4_BOSS_TELEGRAPH_METEOR_SEC,
    FINAL_BOSS_METEOR_DAMAGE,
    FINAL_BOSS_REVIVE_MESSAGE_DURATION_SEC,
    PLAYER_MOVEMENT_HITBOX_W,
    PLAYER_MOVEMENT_HITBOX_H,
    DEBUG_TOP_EDGE,
    DEBUG_MOVEMENT_HITBOX,
    DEBUG_PLAYER_ATTACK_PROXIMITY,
    DEBUG_PLAYER_ATTACK_WALK_TRACE,
    DEBUG_LIVE_SHORT_ATTACK_TRACE,
    DEBUG_SHORT_ATTACK_INPUT,
    DEBUG_BLOCK_PARRY_TRACE,
    DEBUG_BOSS_HP_BAR,
    DEBUG_RANGED_ENEMY_LIFECYCLE,
    HEAVY_RETREAT_TOWARD_PLAYER_BLEND,
)

# Proportional enemy/boss HP bar fill (remaining HP = hp / max_hp; never inverted).
BOSS_ENEMY_HP_BAR_COLOR = (220, 40, 40)

# Player HP HUD row (must match _draw_player_health_bar layout for boss text fallback / spacing).
_PLAYER_HP_HUD_TOP_MARGIN = 14
_PLAYER_HP_BAR_H = 18
# Outlined 17–18px text is taller than the bar; row bottom uses max(bar, text) alignment.
_PLAYER_HP_HUD_TEXT_EXTENT = 26
PLAYER_HP_HUD_ROW_BOTTOM = _PLAYER_HP_HUD_TOP_MARGIN + max(_PLAYER_HP_BAR_H, _PLAYER_HP_HUD_TEXT_EXTENT)

_hp_hud_font_cache: dict[int, pygame.font.Font] = {}


def _hp_hud_font(size: int = 18) -> pygame.font.Font:
    if size not in _hp_hud_font_cache:
        try:
            _hp_hud_font_cache[size] = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", size)
        except (pygame.error, OSError):
            _hp_hud_font_cache[size] = pygame.font.SysFont("arial", max(12, size - 2))
    return _hp_hud_font_cache[size]


def _render_outlined_hud_text(
    s: str,
    font: pygame.font.Font,
    fg: tuple[int, int, int] = (255, 255, 255),
    outline: tuple[int, int, int] = (0, 0, 0),
) -> pygame.Surface:
    """Bold-looking HP readout: dark outline + bright fill."""
    main = font.render(s, True, fg)
    w, h = main.get_size()
    pad = 2
    surf = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
        t = font.render(s, True, outline)
        surf.blit(t, (pad + dx, pad + dy))
    surf.blit(main, (pad, pad))
    return surf

# Biome 3 Room 21 safe room: campaign index for upgrade panel (deterministic 3 choices, pick 1).
BIOME3_SAFE_ROOM_INDEX = 21
# Biome 4 Room 28 safe room: 4 options, choose exactly 2.
BIOME4_SAFE_ROOM_INDEX = 28
# Upgrade effects (Phase 2 safe room extension).
SAFE_ROOM_UPGRADE_HEALTH_MULT = 1.20   # +20% max HP
SAFE_ROOM_UPGRADE_SPEED_MULT = 1.10   # +10% movement speed
SAFE_ROOM_UPGRADE_ATTACK_MULT = 1.12  # +12% attack damage
SAFE_ROOM_UPGRADE_DEFENCE_MULT = 0.88  # -12% incoming damage
from entities.player import Player
from entities.swarm import Swarm
from entities.flanker import Flanker
from entities.brute import Brute
from entities.heavy import Heavy
from entities.ranged import Ranged
from entities.mini_boss import MiniBoss
from entities.mini_boss_2 import MiniBoss2
from entities.biome3_miniboss import (
    Biome3MiniBoss,
    configure_biome3_miniboss_director,
    preload_biome3_miniboss_animations,
)
from entities.final_boss import FinalBoss, preload_final_boss_animations
from entities.training_dummy import TrainingDummy
from entities import enemy_base as enemy_base_module
from entities.enemy_base import (
    enemy_min_separation,
    enemy_movement_half_extents_for_class,
    enemy_type_key_for_class,
    enemy_type_priority,
    preload_enemy_animations,
)
from systems.combat import apply_player_attacks, apply_enemy_attacks, apply_projectile_hits, DamageEvent
from systems.spawn_system import SpawnSystem
from systems.spawn_helper import (
    ensure_valid_spawn_position,
    generate_valid_spawn_position,
    spawn_spread,
    spawn_triangle,
    spawn_ambush,
)
from systems.vfx import VfxManager
from systems.movement import apply_player_movement
from systems.collisions import tile_range_for_centered_aabb
from game.asset_loader import load_image
from dungeon.room_controller import RoomController
from dungeon.room import RoomType, TILE_FLOOR, TILE_LAVA, TILE_SLOW, total_campaign_rooms
from dungeon.door_system import DoorState
from dungeon.biome2_rooms import get_biome2_spawn_specs, get_biome2_spawn_pattern
from dungeon.biome3_rooms import get_biome3_spawn_specs, get_biome3_spawn_pattern
from dungeon.biome1_rooms import get_biome1_spawn_specs
from dungeon.biome4_rooms import (
    get_biome4_spawn_specs,
    get_biome4_spawn_pattern,
    BIOME4_AMBUSH_RADIUS_PX,
    BIOME4_TRIANGLE_OFFSET_PX,
    BIOME4_FINAL_BOSS_SPAWN_DELAY_SEC,
)
from dungeon.biome4_visuals import (
    get_biome4_background,
    get_biome4_prop_placements,
    SOLID_PROP_INDICES,
    Biome4Visuals,
    load_boss_telegraph,
    load_boss_fx_teleport,
    load_boss_fx_spawn,
    load_boss_fx_death,
    load_boss_fx_image,
    load_boss_projectile,
)
from game.rng import initialize_run_seed, get_run_seed, get_variant_id
from game.phase1_seed_debug import log_run_start, log_spawn_setup
from game.ai.ai_director import AIDirector, EncounterDirectorSnapshot
from game.ai.ai_logger import AILogger
from game.ai.biome1_director_spawn import (
    adjust_biome1_spawn_specs,
    biome1_director_spawn_eligible,
    biome1_effective_heal_drop_chance,
    biome1_trial_phase_active,
)
from game.ai.biome2_director_spawn import (
    adjust_biome2_spawn_specs,
    biome2_director_spawn_eligible,
    biome2_effective_heal_drop_chance,
    biome2_safe_room_heal_multiplier,
)
from game.ai.biome3_director_spawn import (
    adjust_biome3_spawn_specs,
    apply_biome3_ranged_position_offsets,
    biome3_director_spawn_eligible,
    biome3_effective_heal_drop_chance,
    biome3_safe_room_heal_multiplier,
)
from game.ai.biome4_director_spawn import (
    adjust_biome4_spawn_specs,
    biome4_director_spawn_eligible,
    biome4_effective_heal_drop_chance,
    biome4_safe_room_heal_multiplier,
)
from game.ai.metrics_tracker import MetricsTracker
from game.debug.debug_overlay import DebugOverlay
from game.ai.player_model import PlayerModel, PlayerStateClass, build_player_model_summary

# Requirements_Analysis_Biome1.md / REBUILT: gameplay background (Room 0 / arena).
GAMEPLAY_BG_PATH = "assets/backgrounds/room0_bg.png"
# Room 0 props and UI (Biome1 §9.3, §9.4)
ALTAR_BOOK_PATH = "assets/props/altar_book.png"
ROOM0_EXIT_PROP_PATH = "assets/props/door_open.png"
INTERACT_PROMPT_BG_PATH = "assets/ui/prompts/interact_prompt_bg.png"
STORY_PANEL_PATH = "assets/ui/panels/story_panel.png"
ALTAR_INTERACTION_RADIUS_PX = 90.0
# Floor tile: use only the second user PNG (stone tile 2).
FLOOR_TILE_PATH = "assets/c__Users_maham_AppData_Roaming_Cursor_User_workspaceStorage_96d0f074b8ae6064a4aab048d1ffbd3a_images_image-887aaf8d-e0af-4fa9-af4a-8aa8e389b79c.png"
FLOOR_TILE_FALLBACK = "assets/tiles/floor/floor_tile.png"
# Room 0 prop sizes (increased for visibility)
ROOM0_ALTAR_SIZE = (120, 120)
ROOM0_EXIT_PROP_SIZE = (96, 96)
ROOM0_STORY_TEXT = (
    "Long ago, this dungeon was built to imprison what the world feared. "
    "Its gates have sealed once more—and you now stand within its depths.\n\n"
    "Four biomes lie between you and freedom. "
    "Each grows more hostile than the last, guarded by powerful champions who answer only to the dungeon itself.\n\n"
    "Every chamber will test you—combat arenas, sudden ambushes, narrow corridors, and rare sanctuaries of rest. "
    "Learn the movements of your enemies. Master your strikes and your dash. Choose your healing and upgrades wisely.\n\n"
    "At the end of the thirtieth room waits the final guardian. "
    "Only by defeating it can the gates reopen… and only then may you return to the outside world."
)

PAUSE_RESUME_BTN_PATH = "assets/ui/buttons/btn_resume.png"
# Same asset family as Controls/Settings "Back" (return to main menu).
PAUSE_MAIN_MENU_BTN_PATH = "assets/ui/buttons/btn_back.png"
PAUSE_MENU_BUTTON_W = 320
PAUSE_MENU_BUTTON_H = 96
PAUSE_MENU_BUTTON_SPACING = 16


def _pause_screen_to_logical(pos: tuple[int, int]) -> tuple[int, int]:
    """Window mouse → logical buffer (960×640), same as main menu / controls."""
    surf = pygame.display.get_surface()
    if surf is None:
        return (0, 0)
    ww, wh = surf.get_size()
    ww, wh = max(1, ww), max(1, wh)
    x, y = pos
    return (int(x * LOGICAL_W / ww), int(y * LOGICAL_H / wh))


def _pause_hover_from_normal(src: pygame.Surface) -> pygame.Surface:
    """Yellow highlight when no dedicated hover PNG (matches StartScene fallback)."""
    out = src.copy()
    overlay = pygame.Surface(out.get_size(), pygame.SRCALPHA)
    overlay.fill((255, 220, 0, 100))
    out.blit(overlay, (0, 0))
    return out


class GameScene(BaseScene):
    # Movement keys we care about (for held state)
    _MOVEMENT_KEYS = {pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d}

    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        self._camera_target_world = (LOGICAL_W / 2.0, LOGICAL_H / 2.0)
        self._run_seed: int = int(get_run_seed())
        self._variant_id: int = int(get_variant_id())
        self._player: Player | None = None
        self._enemies: list = []
        self._projectiles: list = []
        self._spawned_enemies = False  # Tracks whether initial spawn slots have been set up.
        self._dash_request = False
        self._attack_short_request = False
        self._attack_long_request = False
        self._parry_request = False  # K key just pressed (one-shot; window length = PLAYER_PARRY_WINDOW_SEC)
        # Edge-detect mouse buttons so attacks still register if MOUSEBUTTONDOWN was missed.
        self._prev_mouse_left = False
        self._prev_mouse_right = False
        # Track held keys via KEYDOWN/KEYUP so holding a key keeps moving
        self._keys_held = set()
        # Death sequence state
        self._death_phase: str | None = None  # None, "anim", "freeze", "game_over"
        self._death_timer: float = 0.0
        # Life-loss respawn: fade to black, then existing _respawn_player_in_current_room (no logic change there).
        self._is_in_life_loss_transition: bool = False
        self._life_loss_transition_timer: float = 0.0
        self._life_loss_fade_in_timer: float = 0.0
        # VFX manager (slash + hit sparks)
        self._vfx = VfxManager()
        # Phase 5: spawn system (telegraphs + portals)
        self._spawn_system: SpawnSystem | None = None
        # Phase 6: mini boss death → reward + door unlock
        self._rewards: list = []  # list of {"pos": (x,y), "collected": bool}
        self._doors_unlocked = False
        self._door_unlock_timer: float | None = None
        self._mini_boss_death_pos: tuple[float, float] | None = None
        # Phase 6: mini boss health bar frame only (fill drawn as solid rect; see draw())
        self._mini_boss_bar_frame: pygame.Surface | None = None
        # Phase 3: Final Boss (Room 29) spawn and victory
        self._final_boss_spawn_timer: float | None = None
        self._final_boss_spawned = False
        self._room_time = 0.0
        self._meteor_impacts: list = []
        self._final_boss_contact_timer = 0.0
        self._victory_phase = False
        self._victory_timer: float = 0.0
        self._boss_ui_frame: pygame.Surface | None = None
        self._boss_name_banner: pygame.Surface | None = None
        self._victory_bg: pygame.Surface | None = None
        self._victory_banner: pygame.Surface | None = None
        # Boss telegraphs and VFX (loaded by _ensure_boss_fx_loaded)
        self._boss_telegraph_attack_circle: pygame.Surface | None = None
        self._boss_telegraph_wave_line: pygame.Surface | None = None
        self._boss_telegraph_meteor_target: pygame.Surface | None = None
        self._boss_fx_teleport_frames: list = []
        self._boss_fx_teleport_flash: pygame.Surface | None = None
        self._boss_fx_teleport_smoke: pygame.Surface | None = None
        self._boss_fx_teleport_anim: list = []
        self._boss_fx_spawn_portal: pygame.Surface | None = None
        self._boss_fx_spawn_portal_anim: list = []
        self._boss_fx_spawn_explosion: pygame.Surface | None = None
        self._boss_fx_death_frames: list = []
        self._boss_fx_death_explosion: pygame.Surface | None = None
        self._boss_fx_death_energy: pygame.Surface | None = None
        self._boss_fx_death_particles: pygame.Surface | None = None
        self._boss_meteor_sprite: pygame.Surface | None = None
        self._boss_meteor_impact_sprite: pygame.Surface | None = None
        self._boss_spawn_fx_timer: float = 0.0
        self._boss_spawn_fx_pos: tuple[float, float] | None = None
        self._boss_death_fx_timer: float = 0.0
        self._boss_death_fx_pos: tuple[float, float] | None = None
        self._boss_revive_message_until: float = 0.0  # room_time when center-screen revive message hides
        self._boss_revive_message_shown: bool = False  # True once we've triggered the one-time revive message
        self._biome4_blocking_tiles: set[tuple[int, int]] = set()
        self._biome4_blocking_tiles_room: int | None = None
        self._boss_teleport_fx_frame: tuple | None = None  # (old_pos, new_pos) for one frame
        self._meteor_impact_display: list = []  # [{"x", "y", "until": room_time}]
        # Background (Requirements: room0_bg for arena / Room 0)
        self._gameplay_bg: pygame.Surface | None = None
        # Phase 7: dungeon rooms 0-7, doors, hazards
        self._room_controller: RoomController | None = None
        self._room_cleared_flag = False  # True after we called on_room_clear for this room
        # Phase 7 tile/door asset cache (Requirements paths); None = not loaded yet
        self._tile_floor: pygame.Surface | None = None
        self._tile_lava: pygame.Surface | None = None
        self._tile_slow: pygame.Surface | None = None
        self._door_open: pygame.Surface | None = None
        self._door_locked: pygame.Surface | None = None
        self._door_safe: pygame.Surface | None = None
        self._door_closed: pygame.Surface | None = None
        # Big door variants (96x96) for visuals
        self._door_open_big: pygame.Surface | None = None
        self._door_closed_big: pygame.Surface | None = None
        self._door_locked_big: pygame.Surface | None = None
        self._door_safe_big: pygame.Surface | None = None
        # Wall tiles for border (Requirements: assets/tiles/walls)
        self._wall_top: pygame.Surface | None = None
        self._wall_bottom: pygame.Surface | None = None
        self._wall_left: pygame.Surface | None = None
        self._wall_right: pygame.Surface | None = None
        self._wall_corner_tl: pygame.Surface | None = None
        self._wall_corner_tr: pygame.Surface | None = None
        self._wall_corner_bl: pygame.Surface | None = None
        self._wall_corner_br: pygame.Surface | None = None
        # Debug: show "HIT!" when player deals damage (draw for 0.5s after player_events)
        self._debug_player_hit_time: float = 0.0
        self._debug_combat_lines: list[str] = []
        self._live_trace_frame: int = 0
        self._block_parry_trace_frame: int = 0
        # Room 0 (Start): altar, dummy, exit trigger, story panel (Requirements_Analysis_Biome1 §9)
        self._room0_altar_pos: tuple[float, float] | None = None
        self._room0_exit_rect: pygame.Rect | None = None  # world rect, top-right trigger
        self._room0_story_panel_open = False
        self._room0_exit_fade_timer: float | None = None  # sec until transition to Room 1
        self._room0_prop_altar: pygame.Surface | None = None
        self._room0_prop_exit: pygame.Surface | None = None
        self._room0_prompt_bg: pygame.Surface | None = None
        self._room0_story_panel_surf: pygame.Surface | None = None
        self._metrics = MetricsTracker()
        self._metrics_pending_room_start = False
        self.player_model = PlayerModel()
        self.player_state: PlayerStateClass | None = None
        # Set True on life-loss respawn; consumed on next PlayerModel classify (then cleared).
        self._recent_life_loss_flag: bool = False
        self.ai_director = AIDirector()
        # Encounter spawn uses this snapshot only; updated in _update_player_model_after_room_end (not per-frame classify).
        self._encounter_directive_for_next_room: EncounterDirectorSnapshot = EncounterDirectorSnapshot.neutral_default()
        # File-backed logging starts in reset() with initialize_run_seed(); no file until a run begins.
        self.ai_logger = AILogger(run_seed=None)
        self._debug_overlay = DebugOverlay(self)
        # One-room hazard relief after heavy lava damage (Biome 3 / 4 director)
        self._pending_b3_hazard_relief: float = 1.0
        self._pending_b4_hazard_relief: float = 1.0
        # In-run pause overlay (not StartScene); ESC toggles; Resume + Main Menu (logical rects).
        self._paused: bool = False
        self._pause_resume_normal: pygame.Surface | None = None
        self._pause_resume_hover: pygame.Surface | None = None
        self._pause_resume_rect: pygame.Rect | None = None
        self._pause_resume_hovered: bool = False
        self._pause_resume_hover_prev: bool = False
        self._pause_main_normal: pygame.Surface | None = None
        self._pause_main_hover: pygame.Surface | None = None
        self._pause_main_rect: pygame.Rect | None = None
        self._pause_main_hovered: bool = False
        self._pause_main_hover_prev: bool = False
        self._pause_paused_font: pygame.font.Font | None = None
        self._boss_hp_bar_dbg_t = 0.0

    def _iter_door_groups(self, doors: list) -> list[tuple[object, int, int]]:
        """Group vertical 2-tile doors by (tile_x, tile_y). Returns (door, top_ty, bottom_ty)."""
        ordered = sorted(doors, key=lambda d: (int(d.tile_x), int(d.tile_y)))
        i = 0
        groups: list[tuple[object, int, int]] = []
        while i < len(ordered):
            d = ordered[i]
            tx = int(d.tile_x)
            ty = int(d.tile_y)
            top_ty = ty
            bottom_ty = ty
            if i + 1 < len(ordered):
                n = ordered[i + 1]
                if int(n.tile_x) == tx and n.target_room_index == d.target_room_index and int(n.tile_y) == ty + 1:
                    bottom_ty = int(n.tile_y)
                    i += 2
                    groups.append((d, top_ty, bottom_ty))
                    continue
            groups.append((d, top_ty, bottom_ty))
            i += 1
        return groups

    def _iter_doorways(self, doors: list, room) -> list[tuple[float, float, int, object, bool]]:
        """One entry per logical doorway (2×2 gap). Returns (center_x, center_y, target_room_index, state, is_safe_door)."""
        if not doors or room is None:
            return []
        by_target: dict[int, list] = {}
        for d in doors:
            t = d.target_room_index
            if t not in by_target:
                by_target[t] = []
            by_target[t].append(d)
        out = []
        for target_room_index, group in by_target.items():
            txs = [int(d.tile_x) for d in group]
            tys = [int(d.tile_y) for d in group]
            min_tx, max_tx = min(txs), max(txs)
            min_ty, max_ty = min(tys), max(tys)
            center_x = (min_tx + max_tx + 1) / 2.0 * TILE_SIZE
            center_y = (min_ty + max_ty + 1) / 2.0 * TILE_SIZE
            d0 = group[0]
            out.append((center_x, center_y, target_room_index, d0.state, d0.is_safe_door))
        return out

    def reset(self) -> None:
        """Reset player, enemies, and input so GameScene can be reused after death."""
        # Seed determinism: one run seed generated at run start.
        run_seed = initialize_run_seed()
        self._run_seed = int(run_seed)
        self._variant_id = int(get_variant_id())
        self._metrics.start_run(run_seed)
        self._metrics_pending_room_start = True
        self.player_state = None
        self._recent_life_loss_flag = False
        self._encounter_directive_for_next_room = EncounterDirectorSnapshot.neutral_default()
        self.ai_logger = AILogger(run_seed=int(run_seed))
        log_run_start(run_seed)
        self._camera_target_world = (LOGICAL_W / 2.0, LOGICAL_H / 2.0)
        self._player = None
        self._enemies = []
        self._projectiles = []
        self._spawned_enemies = False
        self._dash_request = False
        self._attack_short_request = False
        self._attack_long_request = False
        self._parry_request = False
        try:
            _mb = pygame.mouse.get_pressed(3)
            self._prev_mouse_left = bool(_mb[0])
            self._prev_mouse_right = bool(_mb[2])
        except pygame.error:
            self._prev_mouse_left = False
            self._prev_mouse_right = False
        self._keys_held.clear()
        self._death_phase = None
        self._death_timer = 0.0
        self._is_in_life_loss_transition = False
        self._life_loss_transition_timer = 0.0
        self._life_loss_fade_in_timer = 0.0
        self._vfx = VfxManager()
        self._spawn_system = None
        self._rewards = []
        self._doors_unlocked = False
        self._door_unlock_timer = None
        self._final_boss_spawn_timer = None
        self._final_boss_spawned = False
        self._room_time = 0.0
        self._meteor_impacts = []
        self._meteor_impact_display = []
        self._final_boss_contact_timer = 0.0
        self._boss_spawn_fx_timer = 0.0
        self._boss_spawn_fx_pos = None
        self._boss_revive_message_until = 0.0
        self._boss_revive_message_shown = False
        self._boss_death_fx_timer = 0.0
        self._boss_death_fx_pos = None
        self._boss_teleport_fx_frame = None
        self._victory_phase = False
        self._victory_timer = 0.0
        self._mini_boss_death_pos = None
        self._mini_boss_bar_frame = None
        self._gameplay_bg = None
        self._room_controller = None
        self._room_cleared_flag = False
        self._room0_story_panel_open = False
        self._room0_exit_fade_timer = None
        self._room0_altar_pos = None
        self._room0_exit_rect = None
        self._tile_floor = None
        self._tile_floor_2 = None
        self._tile_lava = None
        self._tile_slow = None
        self._door_open = None
        self._door_locked = None
        self._door_safe = None
        self._safe_room_heal_done = False
        self._safe_room_upgrade_pending = False
        self._heal_drop_rolled_this_room = False
        # Safe Room heal object: one per Safe Room, position set when entering; cleared on room leave
        self._safe_room_heal_pos: tuple[float, float] | None = None
        self._near_safe_room_heal = False
        self._heal_flash_timer: float = 0.0
        # Biome 3 Room 21 safe room: 3 upgrade choices, player picks 1 (deterministic order 1=Health, 2=Speed, 3=Attack).
        self._safe_room_upgrade_chosen_this_room = False
        self._safe_room_upgrade_icon_health: pygame.Surface | None = None
        self._safe_room_upgrade_icon_speed: pygame.Surface | None = None
        self._safe_room_upgrade_icon_attack: pygame.Surface | None = None
        self._safe_room_upgrade_icon_defence: pygame.Surface | None = None
        # Biome 4 safe room: 4 options, choose 2.
        self._safe_room_biome4_picks_remaining = 0
        self._safe_room_biome4_chosen: set[int] = set()
        self._paused = False
        self._pause_resume_hover_prev = False
        self._pause_main_hover_prev = False
        self._pause_main_hovered = False
        self._boss_hp_bar_dbg_t = 0.0

    def _layout_pause_menu_buttons(self) -> None:
        """Stack Resume (top) and Main Menu below; logical coords; same sizes as main menu buttons."""
        if self._pause_resume_normal is None or self._pause_main_normal is None:
            return
        cx = LOGICAL_W // 2
        top_y = 80
        self._pause_resume_rect = self._pause_resume_normal.get_rect(
            center=(cx, top_y + PAUSE_MENU_BUTTON_H // 2)
        )
        row2_top = top_y + PAUSE_MENU_BUTTON_H + PAUSE_MENU_BUTTON_SPACING
        self._pause_main_rect = self._pause_main_normal.get_rect(
            center=(cx, row2_top + PAUSE_MENU_BUTTON_H // 2)
        )
        print(
            f"[PAUSE] layout Resume rect={self._pause_resume_rect} "
            f"Main Menu rect={self._pause_main_rect}"
        )

    def _ensure_pause_menu_assets(self) -> None:
        if self._pause_resume_normal is not None and self._pause_main_normal is not None:
            return
        if self._pause_resume_normal is None:
            self._pause_resume_normal = load_image(
                PAUSE_RESUME_BTN_PATH,
                size=(PAUSE_MENU_BUTTON_W, PAUSE_MENU_BUTTON_H),
                use_colorkey=True,
                colorkey_color=(255, 255, 255),
                near_white_threshold=0,
                corner_bg_tolerance=50,
                exact_size=True,
            )
            self._pause_resume_hover = _pause_hover_from_normal(self._pause_resume_normal)
        if self._pause_main_normal is None:
            self._pause_main_normal = load_image(
                PAUSE_MAIN_MENU_BTN_PATH,
                size=(PAUSE_MENU_BUTTON_W, PAUSE_MENU_BUTTON_H),
                use_colorkey=True,
                colorkey_color=(255, 255, 255),
                near_white_threshold=0,
                corner_bg_tolerance=50,
                exact_size=True,
            )
            self._pause_main_hover = _pause_hover_from_normal(self._pause_main_normal)
        self._layout_pause_menu_buttons()

    def _update_pause_hover(self) -> None:
        if self._pause_resume_rect is None and self._pause_main_rect is None:
            return
        logical = _pause_screen_to_logical(pygame.mouse.get_pos())
        if self._pause_resume_rect is not None:
            self._pause_resume_hovered = self._pause_resume_rect.collidepoint(logical)
            if self._pause_resume_hovered and not self._pause_resume_hover_prev:
                print("[PAUSE] Resume button hovered")
            self._pause_resume_hover_prev = self._pause_resume_hovered
        if self._pause_main_rect is not None:
            self._pause_main_hovered = self._pause_main_rect.collidepoint(logical)
            if self._pause_main_hovered and not self._pause_main_hover_prev:
                print("[PAUSE] Main Menu button hovered")
            self._pause_main_hover_prev = self._pause_main_hovered

    def _go_to_main_menu_from_pause(self) -> None:
        """Leave run UI; switch to StartScene. Next Play calls reset() — do not reset here (avoids extra seed log)."""
        self._paused = False
        print("[PAUSE] Main Menu clicked -> scene_manager.switch_to_start() (startup main menu)")
        self.scene_manager.switch_to_start()

    def _set_paused(self, value: bool, *, reason: str = "") -> None:
        if self._paused == value:
            return
        self._paused = value
        print(f"[PAUSE] paused_state={self._paused}" + (f" ({reason})" if reason else ""))
        if value:
            self._pause_resume_hover_prev = False
            self._pause_main_hover_prev = False
            self._ensure_pause_menu_assets()
            if self._player is not None:
                self._player.clear_short_attack_buffer(reason="pause")

    def _player_hp_percent(self) -> float:
        p = self._player
        if p is None:
            return 100.0
        mx = float(getattr(p, "max_hp", 1.0))
        if mx <= 0:
            return 100.0
        return 100.0 * float(p.hp) / mx

    def _respawn_player_in_current_room(self) -> None:
        """Lose one life; apply next life tier max HP; spawn at room entry; brief invulnerability."""
        p = self._player
        room = self._room_controller.current_room if self._room_controller is not None else None
        if p is None or room is None:
            return
        p.lives = max(0, int(getattr(p, "lives", 1)) - 1)
        p.life_index = int(getattr(p, "life_index", 0)) + 1
        idx = min(p.life_index, len(PLAYER_MAX_HP_BY_LIFE) - 1)
        cap = float(PLAYER_MAX_HP_BY_LIFE[idx])
        p.base_max_hp = cap
        p.max_hp = cap
        p.hp = cap
        p.clear_reserve_heals()
        p.invulnerable_timer = float(PLAYER_RESPAWN_INVULN_SEC)
        p.velocity_xy = (0.0, 0.0)
        p.dash_active = False
        p.dash_timer = 0.0
        p.dash_cooldown_timer = 0.0
        p.inactive = False
        p._pending_short_attack = False
        p._set_state("idle")
        stx, sty = room.spawn_tile
        wx, wy = room.world_pos_for_tile(stx, sty)
        p.world_pos = (wx, wy)
        self._recent_life_loss_flag = True
        self._classify_player_model_from_current_run()

    def _classify_player_model_from_current_run(self) -> None:
        """Build summary from metrics + player life_index / recent life loss; update player_state and AI Director."""
        if self._player is None:
            return
        summary = build_player_model_summary(
            self._metrics.run,
            hp_percent_current=self._player_hp_percent(),
            life_index=int(getattr(self._player, "life_index", 0)),
            recent_life_loss_flag=self._recent_life_loss_flag,
        )
        self.player_state = self.player_model.classify(summary).player_state
        self.ai_director.update(self.player_state)
        self._recent_life_loss_flag = False

    def _handle_player_hp_zero(self) -> str | None:
        """If HP <= 0: start life-loss transition or respawn-after-timer, else game over. Returns \"game_over\" or None."""
        p = self._player
        if p is None or self._death_phase is not None:
            return None
        if p.hp > 0:
            return None
        if int(getattr(p, "lives", 1)) > 1:
            if self._is_in_life_loss_transition:
                return None
            self._is_in_life_loss_transition = True
            self._life_loss_transition_timer = float(LIFE_LOSS_TRANSITION_SEC)
            self._life_loss_fade_in_timer = 0.0
            return None
        if self._metrics.run.room_active_flag:
            self._metrics.record_player_hp_percent(self._player_hp_percent())
        p.clear_reserve_heals()
        self._death_phase = "anim"
        self._death_timer = 0.0
        self._metrics.record_death()
        for enemy in self._enemies:
            if hasattr(enemy, "on_player_death_start"):
                enemy.on_player_death_start(p)
        return "game_over"

    def _tick_life_loss_transition(self, dt: float) -> None:
        """Count down fade-to-black; then run existing respawn. Fade-in timer is visual-only."""
        if self._life_loss_fade_in_timer > 0.0:
            self._life_loss_fade_in_timer = max(0.0, self._life_loss_fade_in_timer - dt)
        if not self._is_in_life_loss_transition:
            return
        self._life_loss_transition_timer -= dt
        if self._life_loss_transition_timer <= 0.0:
            self._is_in_life_loss_transition = False
            self._respawn_player_in_current_room()
            self._life_loss_fade_in_timer = float(LIFE_LOSS_FADE_IN_SEC)

    def _draw_life_loss_overlay(self, screen: pygame.Surface) -> None:
        """Fade to black during life-loss wait; fade back in after respawn."""
        alpha: int | None = None
        if self._is_in_life_loss_transition:
            dur = float(LIFE_LOSS_TRANSITION_SEC)
            if dur <= 0:
                t = 1.0
            else:
                t = max(0.0, min(1.0, 1.0 - (self._life_loss_transition_timer / dur)))
            alpha = int(min(240, 255 * t))
        elif self._life_loss_fade_in_timer > 0.0:
            dur = float(LIFE_LOSS_FADE_IN_SEC)
            if dur <= 0:
                t = 0.0
            else:
                t = max(0.0, min(1.0, self._life_loss_fade_in_timer / dur))
            alpha = int(255 * t)
        if alpha is None or alpha <= 0:
            return
        overlay = pygame.Surface((LOGICAL_W, LOGICAL_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, min(255, alpha)))
        screen.blit(overlay, (0, 0))

    def _final_boss_director_kwargs(self) -> dict:
        """Small deterministic tuning from AI Director boss_pressure (does not change attack types)."""
        bp = self._encounter_directive_for_next_room.boss_pressure
        if bp == "low":
            return {
                "ai_telegraph_mult": 1.12,
                "ai_cooldown_mult": 1.1,
                "ai_recovery_mult": 1.08,
                "ai_post_revive_delay_sec": 1.5,
            }
        if bp == "high":
            return {
                "ai_telegraph_mult": 0.9,
                "ai_cooldown_mult": 0.94,
                "ai_recovery_mult": 0.92,
                "ai_post_revive_delay_sec": 0.0,
            }
        return {
            "ai_telegraph_mult": 1.0,
            "ai_cooldown_mult": 1.0,
            "ai_recovery_mult": 1.0,
            "ai_post_revive_delay_sec": 0.0,
        }

    def _update_player_model_after_room_end(self) -> None:
        """After MetricsTracker.end_room; does not touch gameplay."""
        self._classify_player_model_from_current_run()
        # Freeze director outputs for the *next* room's spawns (current room already populated or done).
        self._encounter_directive_for_next_room = self.ai_director.capture_encounter_snapshot()
        # Heavy hazard damage in Biome 3/4 → one-room relief factor on next encounter (spawn tuning / debug).
        hist = getattr(self._metrics.run, "room_history", None)
        if hist:
            last_rm = hist[-1]
            hl = float(getattr(last_rm, "damage_taken_by_enemy_type", {}).get("hazard_lava", 0.0))
            bio = int(getattr(last_rm, "current_biome_index", 0))
            if bio == 3 and hl >= 22.0:
                self._pending_b3_hazard_relief = 0.88
            if bio == 4 and hl >= 22.0:
                self._pending_b4_hazard_relief = 0.88
        run = self._metrics.run
        rr = run.room_result
        room_result_s = rr.value if hasattr(rr, "value") else str(rr)
        ps = self.player_state.name if self.player_state is not None else None
        self.ai_logger.log_room(
            {
                "seed": int(run.run_seed),
                "room_index": int(run.current_room_index),
                "biome_index": int(run.current_biome_index),
                "player_state": ps,
                "difficulty_modifier": float(self.ai_director.difficulty_modifier),
                "enemy_adjustment": int(self.ai_director.effective_enemy_adjustment()),
                "reinforcement_chance": float(self.ai_director.reinforcement_chance),
                "room_result": room_result_s,
                "hp_end": float(run.hp_percent_end_room),
                "damage_taken": float(run.damage_taken_in_room),
                "hp_percent_start_room": float(run.hp_percent_start_room),
                "min_hp_during_room": float(run.min_hp_during_room),
                "max_hp_during_room": float(run.max_hp_during_room),
                "hp_lost_in_room": float(run.hp_lost_in_room),
            }
        )

    def get_player_state(self):
        return self.player_state

    def _ensure_room(self) -> None:
        """Phase 7: ensure room controller exists when USE_PHASE7_DUNGEON; else leave None (single arena)."""
        if not USE_PHASE7_DUNGEON:
            return
        if self._room_controller is None:
            seed_now = int(get_run_seed())
            self._room_controller = RoomController(seed_now)
            self._room_controller.load_room(START_ROOM_INDEX)
            self._room_cleared_flag = False
            self._metrics_pending_room_start = True
            room0 = self._room_controller.current_room
            if room0 is not None and room0.room_type == RoomType.FINAL_BOSS:
                self._final_boss_spawn_timer = BIOME4_FINAL_BOSS_SPAWN_DELAY_SEC
                self._final_boss_spawned = False
                self._room_time = 0.0
                preload_final_boss_animations()
                preload_enemy_animations("swarm")
                preload_enemy_animations("flanker")
            self._setup_room0_props_and_dummy()

    def _setup_room0_props_and_dummy(self) -> None:
        """Requirements_Analysis_Biome1 §9: Room 0 altar (center), dummy (bottom-left), exit trigger (top-right)."""
        if self._room_controller is None or self._room_controller.current_room_index != 0:
            return
        room = self._room_controller.current_room
        if room is None:
            return
        # Center = altar; bottom-left = dummy (inside playable, ≥2 tiles from wall border)
        cx, cy = room.width // 2, room.height // 2
        self._room0_altar_pos = room.world_pos_for_tile(cx, cy)
        b = room.wall_border()
        min_col = b + 2
        max_col = room.width - b - 3
        min_row = b + 2
        max_row = room.height - b - 3
        dummy_tx = min_col
        dummy_ty = max_row
        dummy_wx, dummy_wy = room.world_pos_for_tile(dummy_tx, dummy_ty)
        # Exit trigger: aligned to top-right corner of room (Requirements: exit at corner)
        trigger_w = 3 * TILE_SIZE
        trigger_h = 3 * TILE_SIZE
        self._room0_exit_rect = pygame.Rect(
            int(room.pixel_width - trigger_w),
            0,
            int(trigger_w),
            int(trigger_h),
        )
        # Single training dummy in Room 0
        if not any(getattr(e, "is_training_dummy", False) for e in self._enemies):
            self._enemies.append(TrainingDummy((dummy_wx, dummy_wy)))

    def _ensure_player(self) -> None:
        if self._player is None:
            self._player = Player()
            # Guarantee 100% HP on new run
            base_hp = float(PLAYER_BASE_HP)
            self._player.hp = base_hp
            self._player.base_max_hp = base_hp
            self._player.max_hp = base_hp
            if self._room_controller is not None and self._room_controller.current_room is not None:
                room = self._room_controller.current_room
                wx, wy = room.world_pos_for_tile(room.spawn_tile[0], room.spawn_tile[1])
                self._player.world_pos = (wx, wy)
                # Re-apply full HP after spawn so nothing (e.g. one frame of logic) can leave player below 100%
                if room.room_type == RoomType.START:
                    self._player.hp = base_hp
                    self._player.base_max_hp = base_hp
                    self._player.max_hp = base_hp

    def _ensure_spawn_system(self) -> None:
        """Setup initial Phase 5 spawn slots (telegraph + portal) once per scene."""
        if self._spawned_enemies or self._player is None:
            return
        self._spawned_enemies = True

        room = self._room_controller.current_room if self._room_controller else None
        if room is not None:
            # Frozen at last room-end classify; not live ai_director (per-frame classify must not rebalance this room).
            enc = self._encounter_directive_for_next_room
            # Per-slot spawn clamp uses enemy class + room in SpawnSystem.update (no generic half-max).
            self._spawn_system = SpawnSystem(self._vfx, room_bounds=None)
            b2_spawn_mods: dict[str, float] = {}
            b3_spawn_mods: dict[str, float] = {}
            b4_spawn_mods: dict[str, float] = {}
            stx, sty = room.spawn_tile
            rtype = room.room_type
            room_idx = self._room_controller.current_room_index

            # Door positions (world center) for spawn safe-distance checks
            doors = list(self._room_controller.door_system.doors())
            door_positions: list[tuple[float, float]] = []
            for d, top_ty, bottom_ty in self._iter_door_groups(doors):
                center_y = (top_ty + bottom_ty + 1) * TILE_SIZE / 2.0
                door_positions.append((d.world_x, center_y))
            player_center = room.world_pos_for_tile(room.spawn_tile[0], room.spawn_tile[1])
            active_seed = int(get_run_seed())
            rng = random.Random(active_seed + room.room_index * 10000)

            # Spawn specs: (enemy_cls, elite, start_time_sec, telegraph_sec or None)
            spawn_specs: list[tuple] = []
            if room_idx >= BIOME4_START_INDEX:  # Biome 4 rooms 24-29; Room 29 FINAL_BOSS metadata only
                spawn_specs = get_biome4_spawn_specs(
                    room_idx - BIOME4_START_INDEX,
                    rtype,
                    Swarm,
                    Flanker,
                    Brute,
                    Heavy,
                    Ranged,
                    seed=active_seed,
                )
                b4b = int(getattr(room, "biome_index", 1))
                if biome4_director_spawn_eligible(
                    room_idx=room_idx,
                    biome_index=b4b,
                    room_type=rtype,
                    beginner_test_mode=BEGINNER_TEST_MODE,
                ):
                    hte4 = float(enc.hazard_tune_factor_b4) * float(self._pending_b4_hazard_relief)
                    spawn_specs, b4_spawn_mods = adjust_biome4_spawn_specs(
                        spawn_specs,
                        room_type=rtype,
                        room_idx=room_idx,
                        biome_index=b4b,
                        difficulty_modifier=enc.difficulty_modifier,
                        enemy_adjustment=enc.enemy_adjustment,
                        reinforcement_chance_b4=enc.reinforcement_chance_b4,
                        pressure_level=enc.pressure_level,
                        composition_bias_b4=enc.composition_bias_b4,
                        pacing_bias=enc.pacing_bias,
                        player_state_name=enc.last_player_state_name,
                        hazard_tune_factor=hte4,
                        Swarm=Swarm,
                        Flanker=Flanker,
                        Brute=Brute,
                        Heavy=Heavy,
                        Ranged=Ranged,
                    )
                    self._pending_b4_hazard_relief = 1.0
            elif room_idx >= BIOME3_START_INDEX:  # Biome 3 rooms 16-23; Room 23 uses Biome3MiniBoss
                configure_biome3_miniboss_director(fireball_cd_mult=1.0, fireball_telegraph_mult=1.0)
                if room_idx == 23 and rtype == RoomType.MINI_BOSS:
                    psn_b3 = enc.last_player_state_name
                    if psn_b3 == "STRUGGLING":
                        configure_biome3_miniboss_director(fireball_cd_mult=1.15, fireball_telegraph_mult=1.12)
                    elif psn_b3 == "DOMINATING":
                        configure_biome3_miniboss_director(fireball_cd_mult=0.9, fireball_telegraph_mult=0.94)
                spawn_specs = get_biome3_spawn_specs(
                    room_idx - BIOME3_START_INDEX,
                    rtype,
                    Swarm,
                    Flanker,
                    Brute,
                    Heavy,
                    Ranged,
                    Biome3MiniBoss,
                    seed=active_seed,
                )
                # Preload boss and add-enemy assets when this room will spawn Biome3MiniBoss to avoid stall on spawn and when boss calls for help.
                if any(s[0] is Biome3MiniBoss for s in spawn_specs):
                    preload_biome3_miniboss_animations()
                    preload_enemy_animations("swarm")
                    preload_enemy_animations("flanker")
                b3b = int(getattr(room, "biome_index", 1))
                if biome3_director_spawn_eligible(
                    room_idx=room_idx,
                    biome_index=b3b,
                    room_type=rtype,
                    beginner_test_mode=BEGINNER_TEST_MODE,
                ):
                    hte3 = float(enc.hazard_tune_factor_b3) * float(self._pending_b3_hazard_relief)
                    spawn_specs, b3_spawn_mods = adjust_biome3_spawn_specs(
                        spawn_specs,
                        room_type=rtype,
                        room_idx=room_idx,
                        biome_index=b3b,
                        difficulty_modifier=enc.difficulty_modifier,
                        enemy_adjustment=enc.enemy_adjustment,
                        reinforcement_chance_b3=enc.reinforcement_chance_b3,
                        pressure_level=enc.pressure_level,
                        composition_bias_b3=enc.composition_bias_b3,
                        ranged_bias_b3=enc.ranged_bias_b3,
                        player_state_name=enc.last_player_state_name,
                        hazard_tune_factor=hte3,
                        Swarm=Swarm,
                        Flanker=Flanker,
                        Brute=Brute,
                        Heavy=Heavy,
                        Ranged=Ranged,
                    )
                    self._pending_b3_hazard_relief = 1.0
            elif room_idx >= 8:  # Biome 2 rooms (campaign indices 8-15) use MiniBoss2
                spawn_specs = get_biome2_spawn_specs(
                    room_idx - 8, rtype, Swarm, Flanker, Brute, Heavy, MiniBoss2, seed=active_seed
                )
                b2b = int(getattr(room, "biome_index", 1))
                if biome2_director_spawn_eligible(
                    room_idx=room_idx,
                    biome_index=b2b,
                    room_type=rtype,
                    beginner_test_mode=BEGINNER_TEST_MODE,
                ):
                    spawn_specs, b2_spawn_mods = adjust_biome2_spawn_specs(
                        spawn_specs,
                        room_type=rtype,
                        room_idx=room_idx,
                        biome_index=b2b,
                        difficulty_modifier=enc.difficulty_modifier,
                        enemy_adjustment=enc.enemy_adjustment,
                        reinforcement_chance_b2=enc.reinforcement_chance_b2,
                        pressure_level=enc.pressure_level,
                        composition_bias_b2=enc.composition_bias_b2,
                        player_state_name=enc.last_player_state_name,
                        Swarm=Swarm,
                        Flanker=Flanker,
                        Brute=Brute,
                        Heavy=Heavy,
                    )
            elif BEGINNER_TEST_MODE:
                if room_idx == 0 or rtype in (RoomType.START, RoomType.SAFE):
                    pass
                elif room_idx == 1:
                    spawn_specs = [(Swarm, False, 0.0, None)]
                elif room_idx == 2:
                    spawn_specs = [
                        (Swarm, False, 0.0, None),
                        (Swarm, False, SPAWN_SLOT_DELAY_SEC, None),
                        (Flanker, False, SPAWN_SLOT_DELAY_SEC * 2, None),
                    ]
                elif room_idx == 4:
                    spawn_specs = [
                        (Swarm, False, 0.0, None),
                        (Swarm, False, SPAWN_SLOT_DELAY_SEC, None),
                        (Flanker, False, SPAWN_SLOT_DELAY_SEC * 2, None),
                    ]
                elif room_idx == 5:
                    spawn_specs = [(Brute, True, 0.0, None), (Swarm, False, SPAWN_SLOT_DELAY_SEC, None)]
                elif room_idx == 6:
                    spawn_specs = [
                        (Swarm, False, 0.0, 1.5),
                        (Swarm, False, SPAWN_SLOT_DELAY_SEC, 1.5),
                    ]
                elif room_idx == 7:
                    spawn_specs = [(MiniBoss, False, 2.0, None)]
            elif rtype in (RoomType.START, RoomType.SAFE):
                pass
            else:
                spawn_specs = get_biome1_spawn_specs(
                    room_idx, rtype, Swarm, Flanker, Brute, MiniBoss, seed=active_seed
                )
                bidx = int(getattr(room, "biome_index", 1))
                if biome1_director_spawn_eligible(
                    room_idx=room_idx,
                    biome_index=bidx,
                    room_type=rtype,
                    beginner_test_mode=BEGINNER_TEST_MODE,
                ):
                    if biome1_trial_phase_active(room_idx, bidx):
                        spawn_specs = adjust_biome1_spawn_specs(
                            spawn_specs,
                            room_type=rtype,
                            room_idx=room_idx,
                            biome_index=bidx,
                            difficulty_modifier=1.0,
                            enemy_adjustment=0,
                            reinforcement_chance=0.0,
                            composition_bias="normal",
                            Swarm=Swarm,
                            Flanker=Flanker,
                            Brute=Brute,
                        )
                    else:
                        spawn_specs = adjust_biome1_spawn_specs(
                            spawn_specs,
                            room_type=rtype,
                            room_idx=room_idx,
                            biome_index=bidx,
                            difficulty_modifier=enc.difficulty_modifier,
                            enemy_adjustment=enc.enemy_adjustment,
                            reinforcement_chance=enc.reinforcement_chance,
                            composition_bias=enc.composition_bias,
                            Swarm=Swarm,
                            Flanker=Flanker,
                            Brute=Brute,
                        )

            # Advanced spawn: spread / triangle / ambush by room type; world_pos per slot.
            # Movement clamp / spawn acceptance use same per-class body as in-game movement.
            spawn_move_et = enemy_type_key_for_class(spawn_specs[0][0]) if spawn_specs else "swarm"
            positions_world: list[tuple[float, float]] = []
            if room_idx >= BIOME4_START_INDEX:  # Biome 4 rooms
                pattern = get_biome4_spawn_pattern(rtype)
                b4_amb = b4_spawn_mods.get("ambush_radius_px")
                b4_tri = b4_spawn_mods.get("triangle_offset_px")
                if pattern == "triangle":
                    positions_world = spawn_triangle(
                        room, player_center, is_elite=True, rng=rng, door_positions=door_positions,
                        offset_px=b4_tri if b4_tri is not None else BIOME4_TRIANGLE_OFFSET_PX,
                        enemy_type=spawn_move_et,
                    )
                elif pattern == "ambush":
                    positions_world = spawn_ambush(
                        room, player_center, len(spawn_specs), rng=rng,
                        radius_px=b4_amb if b4_amb is not None else BIOME4_AMBUSH_RADIUS_PX,
                        enemy_type=spawn_move_et,
                    )
                elif pattern == "spread":
                    positions_world = spawn_spread(
                        room, player_center, len(spawn_specs),
                        is_elite=(rtype == RoomType.ELITE),
                        rng=rng, door_positions=door_positions,
                        enemy_type=spawn_move_et,
                    )
                else:
                    positions_world = []
            elif room_idx >= BIOME3_START_INDEX:  # Biome 3 rooms
                pattern = get_biome3_spawn_pattern(rtype)
                b3_amb = b3_spawn_mods.get("ambush_radius_px")
                b3_tri = b3_spawn_mods.get("triangle_offset_px")
                if pattern == "triangle":
                    positions_world = spawn_triangle(
                        room,
                        player_center,
                        is_elite=True,
                        rng=rng,
                        door_positions=door_positions,
                        offset_px=b3_tri if b3_tri is not None else TRIANGLE_OFFSET_PX,
                        enemy_type=spawn_move_et,
                    )
                elif pattern == "ambush":
                    positions_world = spawn_ambush(
                        room,
                        player_center,
                        len(spawn_specs),
                        rng=rng,
                        radius_px=b3_amb if b3_amb is not None else AMBUSH_SPAWN_RADIUS_PX,
                        enemy_type=spawn_move_et,
                    )
                elif pattern == "single":
                    if len(spawn_specs) == 1:
                        # Spawn boss at a valid position at least MIN_DISTANCE_FROM_PLAYER_PX from player
                        # so the boss has room to move toward the player (avoids boss stuck at center)
                        xy = generate_valid_spawn_position(
                            room, player_center, [], is_elite=False, rng=rng, enemy_type=spawn_move_et
                        )
                        positions_world = [xy]
                    else:
                        positions_world = []
                        for i in range(len(spawn_specs)):
                            xy = generate_valid_spawn_position(
                                room,
                                player_center,
                                positions_world,
                                is_elite=False,
                                rng=rng,
                                enemy_type=enemy_type_key_for_class(spawn_specs[i][0]),
                            )
                            positions_world.append(xy)
                elif pattern == "spread":
                    positions_world = spawn_spread(
                        room, player_center, len(spawn_specs),
                        is_elite=(rtype == RoomType.ELITE),
                        rng=rng, door_positions=door_positions,
                        enemy_type=spawn_move_et,
                    )
                b3b_chk = int(getattr(room, "biome_index", 1))
                if (
                    b3_spawn_mods
                    and biome3_director_spawn_eligible(
                        room_idx=room_idx,
                        biome_index=b3b_chk,
                        room_type=rtype,
                        beginner_test_mode=BEGINNER_TEST_MODE,
                    )
                    and positions_world
                ):
                    apply_biome3_ranged_position_offsets(
                        positions_world,
                        spawn_specs,
                        player_center,
                        enc.ranged_bias_b3,
                    )
            elif room_idx >= 8:  # Biome 2 rooms
                pattern = get_biome2_spawn_pattern(rtype)
                amb_r = b2_spawn_mods.get("ambush_radius_px")
                tri_o = b2_spawn_mods.get("triangle_offset_px")
                if pattern == "triangle":
                    positions_world = spawn_triangle(
                        room,
                        player_center,
                        is_elite=True,
                        rng=rng,
                        door_positions=door_positions,
                        offset_px=tri_o if tri_o is not None else TRIANGLE_OFFSET_PX,
                        enemy_type=spawn_move_et,
                    )
                elif pattern == "ambush":
                    positions_world = spawn_ambush(
                        room,
                        player_center,
                        len(spawn_specs),
                        rng=rng,
                        radius_px=amb_r if amb_r is not None else AMBUSH_SPAWN_RADIUS_PX,
                        enemy_type=spawn_move_et,
                    )
                elif pattern == "single":
                    if len(spawn_specs) == 1:
                        xy = generate_valid_spawn_position(
                            room, player_center, [], is_elite=False, rng=rng, enemy_type=spawn_move_et
                        )
                        positions_world = [xy]
                    else:
                        # Biome 2 mini boss with adds: one position per spawn (mini boss + adds)
                        positions_world = []
                        for i in range(len(spawn_specs)):
                            xy = generate_valid_spawn_position(
                                room,
                                player_center,
                                positions_world,
                                is_elite=False,
                                rng=rng,
                                enemy_type=enemy_type_key_for_class(spawn_specs[i][0]),
                            )
                            positions_world.append(xy)
                elif pattern == "spread":
                    positions_world = spawn_spread(
                        room, player_center, len(spawn_specs),
                        is_elite=(rtype == RoomType.ELITE),
                        rng=rng, door_positions=door_positions,
                        enemy_type=spawn_move_et,
                    )
            elif not spawn_specs:
                pass
            elif rtype == RoomType.ELITE:
                positions_world = spawn_triangle(
                    room, player_center, is_elite=True, rng=rng, door_positions=door_positions,
                    enemy_type=spawn_move_et,
                )
            elif rtype == RoomType.AMBUSH:
                positions_world = spawn_ambush(
                    room, player_center, len(spawn_specs), rng=rng, enemy_type=spawn_move_et
                )
            elif len(spawn_specs) == 1 and spawn_specs[0][0] == MiniBoss:
                # Mini boss: single safe position (central, no cluster)
                xy = generate_valid_spawn_position(
                    room, player_center, [], is_elite=False, rng=rng, enemy_type=spawn_move_et
                )
                positions_world = [xy]
            else:
                # Combat: spread pattern
                positions_world = spawn_spread(
                    room, player_center, len(spawn_specs), is_elite=False, rng=rng, door_positions=door_positions,
                    enemy_type=spawn_move_et,
                )

            logged_final_spawn_world: list[tuple[float, float]] = []
            for i, (cls, elite_flag, start_time_sec, telegraph_sec) in enumerate(spawn_specs):
                if i < len(positions_world):
                    wx, wy = positions_world[i]
                    # Heavy: ensure spawn not near corners, walls, or solid props
                    if cls.__name__ == "Heavy":
                        self._ensure_biome4_blocking_tiles(room)
                        blocked = getattr(self, "_biome4_blocking_tiles", set()) if (room and self._room_controller and self._room_controller.current_room_index >= BIOME4_START_INDEX) else None
                        other_positions = [positions_world[j] for j in range(len(positions_world)) if j != i]
                        wx, wy = ensure_valid_spawn_position(
                            room, wx, wy, existing_positions=other_positions, rng=rng, for_heavy=True, blocked_tiles=blocked
                        )
                    self._spawn_system.add_spawn(
                        0, 0, cls, elite_flag, start_time_sec,
                        telegraph_duration_sec=telegraph_sec,
                        world_pos=(wx, wy),
                    )
                    logged_final_spawn_world.append((wx, wy))
                else:
                    # Fallback: pattern returned too few positions — must still apply Heavy rules (tile 0,0 + clamp bypassed spawn_helper).
                    et_fb = enemy_type_key_for_class(cls)
                    if cls.__name__ == "Heavy":
                        self._ensure_biome4_blocking_tiles(room)
                        blocked_fb = (
                            getattr(self, "_biome4_blocking_tiles", set())
                            if (
                                room
                                and self._room_controller
                                and self._room_controller.current_room_index >= BIOME4_START_INDEX
                            )
                            else None
                        )
                        hw, hh = enemy_movement_half_extents_for_class(cls)
                        min_x, min_y, max_x, max_y = room.playable_bounds_for_half_extents(hw, hh)
                        cx, cy = (min_x + max_x) / 2.0, (min_y + max_y) / 2.0
                        wx, wy = ensure_valid_spawn_position(
                            room,
                            cx,
                            cy,
                            existing_positions=[],
                            rng=rng,
                            for_heavy=True,
                            blocked_tiles=blocked_fb,
                            enemy_type=et_fb,
                        )
                    else:
                        wx, wy = generate_valid_spawn_position(
                            room, player_center, [], is_elite=False, rng=rng, for_heavy=False, enemy_type=et_fb
                        )
                    self._spawn_system.add_spawn(
                        0, 0, cls, elite_flag, start_time_sec,
                        telegraph_duration_sec=telegraph_sec,
                        world_pos=(wx, wy),
                    )
                    logged_final_spawn_world.append((wx, wy))

            if room_idx >= BIOME4_START_INDEX:
                spawn_pattern_label = f"biome4:{get_biome4_spawn_pattern(rtype)}"
            elif room_idx >= BIOME3_START_INDEX:
                spawn_pattern_label = f"biome3:{get_biome3_spawn_pattern(rtype)}"
            elif room_idx >= 8:
                spawn_pattern_label = f"biome2:{get_biome2_spawn_pattern(rtype)}"
            elif not spawn_specs:
                spawn_pattern_label = "no_specs"
            elif rtype == RoomType.ELITE:
                spawn_pattern_label = "biome1_triangle_elite"
            elif rtype == RoomType.AMBUSH:
                spawn_pattern_label = "biome1_ambush"
            elif len(spawn_specs) == 1 and spawn_specs[0][0] == MiniBoss:
                spawn_pattern_label = "biome1_miniboss_single"
            else:
                spawn_pattern_label = "biome1_spread_combat"

            spawn_specs_summary = [
                f"{spec[0].__name__}, elite={spec[1]}, start={spec[2]}, tele={spec[3]}"
                for spec in spawn_specs
            ]
            log_spawn_setup(
                procedural_seed=active_seed,
                room_index=room_idx,
                room_type_name=rtype.value,
                biome_index=int(getattr(room, "biome_index", 1)),
                spawn_legacy_seed=active_seed + room.room_index * 10000,
                spawn_specs_summary=spawn_specs_summary,
                positions_world=logged_final_spawn_world,
                spawn_pattern_label=spawn_pattern_label,
                room=room,
                player_center_world=player_center,
                spawn_specs=spawn_specs,
            )
        else:
            self._spawn_system = SpawnSystem(self._vfx)
            px, py = self._player.world_pos
            px_tile = int(px // TILE_SIZE)
            py_tile = int(py // TILE_SIZE)
            center_tx = LOGICAL_W // TILE_SIZE // 2
            center_ty = LOGICAL_H // TILE_SIZE // 2
            spawn_specs = [
                (Swarm, (px_tile - 6, py_tile - 6), False),
                (Flanker, (px_tile + 6, py_tile - 6), False),
                (Brute, (px_tile - 6, py_tile + 6), True),
                (MiniBoss, (center_tx, center_ty), False),
            ]
            time_acc = 0.0
            for cls, (tx, ty), elite in spawn_specs:
                self._spawn_system.add_spawn(tx, ty, cls, elite, start_time_sec=time_acc)
                time_acc += SPAWN_SLOT_DELAY_SEC if cls is not MiniBoss else 2.0

    def _tile_blocks_movement(self, room, tx: int, ty: int) -> bool:
        """Return True if this tile is a solid wall/closed door or a solid Biome 4 prop. Uses wall band (2 or 4 tiles)."""
        if room is None:
            return False
        if tx < 0 or ty < 0 or tx >= room.width or ty >= room.height:
            return True
        if (self._room_controller is not None and self._room_controller.current_room_index == getattr(self, "_biome4_blocking_tiles_room", None)
                and (tx, ty) in getattr(self, "_biome4_blocking_tiles", set())):
            return True
        if not room.is_tile_in_wall_band(tx, ty):
            return False
        for d in self._room_controller.door_system.doors() if self._room_controller else []:
            if int(d.tile_x) == tx and int(d.tile_y) == ty:
                return d.state != DoorState.OPEN
        return True

    def _ensure_biome4_blocking_tiles(self, room) -> None:
        """Build _biome4_blocking_tiles for current room if Biome 4, so spawn/collision can use it."""
        if self._room_controller is None or room is None:
            return
        room_index = self._room_controller.current_room_index
        if room_index < BIOME4_START_INDEX:
            return
        if self._biome4_blocking_tiles_room == room_index:
            return
        doors = list(self._room_controller.door_system.doors())
        door_tiles = set((int(d.tile_x), int(d.tile_y)) for d in doors)
        for d in doors:
            door_tiles.add((int(d.tile_x), int(d.tile_y) + 1))
        placements = get_biome4_prop_placements(room, room_index, door_tiles, SEED)
        self._biome4_blocking_tiles = set()
        self._biome4_blocking_tiles_room = room_index
        for surf, wx, wy, prop_type in placements:
            if prop_type not in SOLID_PROP_INDICES or surf is None:
                continue
            sw, sh = surf.get_size()
            if sw <= TILE_SIZE and sh <= TILE_SIZE:
                tx = int((wx + sw / 2) // TILE_SIZE)
                ty = int((wy + sh / 2) // TILE_SIZE)
                self._biome4_blocking_tiles.add((tx, ty))
            else:
                tx0, ty0 = int(wx // TILE_SIZE), int(wy // TILE_SIZE)
                for dx in range(2):
                    for dy in range(2):
                        self._biome4_blocking_tiles.add((tx0 + dx, ty0 + dy))

    def _heavy_clearance_ok(self, room, rect: pygame.Rect, padding_px: float) -> bool:
        """True if Heavy's probe rect (inflated by padding_px) does not overlap any solid blocker.
        Heavy must not move through walls, props, or obstacle tiles; use same blocking map as other entities."""
        if room is None:
            return True
        r = rect.inflate(2 * padding_px, 2 * padding_px)
        cx, cy = float(r.centerx), float(r.centery)
        min_tx, max_tx, min_ty, max_ty = tile_range_for_centered_aabb(
            cx, cy, float(r.width), float(r.height)
        )
        for ty in range(min_ty, max_ty + 1):
            for tx in range(min_tx, max_tx + 1):
                if self._tile_blocks_movement(room, tx, ty):
                    return False
        return True

    def _heavy_retreat_direction(
        self,
        room,
        world_pos: tuple[float, float],
        player_world_pos: tuple[float, float],
    ) -> tuple[float, float]:
        """
        Unit vector away from obstacle cluster (centroid of nearby blockers) or nearest room edge.
        Blends a fraction toward the player so pure vertical / axis edge escape does not dominate.
        """
        x, y = world_pos
        px, py = player_world_pos
        blend = float(HEAVY_RETREAT_TOWARD_PLAYER_BLEND)

        def _blend_escape_toward_player(ux: float, uy: float) -> tuple[float, float]:
            dpx = px - x
            dpy = py - y
            d = math.hypot(dpx, dpy)
            if d < 1e-6:
                return (ux, uy)
            tx, ty = dpx / d, dpy / d
            bx = (1.0 - blend) * ux + blend * tx
            by = (1.0 - blend) * uy + blend * ty
            n = math.hypot(bx, by)
            if n < 1e-6:
                return (ux, uy)
            return (bx / n, by / n)

        block_check = self._tile_blocks_movement
        tx0, ty0 = int(x // TILE_SIZE), int(y // TILE_SIZE)
        search = 5
        blocked_centers: list[tuple[float, float]] = []
        for dy in range(-search, search + 1):
            for dx in range(-search, search + 1):
                tx, ty = tx0 + dx, ty0 + dy
                if block_check(room, tx, ty):
                    cell_center_x = (tx + 0.5) * TILE_SIZE
                    cell_center_y = (ty + 0.5) * TILE_SIZE
                    blocked_centers.append((cell_center_x, cell_center_y))
        if blocked_centers:
            cx = sum(c[0] for c in blocked_centers) / len(blocked_centers)
            cy = sum(c[1] for c in blocked_centers) / len(blocked_centers)
            dx = x - cx
            dy = y - cy
            n = math.hypot(dx, dy)
            if n > 1e-6:
                return _blend_escape_toward_player(dx / n, dy / n)
            return _blend_escape_toward_player(1.0, 0.0)
        if self._room_controller is not None and room is not None:
            min_x, min_y, max_x, max_y = room.playable_bounds_pixels()
            room_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
            from entities.enemy_base import _get_retreat_direction_away_from_wall

            wx, wy = _get_retreat_direction_away_from_wall(world_pos, room_rect)
            return _blend_escape_toward_player(wx, wy)
        return _blend_escape_toward_player(1.0, 0.0)

    def _resolve_entity_wall_collision(self, entity, prev_pos: tuple[float, float], room) -> None:
        """If entity overlaps a solid wall/prop tile, revert to prev position. Lava/slow are walkable (no block); lava damage is applied separately to player and enemies."""
        if room is None or self._room_controller is None:
            return
        if getattr(entity, "inactive", False):
            return
        block_check = self._tile_blocks_movement
        cx, cy = float(entity.world_pos[0]), float(entity.world_pos[1])
        if hasattr(entity, "get_movement_hitbox_rect"):
            r = entity.get_movement_hitbox_rect()
            fw, fh = float(r.width), float(r.height)
        elif hasattr(entity, "get_hitbox_rect"):
            r = entity.get_hitbox_rect()
            fw, fh = float(r.width), float(r.height)
        else:
            fw, fh = 32.0, 32.0
        min_tx, max_tx, min_ty, max_ty = tile_range_for_centered_aabb(cx, cy, fw, fh)
        for ty in range(min_ty, max_ty + 1):
            for tx in range(min_tx, max_tx + 1):
                if block_check(room, tx, ty):
                    entity.world_pos = prev_pos
                    setattr(entity, "_wall_collision_this_frame", True)
                    # Slide along wall: nudge perpendicular to velocity so enemies don't stay stuck
                    vx, vy = getattr(entity, "velocity_xy", (0.0, 0.0))
                    speed = math.hypot(vx, vy)
                    if speed > 1.0:
                        perp_x = -vy / speed
                        perp_y = vx / speed
                        nudge = 6.0
                        nx = prev_pos[0] + perp_x * nudge
                        ny = prev_pos[1] + perp_y * nudge
                        min_tx2, max_tx2, min_ty2, max_ty2 = tile_range_for_centered_aabb(
                            nx, ny, fw, fh
                        )
                        blocked = False
                        for ty2 in range(min_ty2, max_ty2 + 1):
                            for tx2 in range(min_tx2, max_tx2 + 1):
                                if block_check(room, tx2, ty2):
                                    blocked = True
                                    break
                            if blocked:
                                break
                        if not blocked:
                            entity.world_pos = (nx, ny)
                    return

    @property
    def camera_offset(self) -> tuple[float, float]:
        # Phase 7: center room in screen; Phase 3 fallback: (0, 0).
        if self._room_controller is not None and self._room_controller.current_room is not None:
            room = self._room_controller.current_room
            ox = (LOGICAL_W - room.pixel_width) / 2.0
            oy = (LOGICAL_H - room.pixel_height) / 2.0
            return (-ox, -oy)
        return (0.0, 0.0)

    def set_camera_target(self, world_x: float, world_y: float) -> None:
        self._camera_target_world = (world_x, world_y)

    def update(self, dt: float) -> None:
        self._ensure_room()
        self._ensure_player()
        if self._player is None:
            return
        if DEBUG_LIVE_SHORT_ATTACK_TRACE:
            self._live_trace_frame += 1
        if DEBUG_BLOCK_PARRY_TRACE:
            self._block_parry_trace_frame += 1
        if self._paused:
            self._ensure_pause_menu_assets()
            self._update_pause_hover()
            return
        self._tick_life_loss_transition(dt)
        # Life 1 only: visible state must follow current HP during the room. Room-end/respawn classify alone
        # leaves player_state stale (e.g. stays DOMINATING after taking damage). Phases 2–3 unchanged.
        if int(getattr(self._player, "life_index", 0)) == 0:
            self._classify_player_model_from_current_run()
        self._metrics.update(dt)
        if (
            USE_PHASE7_DUNGEON
            and self._room_controller is not None
            and self._metrics_pending_room_start
        ):
            room_m = self._room_controller.current_room
            if room_m is not None:
                self._metrics.start_room(
                    self._room_controller.current_room_index,
                    int(room_m.biome_index),
                    self._player_hp_percent(),
                )
            self._metrics_pending_room_start = False
        room = self._room_controller.current_room if self._room_controller else None
        if self._room_controller is not None and room is not None:
            self.ai_director.update_room_context(
                int(self._room_controller.current_room_index),
                int(getattr(room, "biome_index", 1)),
            )
        else:
            self.ai_director.update_room_context(None, None)
        if room is not None and self._room_controller is not None:
            # Playable area only (inside wall band); walls/doors block via collision.
            min_x, min_y, max_x, max_y = room.playable_bounds_for_half_extents(
                PLAYER_MOVEMENT_HITBOX_W * 0.5, PLAYER_MOVEMENT_HITBOX_H * 0.5
            )
            self._player.room_bounds = (min_x, min_y, max_x, max_y)
            if DEBUG_MOVEMENT_HITBOX:
                rid = self._room_controller.current_room_index
                if getattr(self, "_debug_player_mov_hb_room", None) != rid:
                    self._debug_player_mov_hb_room = rid
                    px, py = self._player.world_pos
                    ptx, pty = room.tile_at_world(px, py)
                    print(
                        f"[PLAYER MOVEMENT HB] wh=({PLAYER_MOVEMENT_HITBOX_W},{PLAYER_MOVEMENT_HITBOX_H}) "
                        f"room_min_y={min_y:.2f} pos_y={py:.2f} tile_row={pty} tile_col={ptx}"
                    )
            tx, ty = self._room_controller.hazard_system.tile_at_world(
                self._player.world_pos[0], self._player.world_pos[1]
            )
            self._player.speed_factor = (
                SLOW_TILE_SPEED_FACTOR
                if self._room_controller.hazard_system.is_slow_tile(tx, ty)
                else 1.0
            )
        else:
            self._player.room_bounds = None
            self._player.speed_factor = 1.0
        # Biome 4 Phase 2: use Biome 4 spawn portal/telegraph assets only in Biome 4 rooms.
        if self._room_controller is not None and self._room_controller.current_room is not None:
            room = self._room_controller.current_room
            self._vfx.set_biome4_spawn_visuals(getattr(room, "biome_index", 1) == 4)
        else:
            self._vfx.set_biome4_spawn_visuals(False)
        self._ensure_spawn_system()
        if self._spawn_system is not None:
            heavy_blocked = None
            if (
                self._room_controller is not None
                and room is not None
                and self._room_controller.current_room_index >= BIOME4_START_INDEX
            ):
                self._ensure_biome4_blocking_tiles(room)
                heavy_blocked = getattr(self, "_biome4_blocking_tiles", None)
            self._spawn_system.update(
                dt, self._player, self._enemies, room=room, heavy_blocked_tiles=heavy_blocked
            )

        if self._room_controller is not None:
            self._room_controller.update(dt)

        # Phase 3: victory after beating final boss (last room exit)
        if self._victory_phase:
            self._victory_timer += dt
            # 0.0 - 2.0 sec: full victory screen
            # 2.0 - 5.0 sec: blackscreen + victory banner
            # 5.0 sec: return to main menu
            if self._victory_timer >= 5.0:
                self._victory_phase = False
                self._victory_timer = 0.0
                self.scene_manager.switch_to_start()
            return

        # If we're in a death sequence, run its timeline and skip normal combat.
        if self._death_phase is not None:
            self._update_death_sequence(dt)
            return

        # Normal play: player + enemies. Room 0 story panel open = disable movement (Requirements §9.4.2)
        # Life-loss transition: no input/movement until respawn (same frame semantics as story panel).
        _input_blocked = self._room0_story_panel_open or self._is_in_life_loss_transition
        pressed = pygame.key.get_pressed()
        keys = set()
        if not _input_blocked:
            if pressed[pygame.K_w]:
                keys.add(pygame.K_w)
            if pressed[pygame.K_s]:
                keys.add(pygame.K_s)
            if pressed[pygame.K_a]:
                keys.add(pygame.K_a)
            if pressed[pygame.K_d]:
                keys.add(pygame.K_d)
        block_held = False if _input_blocked else (pygame.K_j in self._keys_held or pressed[pygame.K_j])
        parry_request = False if _input_blocked else self._parry_request
        if DEBUG_BLOCK_PARRY_TRACE:
            print(
                f"[BLOCK_PARRY_TRACE] GameScene.update f={self._block_parry_trace_frame} "
                f"paused={self._paused} story_panel={self._room0_story_panel_open} life_loss={self._is_in_life_loss_transition} "
                f"death={self._death_phase!r} victory={self._victory_phase} "
                f"block_held={block_held} _parry_request={self._parry_request} -> parry_request={parry_request} "
                f"K_in_keys_held={pygame.K_k in self._keys_held}"
            )
        mouse = (0, 0, 0) if _input_blocked else pygame.mouse.get_pressed(3)
        dash_req = False if _input_blocked else self._dash_request
        if _input_blocked:
            short_req = False
            long_req = False
            if DEBUG_LIVE_SHORT_ATTACK_TRACE:
                print(
                    f"[LIVE_TRACE] GameScene.update f={self._live_trace_frame} story_panel_open=True "
                    f"-> short_req=False long_req=False (mouse/poll ignored for combat)"
                )
        else:
            prev_lmb_stored = self._prev_mouse_left
            left_now, _, right_now = mouse[0], mouse[1], mouse[2]
            left_edge = left_now and not self._prev_mouse_left
            right_edge = right_now and not self._prev_mouse_right
            self._prev_mouse_left = left_now
            self._prev_mouse_right = right_now
            short_req = self._attack_short_request or left_edge
            long_req = self._attack_long_request or right_edge
            if DEBUG_SHORT_ATTACK_INPUT and short_req:
                print(
                    f"[SHORT_ATK_IN] GameScene.update short_req=True "
                    f"(_attack_short_request={self._attack_short_request} left_edge={left_edge} "
                    f"left_now={left_now}) -> Player.update"
                )
            if DEBUG_LIVE_SHORT_ATTACK_TRACE:
                _pend = getattr(self._player, "_pending_short_attack", False)
                print(
                    f"[LIVE_TRACE] GameScene.update f={self._live_trace_frame} poll: "
                    f"left_now={left_now} prev_lmb={prev_lmb_stored} left_edge={left_edge} "
                    f"_attack_short_request={self._attack_short_request} short_req={short_req} "
                    f"player._pending_short_attack(before)={_pend}"
                )
            if DEBUG_PLAYER_ATTACK_WALK_TRACE and (short_req or self._attack_short_request):
                print(
                    f"[GAMESCENE] pre Player.update: short_req={short_req} "
                    f"_attack_short_request={self._attack_short_request} left_edge={left_edge} "
                    f"left_down={left_now} prev_lmb_before={prev_lmb_stored}"
                )
        prev_player_pos = self._player.world_pos
        if not self._is_in_life_loss_transition:
            self._player.update(
                dt,
                keys,
                mouse,
                block_held,
                parry_request,
                dash_req,
                short_req,
                long_req,
            )
            # Wall collision: revert if player moved into a wall/closed door tile.
            if room is not None:
                self._resolve_entity_wall_collision(self._player, prev_player_pos, room)
        if not self._is_in_life_loss_transition and room is not None and DEBUG_TOP_EDGE:
            b = room.wall_border()
            px, py = self._player.world_pos
            ptx, pty = room.tile_at_world(px, py)
            if pty < b + 6:
                phw, phh = PLAYER_MOVEMENT_HITBOX_W * 0.5, PLAYER_MOVEMENT_HITBOX_H * 0.5
                pmn_x, pmn_y, pmx_x, pmx_y = room.playable_bounds_for_half_extents(phw, phh)
                # Top-only gameplay padding: none (HUD uses screen-space draw only).
                print(
                    f"[TOP BOUNDS] wall_border_tiles={b} player_min_y={pmn_y:.2f} player_max_y={pmx_y:.2f} "
                    f"movement_wh=({PLAYER_MOVEMENT_HITBOX_W},{PLAYER_MOVEMENT_HITBOX_H}) "
                    f"hud_top_padding_px=0"
                )
                _sample = next(
                    (e for e in self._enemies if not getattr(e, "inactive", False)),
                    None,
                )
                if _sample is not None:
                    ehw, ehh = enemy_movement_half_extents_for_class(type(_sample))
                    emn_x, emn_y, emx_x, emx_y = room.playable_bounds_for_half_extents(ehw, ehh)
                    print(
                        f"[TOP BOUNDS] sample_enemy={type(_sample).__name__} enemy_min_y={emn_y:.2f} "
                        f"enemy_max_y={emx_y:.2f}"
                    )
                vy = self._player.velocity_xy[1] if self._player.velocity_xy else 0.0
                print(
                    f"[TOP TILE CHECK] world_y={py:.2f} tile_y={pty} tile_x={ptx} "
                    f"in_wall_band={room.is_tile_in_wall_band(ptx, pty)} vy={vy:.1f}"
                )
                print(
                    f"[TOP EDGE CHECK] player world=({px:.2f},{py:.2f}) tile=({ptx},{pty}) "
                    f"in_wall_band={room.is_tile_in_wall_band(ptx, pty)} wall_border_b={b}"
                )
                print(
                    f"[PLAYABLE BOUNDS] min_y={pmn_y:.2f} max_y={pmx_y:.2f} "
                    f"min_x={pmn_x:.2f} max_x={pmx_x:.2f}"
                )
                print(f"[PLAYER CLAMP] room_bounds_y=[{pmn_y:.2f},{pmx_y:.2f}] (applied in apply_player_movement)")
                print("[TOP OFFSET FOUND] source=none (no extra top-only clamp beyond wall_band+half_extents)")
        if getattr(self._player, "_consumed_dash_request", False):
            self._dash_request = False
        if DEBUG_LIVE_SHORT_ATTACK_TRACE:
            print(
                f"[LIVE_TRACE] CLEAR _attack_short_request end_frame f={self._live_trace_frame} "
                f"was_true={bool(self._attack_short_request)} "
                f"pending_after={getattr(self._player, '_pending_short_attack', None)} "
                f"player.state={getattr(self._player, 'state', None)!r}"
            )
        # One-shot pygame flag: Player buffers locked clicks into _pending_short_attack so this can clear every frame.
        self._attack_short_request = False
        self._attack_long_request = False
        self._parry_request = False
        self._metrics.player_idle = len(keys) == 0
        px0, py0 = self._player.world_pos
        _near_e = False
        for _e in self._enemies:
            if getattr(_e, "inactive", False):
                continue
            _ex, _ey = getattr(_e, "world_pos", (0.0, 0.0))
            if math.hypot(px0 - _ex, py0 - _ey) < 280.0:
                _near_e = True
                break
        self._metrics.near_enemy = _near_e

        # Build list of all hostiles (enemies + mini boss when present)
        all_hostiles = list(self._enemies)
        # Resolve player attacks first (enemy attacks resolved after enemy update so e.g. mini_boss_3 is in attack_01/attack_02).
        if self._is_in_life_loss_transition:
            player_events = []
        else:
            player_events = apply_player_attacks(self._player, all_hostiles)
        for _pe in player_events:
            if not _pe.is_player:
                self._metrics.record_damage_dealt(_pe.amount)
                _tgt = _pe.target
                if not getattr(_tgt, "is_training_dummy", False) and getattr(_tgt, "hp", 0) <= 0:
                    _et = getattr(_tgt, "enemy_type", type(_tgt).__name__)
                    self._metrics.record_kill(str(_et))
        if player_events:
            self._debug_player_hit_time = pygame.time.get_ticks() / 1000.0
        # Room 0: training dummy HP resets after each hit (Requirements §9.5.3)
        if self._room_controller is not None and self._room_controller.current_room_index == 0:
            for e in self._enemies:
                if getattr(e, "is_training_dummy", False):
                    e.hp = getattr(e, "max_hp", 9999.0)

        # Update enemies after player (Phase 3); clamp each enemy using its own hitbox half-extents
        # (sprite size). Shared player-sized bounds made tall enemies overlap the top wall row.
        fallback_rect = pygame.Rect(ENEMY_MIN_X, ENEMY_MIN_Y, ENEMY_MAX_X - ENEMY_MIN_X, ENEMY_MAX_Y - ENEMY_MIN_Y)
        self._room_time += dt
        # Phase 3: Final Boss spawn at 2.0s in Room 29 (with spawn portal/explosion VFX)
        if room is not None and room.room_type == RoomType.FINAL_BOSS and self._final_boss_spawn_timer is not None:
            self._final_boss_spawn_timer -= dt
            if self._final_boss_spawn_timer <= 0.0:
                self._final_boss_spawn_timer = None
                self._final_boss_spawned = True
                cx, cy = room.width // 2, room.height // 2
                wx, wy = room.world_pos_for_tile(cx, cy)
                self._enemies.append(
                    FinalBoss((wx, wy), room_index=self._room_controller.current_room_index, **self._final_boss_director_kwargs())
                )
                self._boss_spawn_fx_timer = 1.2
                self._boss_spawn_fx_pos = (float(wx), float(wy))
                self._boss_revive_message_until = 0.0
                self._boss_revive_message_shown = False
        for enemy in list(self._enemies):
            if getattr(enemy, "inactive", False):
                continue
            prev_enemy_pos = enemy.world_pos
            if room is not None:
                mw, mh = getattr(enemy, "movement_size", getattr(enemy, "size", (32, 32)))
                emin_x, emin_y, emax_x, emax_y = room.playable_bounds_for_half_extents(
                    mw * 0.5, mh * 0.5
                )
                room_rect = pygame.Rect(emin_x, emin_y, emax_x - emin_x, emax_y - emin_y)
            else:
                room_rect = fallback_rect
            if isinstance(enemy, FinalBoss):
                block_check = (lambda r, tx, ty: self._tile_blocks_movement(r, tx, ty)) if room is not None else None
                enemy.update(dt, self._player, room_rect, room, block_check=block_check)
            else:
                if getattr(enemy, "enemy_type", None) == "heavy" and room is not None:
                    heavy_clearance_cb = lambda rect, pad: self._heavy_clearance_ok(room, rect, pad)
                    heavy_retreat_cb = lambda: self._heavy_retreat_direction(
                        room, enemy.world_pos, self._player.world_pos
                    )
                    enemy.update(dt, self._player, room_rect, heavy_clearance_cb=heavy_clearance_cb, heavy_retreat_cb=heavy_retreat_cb)
                else:
                    enemy.update(dt, self._player, room_rect)
            if room is not None:
                self._resolve_entity_wall_collision(enemy, prev_enemy_pos, room)
        # Phase 6: detect mini boss / Final Boss death after update (before removing from list)
        for e in self._enemies:
            if isinstance(e, FinalBoss) and getattr(e, "state", None) == "death" and not getattr(e, "_revived", False) and not getattr(e, "_final_death", False):
                self._boss_death_fx_timer = 2.0
                self._boss_death_fx_pos = (float(e.world_pos[0]), float(e.world_pos[1]))
            if isinstance(e, (MiniBoss, MiniBoss2, Biome3MiniBoss, FinalBoss)) and getattr(e, "inactive", False):
                self._mini_boss_death_pos = e.world_pos
                if isinstance(e, FinalBoss):
                    self._boss_death_fx_timer = 2.0
                    self._boss_death_fx_pos = (float(e.world_pos[0]), float(e.world_pos[1]))
                break
        # Capture one-frame teleport FX from Final Boss (then clear on boss)
        self._boss_teleport_fx_frame = None
        for e in self._enemies:
            if isinstance(e, FinalBoss) and getattr(e, "_teleport_fx_frame", None) is not None:
                self._boss_teleport_fx_frame = e._teleport_fx_frame
                e._teleport_fx_frame = None
                break
        # Final Boss revive: show center-screen message when boss enters revive_wait (once per encounter)
        for e in self._enemies:
            if isinstance(e, FinalBoss) and getattr(e, "state", None) == "revive_wait" and not self._boss_revive_message_shown:
                self._boss_revive_message_until = self._room_time + FINAL_BOSS_REVIVE_MESSAGE_DURATION_SEC
                self._boss_revive_message_shown = True
                break
        # Biome 3 mini boss: spawn 2 Swarm + 1 Flanker in ring when boss requests adds
        for e in self._enemies:
            if getattr(e, "_pending_adds", False):
                bx, by = e.world_pos
                radius = 120.0
                add_positions = [(bx, by)]
                for i, (add_cls, elite) in enumerate([(Swarm, False), (Swarm, False), (Flanker, False)]):
                    angle = (i * 2 * math.pi / 3)
                    wx = bx + radius * math.cos(angle)
                    wy = by + radius * math.sin(angle)
                    if room is not None:
                        wx, wy = ensure_valid_spawn_position(
                            room,
                            wx,
                            wy,
                            existing_positions=add_positions,
                            enemy_type=enemy_type_key_for_class(add_cls),
                        )
                    add_positions.append((wx, wy))
                    add_enemy = add_cls((wx, wy), elite=elite)
                    self._enemies.append(add_enemy)
                e._pending_adds = False
                break
        # Phase 3: copy Final Boss meteor impacts with trigger_at = room_time + phase-specific telegraph
        for e in self._enemies:
            pending = getattr(e, "pending_meteor_impacts", None)
            if pending:
                for imp in pending:
                    telegraph_sec = imp.get("telegraph_sec", BIOME4_BOSS_TELEGRAPH_METEOR_SEC)
                    self._meteor_impacts.append({
                        "x": imp["x"], "y": imp["y"], "damage": imp["damage"],
                        "radius": imp.get("radius", 64.0),
                        "trigger_at": self._room_time + telegraph_sec,
                        "telegraph_sec": telegraph_sec,
                        "start_at": self._room_time,
                    })
                e.pending_meteor_impacts.clear()
        if DEBUG_RANGED_ENEMY_LIFECYCLE:
            for e in self._enemies:
                if getattr(e, "inactive", False) and type(e).__name__ == "Ranged":
                    st = getattr(e, "state", None)
                    print(
                        f"[RANGED LIFECYCLE] prune_from_list reason=inactive id={id(e)} hp={getattr(e, 'hp', None)!r} "
                        f"state={st!r}"
                    )
        self._enemies = [e for e in self._enemies if not getattr(e, "inactive", False)]

        # Resolve enemy melee attacks after enemy update so bosses (e.g. Biome 3 mini_boss_3) are in attack_01/attack_02 when we check.
        all_hostiles = list(self._enemies)
        if self._is_in_life_loss_transition:
            enemy_events, melee_parry_negations = [], 0
        else:
            enemy_events, melee_parry_negations = apply_enemy_attacks(self._player, all_hostiles, dt)
        if melee_parry_negations > 0 and self._player is not None:
            px, py = self._player.world_pos
            label = "PARRY!" if melee_parry_negations == 1 else f"PARRY! x{melee_parry_negations}"
            self._vfx.spawn_parry_negation_feedback((px, py), text=label)
        if DEBUG_COMBAT_HITS:
            room_idx = self._room_controller.current_room_index if self._room_controller is not None else -1
            p = self._player
            self._debug_combat_lines = [
                f"room={room_idx} enemies={len(self._enemies)} hostiles={len(all_hostiles)}",
                f"player_state={getattr(p, 'state', '?')} short_t={getattr(p, '_short_attack_timer', 0.0):.2f} long_t={getattr(p, '_long_attack_timer', 0.0):.2f}",
                f"player_events={len(player_events)} enemy_events={len(enemy_events)} hit_zone_r={ENEMY_HIT_ZONE_RADIUS}",
            ]
            if len(all_hostiles) > 0:
                e0 = all_hostiles[0]
                self._debug_combat_lines.append(
                    f"enemy0={getattr(e0, 'enemy_type', type(e0).__name__)} hp={float(getattr(e0, 'hp', 0.0)):.1f}/{float(getattr(e0, 'max_hp', 0.0)):.1f}"
                )
        self._spawn_vfx_for_damage(player_events + enemy_events)
        for _ee in enemy_events:
            if _ee.is_player:
                self._metrics.record_damage_taken(_ee.amount, _ee.source or "enemy_melee")
        # Phase 3: Final Boss contact damage (every 0.5s when player overlaps boss)
        if self._player is not None and room is not None:
            player_rect = self._player.get_hitbox_rect()
            for e in self._enemies:
                if isinstance(e, FinalBoss) and not getattr(e, "inactive", False):
                    if e.state == "revive_wait":
                        continue
                    ex, ey = e.world_pos
                    boss_rect = pygame.Rect(ex - 64, ey - 64, 128, 128)
                    if player_rect.colliderect(boss_rect):
                        self._final_boss_contact_timer -= dt
                        if self._final_boss_contact_timer <= 0.0:
                            self._final_boss_contact_timer = 0.5
                            if not self._is_in_life_loss_transition:
                                contact_dmg = FINAL_BOSS_CONTACT_DAMAGE_REVIVE if getattr(e, "_revived", False) else FINAL_BOSS_CONTACT_DAMAGE
                                if float(getattr(self._player, "invulnerable_timer", 0.0)) <= 0.0:
                                    self._player.hp = max(0, self._player.hp - contact_dmg)
                                    self._metrics.record_damage_taken(float(contact_dmg), "final_boss_contact")
                                if hasattr(self._player, "damage_flash_timer"):
                                    self._player.damage_flash_timer = 0.15
                    else:
                        self._final_boss_contact_timer = 0.0
        # Phase 3: process meteor impacts (damage + add to impact display for VFX)
        still_pending = []
        for imp in self._meteor_impacts:
            if self._room_time >= imp["trigger_at"]:
                if self._player is not None and not self._is_in_life_loss_transition:
                    px, py = self._player.world_pos
                    dx = px - imp["x"]
                    dy = py - imp["y"]
                    if math.hypot(dx, dy) <= imp["radius"]:
                        if float(getattr(self._player, "invulnerable_timer", 0.0)) <= 0.0:
                            self._player.hp = max(0, self._player.hp - imp["damage"])
                            self._metrics.record_damage_taken(float(imp["damage"]), "meteor")
                        if hasattr(self._player, "damage_flash_timer"):
                            self._player.damage_flash_timer = 0.15
                self._meteor_impact_display.append({"x": imp["x"], "y": imp["y"], "until": self._room_time + 0.4})
            else:
                still_pending.append(imp)
        self._meteor_impacts = still_pending
        # Decay spawn FX, death FX, meteor impact display
        if self._boss_spawn_fx_timer > 0.0:
            self._boss_spawn_fx_timer -= dt
        if self._boss_death_fx_timer > 0.0:
            self._boss_death_fx_timer -= dt
        self._meteor_impact_display = [m for m in self._meteor_impact_display if self._room_time < m["until"]]
        # Fatal HP: respawn with spare life or game over
        z_hp = self._handle_player_hp_zero()
        if z_hp == "game_over":
            return

        # Biome 3: collect projectiles from ranged, update, resolve vs player
        for enemy in self._enemies:
            pending = getattr(enemy, "_pending_projectile", None)
            if pending is not None:
                self._projectiles.append(pending)
                enemy._pending_projectile = None
        for p in self._projectiles:
            p.update(dt)
        if self._is_in_life_loss_transition:
            proj_events = []
        else:
            proj_events = apply_projectile_hits(self._player, self._projectiles)
        if proj_events:
            self._spawn_vfx_for_damage(proj_events)
        for _pev in proj_events:
            if _pev.is_player:
                self._metrics.record_damage_taken(_pev.amount, _pev.source or "enemy_projectile")
        self._projectiles = [p for p in self._projectiles if not getattr(p, "inactive", True)]
        z_proj = self._handle_player_hp_zero()
        if z_proj == "game_over":
            return

        # Phase 7: room clear -> start door open timer (once per room); 25% heal drop (seeded)
        if self._room_controller is not None and not self._room_cleared_flag:
            room_type = room.room_type if room is not None else None
            is_combat_room = room_type in (RoomType.COMBAT, RoomType.AMBUSH, RoomType.ELITE, RoomType.MINI_BOSS)
            if is_combat_room:
                # Only consider room cleared when there are no active enemies AND all spawns have completed.
                spawns_done = self._spawn_system is None or self._spawn_system.all_spawns_completed()
                if DEBUG_RANGED_ENEMY_LIFECYCLE:
                    _t = getattr(self, "_ranged_debug_room_clear_log_t", -999.0)
                    if self._room_time - _t >= 0.5:
                        self._ranged_debug_room_clear_log_t = self._room_time
                        _names = [type(x).__name__ for x in self._enemies]
                        print(
                            f"[RANGED LIFECYCLE] room_clear_check n={len(self._enemies)} "
                            f"types={_names} spawns_done={spawns_done}"
                        )
                if spawns_done and len(self._enemies) == 0:
                    if DEBUG_RANGED_ENEMY_LIFECYCLE:
                        print("[RANGED LIFECYCLE] room_clear_triggered -> on_room_clear()")
                    self._room_controller.on_room_clear()
                    self._room_cleared_flag = True
                    self._metrics.end_room(self._player_hp_percent())
                    self._update_player_model_after_room_end()
                    if not self._heal_drop_rolled_this_room:
                        self._heal_drop_rolled_this_room = True
                        rng = random.Random(SEED + self._room_controller.current_room_index * 100)
                        heal_p = HEAL_DROP_CHANCE
                        ri = self._room_controller.current_room_index
                        psn = self.player_state.name if self.player_state is not None else None
                        if (
                            room is not None
                            and int(getattr(room, "biome_index", 1)) == 1
                            and ri < 8
                            and not BEGINNER_TEST_MODE
                            and room.room_type
                            in (RoomType.COMBAT, RoomType.AMBUSH, RoomType.ELITE)
                        ):
                            heal_p = biome1_effective_heal_drop_chance(HEAL_DROP_CHANCE, psn)
                        elif (
                            room is not None
                            and int(getattr(room, "biome_index", 1)) == 2
                            and BIOME3_START_INDEX > ri >= 8
                            and not BEGINNER_TEST_MODE
                            and room.room_type
                            in (RoomType.COMBAT, RoomType.AMBUSH, RoomType.ELITE)
                        ):
                            heal_p = biome2_effective_heal_drop_chance(HEAL_DROP_CHANCE, psn)
                        elif (
                            room is not None
                            and int(getattr(room, "biome_index", 1)) == 3
                            and BIOME4_START_INDEX > ri >= BIOME3_START_INDEX
                            and not BEGINNER_TEST_MODE
                            and room.room_type
                            in (RoomType.COMBAT, RoomType.AMBUSH, RoomType.ELITE)
                        ):
                            heal_p = biome3_effective_heal_drop_chance(HEAL_DROP_CHANCE, psn)
                        elif (
                            room is not None
                            and int(getattr(room, "biome_index", 1)) == 4
                            and 29 > ri >= BIOME4_START_INDEX
                            and not BEGINNER_TEST_MODE
                            and room.room_type
                            in (RoomType.COMBAT, RoomType.AMBUSH, RoomType.ELITE)
                        ):
                            heal_p = biome4_effective_heal_drop_chance(HEAL_DROP_CHANCE, psn)
                        if rng.random() < heal_p and room is not None and room.room_type not in (RoomType.START, RoomType.SAFE):
                            cx, cy = room.width // 2, room.height // 2
                            wx, wy = room.world_pos_for_tile(cx, cy)
                            self._rewards.append({"pos": (wx, wy), "collected": False})
        # Phase 7: Safe Room heal object position (one corner of playable area); set once when in Safe Room
        if self._room_controller is not None and room is not None and room.room_type == RoomType.SAFE:
            if self._safe_room_heal_pos is None:
                b = room.wall_border()
                tx = b + 2
                ty = b + 2
                wx, wy = room.world_pos_for_tile(tx, ty)
                self._safe_room_heal_pos = (wx, wy)
            # Proximity for "Press [F]" safe room heal prompt and interaction
            if self._player is not None and self._safe_room_heal_pos is not None:
                px, py = self._player.world_pos
                hx, hy = self._safe_room_heal_pos
                self._near_safe_room_heal = math.hypot(px - hx, py - hy) <= 70.0
            else:
                self._near_safe_room_heal = False
        else:
            self._safe_room_heal_pos = None
            self._near_safe_room_heal = False

        # Heal flash countdown (visual feedback after collecting heal)
        if self._heal_flash_timer > 0:
            self._heal_flash_timer = max(0.0, self._heal_flash_timer - dt)
        if self._player is not None and getattr(self._player, "reserve_heal_cooldown_timer", 0.0) > 0:
            self._player.reserve_heal_cooldown_timer = max(
                0.0, float(self._player.reserve_heal_cooldown_timer) - dt
            )

        # Phase 7: lava damage (6 HP/sec); dash ignores; block/parry do not reduce
        if self._room_controller is not None and self._player is not None:
            hz = self._room_controller.hazard_system
            px, py = self._player.world_pos
            tx, ty = hz.tile_at_world(px, py)
            self._metrics.in_hazard = hz.is_lava_tile(tx, ty) or hz.is_slow_tile(tx, ty)
            if (
                hz.is_lava_tile(tx, ty)
                and not getattr(self._player, "dash_active", False)
                and not self._is_in_life_loss_transition
            ):
                dmg = LAVA_DAMAGE_PER_SECOND * dt
                if dmg > 0 and float(getattr(self._player, "invulnerable_timer", 0.0)) <= 0.0:
                    self._player.hp = max(0, self._player.hp - dmg)
                    self._metrics.record_damage_taken(float(dmg), "hazard_lava")
                    if hasattr(self._player, "damage_flash_timer"):
                        self._player.damage_flash_timer = 0.15
            # Enemies do not take lava damage (spawn_helper / combat design: hazards are player-only).
            z_lava = self._handle_player_hp_zero()
            if z_lava == "game_over":
                return

        # Phase 6: on mini boss death spawn reward and start door-unlock delay
        if self._mini_boss_death_pos is not None:
            self._rewards.append({"pos": self._mini_boss_death_pos, "collected": False})
            self._door_unlock_timer = MINI_BOSS_DOOR_UNLOCK_DELAY_SEC
            self._mini_boss_death_pos = None

        # Phase 6: door unlock timer
        if self._door_unlock_timer is not None:
            self._door_unlock_timer -= dt
            if self._door_unlock_timer <= 0.0:
                self._doors_unlocked = True
                self._door_unlock_timer = None
                if room is not None and room.room_type == RoomType.FINAL_BOSS and not self._room_cleared_flag:
                    self._room_controller.on_room_clear()
                    self._room_cleared_flag = True
                    self._metrics.end_room(self._player_hp_percent())
                    self._update_player_model_after_room_end()

        # Phase 7: door transition (rooms 0–7) — player rect overlapping open doorway trigger loads next room
        if (
            self._room_controller is not None
            and self._player is not None
            and self._death_phase is None
            and not self._is_in_life_loss_transition
        ):
            room = self._room_controller.current_room
            pr = self._player.get_hitbox_rect()
            next_idx = None
            doors = list(self._room_controller.door_system.doors())
            cur_idx = self._room_controller.current_room_index
            B = room.wall_border()
            playable_right_x = (room.width - B) * TILE_SIZE
            # Inner edge of bottom opening: last playable row is (height - B - 1), opening starts at row (height - B)
            inner_bottom_center_y = (room.height - B - 0.5) * TILE_SIZE
            door_size = TILE_SIZE * 3
            trigger_shrink = 20
            trigger_half_w = (door_size - trigger_shrink * 2) // 2
            for center_x, center_y, target_room_index, state, _ in self._iter_doorways(doors, room):
                if state != DoorState.OPEN or target_room_index <= cur_idx:
                    continue
                if target_room_index > cur_idx:
                    center_x = playable_right_x - trigger_half_w
                    center_y = inner_bottom_center_y
                door_rect = pygame.Rect(0, 0, door_size, door_size)
                door_rect.center = (center_x, center_y)
                trigger_rect = door_rect.inflate(-trigger_shrink, -trigger_shrink)
                if pr.colliderect(trigger_rect):
                    next_idx = target_room_index
                    break
            if next_idx is not None:
                total = total_campaign_rooms()
                if self._room_controller.current_room_index == total - 1:
                    self._victory_phase = True
                    self._victory_timer = 0.0
                    return
                if next_idx < total:
                    self._metrics.end_room(self._player_hp_percent())
                    self._update_player_model_after_room_end()
                    self._room_controller.load_room(next_idx)
                    self._metrics_pending_room_start = True
                    room = self._room_controller.current_room
                    wx, wy = room.world_pos_for_tile(room.spawn_tile[0], room.spawn_tile[1])
                    self._player.world_pos = (wx, wy)
                    self._enemies = []
                    self._projectiles = []
                    self._spawned_enemies = False
                    self._spawn_system = None
                    self._room_cleared_flag = False
                    self._rewards = []
                    self._doors_unlocked = False
                    self._door_unlock_timer = None
                    self._final_boss_spawn_timer = None
                    self._final_boss_spawned = False
                    self._room_time = 0.0
                    self._meteor_impacts = []
                    self._meteor_impact_display = []
                    self._final_boss_contact_timer = 0.0
                    self._boss_spawn_fx_timer = 0.0
                    self._boss_spawn_fx_pos = None
                    self._boss_revive_message_until = 0.0
                    self._boss_revive_message_shown = False
                    self._boss_death_fx_timer = 0.0
                    self._boss_death_fx_pos = None
                    self._boss_teleport_fx_frame = None
                    self._victory_phase = False
                    self._victory_timer = 0.0
                    self._safe_room_heal_done = False
                    if room.room_type == RoomType.FINAL_BOSS:
                        self._final_boss_spawn_timer = BIOME4_FINAL_BOSS_SPAWN_DELAY_SEC
                        self._final_boss_spawned = False
                        preload_final_boss_animations()
                        preload_enemy_animations("swarm")
                        preload_enemy_animations("flanker")
                    self._safe_room_upgrade_pending = False
                    self._safe_room_upgrade_chosen_this_room = False
                    self._safe_room_biome4_picks_remaining = 0
                    self._safe_room_biome4_chosen = set()
                    self._heal_drop_rolled_this_room = False
                    self._safe_room_heal_pos = None

        # Phase 6: reward collection (heal 30% on overlap)
        if self._player is not None:
            player_rect = self._player.get_hitbox_rect()
            reward_radius = 24.0
            for r in self._rewards:
                if r["collected"]:
                    continue
                rx, ry = r["pos"]
                dx = (player_rect.centerx - rx)
                dy = (player_rect.centery - ry)
                if math.hypot(dx, dy) <= reward_radius + max(player_rect.w, player_rect.h) / 2:
                    r["collected"] = True
                    base_max_hp = getattr(self._player, "base_max_hp", 100.0)
                    heal_pct = FINAL_BOSS_REWARD_HEAL_PERCENT if (room is not None and room.room_type == RoomType.FINAL_BOSS) else MINI_BOSS_REWARD_HEAL_PERCENT
                    heal_amt = float(base_max_hp) * heal_pct
                    applied = self._player.apply_incoming_heal(heal_amt)
                    self._metrics.record_healing(applied)

        # Intra-room HP % extrema for metrics (min/max during room → hp_lost_in_room / room_result at end_room)
        if self._player is not None and self._metrics.run.room_active_flag:
            self._metrics.record_player_hp_percent(self._player_hp_percent())

        self._enforce_enemy_separation()
        self._enforce_player_enemy_separation()
        self._vfx.update(dt)

    def _update_death_sequence(self, dt: float) -> None:
        """Cinematic death flow: anim (3–4s) → freeze → Game Over overlay → main menu."""
        if self._player is None:
            return
        self._death_timer += dt

        # Durations within contract ranges
        DEATH_ANIM_DURATION = 3.5   # 3–4 seconds
        FREEZE_DURATION = 1.5       # 1–2 seconds
        GAME_OVER_DURATION = 4.0    # 3–5 seconds

        if self._death_phase == "anim":
            # Drive player death animation with no input.
            self._player.update(
                dt,
                set(),
                (False, False, False),
                False,
                False,
                False,
                False,
                False,
            )
            if self._death_timer >= DEATH_ANIM_DURATION:
                self._death_phase = "freeze"
                self._death_timer = 0.0
        elif self._death_phase == "freeze":
            # Screen is frozen; no updates to player/enemies.
            if self._death_timer >= FREEZE_DURATION:
                self._death_phase = "game_over"
                self._death_timer = 0.0
        elif self._death_phase == "game_over":
            # Just wait while overlay is shown (draw handles visuals).
            if self._death_timer >= GAME_OVER_DURATION:
                self.reset()
                self.scene_manager.switch_to_start()
        # Even during death, keep enemies separated visually and advance VFX.
        self._enforce_enemy_separation()
        self._enforce_player_enemy_separation()
        self._vfx.update(dt)

    def _spawn_vfx_for_damage(self, events: list[DamageEvent]) -> None:
        for ev in events:
            pos = ev.world_pos
            if pos is None:
                continue
            if not ev.is_player:
                # Enemy took damage from player: spawn slash and hit spark.
                if ev.source == "player_long":
                    self._vfx.spawn_slash(pos, kind="long")
                else:
                    self._vfx.spawn_slash(pos, kind="short")
                self._vfx.spawn_hit_spark(pos)
                self._vfx.spawn_damage_number(ev.amount, pos, is_player=False)
            else:
                # Player took damage from enemy: hit spark only.
                self._vfx.spawn_hit_spark(pos)
                self._vfx.spawn_damage_number(ev.amount, pos, is_player=True)

    def _clamp_enemy_world_to_room(self, room, enemy, x: float, y: float) -> tuple[float, float]:
        """Clamp enemy center using that enemy's movement half extents (same as AI clamp / wall body)."""
        if room is None:
            return (
                max(ENEMY_MIN_X, min(ENEMY_MAX_X, x)),
                max(ENEMY_MIN_Y, min(ENEMY_MAX_Y, y)),
            )
        hw, hh = enemy_movement_half_extents_for_class(type(enemy))
        min_x, min_y, max_x, max_y = room.playable_bounds_for_half_extents(hw, hh)
        return (max(min_x, min(max_x, x)), max(min_y, min(max_y, y)))

    def _enforce_enemy_separation(self) -> None:
        """Apply enemy–enemy separation rules so they never visually stack."""
        room = self._room_controller.current_room if self._room_controller else None
        n = len(self._enemies)
        for i in range(n):
            a = self._enemies[i]
            if getattr(a, "inactive", False):
                continue
            if getattr(a, "is_training_dummy", False):
                continue
            ax, ay = a.world_pos
            for j in range(i + 1, n):
                b = self._enemies[j]
                if getattr(b, "inactive", False):
                    continue
                if getattr(b, "is_training_dummy", False):
                    continue
                bx, by = b.world_pos
                dx = bx - ax
                dy = by - ay
                dist = math.hypot(dx, dy)
                min_dist = enemy_min_separation(getattr(a, "enemy_type", "swarm"), getattr(b, "enemy_type", "swarm"))
                if dist < 1e-3 or dist >= min_dist:
                    continue
                nx = dx / dist
                ny = dy / dist
                overlap = min_dist - dist
                pa = enemy_type_priority(getattr(a, "enemy_type", "swarm"))
                pb = enemy_type_priority(getattr(b, "enemy_type", "swarm"))
                if pa == pb:
                    fa = fb = 0.5
                elif pa < pb:
                    # a lower priority -> moves more
                    fa, fb = 0.75, 0.25
                else:
                    fa, fb = 0.25, 0.75
                ax_new = ax - nx * overlap * fa
                ay_new = ay - ny * overlap * fa
                bx_new = bx + nx * overlap * fb
                by_new = by + ny * overlap * fb
                ax_new, ay_new = self._clamp_enemy_world_to_room(room, a, ax_new, ay_new)
                bx_new, by_new = self._clamp_enemy_world_to_room(room, b, bx_new, by_new)
                a.world_pos = (ax_new, ay_new)
                b.world_pos = (bx_new, by_new)

    def _enemy_stop_distance(self, enemy_type: str) -> float:
        """Minimum center-to-center distance enemy must keep from player (no overlap)."""
        if enemy_type == "brute":
            return float(ENEMY_BRUTE_STOP_DISTANCE)
        if enemy_type == "flanker":
            return float(ENEMY_FLANKER_STOP_DISTANCE)
        if enemy_type == "heavy":
            from game.config import ENEMY_HEAVY_STOP_DISTANCE
            return float(ENEMY_HEAVY_STOP_DISTANCE)
        if enemy_type == "ranged":
            from game.config import ENEMY_RANGED_STOP_DISTANCE
            return float(ENEMY_RANGED_STOP_DISTANCE)
        return float(ENEMY_SWARM_STOP_DISTANCE)

    def _enforce_player_enemy_separation(self) -> None:
        """Ensure no enemy (especially swarm) overlaps the player; push enemies out to stop distance."""
        if self._player is None:
            return
        room = self._room_controller.current_room if self._room_controller else None
        px, py = self._player.world_pos
        for a in self._enemies:
            if getattr(a, "inactive", False) or getattr(a, "is_training_dummy", False):
                continue
            ax, ay = a.world_pos
            dx = ax - px
            dy = ay - py
            dist = math.hypot(dx, dy)
            stop_dist = self._enemy_stop_distance(getattr(a, "enemy_type", "swarm"))
            if dist < 1e-3:
                dist = 1e-3
                dx, dy = 1.0, 0.0
            if dist < stop_dist:
                nx = dx / dist
                ny = dy / dist
                ax_new = px + nx * stop_dist
                ay_new = py + ny * stop_dist
                ax_new, ay_new = self._clamp_enemy_world_to_room(room, a, ax_new, ay_new)
                a.world_pos = (ax_new, ay_new)

    def _ensure_mini_boss_bar_loaded(self) -> None:
        if self._mini_boss_bar_frame is not None:
            return
        self._mini_boss_bar_frame = load_image(
            "assets/ui/hud/mini_boss_health_frame_400x40.png",
            size=(BIOME4_BOSS_UI_ANCHOR_W, 40),
            use_colorkey=True,
            colorkey_color=(255, 255, 255),
            corner_bg_tolerance=40,
            exact_size=True,
        )

    def _ensure_boss_ui_loaded(self) -> None:
        """Phase 3: Final Boss health bar (assets/ui/)."""
        if self._boss_ui_frame is not None:
            return
        self._boss_ui_frame = load_image(
            "assets/ui/boss_health_bar_frame.png",
            size=(BIOME4_BOSS_UI_ANCHOR_W, BIOME4_BOSS_UI_ANCHOR_H),
            use_colorkey=True,
            colorkey_color=(255, 255, 255),
            corner_bg_tolerance=40,
        )
        self._boss_name_banner = load_image(
            "assets/ui/boss_name_banner.png",
            size=(BIOME4_BOSS_UI_ANCHOR_W, 20),
            use_colorkey=True,
            colorkey_color=(255, 255, 255),
            corner_bg_tolerance=40,
        )
        self._victory_bg = load_image("assets/ui/victory_screen_bg.png", size=(LOGICAL_W, LOGICAL_H), use_colorkey=False)
        self._victory_banner = load_image(
            "assets/ui/victory_banner.png",
            use_colorkey=True,
            colorkey_color=(255, 255, 255),
            corner_bg_tolerance=40,
        )

    def _is_placeholder_surface(self, surf: pygame.Surface | None) -> bool:
        """True if surf is the asset-loader grey placeholder (avoid drawing as boss FX)."""
        if surf is None or surf.get_width() == 0 or surf.get_height() == 0:
            return False
        try:
            c = surf.get_at((0, 0))[:3]
            return c == (80, 80, 80)
        except Exception:
            return False

    def _ensure_boss_fx_loaded(self) -> None:
        """Load Biome 4 boss telegraphs and VFX via biome4_visuals loaders (once)."""
        if self._boss_telegraph_attack_circle is not None:
            return
        self._boss_telegraph_attack_circle = load_boss_telegraph("boss_attack_circle_128x128.png", (128, 128))
        self._boss_telegraph_wave_line = load_boss_telegraph("boss_wave_line_256x64.png", (256, 64))
        self._boss_telegraph_meteor_target = load_boss_telegraph("boss_meteor_target_96x96.png", (96, 96))
        teleport_frames = load_boss_fx_teleport()
        if teleport_frames and not self._is_placeholder_surface(teleport_frames[0]):
            self._boss_fx_teleport_frames = teleport_frames
            if len(teleport_frames) >= 1:
                self._boss_fx_teleport_flash = teleport_frames[0]
            if len(teleport_frames) >= 2:
                self._boss_fx_teleport_smoke = teleport_frames[1]
            if len(teleport_frames) >= 3:
                self._boss_fx_teleport_anim = teleport_frames[2:]
        if not self._boss_fx_teleport_flash or self._is_placeholder_surface(self._boss_fx_teleport_flash):
            self._boss_fx_teleport_flash = load_boss_fx_image("boss_teleport_flash_64x64.png", (64, 64))
        if not self._boss_fx_teleport_smoke or self._is_placeholder_surface(self._boss_fx_teleport_smoke):
            self._boss_fx_teleport_smoke = load_boss_fx_image("boss_teleport_smoke_64x64.png", (64, 64))
        if not self._boss_fx_teleport_anim or (self._boss_fx_teleport_anim and self._is_placeholder_surface(self._boss_fx_teleport_anim[0])):
            anim_surf = load_boss_fx_image("boss_teleport_anim_64x64.png", (64, 64))
            if anim_surf:
                self._boss_fx_teleport_anim = [anim_surf]
        spawn_frames = load_boss_fx_spawn()
        if spawn_frames and not self._is_placeholder_surface(spawn_frames[0]):
            self._boss_fx_spawn_portal = spawn_frames[0]
            self._boss_fx_spawn_portal_anim = spawn_frames[1:] if len(spawn_frames) > 1 else []
            if len(spawn_frames) >= 2:
                self._boss_fx_spawn_explosion = spawn_frames[-1] if not self._is_placeholder_surface(spawn_frames[-1]) else None
        if not self._boss_fx_spawn_portal or self._is_placeholder_surface(self._boss_fx_spawn_portal):
            self._boss_fx_spawn_portal = load_boss_fx_image("boss_spawn_portal_256x256.png", (256, 256))
        if not self._boss_fx_spawn_explosion or self._is_placeholder_surface(self._boss_fx_spawn_explosion):
            self._boss_fx_spawn_explosion = load_boss_fx_image("boss_spawn_explosion_128x128.png", (128, 128))
        death_frames = load_boss_fx_death()
        if death_frames and not self._is_placeholder_surface(death_frames[0]):
            self._boss_fx_death_frames = death_frames
            if death_frames:
                self._boss_fx_death_explosion = death_frames[0]
                self._boss_fx_death_energy = death_frames[1] if len(death_frames) > 1 else death_frames[0]
                self._boss_fx_death_particles = death_frames[2] if len(death_frames) > 2 else death_frames[0]
        if not self._boss_fx_death_explosion or self._is_placeholder_surface(self._boss_fx_death_explosion):
            self._boss_fx_death_explosion = load_boss_fx_image("boss_death_explosion_256x256.png", (256, 256))
        if not self._boss_fx_death_energy or self._is_placeholder_surface(self._boss_fx_death_energy):
            self._boss_fx_death_energy = load_boss_fx_image("boss_death_energy_128x128.png", (128, 128))
        if not self._boss_fx_death_particles or self._is_placeholder_surface(self._boss_fx_death_particles):
            self._boss_fx_death_particles = load_boss_fx_image("boss_death_particles.png", (128, 128))
        self._boss_meteor_sprite = load_boss_projectile("boss_meteor_64x64.png", (64, 64))
        if not self._boss_meteor_sprite:
            self._boss_meteor_sprite = load_boss_projectile("boss_meteor_anim_64x64.png", (64, 64))
        self._boss_meteor_impact_sprite = load_boss_projectile("boss_meteor_impact_128x128.png", (128, 128))

    def _ensure_safe_room_upgrade_icons_loaded(self) -> None:
        """Biome 3 Room 21 / Biome 4 Room 28: load upgrade choice icons (health, speed, attack, defence)."""
        if self._safe_room_upgrade_icon_health is not None:
            return
        size = (24, 24)
        self._safe_room_upgrade_icon_health = load_image(
            "assets/ui/hud/icon_health_24x24.png", size=size, exact_size=True
        )
        self._safe_room_upgrade_icon_speed = load_image(
            "assets/ui/hud/icon_speed_24x24.png", size=size, exact_size=True
        )
        self._safe_room_upgrade_icon_attack = load_image(
            "assets/ui/hud/icon_attack_24x24.png", size=size, exact_size=True
        )
        self._safe_room_upgrade_icon_defence = load_image(
            "assets/ui/hud/icon_defence_24x24.png", size=size, exact_size=True
        )

    def _ensure_gameplay_bg(self) -> None:
        """Load gameplay background from Requirements (room0_bg.png)."""
        if self._gameplay_bg is not None:
            return
        self._gameplay_bg = load_image(GAMEPLAY_BG_PATH, size=(LOGICAL_W, LOGICAL_H))

    def _ensure_phase7_tile_cache(self) -> None:
        """Load Phase 7 tile/door assets once. Floor: use only floor tile 2 PNG."""
        if self._tile_floor is not None:
            return
        sz = (TILE_SIZE, TILE_SIZE)
        full = os.path.normpath(os.path.join(PROJECT_ROOT, FLOOR_TILE_PATH))
        if os.path.isfile(full):
            self._tile_floor = load_image(FLOOR_TILE_PATH, size=sz, exact_size=True)
        else:
            self._tile_floor = load_image(FLOOR_TILE_FALLBACK, size=sz, exact_size=True)
        self._tile_floor_2 = None  # not used; single floor tile only
        LAVA = "assets/tiles/hazards/lava_tile_32x32.png"
        SLOW = "assets/tiles/hazards/slow_tile_32x32.png"
        OPEN = "assets/tiles/doors/door_open_32x32.png"
        LOCKED = "assets/tiles/doors/door_locked_32x32.png"
        SAFE = "assets/tiles/doors/door_safe_32x32.png"
        self._tile_lava = load_image(LAVA, size=sz)
        self._tile_slow = load_image(SLOW, size=sz)
        # Doors: 2 tiles wide in the wall border, so use tile-size door sprites (32×32).
        door_sz = (TILE_SIZE, TILE_SIZE)
        self._door_open = load_image(OPEN, size=door_sz, exact_size=True)
        self._door_locked = load_image(LOCKED, size=door_sz, exact_size=True)
        self._door_safe = load_image(SAFE, size=door_sz, exact_size=True)
        self._door_closed = load_image("assets/tiles/doors/door_closed_32x32.png", size=door_sz, exact_size=True)
        # Big door sprites (visual only): 96x96 (32 * 3)
        door_big = (TILE_SIZE * 3, TILE_SIZE * 3)
        self._door_open_big = load_image(OPEN, size=door_big, exact_size=True)
        self._door_closed_big = load_image("assets/tiles/doors/door_closed_32x32.png", size=door_big, exact_size=True)
        self._door_locked_big = load_image(LOCKED, size=door_big, exact_size=True)
        self._door_safe_big = load_image(SAFE, size=door_big, exact_size=True)
        # Wall tiles (Requirements: assets/tiles/walls/*.png)
        wall_sz = (TILE_SIZE, TILE_SIZE)
        self._wall_top = load_image("assets/tiles/walls/wall_top.png", size=wall_sz, exact_size=True)
        self._wall_bottom = load_image("assets/tiles/walls/wall_bottom.png", size=wall_sz, exact_size=True)
        self._wall_left = load_image("assets/tiles/walls/wall_left.png", size=wall_sz, exact_size=True)
        self._wall_right = load_image("assets/tiles/walls/wall_right.png", size=wall_sz, exact_size=True)
        self._wall_corner_tl = load_image("assets/tiles/walls/wall_corner_tl.png", size=wall_sz, exact_size=True)
        self._wall_corner_tr = load_image("assets/tiles/walls/wall_corner_tr.png", size=wall_sz, exact_size=True)
        self._wall_corner_bl = load_image("assets/tiles/walls/wall_corner_bl.png", size=wall_sz, exact_size=True)
        # wall_corner_br.png may be missing in some asset drops; fall back to BL corner if absent.
        corner_br_path = os.path.join(PROJECT_ROOT, "assets/tiles/walls/wall_corner_br.png")
        if os.path.isfile(corner_br_path):
            self._wall_corner_br = load_image("assets/tiles/walls/wall_corner_br.png", size=wall_sz, exact_size=True)
        else:
            self._wall_corner_br = self._wall_corner_bl
        # Safe Room heal object and reward drop: 70x70 (heal_health_32x32 asset scaled)
        heal_sprite_sz = (70, 70)
        self._heal_object_surf = load_image("assets/tiles/powerups/heal_health_32x32.png", size=heal_sprite_sz)
        self._reward_heal_surf = load_image("assets/tiles/powerups/heal_health_32x32.png", size=heal_sprite_sz)

    def _fill_fullscreen_floor(self, screen: pygame.Surface) -> None:
        """Fill logical screen with void (black). Room tiles draw only inside room bounds; no floor outside."""
        screen.fill(BACKGROUND_COLOR)

    def _draw_wall_border(self, screen: pygame.Surface, room) -> None:
        """Draw wall tiles over the black area surrounding the room (Requirements: assets/tiles/walls)."""
        self._ensure_phase7_tile_cache()
        ox = int((LOGICAL_W - room.pixel_width) / 2)
        oy = int((LOGICAL_H - room.pixel_height) / 2)
        pw, ph = room.pixel_width, room.pixel_height
        ts = TILE_SIZE
        # Pick surfaces (use fallbacks if some assets missing)
        top = self._wall_top or self._wall_bottom
        bottom = self._wall_bottom
        left = self._wall_left
        right = self._wall_right
        corner_tl = self._wall_corner_tl
        corner_tr = self._wall_corner_tr
        corner_bl = self._wall_corner_bl
        corner_br = self._wall_corner_br or self._wall_corner_bl
        # Top band: y in [0, oy)
        for sy in range(0, oy, ts):
            for sx in range(0, LOGICAL_W, ts):
                if top and top.get_size() == (ts, ts):
                    screen.blit(top, (sx, sy))
                else:
                    screen.fill((50, 45, 45), pygame.Rect(sx, sy, ts, ts))
        # Bottom band: y in [oy + ph, LOGICAL_H)
        for sy in range(oy + ph, LOGICAL_H, ts):
            for sx in range(0, LOGICAL_W, ts):
                if bottom and bottom.get_size() == (ts, ts):
                    screen.blit(bottom, (sx, sy))
                else:
                    screen.fill((50, 45, 45), pygame.Rect(sx, sy, ts, ts))
        # Left band: x in [0, ox), y in [oy, oy + ph)
        for sy in range(oy, oy + ph, ts):
            for sx in range(0, ox, ts):
                if left and left.get_size() == (ts, ts):
                    screen.blit(left, (sx, sy))
                else:
                    screen.fill((50, 45, 45), pygame.Rect(sx, sy, ts, ts))
        # Right band: x in [ox + pw, LOGICAL_W), y in [oy, oy + ph)
        for sy in range(oy, oy + ph, ts):
            for sx in range(ox + pw, LOGICAL_W, ts):
                if right and right.get_size() == (ts, ts):
                    screen.blit(right, (sx, sy))
                else:
                    screen.fill((50, 45, 45), pygame.Rect(sx, sy, ts, ts))
        # Four corners at room border (one tile at each corner of the room rect)
        if corner_tl and corner_tl.get_size() == (ts, ts):
            screen.blit(corner_tl, (ox - ts, oy - ts))
        if corner_tr and corner_tr.get_size() == (ts, ts):
            screen.blit(corner_tr, (ox + pw, oy - ts))
        if corner_bl and corner_bl.get_size() == (ts, ts):
            screen.blit(corner_bl, (ox - ts, oy + ph))
        if corner_br and corner_br.get_size() == (ts, ts):
            screen.blit(corner_br, (ox + pw, oy + ph))

    def _ensure_room0_prop_surfaces(self) -> None:
        """Load Room 0 prop and UI assets. Remove background (colorkey + strip) for transparency."""
        if self._room0_prop_altar is not None:
            return
        # Altar and exit: larger size, strip grey/white background so floor shows through
        self._room0_prop_altar = load_image(
            ALTAR_BOOK_PATH,
            size=ROOM0_ALTAR_SIZE,
            use_colorkey=True,
            colorkey_color=(255, 255, 255),
            corner_bg_tolerance=60,
            strip_flat_bg=True,
            exact_size=True,
        )
        self._room0_prop_exit = load_image(
            ROOM0_EXIT_PROP_PATH,
            size=ROOM0_EXIT_PROP_SIZE,
            use_colorkey=True,
            colorkey_color=(255, 255, 255),
            corner_bg_tolerance=60,
            strip_flat_bg=True,
            exact_size=True,
        )
        self._room0_prompt_bg = load_image(INTERACT_PROMPT_BG_PATH, size=(200, 48))
        # Taller panel so full story text fits inside frame (was LOGICAL_H - 80; now LOGICAL_H - 24)
        self._room0_story_panel_surf = load_image(STORY_PANEL_PATH, size=(LOGICAL_W - 80, LOGICAL_H - 24))

    def _draw_room_tiles_and_doors(self, screen: pygame.Surface, co: tuple[float, float]) -> None:
        """Phase 7: draw floor/lava/slow tiles and doors using assets from Requirements; fallback to colored rects if missing."""
        if self._room_controller is None or self._room_controller.current_room is None:
            return
        self._ensure_phase7_tile_cache()
        room = self._room_controller.current_room
        cx, cy = co
        # Door tiles (2-high) replace walls at their positions.
        door_tiles: dict[tuple[int, int], DoorState] = {}
        doors = list(self._room_controller.door_system.doors())
        for d in doors:
            door_tiles[(int(d.tile_x), int(d.tile_y))] = d.state
        border = room.wall_border()
        for ty in range(room.height):
            for tx in range(room.width):
                tile = room.get_tile_type(tx, ty)
                wx = tx * TILE_SIZE
                wy = ty * TILE_SIZE
                sx = int(wx - cx)
                sy = int(wy - cy)
                rect = pygame.Rect(sx, sy, TILE_SIZE, TILE_SIZE)
                # Walls: 2- or 4-tile border by room type; only border tiles are walls (32px each).
                is_wall = room.is_tile_in_wall_band(tx, ty) and (tx, ty) not in door_tiles
                if is_wall:
                    on_outer_top = ty == 0
                    on_outer_bottom = ty == room.height - 1
                    on_outer_left = tx == 0
                    on_outer_right = tx == room.width - 1
                    if on_outer_top and on_outer_left:
                        wall = self._wall_corner_tl
                    elif on_outer_top and on_outer_right:
                        wall = self._wall_corner_tr
                    elif on_outer_bottom and on_outer_left:
                        wall = self._wall_corner_bl
                    elif on_outer_bottom and on_outer_right:
                        wall = self._wall_corner_br
                    elif on_outer_top or ty < border:
                        wall = self._wall_top
                    elif on_outer_bottom or ty >= room.height - border:
                        wall = self._wall_bottom
                    elif on_outer_left or tx < border:
                        wall = self._wall_left
                    else:
                        wall = self._wall_right
                    if wall is not None and wall.get_size() == (TILE_SIZE, TILE_SIZE):
                        screen.blit(wall, rect.topleft)
                    else:
                        screen.fill((45, 45, 45), rect)
                    continue
                if tile == TILE_LAVA:
                    if self._tile_lava and self._tile_lava.get_size() == (TILE_SIZE, TILE_SIZE):
                        screen.blit(self._tile_lava, rect.topleft)
                    else:
                        screen.fill((220, 60, 40), rect)
                elif tile == TILE_SLOW:
                    if self._tile_slow and self._tile_slow.get_size() == (TILE_SIZE, TILE_SIZE):
                        screen.blit(self._tile_slow, rect.topleft)
                    else:
                        screen.fill((80, 80, 140), rect)
                else:
                    if self._tile_floor and self._tile_floor.get_size() == (TILE_SIZE, TILE_SIZE):
                        screen.blit(self._tile_floor, rect.topleft)
                    else:
                        screen.fill((60, 55, 50), rect)
        # Draw one 96×96 door sprite per logical doorway (2×2 gap), centered on opening.
        for center_x, center_y, _target, state, is_safe_door in self._iter_doorways(doors, room):
            if state == DoorState.OPEN:
                surf = self._door_safe_big if is_safe_door else self._door_open_big
            else:
                if is_safe_door:
                    surf = self._door_safe_big
                elif state == DoorState.CLOSED:
                    surf = self._door_closed_big
                else:
                    surf = self._door_locked_big
            if surf is None:
                continue
            sw, sh = surf.get_size()
            sx = int(center_x - cx - sw / 2)
            sy = int(center_y - cy - sh / 2)
            screen.blit(surf, (sx, sy))

    def _draw_biome4_hazard_overlays(self, screen: pygame.Surface, co: tuple[float, float]) -> None:
        """Draw Biome 4 lava/slow overlay variants on top of hazard tiles (visual only)."""
        if self._room_controller is None or self._room_controller.current_room is None:
            return
        room = self._room_controller.current_room
        hz = self._room_controller.hazard_system
        frame_idx = hz.lava_frame_index()
        cx, cy = co
        b4 = Biome4Visuals.get()
        b4.ensure_loaded()
        for ty in range(room.height):
            for tx in range(room.width):
                tile = room.get_tile_type(tx, ty)
                if tile != TILE_LAVA and tile != TILE_SLOW:
                    continue
                overlay = b4.get_lava_overlay_frame(tx, ty, frame_idx) if tile == TILE_LAVA else b4.get_slow_overlay_frame(tx, ty, frame_idx)
                if overlay is None:
                    continue
                wx = tx * TILE_SIZE
                wy = ty * TILE_SIZE
                sx = int(wx - cx)
                sy = int(wy - cy)
                screen.blit(overlay, (sx, sy))

    def _draw_biome4_props(self, screen: pygame.Surface, co: tuple[float, float]) -> None:
        """Draw Biome 4 props (seeded placement). Solid props (pillar, statue, spike, rock_cluster) also block movement."""
        if self._room_controller is None or self._room_controller.current_room is None:
            return
        room = self._room_controller.current_room
        room_index = self._room_controller.current_room_index
        doors = list(self._room_controller.door_system.doors())
        door_tiles = set((int(d.tile_x), int(d.tile_y)) for d in doors)
        for d in doors:
            door_tiles.add((int(d.tile_x), int(d.tile_y) + 1))
        placements = get_biome4_prop_placements(room, room_index, door_tiles, SEED)
        if self._biome4_blocking_tiles_room != room_index:
            self._biome4_blocking_tiles = set()
            self._biome4_blocking_tiles_room = room_index
            for surf, wx, wy, prop_type in placements:
                if prop_type not in SOLID_PROP_INDICES or surf is None:
                    continue
                sw, sh = surf.get_size()
                if sw <= TILE_SIZE and sh <= TILE_SIZE:
                    tx = int((wx + sw / 2) // TILE_SIZE)
                    ty = int((wy + sh / 2) // TILE_SIZE)
                    self._biome4_blocking_tiles.add((tx, ty))
                else:
                    # 64x64 prop: block 2x2 tiles from placement origin
                    tx0, ty0 = int(wx // TILE_SIZE), int(wy // TILE_SIZE)
                    for dx in range(2):
                        for dy in range(2):
                            self._biome4_blocking_tiles.add((tx0 + dx, ty0 + dy))
        cx, cy = co
        for surf, wx, wy, _prop_type in placements:
            if surf is None:
                continue
            screen.blit(surf, (int(wx - cx), int(wy - cy)))

    def _draw_boss_telegraphs_and_meteor_targets(self, screen: pygame.Surface, co: tuple[float, float]) -> None:
        """Draw Final Boss attack telegraphs and meteor target circles (before boss sprite)."""
        self._ensure_boss_fx_loaded()
        cx, cy = co
        boss = next((e for e in self._enemies if isinstance(e, FinalBoss)), None)
        if boss is not None and not getattr(boss, "inactive", False):
            bx, by = boss.world_pos
            # Fireball telegraph: attack_circle at boss
            if boss.state == "attack1" and getattr(boss, "_pending_fireball_dir", None) and getattr(boss, "_attack_telegraph_timer", 0) > 0:
                if self._boss_telegraph_attack_circle is not None:
                    surf = self._boss_telegraph_attack_circle
                    screen.blit(surf, (int(bx - surf.get_width() // 2 - cx), int(by - surf.get_height() // 2 - cy)))
            # Lava wave telegraph: wave_line at boss, rotated toward pending direction
            if boss.state == "attack2" and getattr(boss, "_pending_lava_wave_dir", None) and getattr(boss, "_attack_telegraph_timer", 0) > 0:
                if self._boss_telegraph_wave_line is not None:
                    dx, dy = boss._pending_lava_wave_dir
                    angle_deg = -math.degrees(math.atan2(dy, dx))
                    surf = pygame.transform.rotate(self._boss_telegraph_wave_line, angle_deg)
                    screen.blit(surf, (int(bx - surf.get_width() // 2 - cx), int(by - surf.get_height() // 2 - cy)))
            # Teleport warning: attack_circle at destination
            if boss.state == "teleport_telegraph" and getattr(boss, "_teleport_dest", None) is not None:
                tx, ty = boss._teleport_dest
                if self._boss_telegraph_attack_circle is not None:
                    surf = self._boss_telegraph_attack_circle
                    screen.blit(surf, (int(tx - surf.get_width() // 2 - cx), int(ty - surf.get_height() // 2 - cy)))
        # Meteor targets: telegraph circle + falling meteor sprite at each impact position until trigger
        METEOR_FALL_HEIGHT = 180.0
        for imp in self._meteor_impacts:
            if self._room_time >= imp["trigger_at"]:
                continue
            mx, my = imp["x"], imp["y"]
            telegraph_sec = imp.get("telegraph_sec", 1.0)
            start_at = imp.get("start_at", imp["trigger_at"] - telegraph_sec)
            progress = 1.0 - (imp["trigger_at"] - self._room_time) / telegraph_sec if telegraph_sec > 0 else 1.0
            progress = max(0.0, min(1.0, progress))
            if self._boss_telegraph_meteor_target is not None:
                surf = self._boss_telegraph_meteor_target
                screen.blit(surf, (int(mx - surf.get_width() // 2 - cx), int(my - surf.get_height() // 2 - cy)))
            if self._boss_meteor_sprite is not None:
                fall_y = my - (1.0 - progress) * METEOR_FALL_HEIGHT
                surf = self._boss_meteor_sprite
                screen.blit(surf, (int(mx - surf.get_width() // 2 - cx), int(fall_y - surf.get_height() // 2 - cy)))

    def _draw_boss_fx_overlays(self, screen: pygame.Surface, co: tuple[float, float]) -> None:
        """Draw boss spawn, death, teleport FX and meteor impact sprites (after entities)."""
        self._ensure_boss_fx_loaded()
        cx, cy = co
        # Spawn FX: portal then explosion at spawn position (skip placeholder surfaces to avoid grey box)
        if self._boss_spawn_fx_timer > 0.0 and self._boss_spawn_fx_pos is not None:
            sx, sy = self._boss_spawn_fx_pos
            if self._boss_spawn_fx_timer > 0.4 and self._boss_fx_spawn_portal is not None and not self._is_placeholder_surface(self._boss_fx_spawn_portal):
                surf = self._boss_fx_spawn_portal
                screen.blit(surf, (int(sx - surf.get_width() // 2 - cx), int(sy - surf.get_height() // 2 - cy)))
            elif self._boss_fx_spawn_explosion is not None and not self._is_placeholder_surface(self._boss_fx_spawn_explosion):
                surf = self._boss_fx_spawn_explosion
                screen.blit(surf, (int(sx - surf.get_width() // 2 - cx), int(sy - surf.get_height() // 2 - cy)))
        # Death FX: explosion, energy, particles at death position
        if self._boss_death_fx_timer > 0.0 and self._boss_death_fx_pos is not None:
            dx, dy = self._boss_death_fx_pos
            if self._boss_fx_death_explosion is not None:
                surf = self._boss_fx_death_explosion
                screen.blit(surf, (int(dx - surf.get_width() // 2 - cx), int(dy - surf.get_height() // 2 - cy)))
            if self._boss_fx_death_energy is not None:
                surf = self._boss_fx_death_energy
                screen.blit(surf, (int(dx - surf.get_width() // 2 - cx), int(dy - surf.get_height() // 2 - cy)))
            if self._boss_fx_death_particles is not None:
                surf = self._boss_fx_death_particles
                screen.blit(surf, (int(dx - surf.get_width() // 2 - cx), int(dy - surf.get_height() // 2 - cy)))
        # Teleport FX: flash at old position, smoke at new (one frame)
        if self._boss_teleport_fx_frame is not None:
            old_pos, new_pos = self._boss_teleport_fx_frame
            ox, oy = old_pos
            nx, ny = new_pos
            if self._boss_fx_teleport_flash is not None:
                surf = self._boss_fx_teleport_flash
                screen.blit(surf, (int(ox - surf.get_width() // 2 - cx), int(oy - surf.get_height() // 2 - cy)))
            if self._boss_fx_teleport_smoke is not None:
                surf = self._boss_fx_teleport_smoke
                screen.blit(surf, (int(nx - surf.get_width() // 2 - cx), int(ny - surf.get_height() // 2 - cy)))
            if self._boss_fx_teleport_anim:
                frame = self._boss_fx_teleport_anim[int(pygame.time.get_ticks() / 100) % len(self._boss_fx_teleport_anim)]
                screen.blit(frame, (int(nx - frame.get_width() // 2 - cx), int(ny - frame.get_height() // 2 - cy)))
        # Meteor impact sprites (after trigger, brief display)
        if self._boss_meteor_impact_sprite is not None:
            for m in self._meteor_impact_display:
                surf = self._boss_meteor_impact_sprite
                screen.blit(surf, (int(m["x"] - surf.get_width() // 2 - cx), int(m["y"] - surf.get_height() // 2 - cy)))

    def _hp_color(self, hp_ratio: float, is_player: bool) -> tuple[int, int, int]:
        """Return high-contrast HP color for dark dungeon, separate palettes for player/enemies."""
        r = max(0.0, min(1.0, hp_ratio))
        if is_player:
            if r < 0.10:
                return (255, 50, 50)      # bright red (danger)
            if r < 0.50:
                return (255, 140, 0)      # orange
            return (0, 170, 255)          # bright blue
        else:
            if r < 0.10:
                return (255, 60, 60)      # red
            if r < 0.50:
                return (255, 200, 0)      # yellow
            return (0, 200, 170)          # teal

    @staticmethod
    def _enemy_hp_remaining_ratio(hp: float, max_hp: float) -> float:
        """Remaining HP fraction 0..1 for bar fill (full when hp ≈ max_hp). Same units for hp and max_hp."""
        if max_hp <= 0.0:
            return 0.0
        return max(0.0, min(1.0, float(hp) / float(max_hp)))

    def _draw_boss_hp_numeric_label(
        self,
        screen: pygame.Surface,
        *,
        frame_left: float,
        frame_top: float,
        frame_width: float,
        bar_inner_top: float,
        bar_inner_height: float,
        chp: float,
        mhp: float,
    ) -> None:
        """Mini/Final Boss: current / max HP next to bar (outlined, matches player HP styling)."""
        font = _hp_hud_font(18)
        s = f"{int(chp)} / {int(mhp)}"
        label_surf = _render_outlined_hud_text(s, font, fg=(255, 255, 255), outline=(0, 0, 0))
        sw, sh = label_surf.get_width(), label_surf.get_height()
        gap = 10
        margin_r = 8
        cy = bar_inner_top + bar_inner_height / 2.0
        text_x = int(frame_left + frame_width + gap)
        text_y = int(cy - sh / 2)
        if text_x + sw > LOGICAL_W - margin_r:
            text_x = int(frame_left + (frame_width - sw) / 2)
            # Keep centered-above fallback below player HP row (avoid overlap with player bar/text).
            text_y = max(PLAYER_HP_HUD_ROW_BOTTOM + 4, int(frame_top - sh - 6))
        screen.blit(label_surf, (text_x, text_y))

    def _draw_lives_hud(self, screen: pygame.Surface) -> None:
        """Top-left: Lives: ♥ ♥ ♥ (filled = remaining lives; hollow = lost)."""
        if self._player is None or self._death_phase is not None:
            return
        lives = int(getattr(self._player, "lives", 0))
        font = _hp_hud_font(17)
        label = _render_outlined_hud_text("Lives:", font, fg=(255, 255, 255), outline=(0, 0, 0))
        margin = 14
        x = margin
        y = margin
        screen.blit(label, (x, y))
        hx = x + label.get_width() + 8
        heart_y = y
        for i in range(PLAYER_LIVES_INITIAL):
            sym = "\u2665"
            fg = (255, 72, 72) if i < lives else (110, 100, 115)
            surf = _render_outlined_hud_text(sym, font, fg=fg, outline=(0, 0, 0))
            screen.blit(surf, (hx, heart_y))
            hx += surf.get_width() + 4

    def _draw_player_health_bar(self, screen: pygame.Surface) -> None:
        """HUD player health bar at top: [Player Health] [bar] [value]; overheal (100–130) shown as extra segment."""
        if self._player is None or getattr(self._player, "base_max_hp", 0) <= 0:
            return
        font_label = _hp_hud_font(17)
        font_value = _hp_hud_font(18)

        base_max_hp = float(getattr(self._player, "base_max_hp", 1.0))
        overheal_cap = base_max_hp * SAFE_ROOM_OVERHEAL_CAP_RATIO
        hp = max(0.0, float(self._player.hp))
        # Base segment: 0–100 HP = 0–100% of bar (so 100 HP shows full)
        ratio_base = max(0.0, min(1.0, hp / base_max_hp))
        # Overheal segment: 100–130 = extra 25% of bar width
        ratio_overheal = max(0.0, min(1.0, (hp - base_max_hp) / (overheal_cap - base_max_hp))) if overheal_cap > base_max_hp else 0.0

        bar_w = 270
        bar_h = _PLAYER_HP_BAR_H
        border = 2
        top_margin = _PLAYER_HP_HUD_TOP_MARGIN
        gap = 12

        label_surf = _render_outlined_hud_text("Player Health", font_label, fg=(255, 255, 255), outline=(0, 0, 0))
        value_surf = _render_outlined_hud_text(f"{int(hp)} / {int(base_max_hp)}", font_value, fg=(255, 255, 255), outline=(0, 0, 0))

        total_w = label_surf.get_width() + gap + bar_w + gap + value_surf.get_width()
        start_x = (LOGICAL_W - total_w) / 2

        bar_x = start_x + label_surf.get_width() + gap
        bar_y = top_margin
        value_x = bar_x + bar_w + gap

        outer = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        inner = outer.inflate(-2 * border, -2 * border)

        label_y = top_margin + (bar_h - label_surf.get_height()) // 2
        value_y = top_margin + (bar_h - value_surf.get_height()) // 2
        screen.blit(label_surf, (int(start_x), label_y))
        screen.blit(value_surf, (int(value_x), value_y))

        # Background (empty HP) and border
        pygame.draw.rect(screen, (40, 40, 40), inner)
        pygame.draw.rect(screen, (180, 180, 180), outer, border)

        # Base HP fill (0–100 = full bar)
        fill_w_base = max(0, int(inner.w * ratio_base))
        if fill_w_base > 0:
            fill_rect = pygame.Rect(inner.x, inner.y, fill_w_base, inner.h)
            fill_color = self._hp_color(ratio_base, is_player=True)
            pygame.draw.rect(screen, fill_color, fill_rect)
        # Overheal fill (100–130 = extra segment to the right, 25% of bar width)
        if ratio_overheal > 0.0:
            overheal_width = int(inner.w * 0.25 * ratio_overheal)
            if overheal_width >= 1:
                oh_rect = pygame.Rect(inner.x + fill_w_base, inner.y, overheal_width, inner.h)
                pygame.draw.rect(screen, (100, 220, 255), oh_rect)

        # Subtle glow when critically low (<10% of base): soft red overlay.
        if 0.0 < ratio_base < 0.10:
            glow_alpha = int(120 * (0.10 - ratio_base) / 0.10)
            glow = pygame.Surface((bar_w + 8, bar_h + 8), pygame.SRCALPHA)
            glow.fill((255, 40, 40, glow_alpha))
            screen.blit(glow, (bar_x - 4, bar_y - 4))

    def _draw_reserve_heal_hud(self, screen: pygame.Surface) -> None:
        """Top-right: reserve pool (FIFO) as xN (v1, v2, ...) oldest first; optional cooldown hint."""
        if self._player is None or self._death_phase is not None:
            return
        pool = getattr(self._player, "reserve_heal_pool", None)
        if pool is None:
            return
        vals = [int(round(float(x))) for x in pool]
        n = len(vals)
        cd = float(getattr(self._player, "reserve_heal_cooldown_timer", 0.0))
        try:
            font = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", 18)
        except (pygame.error, OSError):
            font = pygame.font.SysFont("arial", 16)
        if n == 0:
            msg = "x0"
        else:
            inner = ", ".join(str(v) for v in vals)
            msg = f"x{n} ({inner})"
        if cd > 0.0:
            msg += f"  ({cd:.1f}s)"
        text = font.render(msg, True, (160, 255, 180))
        tw, th = text.get_size()
        margin = 14
        screen.blit(text, (int(LOGICAL_W - tw - margin), margin))

    def _draw_enemy_hit_zones(self, screen: pygame.Surface, camera_offset: tuple[float, float]) -> None:
        """Legacy enemy hit-zone circles (no longer used for damage)."""
        # Kept for reference; not called in draw() anymore.
        return

    def _draw_enemy_health_bars(self, screen: pygame.Surface, camera_offset: tuple[float, float]) -> None:
        """Small health bars above each living enemy (not training dummy), in screen space."""
        cx, cy = camera_offset
        bar_w = 40
        bar_h = 6
        border = 1
        for enemy in self._enemies:
            if getattr(enemy, "inactive", False):
                continue
            if getattr(enemy, "is_training_dummy", False):
                continue
            # Mini boss / Final Boss already have dedicated HUD bars at top; skip per-sprite bar.
            if isinstance(enemy, (MiniBoss, MiniBoss2, Biome3MiniBoss, FinalBoss)):
                continue
            max_hp = float(getattr(enemy, "max_hp", 0.0))
            if max_hp <= 0.0:
                continue
            hp = max(0.0, float(getattr(enemy, "hp", 0.0)))
            if hp <= 0.0:
                continue
            ratio = self._enemy_hp_remaining_ratio(hp, max_hp)
            # Use enemy hitbox to position bar above sprite.
            if hasattr(enemy, "get_hitbox_rect"):
                er = enemy.get_hitbox_rect()
            else:
                ex, ey = enemy.world_pos
                er = pygame.Rect(ex - 16, ey - 16, 32, 32)
            sx = int(er.centerx - cx)
            sy = int(er.top - 12 - bar_h - cy)
            outer = pygame.Rect(sx - bar_w // 2, sy, bar_w, bar_h)
            inner = outer.inflate(-2 * border, -2 * border)
            # Background and border
            pygame.draw.rect(screen, (25, 25, 25), inner)
            pygame.draw.rect(screen, (110, 110, 110), outer, border)
            # Fill (proportional remaining HP; solid red for readability)
            if ratio > 0.0:
                fill_w = max(1, int(inner.w * ratio))
                fill_rect = pygame.Rect(inner.x, inner.y, fill_w, inner.h)
                pygame.draw.rect(screen, BOSS_ENEMY_HP_BAR_COLOR, fill_rect)

    def draw(self, screen: pygame.Surface, camera_offset: tuple[float, float] | None = None) -> None:
        # Fill screen with floor tile to avoid black borders around centered rooms.
        self._fill_fullscreen_floor(screen)
        co = camera_offset if camera_offset is not None else self.camera_offset
        # Requirements: use room0_bg for gameplay (arena or Room 0). When Phase 7 room is active, tiles draw on top.
        if self._room_controller is None or self._room_controller.current_room is None:
            self._ensure_gameplay_bg()
            if self._gameplay_bg is not None:
                screen.blit(self._gameplay_bg, (0, 0))
        # Biome 4 Phase 2: optional backdrop behind tile grid (rooms 24-29).
        room = self._room_controller.current_room if self._room_controller else None
        room_idx = self._room_controller.current_room_index if self._room_controller else -1
        if room is not None and getattr(room, "biome_index", 1) == 4 and room_idx >= 0:
            bg = get_biome4_background(room_idx)
            if bg is not None:
                screen.blit(bg, (0, 0))
        # Wall border is now drawn inside each room grid (1-tile thick), so no outside border here.
        self._draw_room_tiles_and_doors(screen, co)
        # Biome 4 Phase 2: hazard overlays (lava/slow) and props after tile grid.
        if room is not None and getattr(room, "biome_index", 1) == 4:
            self._draw_biome4_hazard_overlays(screen, co)
            self._draw_biome4_props(screen, co)
        # Room 0 props on top of background (Requirements §9.3): altar (center)
        if (
            self._room_controller is not None
            and self._room_controller.current_room_index == 0
            and self._room0_altar_pos is not None
        ):
            self._ensure_room0_prop_surfaces()
            cx, cy = co
            if self._room0_prop_altar is not None:
                ax, ay = self._room0_altar_pos
                sw, sh = self._room0_prop_altar.get_size()
                screen.blit(self._room0_prop_altar, (int(ax - sw / 2 - cx), int(ay - sh / 2 - cy)))
        # Safe Room: heal object in one corner; glow when active, dimmed when used
        if (
            self._room_controller is not None
            and self._room_controller.current_room is not None
            and self._room_controller.current_room.room_type == RoomType.SAFE
            and self._safe_room_heal_pos is not None
            and self._heal_object_surf is not None
        ):
            self._ensure_phase7_tile_cache()
            hx, hy = self._safe_room_heal_pos
            cam_x, cam_y = co
            sw, sh = self._heal_object_surf.get_size()
            sx = int(hx - sw / 2 - cam_x)
            sy = int(hy - sh / 2 - cam_y)
            if self._safe_room_heal_done:
                surf = self._heal_object_surf.copy()
                surf.set_alpha(90)
                screen.blit(surf, (sx, sy))
            else:
                t = pygame.time.get_ticks() / 1000.0
                pulse = 0.7 + 0.3 * math.sin(t * 3.0)
                alpha = int(180 + 75 * pulse)
                surf = self._heal_object_surf.copy()
                surf.set_alpha(min(255, alpha))
                screen.blit(surf, (sx, sy))
        # Biome 4 Phase 2: set current biome so elites draw red aura in Biome 4 only.
        if room is not None:
            enemy_base_module.CURRENT_BIOME_INDEX = getattr(room, "biome_index", 1)
        else:
            enemy_base_module.CURRENT_BIOME_INDEX = 1
        # Boss telegraphs and meteor targets (before enemies, so under boss)
        if room is not None and room.room_type == RoomType.FINAL_BOSS:
            self._draw_boss_telegraphs_and_meteor_targets(screen, co)
        # Draw enemies before player per render order
        for enemy in self._enemies:
            enemy.draw(screen, co)
        for p in self._projectiles:
            p.draw(screen, co)
        # Enemy health bars above sprites
        self._draw_enemy_health_bars(screen, co)
        # Room 0: label above training dummy so it's visible (Requirements §9.5)
        if (
            self._room_controller is not None
            and self._room_controller.current_room_index == 0
        ):
            dummy = next((e for e in self._enemies if isinstance(e, TrainingDummy)), None)
            if dummy is not None:
                try:
                    small_font = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", 14)
                except (pygame.error, OSError):
                    small_font = pygame.font.SysFont("arial", 12)
                cx, cy = co
                sx = int(dummy.world_pos[0] - cx)
                sy = int(dummy.world_pos[1] - cy) - 70
                lbl = small_font.render("Practice target", True, (255, 240, 180))
                lw, lh = lbl.get_size()
                screen.blit(lbl, (sx - lw // 2, sy))
        if self._player is not None and not self._player.inactive and not self._is_in_life_loss_transition:
            self._player.draw(screen, co)
        # VFX layer (slash, hit sparks) after entities
        self._vfx.draw(screen, co)
        # Boss spawn/death/teleport/meteor impact FX (on top of entities)
        if room is not None and room.room_type == RoomType.FINAL_BOSS:
            self._draw_boss_fx_overlays(screen, co)
        # Green flash when Safe Room heal is collected
        if self._heal_flash_timer > 0:
            alpha = int(100 * (self._heal_flash_timer / 0.35))
            flash = pygame.Surface((LOGICAL_W, LOGICAL_H), pygame.SRCALPHA)
            flash.fill((60, 255, 100, min(255, alpha)))
            screen.blit(flash, (0, 0))
        # Debug: draw attack ranges and hitboxes in world-space over the scene.
        if DEBUG_DRAW_ATTACK_RANGE and self._player is not None:
            cx, cy = co
            px, py = self._player.world_pos
            sx = int(px - cx)
            sy = int(py - cy)
            try:
                # Short-range circle (yellow)
                from game.config import PLAYER_SHORT_ATTACK_RANGE_PX, PLAYER_LONG_ATTACK_RANGE_PX

                pygame.draw.circle(screen, (255, 255, 0), (sx, sy), PLAYER_SHORT_ATTACK_RANGE_PX, 1)
                # Long-range circle (cyan)
                pygame.draw.circle(screen, (0, 255, 255), (sx, sy), PLAYER_LONG_ATTACK_RANGE_PX, 1)
            except Exception:
                pass
            # Attack rectangles: short (red), long (magenta)
            short_rect = getattr(self._player, "_debug_short_attack_rect", None)
            if short_rect is not None:
                r = pygame.Rect(short_rect)
                r.x -= cx
                r.y -= cy
                pygame.draw.rect(screen, (255, 0, 0), r, 2)
            long_rect = getattr(self._player, "_debug_long_attack_rect", None)
            if long_rect is not None:
                r = pygame.Rect(long_rect)
                r.x -= cx
                r.y -= cy
                pygame.draw.rect(screen, (255, 0, 255), r, 2)
            # Enemy hurtboxes: green rectangles so we can see what can be hit.
            for enemy in self._enemies:
                if getattr(enemy, "inactive", False):
                    continue
                try:
                    from systems.combat import _enemy_hurtbox_rect
                except Exception:
                    _enemy_hurtbox_rect = None
                if _enemy_hurtbox_rect is None:
                    continue
                hb = _enemy_hurtbox_rect(enemy)
                r = pygame.Rect(hb)
                r.x -= cx
                r.y -= cy
                pygame.draw.rect(screen, (0, 255, 0), r, 1)
        # Phase 6: heal drop rewards — 70x70 with glowing effect
        cx, cy = co
        self._ensure_phase7_tile_cache()
        t_sec = pygame.time.get_ticks() / 1000.0
        for r in self._rewards:
            if r["collected"]:
                continue
            rx, ry = r["pos"]
            sx = int(rx - cx)
            sy = int(ry - cy)
            size = 70
            half = size // 2
            # Soft glow: larger circle behind sprite, pulsing alpha
            glow_radius = int(half * 1.4)
            pulse = 0.5 + 0.35 * math.sin(t_sec * 2.5)
            glow_alpha = int(40 + 50 * pulse)
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (100, 255, 120, glow_alpha), (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surf, (sx - glow_radius + half, sy - glow_radius + half))
            # Main sprite: 70x70 with pulsing alpha
            if self._reward_heal_surf is not None:
                sprite_alpha = int(200 + 55 * math.sin(t_sec * 2.2))
                surf = self._reward_heal_surf.copy()
                surf.set_alpha(min(255, max(180, sprite_alpha)))
                screen.blit(surf, (sx - half, sy - half))
            else:
                pygame.draw.circle(screen, (255, 220, 100), (sx, sy), half - 4)
        # Phase 6: mini boss health bar (top-center, screen-space)
        final_boss = next((e for e in self._enemies if isinstance(e, FinalBoss)), None)
        mini_boss = next((e for e in self._enemies if isinstance(e, (MiniBoss, MiniBoss2, Biome3MiniBoss))), None)
        # Boss health bar: visible whenever encounter is active (not truly dead). Stays visible during teleport and revive_wait.
        if final_boss is not None and not getattr(final_boss, "inactive", False):
            self._ensure_boss_ui_loaded()
            if self._boss_ui_frame is not None:
                fx, fy = BIOME4_BOSS_UI_ANCHOR_X, BIOME4_BOSS_UI_ANCHOR_Y
                fw, fh = BIOME4_BOSS_UI_ANCHOR_W, BIOME4_BOSS_UI_ANCHOR_H
                inner_w = fw - 4
                inner_h = fh - 20
                mhp = float(getattr(final_boss, "max_hp", 1.0))
                chp = max(0.0, float(getattr(final_boss, "hp", 0.0)))
                ratio = self._enemy_hp_remaining_ratio(chp, mhp)
                fill_w = max(0, int(inner_w * ratio))
                screen.blit(self._boss_ui_frame, (fx, fy))
                if fill_w > 0:
                    pygame.draw.rect(
                        screen,
                        BOSS_ENEMY_HP_BAR_COLOR,
                        pygame.Rect(int(fx + 2), int(fy + 10), fill_w, inner_h),
                    )
                self._draw_boss_hp_numeric_label(
                    screen,
                    frame_left=float(fx),
                    frame_top=float(fy),
                    frame_width=float(fw),
                    bar_inner_top=float(fy + 10),
                    bar_inner_height=float(inner_h),
                    chp=chp,
                    mhp=mhp,
                )
                if DEBUG_BOSS_HP_BAR:
                    t = pygame.time.get_ticks() / 1000.0
                    if t - self._boss_hp_bar_dbg_t >= 1.0:
                        self._boss_hp_bar_dbg_t = t
                        print(
                            f"[BOSS HP BAR] FinalBoss hp={chp:.1f} max={mhp:.1f} "
                            f"ratio={ratio:.3f} fill_w={fill_w} inner_w={inner_w}"
                        )
            # Boss name banner: scaled to fit the strip between player HP row and boss bar.
            if self._boss_name_banner is not None:
                bw, bh = self._boss_name_banner.get_size()
                banner_y = max(PLAYER_HP_HUD_ROW_BOTTOM + 4, BIOME4_BOSS_UI_ANCHOR_Y - bh - 4)
                screen.blit(self._boss_name_banner, (LOGICAL_W // 2 - bw // 2, banner_y))
        # Center-screen revive message (before boss reappears)
        if getattr(self, "_boss_revive_message_until", 0) > 0 and self._room_time < self._boss_revive_message_until:
            try:
                revive_font = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", 44)
            except (pygame.error, OSError):
                revive_font = pygame.font.SysFont("arial", 40)
            revive_text = revive_font.render("THE BOSS RISES AGAIN", True, (255, 220, 80))
            tw, th = revive_text.get_size()
            screen.blit(revive_text, (LOGICAL_W // 2 - tw // 2, LOGICAL_H // 2 - th // 2))
        elif mini_boss is not None and not getattr(mini_boss, "inactive", False):
            self._ensure_mini_boss_bar_loaded()
            if self._mini_boss_bar_frame is not None:
                frame_x = float(BIOME4_BOSS_UI_ANCHOR_X)
                frame_y = float(BIOME4_BOSS_UI_ANCHOR_Y)
                fw = float(BIOME4_BOSS_UI_ANCHOR_W)
                inner_w = int(fw) - 4
                inner_h = 24
                mhp = float(getattr(mini_boss, "max_hp", 1.0))
                chp = max(0.0, float(getattr(mini_boss, "hp", 0.0)))
                ratio = self._enemy_hp_remaining_ratio(chp, mhp)
                fill_w = max(0, int(inner_w * ratio))
                screen.blit(self._mini_boss_bar_frame, (int(frame_x), int(frame_y)))
                if fill_w > 0:
                    pygame.draw.rect(
                        screen,
                        BOSS_ENEMY_HP_BAR_COLOR,
                        pygame.Rect(int(frame_x + 2), int(frame_y + 8), fill_w, inner_h),
                    )
                self._draw_boss_hp_numeric_label(
                    screen,
                    frame_left=frame_x,
                    frame_top=frame_y,
                    frame_width=fw,
                    bar_inner_top=float(frame_y + 8),
                    bar_inner_height=float(inner_h),
                    chp=chp,
                    mhp=mhp,
                )
                if DEBUG_BOSS_HP_BAR:
                    t = pygame.time.get_ticks() / 1000.0
                    if t - self._boss_hp_bar_dbg_t >= 1.0:
                        self._boss_hp_bar_dbg_t = t
                        print(
                            f"[BOSS HP BAR] MiniBoss hp={chp:.1f} max={mhp:.1f} "
                            f"ratio={ratio:.3f} fill_w={fill_w} inner_w={inner_w}"
                        )
        # Player low-HP red edge glow (vignette) — uses base_max_hp so 30% of base = danger
        if self._player is not None and getattr(self._player, "base_max_hp", 0) > 0 and self._player.hp > 0:
            hp_ratio = float(self._player.hp) / float(getattr(self._player, "base_max_hp", 1.0))
            if hp_ratio <= 0.3:
                intensity = (0.3 - hp_ratio) / 0.3  # 0..1
                alpha = int(60 + 120 * intensity)
                vignette = pygame.Surface((LOGICAL_W, LOGICAL_H), pygame.SRCALPHA)
                edge = 80
                color = (255, 40, 40, alpha)
                # Top, bottom, left, right bands.
                pygame.draw.rect(vignette, color, pygame.Rect(0, 0, LOGICAL_W, edge))
                pygame.draw.rect(vignette, color, pygame.Rect(0, LOGICAL_H - edge, LOGICAL_W, edge))
                pygame.draw.rect(vignette, color, pygame.Rect(0, 0, edge, LOGICAL_H))
                pygame.draw.rect(vignette, color, pygame.Rect(LOGICAL_W - edge, 0, edge, LOGICAL_H))
                screen.blit(vignette, (0, 0))
        # Debug overlay: wall collision (blue), carved doorway tiles (yellow), door trigger (green), player (red).
        if DEBUG_DOOR_TRIGGER and self._room_controller is not None and self._player is not None:
            room = self._room_controller.current_room
            if room is not None:
                cam_x, cam_y = co
                pr = self._player.get_hitbox_rect()
                dbg_pr = pygame.Rect(int(pr.x - cam_x), int(pr.y - cam_y), pr.w, pr.h)
                pygame.draw.rect(screen, (255, 0, 0), dbg_pr, 2)
                doors = list(self._room_controller.door_system.doors())
                door_tiles = {(int(d.tile_x), int(d.tile_y)) for d in doors}
                for ty in range(room.height):
                    for tx in range(room.width):
                        wx, wy = tx * TILE_SIZE, ty * TILE_SIZE
                        sr = pygame.Rect(int(wx - cam_x), int(wy - cam_y), TILE_SIZE, TILE_SIZE)
                        if (tx, ty) in door_tiles:
                            pygame.draw.rect(screen, (255, 255, 0), sr, 1)
                            continue
                        if not room.is_tile_in_wall_band(tx, ty):
                            continue
                        pygame.draw.rect(screen, (0, 0, 255), sr, 1)
                cur_idx = self._room_controller.current_room_index
                B = room.wall_border()
                playable_right_x = (room.width - B) * TILE_SIZE
                inner_bottom_center_y = (room.height - B - 0.5) * TILE_SIZE
                trigger_shrink = 20
                trigger_half_w = (TILE_SIZE * 3 - trigger_shrink * 2) // 2
                for center_x, center_y, target_room_index, state, _ in self._iter_doorways(doors, room):
                    if state != DoorState.OPEN:
                        continue
                    if target_room_index > cur_idx:
                        center_x = playable_right_x - trigger_half_w
                        center_y = inner_bottom_center_y
                    door_rect = pygame.Rect(0, 0, TILE_SIZE * 3, TILE_SIZE * 3)
                    door_rect.center = (center_x, center_y)
                    trigger_rect = door_rect.inflate(-trigger_shrink, -trigger_shrink)
                    dbg_tr = pygame.Rect(
                        int(trigger_rect.x - cam_x), int(trigger_rect.y - cam_y),
                        trigger_rect.w, trigger_rect.h
                    )
                    pygame.draw.rect(screen, (0, 255, 0), dbg_tr, 2)
        # Player health bar HUD (always visible)
        self._draw_lives_hud(screen)
        self._draw_player_health_bar(screen)
        self._draw_reserve_heal_hud(screen)
        try:
            font = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", 18)
        except (pygame.error, OSError):
            font = pygame.font.SysFont("arial", 16)
        label = font.render(
            "WASD move | Space dash | LMB short | RMB long | J block | K parry | H reserve heal | Esc quit",
            True,
            (200, 200, 200),
        )
        screen.blit(label, (20, LOGICAL_H - 30))
        # Debug: show "HIT!" for 0.5s when player deals damage to an enemy
        now = pygame.time.get_ticks() / 1000.0
        if self._debug_player_hit_time > 0 and (now - self._debug_player_hit_time) < 0.5:
            try:
                hit_font = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", 36)
            except (pygame.error, OSError):
                hit_font = pygame.font.SysFont("arial", 32)
            hit_label = hit_font.render("HIT!", True, (255, 80, 80))
            screen.blit(hit_label, (LOGICAL_W // 2 - hit_label.get_width() // 2, 12))
        if DEBUG_COMBAT_HITS and self._debug_combat_lines:
            try:
                dbg_font = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", 14)
            except (pygame.error, OSError):
                dbg_font = pygame.font.SysFont("consolas", 12)
            pad = 6
            x0, y0 = 10, 10
            rendered = [dbg_font.render(line, True, (235, 235, 235)) for line in self._debug_combat_lines]
            w = max(s.get_width() for s in rendered) + pad * 2
            h = sum(s.get_height() for s in rendered) + pad * 2 + 2 * (len(rendered) - 1)
            bg = pygame.Surface((w, h), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 160))
            screen.blit(bg, (x0, y0))
            yy = y0 + pad
            for s in rendered:
                screen.blit(s, (x0 + pad, yy))
                yy += s.get_height() + 2
        # Room 0: training hint (Requirements §9.5 — player uses dummy to practice short/long attack and dash)
        if (
            self._room_controller is not None
            and self._room_controller.current_room_index == 0
        ):
            hint = font.render("Training: hit the dummy (bottom-left) to practice short attack (LMB), long attack (RMB), and dash (Space)", True, (220, 220, 180))
            screen.blit(hint, (20, LOGICAL_H - 52))

        # Safe Room: "Press [F] to collect heal (+30%)" when near heal object
        if (
            self._room_controller is not None
            and self._room_controller.current_room is not None
            and self._room_controller.current_room.room_type == RoomType.SAFE
            and self._player is not None
            and not self._safe_room_heal_done
            and self._near_safe_room_heal
        ):
            self._ensure_room0_prop_surfaces()
            if self._room0_prompt_bg is not None:
                pw, ph = self._room0_prompt_bg.get_size()
                screen.blit(self._room0_prompt_bg, (LOGICAL_W // 2 - pw // 2, LOGICAL_H // 2 - 80))
            prompt_text = font.render("Press [F] to collect heal (+30% max HP)", True, (240, 240, 240))
            tw, th = prompt_text.get_size()
            screen.blit(prompt_text, (LOGICAL_W // 2 - tw // 2, LOGICAL_H // 2 - 80 + (48 - th) // 2))
        # Biome 3 Room 21 safe room: 3 upgrade choices (pick one with 1/2/3)
        if (
            self._room_controller is not None
            and self._room_controller.current_room is not None
            and self._room_controller.current_room_index == BIOME3_SAFE_ROOM_INDEX
            and self._room_controller.current_room.room_type == RoomType.SAFE
            and not self._safe_room_upgrade_chosen_this_room
            and self._player is not None
        ):
            self._ensure_safe_room_upgrade_icons_loaded()
            self._ensure_room0_prop_surfaces()
            # Panel: title + 3 options with icons (deterministic order: 1=Health, 2=Speed, 3=Attack)
            panel_w, panel_h = 380, 160
            panel_x = (LOGICAL_W - panel_w) // 2
            panel_y = (LOGICAL_H - panel_h) // 2
            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel.fill((40, 40, 50, 220))
            pygame.draw.rect(panel, (180, 180, 200), (0, 0, panel_w, panel_h), 2)
            screen.blit(panel, (panel_x, panel_y))
            try:
                title_font = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", 18)
                row_font = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", 16)
            except (pygame.error, OSError):
                title_font = pygame.font.SysFont("arial", 16)
                row_font = pygame.font.SysFont("arial", 14)
            title = title_font.render("Choose one upgrade (1, 2, or 3)", True, (240, 240, 240))
            screen.blit(title, (panel_x + (panel_w - title.get_width()) // 2, panel_y + 12))
            row_y = panel_y + 44
            icon_size = 24
            options = [
                (self._safe_room_upgrade_icon_health, "1. Health +20% max HP"),
                (self._safe_room_upgrade_icon_speed, "2. Speed +10% movement"),
                (self._safe_room_upgrade_icon_attack, "3. Attack +12% damage"),
            ]
            for icon_surf, label in options:
                if icon_surf is not None:
                    screen.blit(icon_surf, (panel_x + 24, row_y - 2))
                txt = row_font.render(label, True, (220, 220, 220))
                screen.blit(txt, (panel_x + 24 + icon_size + 12, row_y))
                row_y += 36
        # Biome 4 Room 28 safe room: 4 upgrade options, choose exactly 2 (1/2/3/4)
        if (
            self._room_controller is not None
            and self._room_controller.current_room is not None
            and self._room_controller.current_room_index == BIOME4_SAFE_ROOM_INDEX
            and self._room_controller.current_room.room_type == RoomType.SAFE
            and not self._safe_room_upgrade_chosen_this_room
            and self._player is not None
            and (getattr(self, "_safe_room_upgrade_pending", False) or getattr(self, "_safe_room_biome4_picks_remaining", 0) > 0)
        ):
            self._ensure_safe_room_upgrade_icons_loaded()
            self._ensure_room0_prop_surfaces()
            panel_w, panel_h = 400, 200
            panel_x = (LOGICAL_W - panel_w) // 2
            panel_y = (LOGICAL_H - panel_h) // 2
            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel.fill((40, 40, 50, 220))
            pygame.draw.rect(panel, (180, 180, 200), (0, 0, panel_w, panel_h), 2)
            screen.blit(panel, (panel_x, panel_y))
            try:
                title_font = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", 18)
                row_font = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", 16)
            except (pygame.error, OSError):
                title_font = pygame.font.SysFont("arial", 16)
                row_font = pygame.font.SysFont("arial", 14)
            picks_left = getattr(self, "_safe_room_biome4_picks_remaining", 0)
            title = title_font.render(f"Choose two upgrades (1-4) — {picks_left} left", True, (240, 240, 240))
            screen.blit(title, (panel_x + (panel_w - title.get_width()) // 2, panel_y + 12))
            row_y = panel_y + 44
            icon_size = 24
            options_b4 = [
                (self._safe_room_upgrade_icon_health, "1. Health +20% max HP"),
                (self._safe_room_upgrade_icon_speed, "2. Speed +10% movement"),
                (self._safe_room_upgrade_icon_attack, "3. Attack +12% damage"),
                (self._safe_room_upgrade_icon_defence, "4. Defence -12% incoming damage"),
            ]
            for icon_surf, label in options_b4:
                if icon_surf is not None:
                    screen.blit(icon_surf, (panel_x + 24, row_y - 2))
                txt = row_font.render(label, True, (220, 220, 220))
                screen.blit(txt, (panel_x + 24 + icon_size + 12, row_y))
                row_y += 36
        # Room 0: "Press [E] to Read" when near altar (Requirements §9.4.1)
        if (
            not self._room0_story_panel_open
            and self._room0_altar_pos is not None
            and self._player is not None
            and self._room_controller is not None
            and self._room_controller.current_room_index == 0
        ):
            px, py = self._player.world_pos
            ax, ay = self._room0_altar_pos
            if math.hypot(px - ax, py - ay) <= ALTAR_INTERACTION_RADIUS_PX:
                self._ensure_room0_prop_surfaces()
                if self._room0_prompt_bg is not None:
                    pw, ph = self._room0_prompt_bg.get_size()
                    screen.blit(self._room0_prompt_bg, (LOGICAL_W // 2 - pw // 2, LOGICAL_H // 2 - 80))
                prompt_text = font.render("Press [E] to Read", True, (240, 240, 240))
                tw, th = prompt_text.get_size()
                screen.blit(prompt_text, (LOGICAL_W // 2 - tw // 2, LOGICAL_H // 2 - 80 + (48 - th) // 2))

        # Room 0: story panel overlay (Requirements §9.4.2, §9.4.3)
        if self._room0_story_panel_open:
            overlay = pygame.Surface((LOGICAL_W, LOGICAL_H))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            panel_rect = None
            if self._room0_story_panel_surf is not None:
                pw, ph = self._room0_story_panel_surf.get_size()
                px = (LOGICAL_W - pw) // 2
                py = (LOGICAL_H - ph) // 2
                screen.blit(self._room0_story_panel_surf, (px, py))
                panel_rect = pygame.Rect(px, py, pw, ph)
            # Story text (wrapped) aligned inside frame
            try:
                panel_font_body = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", 18)
                panel_font_title = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", 22)
            except (pygame.error, OSError):
                panel_font_body = pygame.font.SysFont("georgia", 16)
                panel_font_title = pygame.font.SysFont("georgia", 20)
            if panel_rect is not None:
                inner_margin_x = 80
                inner_margin_y = 56
                margin_left = panel_rect.x + inner_margin_x
                margin_right = panel_rect.x + panel_rect.w - inner_margin_x
                max_w = max(100, margin_right - margin_left)
                y = panel_rect.y + inner_margin_y
            else:
                margin_left = 60
                max_w = LOGICAL_W - 2 * margin_left
                y = 120
            paragraphs = ROOM0_STORY_TEXT.split("\n\n")
            for idx, para in enumerate(paragraphs):
                is_title = idx == 0
                font_use = panel_font_title if is_title else panel_font_body
                color = (245, 225, 170) if is_title else (220, 220, 220)
                # Simple word wrap
                words = para.replace("\n", " ").split()
                line = ""
                for w in words:
                    test = line + (" " if line else "") + w
                    if font_use.size(test)[0] <= max_w:
                        line = test
                    else:
                        if line:
                            surf = font_use.render(line, True, color)
                            screen.blit(surf, (margin_left, y))
                            y += surf.get_height() + 4
                        line = w
                if line:
                    surf = font_use.render(line, True, color)
                    screen.blit(surf, (margin_left, y))
                    y += surf.get_height() + (10 if is_title else 8)
                # Extra spacing between paragraphs inside frame
                y += 2
            close_hint_font = panel_font_body
            close_hint = close_hint_font.render("Press E or ESC to close", True, (180, 180, 180))
            screen.blit(close_hint, (LOGICAL_W // 2 - close_hint.get_width() // 2, LOGICAL_H - 60))

        # Phase 3: victory overlay (after beating final boss, last room exit)
        if self._victory_phase:
            self._ensure_boss_ui_loaded()
            center_x, center_y = LOGICAL_W // 2, LOGICAL_H // 2
            
            # Phase 1: first 2 seconds -> victory banner
            if self._victory_timer < 2.0:
                if self._victory_banner is not None:
                    banner_rect = self._victory_banner.get_rect(center=(center_x, center_y))
                    screen.blit(self._victory_banner, banner_rect.topleft)
            # Phase 2: next 3 seconds -> blackscreen + victory banner
            else:
                screen.fill((0, 0, 0))

                if self._victory_bg is not None:
                    bg_rect = self._victory_bg.get_rect(center=(center_x, center_y))
                    screen.blit(self._victory_bg, bg_rect.topleft)

        self._draw_life_loss_overlay(screen)

        # Death sequence overlays
        if self._death_phase is not None:
            # Keep the world fully bright so elites and their yellow glow never look greyed out.
            # Only draw the "GAME OVER" label during the final phase.
            if self._death_phase == "game_over":
                try:
                    big_font = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", 40)
                except (pygame.error, OSError):
                    big_font = pygame.font.SysFont("arial", 36)
                text = big_font.render("GAME OVER", True, (230, 230, 230))
                tw, th = text.get_size()
                screen.blit(text, (LOGICAL_W // 2 - tw // 2, LOGICAL_H // 2 - th // 2))

        # In-run pause: dim + PAUSED + Resume (logical coords; mouse mapped in update/handle_event)
        if self._paused:
            self._draw_pause_overlay(screen)

        # AI debug overlay (after all gameplay/UI overlays; read-only)
        self._debug_overlay.draw(screen)

    def _draw_pause_overlay(self, screen: pygame.Surface) -> None:
        self._ensure_pause_menu_assets()
        dim = pygame.Surface((LOGICAL_W, LOGICAL_H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 150))
        screen.blit(dim, (0, 0))
        if self._pause_paused_font is None:
            try:
                self._pause_paused_font = pygame.font.Font("assets/fonts/PixelifySans-Variable.ttf", 36)
            except (pygame.error, OSError):
                self._pause_paused_font = pygame.font.SysFont("arial", 32)
        pt = self._pause_paused_font.render("PAUSED", True, (240, 240, 240))
        screen.blit(pt, (LOGICAL_W // 2 - pt.get_width() // 2, 28))
        if self._pause_resume_rect is not None:
            surf = (
                self._pause_resume_hover
                if (self._pause_resume_hovered and self._pause_resume_hover is not None)
                else self._pause_resume_normal
            )
            if surf is not None:
                screen.blit(surf, self._pause_resume_rect.topleft)
        if self._pause_main_rect is not None:
            ms = (
                self._pause_main_hover
                if (self._pause_main_hovered and self._pause_main_hover is not None)
                else self._pause_main_normal
            )
            if ms is not None:
                screen.blit(ms, self._pause_main_rect.topleft)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
            self._debug_overlay.toggle()
            return True
        # Room 0 story panel: E or ESC closes (Requirements §9.4.2)
        if self._room0_story_panel_open and event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_e, pygame.K_ESCAPE):
                self._room0_story_panel_open = False
                return True
        # In-run pause menu: only Resume + ESC (same logical mouse mapping as main menu)
        if self._paused:
            if event.type == pygame.KEYUP:
                self._keys_held.discard(event.key)
                return True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                print("[PAUSE] ESC resumes game")
                self._set_paused(False, reason="ESC resume")
                return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._ensure_pause_menu_assets()
                lp = _pause_screen_to_logical(event.pos)
                if self._pause_resume_rect is not None and self._pause_resume_rect.collidepoint(lp):
                    print("[PAUSE] Resume button clicked -> continue run")
                    self._set_paused(False, reason="Resume click")
                    return True
                if self._pause_main_rect is not None and self._pause_main_rect.collidepoint(lp):
                    self._go_to_main_menu_from_pause()
                    return True
                return True
            return True
        if self._is_in_life_loss_transition:
            if event.type == pygame.KEYUP:
                self._keys_held.discard(event.key)
            return True
        # During death or victory sequence, ignore player input.
        if self._death_phase is not None or self._victory_phase:
            return True
        if event.type == pygame.KEYDOWN:
            self._keys_held.add(event.key)
            # Safe Room: F to collect heal (+30% max HP); excess → reserve charges (H is reserve heal)
            if event.key == pygame.K_f and self._player is not None:
                if (
                    self._room_controller is not None
                    and self._room_controller.current_room is not None
                    and self._room_controller.current_room.room_type == RoomType.SAFE
                    and not self._safe_room_heal_done
                    and self._near_safe_room_heal
                    and self._safe_room_heal_pos is not None
                ):
                    base_max_hp = getattr(self._player, "base_max_hp", 100.0)
                    _cr = self._room_controller.current_room
                    _psnh = self.player_state.name if self.player_state is not None else None
                    _bidx_safe = int(getattr(_cr, "biome_index", 1)) if _cr is not None else 1
                    if _bidx_safe == 2:
                        _srm = biome2_safe_room_heal_multiplier(_psnh)
                    elif _bidx_safe == 3:
                        _srm = biome3_safe_room_heal_multiplier(_psnh)
                    elif _bidx_safe == 4:
                        _srm = biome4_safe_room_heal_multiplier(_psnh)
                    else:
                        _srm = 1.0
                    heal_amount = float(base_max_hp) * SAFE_ROOM_HEAL_PERCENT * _srm
                    applied = self._player.apply_incoming_heal(heal_amount)
                    self._metrics.record_healing(applied)
                    self._safe_room_heal_done = True
                    self._safe_room_upgrade_pending = True
                    if self._room_controller.current_room_index == BIOME4_SAFE_ROOM_INDEX:
                        self._safe_room_biome4_picks_remaining = 2
                        self._safe_room_biome4_chosen = set()
                    self._vfx.spawn_floating_text(self._safe_room_heal_pos, "+30% Health", (80, 255, 120))
                    self._heal_flash_timer = 0.35
                    return True
            # Reserve heal: H applies front of FIFO reserve_heal_pool (exact HP), cooldown anti-spam
            if event.key == pygame.K_h and self._player is not None:
                if float(getattr(self._player, "reserve_heal_cooldown_timer", 0.0)) <= 0.0:
                    healed = self._player.try_consume_reserve_heal()
                    if healed > 0.0:
                        self._metrics.record_healing(healed)
                        self._player.reserve_heal_cooldown_timer = float(RESERVE_HEAL_USE_COOLDOWN_SEC)
                        self._heal_flash_timer = 0.35
                return True
            # Room 0 altar: E to open story panel when near (Requirements §9.4.1)
            if event.key == pygame.K_e and self._room0_altar_pos and self._player is not None:
                if (
                    self._room_controller is not None
                    and self._room_controller.current_room_index == 0
                    and not self._room0_story_panel_open
                ):
                    px, py = self._player.world_pos
                    ax, ay = self._room0_altar_pos
                    if math.hypot(px - ax, py - ay) <= ALTAR_INTERACTION_RADIUS_PX:
                        self._room0_story_panel_open = True
                        return True
            if event.key == pygame.K_SPACE:
                self._dash_request = True
                return True
            if event.key == pygame.K_k:
                self._parry_request = True
                if DEBUG_BLOCK_PARRY_TRACE:
                    print(
                        f"[BLOCK_PARRY_TRACE] KEYDOWN K -> _parry_request=True "
                        f"paused={self._paused} story_panel={self._room0_story_panel_open} "
                        f"J_held={pygame.K_j in self._keys_held}"
                    )
                return True
            if event.key == pygame.K_ESCAPE:
                if self._room0_story_panel_open:
                    self._room0_story_panel_open = False
                    return True
                print("[PAUSE] ESC pauses game")
                self._set_paused(True, reason="ESC pause")
                return True
            # Biome 4 Room 28 safe room: 4 options, choose exactly 2 (1/2/3/4)
            if (
                self._room_controller is not None
                and self._room_controller.current_room is not None
                and self._room_controller.current_room_index == BIOME4_SAFE_ROOM_INDEX
                and self._room_controller.current_room.room_type == RoomType.SAFE
                and not self._safe_room_upgrade_chosen_this_room
                and self._player is not None
                and event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4)
            ):
                choice = (event.key - pygame.K_1) + 1  # 1, 2, 3, or 4
                if choice not in self._safe_room_biome4_chosen:
                    if choice == 1:
                        self._player.base_max_hp *= SAFE_ROOM_UPGRADE_HEALTH_MULT
                        self._player.max_hp = self._player.base_max_hp
                        self._player.hp = min(self._player.hp, self._player.max_hp)
                    elif choice == 2:
                        self._player.move_speed_mult = SAFE_ROOM_UPGRADE_SPEED_MULT
                    elif choice == 3:
                        self._player.attack_damage_mult = SAFE_ROOM_UPGRADE_ATTACK_MULT
                    elif choice == 4:
                        self._player.damage_taken_mult = SAFE_ROOM_UPGRADE_DEFENCE_MULT
                    self._safe_room_biome4_chosen.add(choice)
                    self._safe_room_biome4_picks_remaining = max(0, self._safe_room_biome4_picks_remaining - 1)
                    if len(self._safe_room_biome4_chosen) >= 2:
                        self._safe_room_upgrade_chosen_this_room = True
                return True
            # Biome 3 Room 21 safe room: 1=Health, 2=Speed, 3=Attack (pick one)
            if (
                self._room_controller is not None
                and self._room_controller.current_room is not None
                and self._room_controller.current_room_index == BIOME3_SAFE_ROOM_INDEX
                and self._room_controller.current_room.room_type == RoomType.SAFE
                and not self._safe_room_upgrade_chosen_this_room
                and self._player is not None
                and event.key in (pygame.K_1, pygame.K_2, pygame.K_3)
            ):
                choice = (event.key - pygame.K_1) + 1  # 1, 2, or 3
                if choice == 1:  # Health +20% max HP
                    self._player.base_max_hp *= SAFE_ROOM_UPGRADE_HEALTH_MULT
                    self._player.max_hp = self._player.base_max_hp
                    self._player.hp = min(self._player.hp, self._player.max_hp)
                elif choice == 2:  # Speed +10%
                    self._player.move_speed_mult = SAFE_ROOM_UPGRADE_SPEED_MULT
                elif choice == 3:  # Attack +12%
                    self._player.attack_damage_mult = SAFE_ROOM_UPGRADE_ATTACK_MULT
                self._safe_room_upgrade_chosen_this_room = True
                return True
            if getattr(self, "_safe_room_upgrade_pending", False) and event.key in (pygame.K_1, pygame.K_2):
                self._safe_room_upgrade_pending = False
                return True
        if event.type == pygame.KEYUP:
            self._keys_held.discard(event.key)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if DEBUG_LIVE_SHORT_ATTACK_TRACE:
                    print(
                        f"[LIVE_TRACE] MOUSEBUTTONDOWN btn=1 GameScene paused={self._paused} "
                        f"story_panel_open={self._room0_story_panel_open} "
                        f"death_phase={self._death_phase!r} victory={self._victory_phase} "
                        f"_attack_short_request_before={self._attack_short_request}"
                    )
                # Room 0 story panel: combat is disabled in update() (short_req=False). Do not arm the
                # one-shot flag or it is cleared at end of frame without Player ever seeing short_req=True.
                if self._room0_story_panel_open:
                    if DEBUG_LIVE_SHORT_ATTACK_TRACE:
                        print("[LIVE_TRACE] LMB not armed for attack (story panel open; E/ESC to close)")
                    return True
                if DEBUG_SHORT_ATTACK_INPUT:
                    print("[SHORT_ATK_IN] LMB MOUSEBUTTONDOWN: arming _attack_short_request")
                self._attack_short_request = True
                # Force poll edge same frame as the event so left_edge matches MOUSEBUTTONDOWN even if
                # _prev_mouse_left was stuck True (missed MOUSEBUTTONUP / focus quirks).
                self._prev_mouse_left = False
                if DEBUG_LIVE_SHORT_ATTACK_TRACE:
                    print(
                        f"[LIVE_TRACE] MOUSEBUTTONDOWN -> _attack_short_request=True "
                        f"(after={self._attack_short_request})"
                    )
                if DEBUG_PLAYER_ATTACK_PROXIMITY:
                    print("[GAMESCENE] short attack request flag (MOUSEBUTTONDOWN button=1)")
                return True
            if event.button == 3:
                if self._room0_story_panel_open:
                    if DEBUG_LIVE_SHORT_ATTACK_TRACE:
                        print("[LIVE_TRACE] RMB not armed (story panel open)")
                    return True
                self._attack_long_request = True
                if DEBUG_PLAYER_ATTACK_PROXIMITY:
                    print("[GAMESCENE] long attack request flag (MOUSEBUTTONDOWN button=3)")
                return True
        return False
