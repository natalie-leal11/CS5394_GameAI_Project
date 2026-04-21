# Core engine and project configuration.
# All procedural systems MUST use SEED for reproducibility.

import os

SEED = 42

# Project root (directory containing assets/). Resolve so assets load regardless of cwd.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = _PROJECT_ROOT

# Fixed logical resolution (do NOT auto-size).
LOGICAL_W = 960
LOGICAL_H = 640

# Room grid fills viewport: cols/rows from logical size (room fills full window).
ROOM_COLS = LOGICAL_W // 32  # 32 = TILE_SIZE; keep literal so config loads before TILE_SIZE if needed
ROOM_ROWS = LOGICAL_H // 32

# Engine.
FPS = 60
TILE_SIZE = 32

# Sprite sizes (pixels). Increased for visibility (player, altar, dummy, exit).
PLAYER_SIZE = (96, 96)
# Hitbox (body) for combat/collision: proportional to sprite.
PLAYER_HITBOX_W = 32
PLAYER_HITBOX_H = 52
# Movement / wall collision / room clamp: tighter body than combat hitbox (same center as world_pos).
PLAYER_MOVEMENT_HITBOX_W = 32
PLAYER_MOVEMENT_HITBOX_H = 32
BRUTE_SIZE = (96, 96)
MINI_BOSS_SIZE = (128, 128)   # Mini Boss / Mini Boss 2 / Biome 3 Mini Boss (imposing vs 96×96 player)
FINAL_BOSS_SIZE = (128, 128)

# --- Phase 3: Enemy system ---
# Enemy logical sizes (readability + bosses more imposing; player remains 96×96).
ENEMY_SWARM_SIZE = (64, 64)
ENEMY_FLANKER_SIZE = (56, 56)
ENEMY_BRUTE_SIZE = BRUTE_SIZE  # 96×96
ENEMY_HEAVY_SIZE = (104, 104)  # Biome 2/3: Heavy armored

# Base stats (Biome 1 baseline; match Requirements tables).
ENEMY_SWARM_BASE_HP = 30      # Melee Grunt
ENEMY_FLANKER_BASE_HP = 22    # Fast Flanker
ENEMY_BRUTE_BASE_HP = 50      # Brute
ENEMY_HEAVY_BASE_HP = 60      # Biome 2: Heavy armored

ENEMY_SWARM_BASE_DAMAGE = 10  # Melee Grunt basic swing
ENEMY_FLANKER_BASE_DAMAGE = 8  # Fast Flanker quick strike
ENEMY_BRUTE_BASE_DAMAGE = 10   # Brute heavy hit
ENEMY_HEAVY_BASE_DAMAGE = 12   # Biome 2: Heavy armored

# Minimum separation / attack radius (px) — enemies must not visually overlap player.
ENEMY_SWARM_STOP_DISTANCE = 40
ENEMY_FLANKER_STOP_DISTANCE = 50
ENEMY_BRUTE_STOP_DISTANCE = 72
ENEMY_HEAVY_STOP_DISTANCE = 82
ENEMY_RANGED_STOP_DISTANCE = 180

# Extra px on base stop for walk→attack only (identity per type; overlap push still uses base stop).
ENEMY_MELEE_ENGAGE_BUFFER_SWARM = 3
ENEMY_MELEE_ENGAGE_BUFFER_FLANKER = 5
ENEMY_MELEE_ENGAGE_BUFFER_BRUTE = 10
ENEMY_MELEE_ENGAGE_BUFFER_HEAVY = 18

# Non-boss melee hit tuning: scale arc radius + optional extra reach on body-distance fallback.
ENEMY_MELEE_HIT_RADIUS_MULT_SWARM = 1.02
ENEMY_MELEE_HIT_RADIUS_MULT_FLANKER = 1.05
ENEMY_MELEE_HIT_RADIUS_MULT_BRUTE = 1.10
ENEMY_MELEE_HIT_RADIUS_MULT_HEAVY = 1.12
ENEMY_MELEE_BODY_FALLBACK_EXTRA_SWARM = 0
ENEMY_MELEE_BODY_FALLBACK_EXTRA_FLANKER = 4
ENEMY_MELEE_BODY_FALLBACK_EXTRA_BRUTE = 8
ENEMY_MELEE_BODY_FALLBACK_EXTRA_HEAVY = 12
# Added to center-distance melee check (all standard melee; bosses use separate paths in combat.py)
ENEMY_MELEE_BODY_EXTRA_UNIVERSAL_PX = 8.0
# Flanker only: extra px when testing distance from player to enemy→arc segment (angled approaches).
ENEMY_MELEE_FLANKER_SEGMENT_REACH_PX = 8.0

