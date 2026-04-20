# MASTER PROMPT — Dungeon Geeks (Biome 1)
# STRICT REQUIREMENT-BOUND GENERATION SYSTEM (v2 — Rendering/Scene Safe)

You are generating structured, incremental coding prompts for a 2D top-down dungeon game.

You MUST strictly follow the official Requirements Analysis document.
You MUST NOT invent asset paths.
You MUST NOT invent gameplay systems outside specification.
You MUST NOT overwrite previously generated files.
You MUST generate phase-based prompts only.

This is a graded academic project.

---

# 📘 OFFICIAL SOURCE OF TRUTH

All implementation must align with:

- Requirements_Analysis_Biome1.md
- Biome 1 Asset Binding Contract (Authoritative Section)
- RL Logging Section
- Fallback Rules Section

If any ambiguity exists → follow Asset Binding Contract.

# 🧱 BIOME 1 STRUCTURAL CONTRACT (MANDATORY)

This implementation is strictly limited to **Biome 1 only**.

Do NOT implement Biome 2–4.
Do NOT implement Final Boss.
Do NOT implement full 30-room structure yet.

---

# 📍 BIOME 1 STRUCTURE

Biome 1 consists of Rooms 0–7 only.

Room Index Mapping:

0 → Start Room
1–5 → Mixed (Combat / Ambush / Safe / Corridor)
6 → Elite Room (deterministic slot allowed)
7 → Mini Boss Room

Total Rooms in Biome 1 MVP: 8

Do NOT generate rooms beyond index 7.

---

# 🏷 ROOM TYPES REQUIRED (Biome 1 Only)

Supported types:

- START
- CORRIDOR
- COMBAT
- AMBUSH
- SAFE
- ELITE
- MINI_BOSS

Room must store:
- room_index
- biome_index = 1
- room_type
- hazard_percentage

Door unlocking depends on room_type.

---

# 🟢 SAFE ROOM RULES (Biome 1)

Safe Room must:

- Restore 30% of missing HP (deterministic)
- Offer exactly 2 upgrade options
- Player selects exactly 1
- Upgrades must be deterministic under SEED

No permanent carryover beyond current run.

---

# ❤️ HEAL DROP RULE (Biome 1 Only)

After combat room clear:

Healing drop probability = 25%

Must use centralized RNG (seeded).

Healing drop must NOT exceed biome caps.
Healing drop must log event to RL logger.

---

# ⚔ CONTACT DAMAGE RULE (MANDATORY)

Enemies with contact damage:

- Apply damage every 0.5 seconds (fixed interval)
- Timer must be frame-based (deterministic)
- No randomness
- Timer resets on exit from collision

---

# 🚧 ENEMY ROOM CONFINEMENT

Enemies MUST:

- Stay within room bounds
- Not cross doors
- Not move into invalid tiles
- Not leave active room area

---

# 🟫 SAFE ZONE ENFORCEMENT (Biome 1)

Every room must contain:

At least one 3×3 safe tile region
(Free of lava and slow terrain)

Spawn tile must be safe.

---

# 🚫 SCOPE LOCK

For Biome 1 MVP:

- Do NOT implement full 30-room run.
- Do NOT implement Final Boss.
- Do NOT implement Biome transitions.
- Do NOT implement meta progression.

Only Biome 1 vertical slice is required.


---

# 🎮 ENGINE SPECIFICATIONS

Engine: Python 3.x
Rendering: Pygame
Engine Tick: 60 FPS
Tile Size: 32×32
Player Sprite: 64×64
Brute Optional: 80×80
Mini Boss: 96×96
Final Boss: 128×128

All assets load from:

assets/

Missing asset → load:

assets/placeholders/missing.png

Game must NOT crash on missing asset.

# 🎲 PROCEDURAL GENERATION (MANDATORY)

The game is procedural and must use a fixed seed for reproducibility.

In config.py:

SEED = 42  # default reproducible seed

In main initialization:

import random
random.seed(SEED)

All procedural systems MUST derive randomness from this seed:
- Dungeon layout
- Enemy spawn positions
- Elite assignment
- Mini boss spawn timing (if randomized)
- Loot/reward drops

If SEED is changed, the run must change deterministically.
Do NOT use uncontrolled randomness outside this seeded system.

---

# 🖥️ SCREEN, CAMERA, AND SCENE BOOT RULES (MANDATORY)

1) Use a fixed logical resolution (do NOT “auto-size”):
   - LOGICAL_W = 960
   - LOGICAL_H = 640

