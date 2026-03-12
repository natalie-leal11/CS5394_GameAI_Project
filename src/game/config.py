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
BRUTE_SIZE = (80, 80)
MINI_BOSS_SIZE = (96, 96)
FINAL_BOSS_SIZE = (128, 128)

# --- Phase 3: Enemy system ---
# Enemy logical sizes.
ENEMY_SWARM_SIZE = (60, 60)
ENEMY_FLANKER_SIZE = (48, 48)
ENEMY_BRUTE_SIZE = BRUTE_SIZE  # 80x80 per master prompt
ENEMY_HEAVY_SIZE = (88, 88)   # Biome 2: Heavy armored

# Base stats (Biome 1 baseline; match Requirements tables).
ENEMY_SWARM_BASE_HP = 30      # Melee Grunt
ENEMY_FLANKER_BASE_HP = 22    # Fast Flanker
ENEMY_BRUTE_BASE_HP = 50      # Brute
ENEMY_HEAVY_BASE_HP = 60      # Biome 2: Heavy armored

ENEMY_SWARM_BASE_DAMAGE = 10  # Melee Grunt basic swing
ENEMY_FLANKER_BASE_DAMAGE = 8  # Fast Flanker quick strike
ENEMY_BRUTE_BASE_DAMAGE = 14   # Brute heavy hit
ENEMY_HEAVY_BASE_DAMAGE = 16   # Biome 2: Heavy armored

# Minimum separation / attack radius (px) — enemies must not visually overlap player.
ENEMY_SWARM_STOP_DISTANCE = 40
ENEMY_FLANKER_STOP_DISTANCE = 50
ENEMY_BRUTE_STOP_DISTANCE = 60
ENEMY_HEAVY_STOP_DISTANCE = 64

# Enemy melee attack hitbox radii/offsets and cooldowns (Biome 1).
ENEMY_SWARM_ATTACK_RADIUS = 20.0
ENEMY_SWARM_ATTACK_OFFSET = 20.0
ENEMY_SWARM_ATTACK_COOLDOWN_SEC = 1.2

ENEMY_FLANKER_ATTACK_RADIUS = 16.0
ENEMY_FLANKER_ATTACK_OFFSET = 18.0
ENEMY_FLANKER_ATTACK_COOLDOWN_SEC = 1.0

ENEMY_BRUTE_ATTACK_RADIUS = 26.0
ENEMY_BRUTE_ATTACK_OFFSET = 22.0
ENEMY_BRUTE_ATTACK_COOLDOWN_SEC = 2.2

ENEMY_HEAVY_ATTACK_RADIUS = 28.0
ENEMY_HEAVY_ATTACK_OFFSET = 24.0
ENEMY_HEAVY_ATTACK_COOLDOWN_SEC = 2.4

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

# --- Phase 2: Player and movement (no hardcoding in entity/system code) ---
# Controls per Requirements_Analysis_Biome1.md §3.2: Movement W/A/S/D, Short LMB, Long RMB, Dash Space, Pause Esc.
# Block = J (pygame.K_j), Parry = K (pygame.K_k). Interact [E] reserved for Room 0 altar.
PLAYER_MOVE_SPEED = 220  # px/sec
PLAYER_DASH_SPEED_MULT = 2.2
PLAYER_DASH_DURATION_SEC = 0.18
# Dash cooldown per Biome 1 spec (snappy via speed/animation, not cooldown hack).
PLAYER_DASH_COOLDOWN_SEC = 0.90
PLAYER_BASE_HP = 100
PLAYER_PARRY_WINDOW_SEC = 0.12
PLAYER_BLOCK_DAMAGE_FACTOR = 0.5

# --- Phase 4: Combat (player attacks, block/parry) ---
# Player base attack damages (Biome 1 defaults).
PLAYER_SHORT_ATTACK_DAMAGE = 10
PLAYER_LONG_ATTACK_DAMAGE = 8

# Attack timings (sec) for Biome 1.
PLAYER_SHORT_ATTACK_WINDUP_SEC = 0.12
PLAYER_SHORT_ATTACK_ACTIVE_SEC = 0.10
PLAYER_SHORT_ATTACK_RECOVERY_SEC = 0.18

PLAYER_LONG_ATTACK_WINDUP_SEC = 0.20
PLAYER_LONG_ATTACK_COOLDOWN_SEC = 0.60

# Short attack melee range and long attack projectile range (px).
PLAYER_SHORT_ATTACK_RANGE_PX = 48  # 1.5 tiles
PLAYER_LONG_ATTACK_RANGE_PX = 192  # 6 tiles

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
MIN_TILES_FROM_DOOR = 3
MIN_DISTANCE_BETWEEN_ENEMIES_PX = 90
ELITE_EXTRA_SPACING_PX = 60
MAX_SPAWN_ATTEMPTS = 60
AMBUSH_SPAWN_RADIUS_PX = 200
TRIANGLE_OFFSET_PX = 80

# --- Phase 6: Mini Boss ---
MINI_BOSS_BASE_HP = 200
MINI_BOSS_BASE_DAMAGE = 18
MINI_BOSS_MOVE_SPEED = 100
MINI_BOSS_DASH_SPEED = 180
MINI_BOSS_ATTACK_RADIUS = 32.0
MINI_BOSS_ATTACK_OFFSET = 28.0
MINI_BOSS_ATTACK_COOLDOWN_SEC = 2.0
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

# Campaign structure (used when USE_BIOME2=True).
BIOME1_ROOM_COUNT = 8
BIOME2_ROOM_COUNT = 8
BIOME2_START_INDEX = 8  # Campaign index 8 = first Biome 2 room

# --- Biome 1 Beginner Test Mode (promptforprompt/Biome1_Beginner_Test_Mode_Spec.md) ---
# Temporary: fixed room order, reduced difficulty, deterministic. Set False to revert to normal.
BEGINNER_TEST_MODE = True
# When BEGINNER_TEST_MODE: enemy speeds as % of player (220 px/s). Swarm fixed at 100 px/s; others as %.
if BEGINNER_TEST_MODE:
    _player_speed = PLAYER_MOVE_SPEED
    ENEMY_SWARM_MOVE_SPEED = 100   # Melee Grunt (fixed 100 px/sec)
    ENEMY_FLANKER_MOVE_SPEED = int(_player_speed * 0.85)  # Fast Flanker
    ENEMY_BRUTE_MOVE_SPEED = int(_player_speed * 0.65)   # Elite Guardian
    ENEMY_HEAVY_MOVE_SPEED = int(_player_speed * 0.55)   # Biome 2 Heavy (slower)
    MINI_BOSS_MOVE_SPEED = int(_player_speed * 0.75)