# Enemy melee attack hitbox radii/offsets and cooldowns (Biome 1).
ENEMY_SWARM_ATTACK_RADIUS = 20.0
ENEMY_SWARM_ATTACK_OFFSET = 20.0
ENEMY_SWARM_ATTACK_COOLDOWN_SEC = 1.0

ENEMY_FLANKER_ATTACK_RADIUS = 17.0
ENEMY_FLANKER_ATTACK_OFFSET = 18.0
ENEMY_FLANKER_ATTACK_COOLDOWN_SEC = 1.0

ENEMY_BRUTE_ATTACK_RADIUS = 38.0
ENEMY_BRUTE_ATTACK_OFFSET = 22.0
ENEMY_BRUTE_ATTACK_COOLDOWN_SEC = 1.2

ENEMY_HEAVY_ATTACK_RADIUS = 56.0
ENEMY_HEAVY_ATTACK_OFFSET = 24.0
ENEMY_HEAVY_ATTACK_COOLDOWN_SEC = 1.7

# Biome 3: Ranged (projectile attacker; no melee).
ENEMY_RANGED_SIZE = (72, 72)
ENEMY_RANGED_BASE_HP = 28
ENEMY_RANGED_BASE_DAMAGE = 8
ENEMY_RANGED_MOVE_SPEED = 60
ENEMY_RANGED_ATTACK_COOLDOWN_SEC = 1.6
RANGED_PROJECTILE_SPEED = 180
RANGED_PROJECTILE_DAMAGE = 8
RANGED_PROJECTILE_LIFETIME_SEC = 3.0
# Kiting: back away if closer than this, approach if farther than RANGED_KITE_FAR_THRESHOLD, strafe in between.
RANGED_KITE_CLOSE_THRESHOLD = 120
RANGED_KITE_FAR_THRESHOLD = 210
# When hitboxes overlap player, nudge apart by this much per correction (avoid teleport to stop distance).
RANGED_PLAYER_OVERLAP_PUSH_PX = 16
# Strafe speed factor (of ENEMY_RANGED_MOVE_SPEED) when in ideal band; lower while firing.
RANGED_STRAFE_SPEED_FACTOR = 0.7
RANGED_ATTACK_STRAFE_SPEED_FACTOR = 0.5

# Radius (px) of the visible hit zone around each enemy; player inside this circle when attacking deals damage. Large so hits always register.
ENEMY_HIT_ZONE_RADIUS = 400

# Movement speeds (px/sec), straight from Requirements (§7, speed table).
ENEMY_SWARM_MOVE_SPEED = 100   # Melee Grunt
ENEMY_FLANKER_MOVE_SPEED = 260  # Fast Flanker
ENEMY_BRUTE_MOVE_SPEED = 120    # Heavy/Brute
ENEMY_HEAVY_MOVE_SPEED = 100    # Biome 2: Heavy armored (slow)

# Contact damage every 0.5s while overlapping.
ENEMY_CONTACT_DAMAGE_INTERVAL_SEC = 0.5

# Elite modifiers (HP +40%, damage +20%).
ENEMY_ELITE_HP_MULT = 1.4
ENEMY_ELITE_DAMAGE_MULT = 1.2

# Simple room/play bounds for Phase 3 (clamp enemies to on-screen area with small padding).
ENEMY_BOUNDS_PAD = 32
ENEMY_MIN_X = ENEMY_BOUNDS_PAD
ENEMY_MIN_Y = ENEMY_BOUNDS_PAD
ENEMY_MAX_X = LOGICAL_W - ENEMY_BOUNDS_PAD
ENEMY_MAX_Y = LOGICAL_H - ENEMY_BOUNDS_PAD

