# MASTER PROMPT — Dungeon Geeks (Biome 1)  
# STRICT REQUIREMENT-BOUND GENERATION SYSTEM

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
Safe door color different

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
- Do NOT restructure src/ unless explicitly instructed by user.

---

# 🧩 PHASED GENERATION ORDER

PHASE 1 → Core Engine + Asset Loader  
PHASE 2 → Player System  
PHASE 3 → Enemy System  
PHASE 4 → Combat + VFX  
PHASE 5 → Spawn + Telegraph  
PHASE 6 → Mini Boss  
PHASE 7 → Dungeon + Doors  
PHASE 8 → RL Logging Hooks  

After each phase:
STOP.
Wait for user confirmation.

---

# OUTPUT RULE

Generate ONLY the coding prompt for the next phase.
Do not output explanations.
Do not output analysis.
Do not output entire game.

Stop after PHASE 1.
Wait.