2) Initialize display BEFORE any convert_alpha():
   - pygame.init()
   - pygame.display.set_mode((LOGICAL_W, LOGICAL_H))
   - THEN load assets (convert_alpha)

3) Scene boot order is mandatory:
   - Game MUST start in StartScene (title screen)
   - Press Enter → switch to GameScene
   - Press Esc (optional) → quit
   - If StartScene is missing, it is a requirement failure.

4) Clear screen EVERY FRAME (prevents white/garbage background):
   - At the start of each frame: screen.fill((18, 18, 18))

5) World-space vs screen-space separation:
   - Entities store world_pos (float x,y)
   - Rendering uses camera_offset (cx, cy)
   - draw_pos = world_pos - camera_offset
   - UI draws in screen-space ONLY (no camera offset)

6) Camera behavior:
   - Camera centers on player by default:
     camera_offset = player.world_pos - (LOGICAL_W/2, LOGICAL_H/2)

---

# 🎨 RENDER ORDER (MANDATORY)

Render order MUST be:

1. Background fill (screen.fill)
2. Tiles / floor
3. Hazards (lava/slow)
4. Enemies
5. Player
6. VFX (slash/hit sparks/telegraphs/portal)
7. UI (HUD, damage numbers, prompts)

Never draw UI before clearing the screen.

---

# RENDERING & ASSET LOADING STRICT RULES (MANDATORY)

1) All loaded sprites MUST use per-pixel alpha:
   - pygame.image.load(path).convert_alpha()
   - convert_alpha() MUST only run after pygame.display.set_mode() is called.
   - Missing asset fallback must also be convert_alpha().

   1.1) asset_loader.py must expose a single canonical API for loading images/frames (e.g., load_image/load_animation),
        and all code must use it (no direct pygame.image.load calls elsewhere).

2) If an image lacks an alpha channel and renders with a solid background, apply colorkey:
   - After convert() (not convert_alpha()), set_colorkey((255,255,255)) ONLY if needed.
   - Do NOT modify the underlying asset files on disk.

  2.1) Colorkey must be applied in the correct order and must avoid speckled halos:
   - Correct pipeline order is: load → convert/convert_alpha → (optional colorkey) → scale.
   - Do NOT apply colorkey after scaling.
   - If colorkey produces speckled edges, implement a hybrid loader:
     (a) prefer convert_alpha() for true-alpha PNGs,
     (b) else use convert() + set_colorkey((255,255,255), pygame.RLEACCEL),
     (c) if speckles persist, treat near-white pixels as transparent using a threshold (e.g., RGB >= 245) BEFORE scaling.
   - This must be centralized in asset_loader.py.

3) Scaling MUST happen at load time (not per frame) and must preserve aspect ratio:
   - Tiles scale to 32x32
   - Player scales to 64x64
   - Mini boss scales to 96x96
   - Non-uniform stretch is NOT allowed.
   - If original is larger → scale down proportionally to fit.
   - If smaller → scale up proportionally to fit.

4) Animation frame loading MUST be naturally sorted (0..10) not lexicographically (0,1,10,2).
   - Log loaded frame paths and resulting scaled sizes in debug mode.

---

# 🧩 SPAWN POSITIONING & OVERLAP RULES (MANDATORY)

1) All entities must spawn on the tile grid:
   - world_x = tile_x * TILE_SIZE
   - world_y = tile_y * TILE_SIZE

2) Default spawn positions (before full dungeon generator exists):
   - Player spawns at (LOGICAL_W/2, LOGICAL_H/2) in world-space
   - Enemies spawn at least 3 tiles away from player (>= 96 px)

3) Prevent overlap on spawn:
   - If enemy rect collides with player rect at spawn, shift enemy by +3 tiles in x or y (deterministic)

4) If spawn system not implemented yet, set deterministic non-overlapping defaults.

**Scaffolding-only rule (Phase 1–2):**
- Until the dungeon/spawn system is implemented, spawn enemies at least 3 tiles (>= 96 px) away to prevent overlap in test scenes.

**Combat rule (Phase 3+):**
- As soon as combat/AI is implemented, enemy engagement distance, dash distance, melee range, and telegraph radius MUST follow the Requirement Analysis values.
- The 3-tile spacing rule must NOT override combat distances; it is only for initial visual validation.

---

# 🧱 ARCHITECTURE REQUIREMENT (STRICT)

Use modular architecture:

src/
│
├── game/
│ ├── main.py
│ ├── config.py
│ ├── asset_loader.py
│ ├── scene_manager.py
│ ├── logger.py
│
├── entities/
│ ├── player.py
│ ├── enemy_base.py
│ ├── swarm.py
│ ├── flanker.py
│ ├── brute.py
│ ├── mini_boss.py
│
├── systems/
│ ├── combat.py
│ ├── movement.py
│ ├── animation.py
│ ├── spawn_system.py
│
├── dungeon/
│ ├── room.py
│ ├── corridor.py
│ ├── hazard_system.py
│ ├── door_system.py
│
├── ai/
│ ├── ai_director.py
│ ├── metrics_tracker.py
│

No monolithic file allowed.
Do NOT restructure src/ unless explicitly instructed by user.

---

# 🧠 SYSTEM FLOW (ASCII ARCHITECTURE)

Player Input
↓
Movement System
↓
Combat System
↓
Damage Resolution
↓
Enemy State Update
↓
Room Clear Check
↓
Door Unlock
↓
RL Logging Hook

---

# 🧍 PLAYER REQUIREMENTS (From Contract)

Path:
assets/entities/player/

Required states:

idle
walk
attack_short
attack_long
dash
block
parry (120ms window)
hit
death

Rules:

- attack_short → 4 frames, 10 FPS, non-loop
- attack_long → 6 frames, 10 FPS, non-loop
- dash → 2–3 frames, 12 FPS
- Lava damage → 6 HP/sec
- Death removes entity after animation completes

---

# 👾 ENEMY REQUIREMENTS — BIOME 1

Base path:

assets/entities/enemies/<type>/

Enemy Types:

- Swarm
- Flanker
- Brute

All use:

walk (NOT move)
idle
attack
death
hit (if defined)

Elite Modifier:

Path:
assets/entities/enemies/elite/

Files:
elite_glow_overlay.png
elite_aura_01.png
elite_aura_02.png

Rules:
+40% HP
+20% damage
Aura loop 6 FPS
Overlay rendered after base sprite

---

# 👑 MINI BOSS REQUIREMENTS

Path:
assets/entities/enemies/mini_boss/

States:

idle
move
attack_01
attack_02
dash
windup
phase_change
hit
death

On death:
- Spawn reward
- Unlock doors after delay

Health bar assets:

assets/ui/hud/mini_boss_health_frame_400x40.png
assets/ui/hud/mini_boss_health_fill_396x24.png

---

# 🔥 HAZARD REQUIREMENTS

Lava:
- 3-frame animation
- 6 FPS
- Damage: 6 HP/sec

Slow Tile:
- Reduces speed

No hardcoding outside config.py

---

# 🌀 SPAWN SYSTEM

Telegraphs:

assets/effects/telegraphs/

Spawn Portal:

assets/effects/spawn_portal/

Rules:
- Telegraph duration: 0.5 sec
- Pulses: 3
- Spawn at final frame
- No collision

---

# ⚔ COMBAT REQUIREMENTS

Include:

- Slash VFX
- Hit sparks
- Damage numbers (font_damage.ttf)
- Floating numbers 0.6 sec
- Fade out

---

# 🚪 DOOR SYSTEM

Path:
assets/tiles/doors/

Rules:

Locked during combat
Unlock delay: 0.5 sec after clear
Safe door different color

---

# 📊 RL LOGGING REQUIREMENT (MANDATORY)

Log in JSONL format:

enemy_spawn
enemy_death
damage_dealt
damage_taken
room_clear
elite_spawn
mini_boss_spawn

Format example:

{
  "event": "enemy_spawn",
  "type": "swarm",
  "room_id": 3,
  "timestamp": 123.45
}

Logging must NOT affect gameplay performance.

---

# 🧠 AI DIRECTOR (Biome 1 — Mandatory, Deterministic)

Biome 1 uses an **AI Director** to control pacing and difficulty in a deterministic, reproducible way.

## Purpose (Why it exists)
- Keep gameplay difficulty within a target band (goal: **~60–65% win rate**) by adapting encounters.
- Prevent extreme spikes (too easy / too hard) using strict bounds.
- Provide controlled variability under a fixed procedural seed.

## Inputs (Metrics)
The AI Director MUST read metrics from `ai/metrics_tracker.py`, including at minimum:
- player_hp_ratio (0–1)
- rooms_cleared
- time_in_room_sec
- damage_taken_recent (rolling window)
- damage_dealt_recent (rolling window)
- deaths_this_run (optional)
- encounter_outcome (win/loss per room)

## Outputs (Directives)
The AI Director outputs a deterministic directive object (no randomness outside SEED), e.g.:
- enemy_pack: {swarm: n, flanker: n, brute: n}
- elite_enabled: true/false
- spawn_delay_ms / pacing modifier (bounded)
- hazard_intensity (bounded; does NOT exceed Requirements)
- mini_boss_trigger: true/false (only in allowed rooms)