# Enemy movement/collision body (centered on world_pos). Smaller than sprite size for top-edge navigation.
# Keys match enemy_type strings; "default" fallback.
ENEMY_MOVEMENT_HITBOX: dict[str, tuple[int, int]] = {
    "swarm": (40, 40),
    "flanker": (44, 44),
    "brute": (72, 72),
    "heavy": (80, 80),
    "ranged": (52, 52),
    "mini_boss": (96, 96),
    "mini_boss_2": (96, 96),
    "final_boss": (112, 112),
    "default": (48, 48),
}


def enemy_movement_size_tuple(enemy_type: str) -> tuple[int, int]:
    """Width × height for movement clamp and wall collision (not combat hitbox)."""
    return ENEMY_MOVEMENT_HITBOX.get(enemy_type, ENEMY_MOVEMENT_HITBOX["default"])


def enemy_movement_half_extents(enemy_type: str) -> tuple[float, float]:
    w, h = enemy_movement_size_tuple(enemy_type)
    return (w * 0.5, h * 0.5)


# Asset paths (relative to project root).
ASSETS_ROOT = "assets"
PLACEHOLDER_IMAGE = "assets/placeholders/missing.png"

# Background fill color (prevents white/garbage).
BACKGROUND_COLOR = (18, 18, 18)

# Debug (set True to log frame paths and scaled sizes in asset loader).
DEBUG_ASSET_LOADER = False
# Debug combat: on-screen overlay + console prints for player->enemy hits.
DEBUG_COMBAT_HITS = False
# Debug player movement: log position/velocity each frame.
DEBUG_PLAYER_MOVEMENT = False
# Debug door trigger rects: draws door/player rects for overlap debugging.
DEBUG_DOOR_TRIGGER = False
# Debug player attack ranges/rects: circles + attack hitbox overlays.
DEBUG_DRAW_ATTACK_RANGE = False
# Debug top-edge walkability: world/tile, wall_band, bounds (verbose; enable briefly).
DEBUG_TOP_EDGE = False
# Debug movement hitbox / spawn clamp alignment (verbose).
DEBUG_MOVEMENT_HITBOX = False

# --- Phase 2: Player and movement (no hardcoding in entity/system code) ---
# Controls per Requirements_Analysis_Biome1.md §3.2: Movement W/A/S/D, Short LMB, Long RMB, Dash Space, Pause Esc.
# Block = J (pygame.K_j), Parry = K (pygame.K_k). Interact [E] reserved for Room 0 altar.
PLAYER_MOVE_SPEED = 220  # px/sec
PLAYER_DASH_SPEED_MULT = 2.2
PLAYER_DASH_DURATION_SEC = 0.18
# Dash cooldown per Biome 1 spec (snappy via speed/animation, not cooldown hack).
PLAYER_DASH_COOLDOWN_SEC = 0.90
PLAYER_BASE_HP = 200  # Must equal PLAYER_MAX_HP_BY_LIFE[0] (first life).
# Lives: remaining stock (3 → game starts; each fatal HP loss consumes one if >1 life left).
PLAYER_LIVES_INITIAL = 3
PLAYER_MAX_HP_BY_LIFE = (200, 100, 50)  # life_index 0, 1, 2
PLAYER_RESPAWN_INVULN_SEC = 1.5
# Visual delay before life-loss respawn (GameScene only; does not change lives/HP math).
LIFE_LOSS_TRANSITION_SEC = 2.0
LIFE_LOSS_FADE_IN_SEC = 0.75
PLAYER_PARRY_WINDOW_SEC = 0.18  # ~11 frames @ 60 FPS; easier to test than 0.12s
# Incoming damage multiplier while blocking (SRS: 60% damage reduction → take 40% of hit).
PLAYER_BLOCK_DAMAGE_FACTOR = 0.4

# --- Phase 4: Combat (player attacks, block/parry) ---
# Player base attack damages (Biome 1 defaults).
PLAYER_SHORT_ATTACK_DAMAGE = 8
PLAYER_LONG_ATTACK_DAMAGE = 14
# Player melee vs enemy category (applied after base × attack_multiplier in combat.apply_player_attacks).
PLAYER_DAMAGE_MULT_NORMAL = 1.0
PLAYER_DAMAGE_MULT_MINIBOSS = 0.85
PLAYER_DAMAGE_MULT_FINAL_BOSS = 0.65

