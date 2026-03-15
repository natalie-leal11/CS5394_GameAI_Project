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
ENEMY_BRUTE_STOP_DISTANCE = 60
ENEMY_HEAVY_STOP_DISTANCE = 64
ENEMY_RANGED_STOP_DISTANCE = 180

# Enemy melee attack hitbox radii/offsets and cooldowns (Biome 1).
ENEMY_SWARM_ATTACK_RADIUS = 20.0
ENEMY_SWARM_ATTACK_OFFSET = 20.0
ENEMY_SWARM_ATTACK_COOLDOWN_SEC = 1.2

ENEMY_FLANKER_ATTACK_RADIUS = 16.0
ENEMY_FLANKER_ATTACK_OFFSET = 18.0
ENEMY_FLANKER_ATTACK_COOLDOWN_SEC = 1.0

ENEMY_BRUTE_ATTACK_RADIUS = 26.0
ENEMY_BRUTE_ATTACK_OFFSET = 22.0
ENEMY_BRUTE_ATTACK_COOLDOWN_SEC = 1.5

# Heavy stops at 64 px; attack center is offset 24 px toward player → player at 40 px from center; radius must cover that
ENEMY_HEAVY_ATTACK_RADIUS = 42.0
ENEMY_HEAVY_ATTACK_OFFSET = 24.0
ENEMY_HEAVY_ATTACK_COOLDOWN_SEC = 1.7

# Biome 3: Ranged (projectile attacker; no melee).
ENEMY_RANGED_SIZE = (72, 72)
ENEMY_RANGED_BASE_HP = 28
ENEMY_RANGED_BASE_DAMAGE = 8
ENEMY_RANGED_MOVE_SPEED = 100
ENEMY_RANGED_ATTACK_COOLDOWN_SEC = 1.4
RANGED_PROJECTILE_SPEED = 260
RANGED_PROJECTILE_DAMAGE = 8
RANGED_PROJECTILE_LIFETIME_SEC = 3.0
# Kiting: back away if closer than this, approach if farther than RANGED_KITE_FAR_THRESHOLD, strafe in between.
RANGED_KITE_CLOSE_THRESHOLD = 140
RANGED_KITE_FAR_THRESHOLD = 220
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
PLAYER_BASE_HP = 1000
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
MIN_TILES_FROM_WALL_HEAVY = 4       # Heavy (88x88) needs 1 extra tile from walls
MIN_TILES_FROM_CORNER_HEAVY = 2    # Heavy must spawn at least 2 tiles from room corners
MIN_TILES_FROM_DOOR = 3
MIN_DISTANCE_BETWEEN_ENEMIES_PX = 90
ELITE_EXTRA_SPACING_PX = 60
MAX_SPAWN_ATTEMPTS = 60
# Safe spawn: when a position is invalid, try this many random nearby positions before falling back to nearest valid.
SPAWN_VALIDATION_RETRY_NEARBY_ATTEMPTS = 10
# Max tile offset for "nearby" retry (e.g. 3 = try positions within ±3 tiles).
SPAWN_NEARBY_TILES_RADIUS = 3
# Heavy unstuck: retreat away from obstacle cluster for this duration (0.5–0.8 s, deterministic)
HEAVY_UNSTUCK_RETREAT_DURATION_SEC = 0.6
# Heavy: time trying to move with near-zero displacement before marking stuck (0.5–0.8 s)
HEAVY_STUCK_TIME_SEC = 0.6
# Heavy clearance: inflate hitbox by this many px when testing if move is valid (avoid narrow gaps)
HEAVY_CLEARANCE_PADDING_PX = 12
# Heavy spawn: minimum tile distance from solid props (blocked tiles); no spawn in this radius
HEAVY_MIN_TILES_FROM_PROP = 2
# Heavy obstacle avoidance: cache chosen reroute direction for this duration (0.4–0.8 s) to avoid jitter
HEAVY_REROUTE_CACHE_SEC = 0.5
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
# Room 29: reserved screen area for boss HP/name UI (top center).
BIOME4_BOSS_UI_ANCHOR_X = LOGICAL_W // 2 - 200
BIOME4_BOSS_UI_ANCHOR_Y = 10
BIOME4_BOSS_UI_ANCHOR_W = 400
BIOME4_BOSS_UI_ANCHOR_H = 60

# --- Biome 4 Phase 3: Final Boss (Room 29) — relentless, hardest encounter ---
FINAL_BOSS_HP = 480
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
FINAL_BOSS_REVIVE_HP = 50
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
START_ROOM_INDEX = 29

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