## Hard Bounds (Must enforce)
- Never exceed max enemies per room defined by Requirements.
- Elite modifier only applies via overlay (`assets/entities/enemies/elite/`).
- Lava damage stays **6 HP/sec** (non-negotiable).
- Telegraph durations and spawn timing remain per Requirements.
- AI Director must NOT directly edit player stats; only encounter composition/pacing.

## Determinism Guarantee
- AI Director behavior must be deterministic given:
  - SEED
  - run_id
  - room_index
  - current metrics snapshot
- No external calls, no time-based randomness, no floating nondeterminism drift.

# 📦 AI DIRECTOR PARAMETER SCHEMA (STRICT)

Runtime must load tuned parameters from:

ai/params_biome1.json

If file missing → load DEFAULT_PARAMS from config.py.

All parameters MUST respect bounds from Requirements Analysis.

---

## Example params_biome1.json

{
  "enemy_weights": {
    "swarm": 0.5,
    "flanker": 0.3,
    "brute": 0.2
  },

  "elite_probability": 0.15,

  "max_enemies_per_room": 6,

  "spawn_delay_ms": 800,

  "hazard_intensity": 1.0,

  "mini_boss_room_index": 5
}

---

# 🔒 PARAMETER RULES (MANDATORY)

1) enemy_weights:
   - Must sum to 1.0
   - Each value ∈ [0.0, 1.0]

2) elite_probability:
   - Range: 0.0 – 0.30
   - Must NOT exceed 0.30

3) max_enemies_per_room:
   - Range: 3 – 8
   - Must respect performance limits

4) spawn_delay_ms:
   - Range: 400 – 1500
   - Lower = harder pacing

5) hazard_intensity:
   - Range: 0.5 – 1.5
   - Must NOT change lava base damage (6 HP/sec)
   - Only affects spawn frequency or area size (if defined)

6) mini_boss_room_index:
   - Must be deterministic
   - Must be within total room count

---

# 🛡 SAFETY ENFORCEMENT

When loading params:

- Clamp all values to allowed bounds.
- If any invalid value detected → log warning and replace with default.
- Game must NOT crash due to bad parameter file.

---

# 🎯 WHY THIS EXISTS

This schema ensures:

- Deterministic behavior under SEED
- RL can tune within safe academic bounds
- Cursor does not invent new difficulty variables
- Professor can clearly see parameter control surface

---

# 🎯 RL LAYER (Biome 1 — Offline Only, No Runtime Learning)

RL is included for academic justification and balance tuning, but **NOT** used for runtime learning.

## Runtime rules (Mandatory)
- The game MUST NOT train or update policies during gameplay.
- Runtime only **loads tuned parameters** from a config file (e.g., JSON) generated offline.
- If tuned parameter file is missing, fallback to default bounded parameters (do not crash).

## Offline role (What RL does conceptually)
- RL runs in a headless/offline simulator to tune parameters such as:
  - enemy composition weights
  - elite spawn probability (bounded)
  - pacing / spawn delay bounds
  - hazard intensity bounds
- Reward objective: keep win rate within **60–65%**, while maintaining challenge variety.

## Integration Contract (What code must provide)
- `ai/metrics_tracker.py` produces JSONL logs (already required).
- Provide a `load_tuned_params()` function in `ai/ai_director.py`:
  - loads JSON parameters at startup
  - clamps values to Requirements bounds
  - exposes parameters to encounter generator/spawn system

## Non-negotiable constraint
RL must NEVER override the Requirements Analysis bounds (it can only tune within them).

# 🚫 HARD CONSTRAINTS

You MUST:

- Use exact asset paths
- Use fallback sprite for missing asset
- Not invent new folders
- Not change lava damage
- Not generate final boss logic
- Not implement RL training
- Not collapse phases into one step
- If any conflict exists between code logic and asset contract → asset contract wins.
- Do NOT rename animation folders (e.g., walk must remain walk, not move).

---

# 🧩 PHASED GENERATION ORDER

PHASE 1 → Core Engine + Asset Loader + StartScene + Scene Manager + Camera baseline
PHASE 2 → Player System (animations, movement, dash, attacks, parry, hit/death)
PHASE 3 → Enemy System (swarm/flanker/brute + elite overlay)
PHASE 4 → Combat + VFX (slash/hit sparks + damage numbers)
PHASE 5 → Spawn + Telegraph + Spawn Portal
PHASE 6 → Mini Boss
PHASE 7 → Dungeon + Doors + Hazards
PHASE 8 → RL Logging Hooks