# Attack timings (sec) for Biome 1.
PLAYER_SHORT_ATTACK_WINDUP_SEC = 0.12
PLAYER_SHORT_ATTACK_ACTIVE_SEC = 0.10
PLAYER_SHORT_ATTACK_RECOVERY_SEC = 0.18
# Enforced by Player.short_attack_cooldown_timer (min time between short-attack starts; independent of anim length).
PLAYER_SHORT_ATTACK_COOLDOWN_SEC = 0.2

PLAYER_LONG_ATTACK_WINDUP_SEC = 0.20
# Enforced by Player.long_attack_cooldown_timer (independent of attack_long animation length / FPS).
PLAYER_LONG_ATTACK_COOLDOWN_SEC = 0.5

# Player melee: proximity radii from player center (px). Facing does not affect hits.
PLAYER_SHORT_ATTACK_RANGE_PX = 48  # 1.5 tiles — smaller radius
PLAYER_LONG_ATTACK_RANGE_PX = 192  # 6 tiles — larger radius

# Temporary: log proximity hits / attack-while-moving (set False to silence).
DEBUG_PLAYER_ATTACK_PROXIMITY = False
# Verbose: walk+LMB trace (state at update end, draw, _set_state, GameScene short_req). Set False to silence.
DEBUG_PLAYER_ATTACK_WALK_TRACE = False
# One-shot frame trace: GameScene + Player + combat for WASD+LMB (set True only while debugging).
DEBUG_PLAYER_ATTACK_INPUT_TRACE = False
# Short-attack input buffer: log buffer / execute / consume (set True only while debugging).
DEBUG_PLAYER_SHORT_ATTACK_BUFFER = False
# Live gameplay trace: GameScene event/poll path + Player short attack (set True only while debugging).
DEBUG_LIVE_SHORT_ATTACK_TRACE = False
# Short attack (LMB) reliability: LMB event, short_req merge, Player receives, attack_short entered (set True only while debugging).
DEBUG_SHORT_ATTACK_INPUT = False
# Block/parry live audit: GameScene K/J, Player guard order, combat melee vs parry/block (set True only while debugging).
DEBUG_BLOCK_PARRY_TRACE = False

# Attack level scaling: +10% damage per level, max level handled later.
PLAYER_ATTACK_LEVEL_STEP = 0.10

# --- Phase 5: Spawn telegraphs and portals ---
# Telegraph duration and pulse count for enemy spawns.
SPAWN_TELEGRAPH_DURATION_SEC = 0.5
SPAWN_TELEGRAPH_PULSES = 3
# Fixed delay between spawn slots (so multiple enemies do not appear on the same frame).
SPAWN_SLOT_DELAY_SEC = 0.4
# Advanced spawn: safe position generator (px / tiles).
MIN_DISTANCE_FROM_PLAYER_PX = 150
MIN_TILES_FROM_WALL = 3
MIN_TILES_FROM_WALL_HEAVY = 6       # Large movement body: stay farther from wall band than standard spawns
# Heavy spawn only: tile-center / padded search must stay ≥ this many tiles inside the playable floor from each wall.
# Set to MIN+1 so the inflated clearance probe (80×80 + 2×HEAVY_CLEARANCE_PADDING_PX) is not tight against the wall band.
SPAWN_HEAVY_WALL_TILE_MARGIN = MIN_TILES_FROM_WALL_HEAVY + 1
MIN_TILES_FROM_CORNER_HEAVY = 4    # Heavy: wider corner exclusion (axis-aligned pocket avoidance)
# General enemy spawn (spread / ambush / triangle): stay off edges and out of corner pockets
SPAWN_EXTRA_INTERIOR_WALL_TILES = 3  # extra tiles inset from playable border (added to MIN_TILES_FROM_WALL)
# Axis-aligned corner pockets: reject if within this many tiles from BOTH meeting edges (all standard melee spawns)
SPAWN_CORNER_ZONE_TILES = 5
# Require at least this many walkable (8-neighbor) tiles around candidate; culls wall pockets / traps
SPAWN_MIN_NEIGHBOR_WALKABLE = 6
SPAWN_MIN_NEIGHBOR_WALKABLE_HEAVY = 6
# Temporary debug: print spawn accept/reject to console (set False to silence)
SPAWN_DEBUG_LOG = False
# Heavy-only spawn logs without enabling full SPAWN_DEBUG_LOG
DEBUG_HEAVY_SPAWN = False
# One-line audit: final Heavy position after SpawnSystem overlap nudge (set True to trace top-left / wall issues)
DEBUG_HEAVY_SPAWN_AUDIT = False
# Heavy movement / stuck diagnostics
DEBUG_HEAVY_MOVE = False
# Heavy clearance: log rejections (main vs fallback path) and movement footprint size
DEBUG_HEAVY_CLEARANCE = False
# Enemy melee registration (attack state + range vs damage applied)
DEBUG_MELEE_HIT = False
# When True, MetricsTracker.end_room prints one line with HP min/max/loss/result (console verification)
DEBUG_ROOM_HP_METRICS_PRINT = False
# When True: log boss HP bar ratio/fill width ~1/sec (game_scene).
DEBUG_BOSS_HP_BAR = False
# When True: console logs for Biome 3 Ranged spawn, list prune, room-clear checks (throttled).
DEBUG_RANGED_ENEMY_LIFECYCLE = False
MIN_TILES_FROM_DOOR = 3
MIN_DISTANCE_BETWEEN_ENEMIES_PX = 90
ELITE_EXTRA_SPACING_PX = 60
MAX_SPAWN_ATTEMPTS = 60
# Extra padding inside wall-margin band (tiles): sides/bottom; Heavy uses larger inset.
SPAWN_EXTRA_EDGE_PADDING_TILES = 3
SPAWN_EXTRA_EDGE_PADDING_TILES_HEAVY = 4
# Extra rows below inner playable top (avoids buggy top wall rows)
SPAWN_EXTRA_TOP_ROWS_TILES = 4
# Random spawn tries in generate_valid_spawn_position (walkability + distance + overlap)
SPAWN_RANDOM_VALIDATION_ATTEMPTS = 20
# Safe spawn: when a position is invalid, try this many random nearby positions before falling back to nearest valid.
SPAWN_VALIDATION_RETRY_NEARBY_ATTEMPTS = 10
# Max tile offset for "nearby" retry (e.g. 3 = try positions within ±3 tiles).
SPAWN_NEARBY_TILES_RADIUS = 3
# Heavy unstuck: retreat away from obstacle cluster for this duration (deterministic)
HEAVY_UNSTUCK_RETREAT_DURATION_SEC = 0.3
# Heavy: time trying to move with near-zero displacement before marking stuck (triggers retreat / anti-stuck)
HEAVY_STUCK_TIME_SEC = 0.32
# Heavy Brute-style only: near-zero displacement while chasing → accumulate; then one deterministic perpendicular sidestep
HEAVY_BRUTE_STUCK_DIST_PX = 1.5
HEAVY_BRUTE_STUCK_TIME_SEC = 0.3
HEAVY_BRUTE_UNSTUCK_SPEED_MULT = 0.42
# Heavy clearance: inflate hitbox by this many px when testing spawn validity (match GameScene probe)
HEAVY_CLEARANCE_PADDING_PX = 12
# Live chase only: tighter inflation than spawn so Heavy commits through gaps instead of zeroing velocity
HEAVY_CLEARANCE_CHASE_PADDING_PX = 8
# If no direction passes at chase padding, retry with max(3px, chase * mult) before last-resort direct @ 0
HEAVY_CLEARANCE_DESPERATION_MULT = 0.5
# Heavy spawn: minimum tile distance from solid props (blocked tiles); no spawn in this radius
HEAVY_MIN_TILES_FROM_PROP = 2
# Heavy obstacle avoidance: cache chosen reroute direction for this duration (shorter = re-test direct toward player sooner)
HEAVY_REROUTE_CACHE_SEC = 0.12
# Blend toward player into unstuck retreat escape (reduces pure wall-axis escape)
HEAVY_RETREAT_TOWARD_PLAYER_BLEND = 0.38
# When a non-direct clearance direction wins, blend this much toward the player before moving (pressure > side-skate)
HEAVY_CLEARANCE_NON_DIRECT_TOWARD_BLEND = 0.58
AMBUSH_SPAWN_RADIUS_PX = 200
TRIANGLE_OFFSET_PX = 80