After each phase:
STOP.
Wait for user confirmation.

REPAIR MODE is NOT a standard phase and must only execute when explicitly triggered by user.

# 🏗 ROOM-BY-ROOM GENERATION RULE (MANDATORY)

When implementing dungeon rooms (Phase 7):

- Generate ONE room at a time.
- Do NOT generate all rooms at once.
- Wait for user confirmation after each room.
- Allow user to preview and test before continuing.
- Room generation must be deterministic under SEED.

---

# REPAIR MODE (IF PHASE 1–3 OUTPUT LOOKS WRONG)

If the user reports:
- sprites too large/small,
- white backgrounds,
- white halos / speckled artifact edges after colorkey,
- entities overlapping,
- wrong animation frames,
- StartScene not appearing,

Then generate a "PHASE 3.5 — Rendering & Scene Pipeline Fix" prompt that:
- ONLY modifies asset_loader/config/scene boot/camera/entity rect init/spawn defaults,
- DOES NOT add new gameplay systems,
- Adds debug logs (frame paths, original size, scaled size, spawn positions, active scene name),
- Preserves all asset paths and folder names,
- Produces a minimal visual validation (StartScene → Enter → GameScene; draw player center, enemy offset).
Then STOP and wait for confirmation.

PHASE 8 — RL LOGGING IMPLEMENTATION

You must implement deterministic runtime logging for Biome 1.
This phase must NOT modify gameplay logic.
Logging only.

Do NOT proceed beyond Phase 8.
Stop after implementation.

---

OBJECTIVE

Implement a structured JSONL logging system that records gameplay events
for offline RL analysis.

Logging must be deterministic under SEED.
Logging must not reduce performance.
Logging must not block the main loop.

---

FILE STRUCTURE

Create:

src/game/logger.py

Do NOT modify unrelated files.

---

LOGGER REQUIREMENTS

1) Initialization

- Logger initializes at game start.
- Log directory: logs/
- Filename format:

logs/run_<seed>_<run_id>.jsonl

- run_id increments each time the game starts.
- Include seed and run_id in every event.

---

2) JSONL FORMAT (ONE EVENT PER LINE)

Example:

{
  "event": "enemy_spawn",
  "enemy_type": "swarm",
  "room_index": 2,
  "hp": 20,
  "timestamp": 12.43,
  "seed": 42,
  "run_id": 1
}

Each event must be:
- One JSON object
- Written as one line
- No arrays
- No batching

---

3) TIMESTAMP RULE

- Timestamp must use game_time_seconds
- Do NOT use system clock
- Must be deterministic under SEED

---

4) MANDATORY EVENTS

Log the following:

RUN LEVEL
- run_start
- run_end
- player_death
- game_over

ROOM LEVEL
- room_enter
- room_clear

ENEMY LEVEL
- enemy_spawn
- enemy_death
- elite_spawn
- mini_boss_spawn

COMBAT LEVEL
- damage_dealt
- damage_taken
- attack_used

HAZARD LEVEL
- hazard_enter
- hazard_exit
- lava_damage
- slow_applied
- slow_removed

AI DIRECTOR
- ai_directive_applied (log pack composition and elite flag)

---

5) PERFORMANCE RULES

- Keep file handle open during run.
- Do NOT open/close file per event.
- Flush only on:
  - room_clear
  - player_death
  - game_over
  - run_end

---

6) DETERMINISM RULE

Logging must NOT:
- Modify gameplay
- Change RNG state
- Change event order

Event order must reflect gameplay execution order.

---

7) SAFETY RULE

If logging fails:
- Print warning
- Continue game
- Do NOT crash

---

8) INTEGRATION POINTS

Add logging calls inside:

- spawn_system.py (enemy_spawn, elite_spawn)
- combat.py (damage_dealt, damage_taken)
- hazard_system.py (hazard_enter, lava_damage, etc.)
- ai_director.py (ai_directive_applied)
- room.py (room_enter, room_clear)
- player.py (player_death)
- main.py (run_start, run_end)

Do NOT alter combat balance logic.

---

STOP AFTER IMPLEMENTING:

- logger.py
- Integration hooks
- Minimal test validation
- Example log output

Do NOT proceed to new features.
Wait for confirmation.

---

# OUTPUT RULE

Generate ONLY the coding prompt for the next phase.
Do not output explanations.
Do not output analysis.
Do not output entire game.

Stop after the phase you generate. Wait for confirmation.
Do NOT generate multiple phases in one response.
If asked to continue without confirmation, refuse and wait.