# --- Phase 6: Mini Boss ---
MINI_BOSS_BASE_HP = 100
MINI_BOSS_BASE_DAMAGE = 18
MINI_BOSS_MOVE_SPEED = 100
MINI_BOSS_DASH_SPEED = 180
MINI_BOSS_ATTACK_RADIUS = 38.0
MINI_BOSS_ATTACK_OFFSET = 28.0
MINI_BOSS_ATTACK_COOLDOWN_SEC = 2.0
# combat.py only: more reliable hit registration for mini_boss / mini_boss_2 / mini_boss_3 (does not change damage)
MINI_BOSS_MELEE_HIT_RADIUS_MULT = 1.10
MINI_BOSS_MELEE_BODY_EXTRA_PX = 12.0
MINI_BOSS_MELEE_ARC_BONUS_PX = 10.0
# Biome 3 mini boss only: ranged fireball (medium/long range).
BIOME3_MINIBOSS_FIREBALL_DAMAGE = 16
BIOME3_MINIBOSS_FIREBALL_SPEED = 280.0
BIOME3_MINIBOSS_FIREBALL_LIFETIME_SEC = 3.0
BIOME3_MINIBOSS_FIREBALL_COOLDOWN_SEC = 2.2
# After death animation + reward spawn, wait this long then set doors unlocked (for Phase 7).
MINI_BOSS_DOOR_UNLOCK_DELAY_SEC = 0.5
# Reward heal when collected (fraction of max HP).
MINI_BOSS_REWARD_HEAL_PERCENT = 0.30

# --- Phase 7: Dungeon, doors, hazards ---
# Door open delay after room clear (sec). Test contract currently expects 0.5s.
DOOR_UNLOCK_DELAY_SEC = 0.5
# Lava: damage per second (Biome 1); 3-frame anim at 6 FPS.
LAVA_DAMAGE_PER_SECOND = 6
LAVA_ANIM_FRAMES = 3
LAVA_ANIM_FPS = 6
# Slow tile: movement speed multiplier (only normal movement; dash ignores).
SLOW_TILE_SPEED_FACTOR = 0.75
# Hazard percentage bounds per room (0–1 or use caps from Requirements).
HAZARD_LAVA_MAX_FRACTION = 0.05
HAZARD_SLOW_MIN_FRACTION = 0.05
HAZARD_SLOW_MAX_FRACTION = 0.10
# Safe room: heal = 30% of base_max_hp; HP cap at 130% of base (overheal).
SAFE_ROOM_HEAL_PERCENT = 0.30
SAFE_ROOM_OVERHEAL_CAP_RATIO = 1.30
SAFE_ROOM_HEAL_MISSING_PERCENT = 0.30  # Legacy name for tests; Safe Room now uses HEAL_PERCENT + OVERHEAL_CAP
# Reserve heal: excess healing banks exact HP leftovers (FIFO list, max entries); H consumes front slice.
RESERVE_HEAL_POOL_MAX_ENTRIES = 3
RESERVE_HEAL_USE_COOLDOWN_SEC = 0.4
# Heal drop after combat clear: 25% chance (seeded).
HEAL_DROP_CHANCE = 0.25
# Room dimensions (tiles): (cols, rows). Start=16x16, Combat=12x12, etc.
ROOM_SIZE_START = (16, 16)
ROOM_SIZE_COMBAT = (12, 12)
ROOM_SIZE_AMBUSH = (8, 8)
ROOM_SIZE_SAFE = (12, 12)
ROOM_SIZE_ELITE = (16, 16)
ROOM_SIZE_MINI_BOSS = (16, 16)
# Set True to enable Phase 7 dungeon (rooms 0-7, doors, hazards). False = single arena for tests.
USE_PHASE7_DUNGEON = True

# Campaign mode: when True, full campaign (Biome 1 rooms 0-7, then Biome 2 rooms 8-15).
# When False, Biome 1 only (8 rooms) for debugging.
USE_BIOME2 = True  # Set True for full campaign; False for Biome 1 only
USE_BIOME3 = True  # Set True to include Biome 3 rooms 16-23.
USE_BIOME4 = True  # Set True to include Biome 4 rooms 24-29 (Final Boss at 29).

# Campaign structure (used when USE_BIOME2=True).
BIOME1_ROOM_COUNT = 8
BIOME2_ROOM_COUNT = 8
BIOME2_START_INDEX = 8  # Campaign index 8 = first Biome 2 room
BIOME3_ROOM_COUNT = 8
BIOME3_START_INDEX = 16  # Campaign index 16 = first Biome 3 room
BIOME4_ROOM_COUNT = 6  # Rooms 24-29 (24-28 content, 29 = Final Boss reserved).
BIOME4_START_INDEX = 24  # Campaign index 24 = first Biome 4 room

# Biome 4 Phase 2: boss telegraph timing — fast and readable (final boss relentless pressure).
# Phase 1
BIOME4_BOSS_TELEGRAPH_FIREBALL_SEC = 0.5  # legacy; use BOSS_TELEGRAPH_*_PHASE1/2
BOSS_TELEGRAPH_FIREBALL_PHASE1 = 0.45
BOSS_TELEGRAPH_LAVA_PHASE1 = 0.5
BOSS_TELEGRAPH_TELEPORT_PHASE1 = 0.5
BOSS_TELEGRAPH_METEOR_PHASE1 = 0.85
# Phase 2 (faster telegraphs)
BOSS_TELEGRAPH_FIREBALL_PHASE2 = 0.35
BOSS_TELEGRAPH_LAVA_PHASE2 = 0.4
BOSS_TELEGRAPH_TELEPORT_PHASE2 = 0.4
BOSS_TELEGRAPH_METEOR_PHASE2 = 0.7
BIOME4_BOSS_TELEGRAPH_METEOR_SEC = 1.0  # default for meteor trigger; phase-specific set by boss
# Room 29 / boss HUD: narrow bar, placed below player HP row to avoid overlap (see GameScene.draw).
BOSS_HUD_BAR_WIDTH = 320
# Below player HP row + small banner strip; avoid overlap with outlined player HUD text.
BOSS_HUD_BAR_TOP = 64
BIOME4_BOSS_UI_ANCHOR_X = LOGICAL_W // 2 - BOSS_HUD_BAR_WIDTH // 2
BIOME4_BOSS_UI_ANCHOR_Y = BOSS_HUD_BAR_TOP
BIOME4_BOSS_UI_ANCHOR_W = BOSS_HUD_BAR_WIDTH
BIOME4_BOSS_UI_ANCHOR_H = 60

# --- Biome 4 Phase 3: Final Boss (Room 29) — relentless, hardest encounter ---
FINAL_BOSS_HP = 200
FINAL_BOSS_CONTACT_DAMAGE = 18
FINAL_BOSS_FIREBALL_DAMAGE = 20
FINAL_BOSS_LAVA_WAVE_DAMAGE = 22
FINAL_BOSS_METEOR_DAMAGE = 18
FINAL_BOSS_TELEPORT_STRIKE_DAMAGE = 24
# Aggressive timing: something threatening every 1–3 s; minimal idle.
FINAL_BOSS_ATTACK_COOLDOWN_SEC = 1.0    # Phase 1
FINAL_BOSS_ATTACK_COOLDOWN_PHASE2_SEC = 0.7   # Phase 2
FINAL_BOSS_MOVE_SPEED = 135              # Phase 1: fast chase (anti-camp)
FINAL_BOSS_MOVE_SPEED_PHASE2 = 175       # Phase 2: hunting speed
FINAL_BOSS_STOP_DISTANCE = 160           # Slightly closer before choosing attack
FINAL_BOSS_FIREBALL_RANGE_MIN = 180      # Fireball from mid range
FINAL_BOSS_FIREBALL_RANGE_MAX = 450
FINAL_BOSS_WAVE_RANGE_MIN = 80
FINAL_BOSS_WAVE_RANGE_MAX = 350
FINAL_BOSS_TELEPORT_RANGE_MIN = 100
FINAL_BOSS_TELEPORT_RANGE_MAX = 340
FINAL_BOSS_FIREBALL_SPEED = 300          # Slightly faster projectile
FINAL_BOSS_FIREBALL_LIFETIME_SEC = 3.0
FINAL_BOSS_FIREBALL_CAST_COOLDOWN = 2 # ~2–3 fireballs per 3 s when in range
FINAL_BOSS_REWARD_HEAL_PERCENT = 0.40
FINAL_BOSS_TELEPORT_COOLDOWN_SEC = 2.5   # Reposition every ~2.5 s when in cycle
FINAL_BOSS_RUSH_SPEED = 260              # Aggressive rush
FINAL_BOSS_RUSH_DURATION_SEC = 0.7
# Short recovery so next action starts quickly (chain pressure).
BOSS_SPAWN_IDLE_DELAY = 0.6
BOSS_ATTACK_RECOVERY = 0.28              # Phase 1
BOSS_ATTACK_RECOVERY_PHASE2 = 0.18       # Phase 2: near-instant chain
BOSS_ATTACK_RECOVERY_FIREBALL_PHASE1 = 0.2   # After fireball: chain faster
BOSS_ATTACK_RECOVERY_FIREBALL_PHASE2 = 0.12
BOSS_PHASE_CHANGE_INVULN_SEC = 2.0
FINAL_BOSS_ATTACK_RECOVERY_FIREBALL_REVIVE = 0.1  # Revive: fireball recovery
# Teleport: min distance from player (playability).
FINAL_BOSS_TELEPORT_MIN_DIST_PX = 96
FINAL_BOSS_METEOR_TARGETS = 3
FINAL_BOSS_METEOR_SPACING_PX = 120
# Melee hitbox (for attack2 / teleport strike)
FINAL_BOSS_ATTACK_RADIUS = 40.0
FINAL_BOSS_ATTACK_OFFSET = 50.0

# --- Final Boss Revive Phase (one last stand at 0 HP) ---
FINAL_BOSS_REVIVE_HP = 100
FINAL_BOSS_REVIVE_DELAY_SEC = 2.0
FINAL_BOSS_REVIVE_INVULN_SEC = 1.5
# Center-screen revive message duration (1.2–1.8 s); show before boss reappears.
FINAL_BOSS_REVIVE_MESSAGE_DURATION_SEC = 1.5
FINAL_BOSS_MOVE_SPEED_REVIVE = 190       # Revive: fastest and most aggressive
FINAL_BOSS_ATTACK_COOLDOWN_REVIVE = 0.6
FINAL_BOSS_ATTACK_RECOVERY_REVIVE = 0.15
FINAL_BOSS_CONTACT_DAMAGE_REVIVE = 15
FINAL_BOSS_FINAL_DEATH_DELAY_SEC = 0.5
# Hit flinch: brief visual only; must not lock AI or reset attack cycle (stagger resistance).
FINAL_BOSS_HIT_FLINCH_SEC = 0.2

# Testing: start dungeon from this room index instead of 0 (e.g. 0 = Biome 1, 8 = Biome 2, 16 = Biome 3).
START_ROOM_INDEX = 0

# --- Biome 1 Beginner Test Mode (promptforprompt/Biome1_Beginner_Test_Mode_Spec.md) ---
# Temporary: fixed room order, reduced difficulty, deterministic. Set False to revert to normal.
BEGINNER_TEST_MODE = False
# When BEGINNER_TEST_MODE: enemy speeds as % of player (220 px/s). Swarm fixed at 100 px/s; others as %.
if BEGINNER_TEST_MODE:
    _player_speed = PLAYER_MOVE_SPEED
    ENEMY_SWARM_MOVE_SPEED = 100   # Melee Grunt (fixed 100 px/sec)
    ENEMY_FLANKER_MOVE_SPEED = int(_player_speed * 0.85)  # Fast Flanker
    ENEMY_BRUTE_MOVE_SPEED = int(_player_speed * 0.65)   # Elite Guardian
    ENEMY_HEAVY_MOVE_SPEED = int(_player_speed * 0.55)   # Biome 2 Heavy (slower)
    MINI_BOSS_MOVE_SPEED = int(_player_speed * 0.75)
