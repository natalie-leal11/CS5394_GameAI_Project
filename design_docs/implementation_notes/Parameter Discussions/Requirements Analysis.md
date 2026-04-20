# Requirements Analysis — Game Start to Room 0 (UI + Assets + Prompts)

**Project:** Adaptive AI Dungeon  
**Group Members:** Natalie Cristina Leal Blanco, Maham Asif  
**Target Resolution:** 1920×1080  
**Engine:** Pygame (2D top-down)

---

## 0) Asset Conventions (Must Follow)

### 0.1 Folder Base
All assets are loaded using relative paths from project root.

### 0.2 Naming Rules
- Lowercase filenames
- Use underscores
- No spaces

### 0.3 Current Asset Structure (Start → Room 0)


assets/
├── backgrounds/
│ ├── main_menu_bg.png
│ ├── controls_bg.png
│ ├── settings_bg.png
│ ├── story_intro_bg.png
│ └── room0_bg.png
│
├── fonts/
│ └── PixelifySans-Variable.ttf
│
├── props/
│ ├── altar_book.png
│ ├── training_dummy.png
│ └── door_open.png
│
└── ui/
├── buttons/
│ ├── btn_play.png
│ ├── btn_controls.png
│ ├── btn_settings.png
│ ├── btn_quit.png
│ ├── btn_apply.png
│ └── btn_back.png
│
├── panels/
│ └── story_panel.png
│
├── prompts/
│ └── interact_prompt_bg.png
│
└── sliders/
├── slider_track.png
└── slider_knob.png


### 0.4 Rendering Rule (Important)
- Background images are rendered as static scene backdrops.
- All UI text (labels, story text, prompts) must be rendered via `pygame.font` using:
  - `assets/fonts/PixelifySans-Variable.ttf`
- Do not bake story text into PNGs.

---

## 1) Game Launch Behavior

### 1.1 First Screen
When the game launches, it opens directly to the **Main Menu**.

### 1.2 Main Menu Background
**Asset:**
- `assets/backgrounds/main_menu_bg.png`

**Design Requirements:**
- Subtle animated dungeon vibe is allowed (torch flicker/fog), but can be static in MVP.
- Must not distract from button readability.

---

## 2) Main Menu

### 2.1 Main Menu Options
Main Menu buttons and their behaviors:

- **Play**
  - Starts a new run and transitions into the Story Intro screen.
- **Controls**
  - Opens the Controls screen.
- **Settings**
  - Opens the Settings screen.
- **Quit**
  - Exits/closes the application immediately.

### 2.2 Button Assets (Main Menu)
**Assets:**
- `assets/ui/buttons/btn_play.png`
- `assets/ui/buttons/btn_controls.png`
- `assets/ui/buttons/btn_settings.png`
- `assets/ui/buttons/btn_quit.png`

**Interaction Requirements:**
- Mouse hover highlight (optional for MVP).
- Mouse click activates selected menu option.
- Keyboard navigation is optional for MVP.

---

## 3) Controls Screen

### 3.1 Controls Background
**Asset:**
- `assets/backgrounds/controls_bg.png`

### 3.2 Controls Mapping (Keyboard + Mouse)
Displayed controls must include:

- **Movement:** W / A / S / D  
- **Short Attack:** Left Mouse Click  
- **Long Attack:** Right Mouse Click  
- **Dash:** Space  
- **Pause / Menu:** Esc  

### 3.3 Controls Screen UI
**Back Button Asset:**
- `assets/ui/buttons/btn_back.png`

**Behavior:**
- Clicking **Back** returns to Main Menu.

---

## 4) Settings Screen

### 4.1 Settings Background
**Asset:**
- `assets/backgrounds/settings_bg.png`

### 4.2 Audio Settings (Sliders)
Settings screen must provide:

- **Master Volume** (0–100)
- **Music Volume** (0–100)
- **SFX Volume** (0–100)

**Slider Assets:**
- Track: `assets/ui/sliders/slider_track.png`
- Knob: `assets/ui/sliders/slider_knob.png`

**Slider Behavior:**
- Sliders are mouse-draggable.
- Knob position maps linearly to 0–100.
- Values persist after Apply/Save.

### 4.3 Display Settings
- **Display Mode Toggle:** Windowed / Fullscreen

Display mode can be implemented as a button/toggle interaction on MVP.

### 4.4 Settings Screen Buttons
**Assets:**
- Apply: `assets/ui/buttons/btn_apply.png`
- Back: `assets/ui/buttons/btn_back.png`

**Behavior:**
- **Apply** saves settings immediately.
- **Back** returns to Main Menu (without starting a run).
- No gameplay-affecting settings are allowed (no difficulty slider, no seed display, no debug options).

---

## 5) Start Run Flow (After Clicking “Play”)

### 5.1 Fade Transition
- The Main Menu fades out smoothly (fade-to-dark).
- Recommended duration: ~1.0–1.5 seconds.

### 5.2 Story Intro Screen
**Background Asset:**
- `assets/backgrounds/story_intro_bg.png`

**Display Rules:**
- Center story text (font-rendered).
- Bottom prompt: “Press any key to continue…”
- Any key proceeds.

**Skip Rules:**
- Fully skippable immediately.
- No forced delay.

---

## 6) LLM Integration (Story Intro Narrative — Optional Enhancement)

### 6.1 Purpose
LLM is used only to generate **narrative text**, not gameplay logic.

### 6.2 Constraints (Must Hold)
- LLM output does not change:
  - dungeon generation
  - enemy spawns
  - AI Director behavior
  - determinism
- If LLM is unavailable, fallback to predefined static story.

### 6.3 LLM Prompt Template (For Story Intro)

Generate a short atmospheric dungeon introduction.
Constraints:

4–8 short lines/paragraphs

Mention 30 rooms

Mention 4 biomes

Mention final boss

No gameplay mechanics explanation

Tone: dark fantasy

Keep under 150 words


### 6.4 Fallback Story Intro Text (Static)
> “You awaken in the depths of a forgotten dungeon.  
> Thirty chambers stand between you and freedom.  
> Powerful guardians watch each biome.  
> Survive the trials. Defeat the bosses.  
> Escape to the outside world.”

---

## 7) Save System (Roguelike Strict)

### 7.1 Save Rules
- The game auto-saves current run progress.
- If the player closes the game mid-run, they can resume from the last saved state.

### 7.2 Death Rule
- On death (HP reaches 0):
  - current run save is deleted
  - next run begins from Room 0

### 7.3 Pause Rule
- Esc pauses the game at the current point.
- When paused:
  - player movement stops
  - enemies stop
  - timers stop
  - projectiles stop
  - director logic stops

---

## 8) Transition from Story Intro to Room 0

### 8.1 Transition
After “Press any key”:
- Fade into gameplay
- Player spawns in **Room 0 (Start Room)**
- Controls become active

---

# 9) Room 0 — Start Room

## 9.1 Purpose
Room 0 is a strictly non-combat safe room.

- No enemies are present.
- No environmental hazards are active.
- AI Director is disabled.
- No room locking occurs.
- The room serves as an introduction and light tutorial space.

---

## 9.2 Room 0 Background
**Asset:**
- `assets/backgrounds/room0_bg.png`

**Visual Zones (Must Be Clear):**
- Practice corner zone (bottom-left)
- Center altar/pedestal zone
- Exit staircase zone (top-right)

---

## 9.3 Room 0 Props (Placed on Top of Background)

### 9.3.1 Altar + Book
**Asset:**
- `assets/props/altar_book.png`

**Placement:**
- Center of room

**Interaction Radius:**
- Prompt appears when player is within ~90 px of altar center.

---

### 9.3.2 Training Dummy
**Asset:**
- `assets/props/training_dummy.png`

**Placement:**
- Bottom-left practice corner zone

---

### 9.3.3 Exit Door / Stairs (Always Open)
**Asset:**
- `assets/props/door_open.png`

**Placement:**
- Top-right staircase zone

---

## 9.4 Story Interaction in Room 0 (Optional)

### 9.4.1 Interaction Prompt
**Prompt Background Asset:**
- `assets/ui/prompts/interact_prompt_bg.png`

**Prompt Text (font-rendered):**
- “Press [E] to Read”

**Behavior:**
- Shows only within altar interaction radius.
- Disappears when player walks away.

---

### 9.4.2 Story Panel Overlay
**Panel Asset:**
- `assets/ui/panels/story_panel.png`

**Behavior:**
- Opens when player presses **E** near altar.
- Darkens background using a translucent overlay.
- Disables player movement while panel is open (UI focus).
- Closes on:
  - ESC
  - E again
  - (optional) Back/Close button

**Skip Rules:**
- Fully skippable immediately.
- No forced reading time.

---

### 9.4.3 Room 0 Book Story Text (Expanded)
Displayed inside the story panel (font-rendered):

> “Long ago, this dungeon was built to imprison what the world feared.  
> Its gates have sealed once more—and you now stand within its depths.  
>  
> Four biomes lie between you and freedom.  
> Each grows more hostile than the last, guarded by powerful champions who answer only to the dungeon itself.  
>  
> Every chamber will test you—combat arenas, sudden ambushes, narrow corridors, and rare sanctuaries of rest.  
> Learn the movements of your enemies. Master your strikes and your dash. Choose your healing and upgrades wisely.  
>  
> At the end of the thirtieth room waits the final guardian.  
> Only by defeating it can the gates reopen…  
> and only then may you return to the outside world.”

---

## 9.5 Training Dummy Logic (Room 0)

### 9.5.1 Purpose
Allows player to safely test:
- short attack
- long attack
- dash positioning

### 9.5.2 Dummy Behavior Rules
- Dummy does not move
- Dummy does not attack
- Dummy does not react (no AI)
- Dummy does not affect room progression

### 9.5.3 Dummy Health Rules
- Dummy has infinite health **OR**
- Dummy HP resets instantly after taking damage

---

## 9.6 Exit Condition (Room 0)
- Exit is always open.
- No requirement to read story.
- No requirement to use dummy.

**Exit Trigger:**
- A rectangular trigger zone is placed at the top-right exit/staircase.
- When the player enters the trigger, transition to Room 1 begins.

Recommended transition:
- Fade-out 0.5–1.0 sec, then load Room 1.

---

## 9.7 Determinism Constraints (Room 0)
Room 0 must:
- Not use seed-based randomness
- Not spawn enemies
- Not trigger AI Director
- Not log combat metrics
- Not modify difficulty parameters

Room 0 is excluded from RL data collection.

---

## 9.8 Room 0 LLM Prompt (Optional Book Story Enhancement)
If LLM is enabled for Room 0 book story:


Generate an atmospheric “book text” for a dungeon start room.
Constraints:

Mention 30 rooms

Mention 4 biomes

Mention guardians and final boss

Keep it immersive (dark fantasy)

Under 180 words

Do not describe game mechanics


Fallback is the static book story text in section 9.4.3.

# BIOME 1 — STRUCTURE & HAZARD LOCK (Phase 1)

Biome 1 = Rooms 0–7  
Total Rooms in Biome 1 = 8  
Room 0 is Start Room (already defined)

Biome 1 Philosophy:
- Introductory
- Teaches combat and dash
- Low hazard pressure
- No overwhelming chaos
- RL may tune enemy count later, but structure remains fixed

---

## 1) Room Type Distribution (Biome 1)

Total Rooms: 8

| Room Type        | Count | Notes |
|------------------|-------|-------|
| Start Room       | 1     | Room 0 (fixed, non-combat) |
| Combat Rooms     | 3     | Standard encounters |
| Ambush Room      | 1     | Soft ambush only |
| Safe Room        | 1     | Exactly one |
| Elite Room       | 1     | Simplified elite (no summon) |
| Mini Boss Room   | 1     | End of Biome 1 |

Total = 8 rooms

---

### Room Order Constraints

- Room 0 = Start Room (fixed)
- Room 7 = Mini Boss (fixed)
- Safe Room cannot be Room 1
- Safe Room cannot be Room 6 (too close to Mini Boss)
- Elite Room cannot immediately follow Safe Room
- Ambush cannot be Room 1
- Ambush cannot directly follow Elite

Exact order is determined by seed within these constraints.

Example valid sequence:
Room 0 – Start  
Room 1 – Combat  
Room 2 – Combat  
Room 3 – Safe  
Room 4 – Combat  
Room 5 – Elite  
Room 6 – Ambush  
Room 7 – Mini Boss  

Seed controls rearrangement within rules.

---

## 2) Room Dimensions (From Final Spec)

| Room Type      | Size      |
|----------------|-----------|
| Start Room     | 16×16     |
| Combat Room    | 12×12     |
| Ambush Room    | 8×8       |
| Safe Room      | 12×12     |
| Elite Room     | 16×16     |
| Mini Boss      | 16×16     |

Tile size = 32×32 px

---

## 3) Hazard Percentages (Biome 1 Only)

Biome 1 is low hazard.

Per room caps:

| Hazard        | Range Per Room |
|--------------|----------------|
| Lava         | 0–5%          |
| Slow Terrain | 5–10%         |
| Walls        | 10–15%        |
| Safe Area    | ≥ 70%         |

Rules:
- Lava never blocks spawn tile.
- Lava never blocks exit tile.
- At least one 3×3 fully safe zone exists.
- Valid path from spawn to exit must always exist.

Safe Room:
- Lava = 0%
- Slow Terrain ≤ 5%
- Walls ≤ 15%

Mini Boss Arena:
- Lava ≤ 5%
- Safe Area ≥ 75%

---

## 4) Hazard Effects

### Lava

Damage: 6 HP per second (Biome 1 reduced)

Rules:
- Damage applied per second using deterministic timer.
- Dash invulnerability prevents lava damage.
- Block/parry does NOT reduce lava damage.
- Enemies avoid lava unless pathing forces it.

Purpose:
- Teaches positioning.
- Not meant to kill player in Biome 1.
- Punishment, not death trap.

---

### Slow Terrain (Mud/Water)

Effect:
- Movement speed reduced by 25%.

Applies to:
- Player
- Enemies

Dash:
- Not affected by slow terrain.

Purpose:
- Teaches movement awareness.
- Encourages spacing and positioning.

---

## 5) Hazard Placement Philosophy

Biome 1 hazards must:

- Appear mostly near edges
- Not cluster heavily
- Not create choke traps
- Not surround player spawn
- Not surround exit

Hazards are educational, not lethal.

---

## 6) RL Boundaries (Biome 1)

RL may later tune:
- Enemy count multiplier
- Ambush probability (within 1 room limit)
- Elite strength slightly

RL may NOT:
- Increase lava percentage above 5%
- Increase slow terrain above 10%
- Add reinforcement waves
- Add additional ambush rooms
- Remove Safe Room

Biome 1 structure is fixed.

# BIOME 1 — Procedural Hazard Placement (Validated System)

Hazards in Biome 1 are procedurally generated using a seeded RNG.
All placements must pass validation checks before the room is accepted.

Hazards are decorative + educational, not lethal traps.

---

## 1) Generation Order (Deterministic)

For each room:

1. Generate wall segments.
2. Generate lava tiles.
3. Generate slow terrain tiles.
4. Validate room.
5. If validation fails → regenerate using next deterministic pattern.

All randomness must come from centralized seeded RNG.

---

## 2) Wall Placement

Walls are placed first because they affect connectivity.

Rules:
- 2–4 wall segments per 12×12 room.
- Each segment length: 2–4 tiles.
- No closed loops allowed.
- Must not block spawn-to-exit path.
- Must not overlap reserved spawn anchors.
- Must not overlap 3×3 guaranteed safe zone.

Validation:
- Run flood-fill path test.
- Ensure path exists from player spawn → exit.

---

## 3) Lava Placement

Biome 1 cap: 0–5% of room tiles.

For 12×12 (144 tiles):
Max lava tiles = 7.

Placement Rules:
- Lava clusters of 1–3 tiles.
- Max 2 clusters.
- Clusters must:
  - Not touch spawn tile.
  - Not touch exit tile.
  - Not create narrow choke.
  - Not appear inside guaranteed 3×3 safe zone.

Lava is mostly near corners or edges.

---

## 4) Slow Terrain Placement

Biome 1 cap: 5–10%

For 12×12:
7–14 tiles.

Placement Rules:
- Prefer 2×2 patches.
- May appear slightly off-center.
- Must not overlap lava.
- Must not fully surround player spawn.

Slow terrain is allowed to influence movement decisions but must not trap.

---

## 5) Guaranteed Safe Zone

Every room must enforce:

- At least one 3×3 fully clear area.
- Usually centered near player spawn.
- No hazards.
- No wall segments.

This is validated after hazard placement.

If missing → regenerate.

---

## 6) Path Validation

After placement:

1. Mark lava and walls as blocked for pathing.
2. Run flood-fill or A* from spawn tile.
3. Confirm exit reachable.
4. Confirm safe zone reachable.
5. Confirm no fully isolated hazard pockets.

If any check fails:
→ discard layout
→ generate next deterministic pattern.

---

## 7) Seed Stability

Given same seed:
- Hazard placement is identical.
- Validation order is identical.
- Room layout is identical.

Seed may vary:
- Exact cluster shapes.
- Exact placement within bounds.

Seed may NOT:
- Break safety constraints.
- Exceed hazard caps.

---

## 8) Why This Works for RL

Procedural with validation ensures:

- Consistent structure.
- Controlled variance.
- No extreme outliers.
- Stable learning signals.

# BIOME 1 — Procedural Hazard Placement System (Room-Type Aware + RL-Tunable)

Biome 1 Hazards are:

- Procedurally generated
- Seed-deterministic
- Validated after placement
- RL-tunable within bounded ranges
- Never allowed to violate safety constraints

Tile Size: 32×32

---

# 1) GLOBAL SAFETY CONSTRAINTS (Hard Locks — RL Cannot Change)

These rules must always hold in Biome 1:

1. Player spawn tile is safe.
2. Exit tile is safe.
3. At least one 3×3 fully safe zone exists.
4. Valid path from spawn → exit must exist.
5. Lava cannot fully block a corridor.
6. Hazards cannot create 1-tile choke traps.
7. No hazard may spawn on reserved spawn anchors.
8. Safe Room has 0% lava (non-negotiable).

These are engine-level guarantees.

---

# 2) RL-TUNABLE HAZARD RANGES (Biome 1 Bounds)

RL may tune hazard percentages only inside these bounds:

| Hazard        | Min | Max |
|--------------|-----|-----|
| Lava         | 0%  | 6%  |
| Slow Terrain | 5%  | 12% |
| Walls        | 10% | 18% |
| Safe Area    | ≥ 65% | Fixed minimum |

These are biome-level caps.

RL cannot exceed these.

---

# 3) Room-Type Specific Hazard Rules (Biome 1)

Hazards are placed AFTER room type is known.

---

## 3.1 Start Room (16×16)

Purpose: Tutorial, zero pressure

Hazard Rules:

- Lava: 0%
- Slow Terrain: 0–5%
- Walls: 10–15%
- Safe Area ≥ 85%

Placement:

- No lava allowed.
- Slow terrain only decorative (edges).
- Center altar zone fully clear.
- Dummy zone fully clear.
- Exit path fully clear.

RL cannot modify this room type.

---

## 3.2 Standard Combat Room (12×12)

Purpose: Teach combat + spacing

Hazard Ranges (RL tunable):

- Lava: 0–6%
- Slow Terrain: 5–12%
- Walls: 10–18%
- Safe Area ≥ 65%

Placement Logic:

- Lava clusters: 1–3 tiles per cluster.
- Max 2 clusters.
- Prefer edges/corners.
- Avoid central spawn region.

- Slow terrain:
  - 2×2 patches preferred.
  - May influence mid-lane movement.
  - Must not block 3×3 safe zone.

- Walls:
  - Short segments (2–4 tiles).
  - Must not create maze structure.
  - Must preserve open center combat area.

Validation required.

---

## 3.3 Ambush Room (8×8)

Purpose: Small pressure chamber

Hazard Ranges:

- Lava: 0–3%
- Slow Terrain: 5–10%
- Walls: 10–15%
- Safe Area ≥ 75%

Additional Rules:

- Central 3×3 area fully safe.
- Lava only at corners.
- No hazards near ambush trigger zone.
- Room must preserve at least 4×4 clear combat area.

RL may adjust within bounds, but cannot reduce safe area below 75%.

---

## 3.4 Safe Room (12×12)

Purpose: Recovery + clarity

Hazard Rules:

- Lava: 0% (hard rule)
- Slow Terrain: 0–5%
- Walls: ≤ 15%
- Safe Area ≥ 80%

Placement:

- Fountain area must be fully clear.
- Upgrade choices placed in safe zone.
- No visual clutter near player spawn.

RL cannot introduce lava in safe room.

---

## 3.5 Elite Room (16×16)

Purpose: Slight escalation

Hazard Ranges:

- Lava: 0–5%
- Slow Terrain: 5–12%
- Walls: 10–18%
- Safe Area ≥ 65%

Placement:

- Central area must allow telegraph reading.
- Lava only near edges.
- No narrow corridors.
- Avoid hazards near elite spawn anchor.

RL may increase density slightly but cannot create trap arena.

---

## 3.6 Mini Boss Room (16×16)

Purpose: Skill check arena

Hazard Rules:

- Lava: 0–5%
- Slow Terrain: 0–8%
- Walls: ≤ 15%
- Safe Area ≥ 75%

Placement:

- Large central open arena.
- Hazards primarily decorative.
- No central lava.
- No choke points.

RL may reduce slow terrain slightly if player dominating, but must respect safe area.

---

# 4) Hazard Generation Algorithm (Room-Type Aware)

For each room:

1. Identify room type.
2. Load room-type hazard bounds.
3. Use seeded RNG to generate target percentages within bounds.
4. Place walls first.
5. Place lava clusters.
6. Place slow terrain patches.
7. Run validation checks.
8. If invalid → regenerate deterministically.

---

# 5) Lava Mechanics (Biome 1)

Damage: 6 HP per second

Rules:

- Applied using deterministic timer.
- Dash invulnerability blocks lava damage.
- Block/parry do NOT reduce lava damage.
- Enemies avoid lava unless pathing requires crossing.

Purpose: positional awareness, not lethal punishment.

---

# 6) Slow Terrain Mechanics

Movement Reduction: 25%

Applies to:
- Player
- Enemies

Dash unaffected.

Purpose: subtle movement control, not immobilization.

---

# 7) RL Integration for Hazards

During offline training, RL may tune:

- Lava percentage bias
- Slow terrain percentage bias
- Wall density bias
- Placement pattern preference weights

RL may NOT:

- Violate global safety rules
- Break connectivity
- Reduce safe area below thresholds
- Modify room-type hazard constraints

At runtime:
- Hazard layout is deterministic from seed + tuned parameters.

Full HUD Layout Placement Guide (1920×1080)
Safe margins

Use a 16 px margin from screen edges (clean + consistent).

Top-left HUD cluster

1) Health Bar

Position: (16, 16)

Frame: health_bar_frame_192x32.png

Fill: health_bar_fill_190x26.png drawn inside frame with inset:

Fill position: (16 + 1, 16 + 3) (tweak if needed)

2) Stats Row background (optional but recommended)

Position: (16, 56)

File: hud_stats_row_bg_280x44.png

3) Stat panels (3 tiles)
Each panel is stat_panel_bg_84x32.png with a 24×24 icon + number text.

Recommended positions (inside the row area):

Attack panel: (24, 62)

Defence panel: (24 + 92, 62) → (116, 62)

Speed panel: (24 + 184, 62) → (208, 62)

Icon placement inside each stat panel:

Icon: top-left inside panel at +8 px, +4 px

Number text: start around +38 px, +8 px

Bottom-center XP bar

Frame position: ( (1920-180)/2 , 1080-16-16 ) = (870, 1048)

Frame: xp_bar_frame_180x16.png

Fill: xp_bar_fill_178x12.png inside with inset:

Fill position: (870 + 1, 1048 + 2)

How to use the animations (quick logic)
Damage flash

When player takes damage:

set flash_timer = 0.15s

while timer > 0: draw flash overlay with alpha scaling down

Low HP glow

If hp_ratio <= 0.25:

alpha = 0.6 + 0.4 * sin(time * speed)

draw glow overlay with that alpha

How Phase Markers Work

If boss has 3 phases:

phase_points = [0.75, 0.50, 0.25]
marker_x = bar_x + (bar_width * phase_ratio)

🔥 1️⃣ Animated Lava Cracks (Boss HP Fill Overlay)

Place this on top of the boss HP fill and animate slight horizontal shift for molten effect.

👉 Download:
boss_lava_cracks_overlay_780x36.png

Usage:

Move overlay slowly left/right (x_offset = sin(time)*3)

Or animate alpha pulse

💥 2️⃣ Phase Change Screen Flash (Fullscreen)

Use for dramatic phase transitions.

👉 Download:
phase_change_flash_fullscreen_1920x1080.png

How to use:

On phase change:

Draw overlay at full alpha

Fade out over 0.4 seconds

Add screen shake (see below)

🩸 3️⃣ Boss HP Chunk Divider (Hades-style)

Use to divide boss HP into chunks (phases).

👉 Download:
boss_hp_chunk_divider_8x60.png

Place at:

75%

50%

25%

Or for 4 chunks:

Every 25%

🎬 4️⃣ Cinematic Boss Intro Splash Panel

Show when boss enters arena.

👉 Download:
boss_intro_splash_panel_900x300.png

Placement (1920×1080):

X = (1920 - 900) / 2 = 510

Y = 250

Add:

Boss name (large font)

Subtitle (e.g., “The Flame Warden”)

Fade in + slight upward slide

🎮 Screen Shake Logic (Clean Implementation)

On phase change:

import random

shake_intensity = 12
shake_duration = 0.35

offset_x = random.randint(-shake_intensity, shake_intensity)
offset_y = random.randint(-shake_intensity, shake_intensity)

screen.blit(world_surface, (offset_x, offset_y))

Decay shake intensity over time.

# Biome 1:
🔵 1️⃣ Combat Room (12×12)
Grid: 12×12

Playable area: inside walls

🚪 Doors

Entrance Door: bottom center → (11,5) & (11,6)

Exit Door: top center → (0,5) & (0,6)

Doors are always 2 tiles wide.

🟢 Player Spawn

Player spawn center bottom:

(9,5)

(9,6)

Reserved 3×3 safe zone:

Rows 8–10

Cols 4–6

No hazards here.

👾 Enemy Spawn Anchors (10 anchors)

Avoid center and spawn zone.

Anchors:

(2,2)
(2,9)
(4,3)
(4,8)
(6,2)
(6,9)
(8,3)
(8,8)
(3,5)
(5,6)

Rules:

Min enemy-to-enemy distance = 2 tiles

Min player-to-enemy spawn distance = 4 tiles

🧱 Center Arena Zone

Keep center 4×4 relatively open:
Rows 4–7
Cols 4–7

No lava here.

🟠 2️⃣ Ambush Room (8×8)

Small and intense.

🚪 Doors

Entrance: bottom center → (7,3) & (7,4)

Exit: top center → (0,3) & (0,4)

🟢 Player Spawn

(6,3)

(6,4)

Central 3×3 safe zone:
Rows 3–5
Cols 2–4

Enemies never spawn here.

👾 Enemy Spawn Anchors (8 anchors)

Edge-based anchors only:

(1,1)
(1,6)
(2,1)
(2,6)
(5,1)
(5,6)
(6,2)
(6,5)

Ambush mechanic:

Tiles flash red for 0.8 sec

Enemy spawns on anchor after delay

No center spawn allowed.

🟢 3️⃣ Safe Room (12×12)

Peaceful layout.

🚪 Doors

Entrance bottom → (11,5) & (11,6)

Exit top → (0,5) & (0,6)

🟢 Player Spawn

Same as combat:
(9,5)
(9,6)

🏛 Fountain / Upgrade Placement

Fountain center:
(5,5)
(5,6)

Upgrade tiles:
(4,4)
(4,7)
(6,4)
(6,7)

No spawn anchors in safe room.

No lava.

🔴 4️⃣ Elite Room (16×16)

Large, readable arena.

🚪 Doors

Entrance bottom → (15,7) & (15,8)

Exit top → (0,7) & (0,8)

🟢 Player Spawn

(13,7)
(13,8)

Reserved 4×4 safe zone:
Rows 12–15
Cols 6–9

👾 Enemy Anchors (12 anchors)

Edge + mid anchors:

(2,2)
(2,13)
(4,4)
(4,11)
(6,2)
(6,13)
(8,4)
(8,11)
(10,2)
(10,13)
(5,8)
(7,8)

Elite spawns near center:

Prefer (6,8) or (8,8)

👑 5️⃣ Mini Boss Room (16×16)

Open arena.

🚪 Doors

Entrance bottom → (15,7) & (15,8)

Exit locked until boss defeated

Exit top → (0,7) & (0,8)

🟢 Player Spawn

(13,7)
(13,8)

Reserved safe zone:
Rows 12–15
Cols 6–9

👾 Boss Spawn

Center:
(7,7)
(7,8)
(8,7)
(8,8)

4-tile block spawn.

👾 Optional Add Spawn Anchors (8)

Used only if boss summons:

(3,3)
(3,12)
(5,3)
(5,12)
(10,3)
(10,12)
(12,5)
(12,10)
🔐 Global Spawn Distance Rules
Rule	Value
Min enemy-to-enemy	2 tiles
Min enemy-to-player spawn	4 tiles
Min enemy-to-door	2 tiles
Min anchor-to-anchor	2 tiles
🧠 Why This Works

Deterministic anchor points

Seed only chooses which anchors get used

RL can tune:

number of enemies

which anchors used

hazard density

Layout remains fair and readable

I’ll visualize Combat Room (12×12) as an ASCII grid with:

# = wall boundary

D = door tiles (2-wide)

P = player spawn tiles (2-wide)

S = safe-zone tiles (3×3)

A = enemy spawn anchors

. = empty floor

Coordinate system:

Rows 0–11 top→bottom

Cols 0–11 left→right

Combat Room (12×12) — ASCII Template
r\c  0 1 2 3 4 5 6 7 8 9 10 11
0   # # # # # D D # # #  #  #
1   # . . . . . . . . .  .  #
2   # . A . . . . . . A  .  #
3   # . . . . A . . . .  .  #
4   # . . A . . . . A .  .  #
5   # . . . . . A . . .  .  #
6   # . A . . . . . . A  .  #
7   # . . . . . . . . .  .  #
8   # . . A S S S . A .  .  #
9   # . . . S P P S . .  .  #
10  # . . . S S S . . .  .  #
11  # # # # # D D # # #  #  #
Anchors used in this grid

(2,2), (2,9)

(4,3), (4,8)

(6,2), (6,9)

(8,3), (8,8)

(3,5), (5,6)

Safe zone

Rows 8–10

Cols 4–6

Doors

Top: (0,5)(0,6)

Bottom: (11,5)(11,6)

Player spawn

(9,5)(9,6)

ASCII templates for the remaining room types, using the same legend:

Legend

# = wall boundary

D = door tiles (2-wide)

P = player spawn tiles (2-wide)

S = safe-zone tiles

A = enemy spawn anchors

F = fountain (safe room)

U = upgrade pedestal (safe room)

B = boss spawn zone (mini boss)

. = empty floor

Coordinates: rows top→bottom, cols left→right.

1) Ambush Room (8×8) — ASCII Template

Doors: top center (0,3)(0,4), bottom center (7,3)(7,4)
Player spawn: (6,3)(6,4)
Safe 3×3 (central): rows 3–5, cols 2–4
Anchors (8): (1,1)(1,6)(2,1)(2,6)(5,1)(5,6)(6,2)(6,5)

r\c  0 1 2 3 4 5 6 7
0   # # # D D # # #
1   # A . . . . A #
2   # A . . . . A #
3   # . S S S . . #
4   # . S S S . . #
5   # A S S S . A #
6   # . A P P A . #
7   # # # D D # # #
2) Safe Room (12×12) — ASCII Template

Doors: top (0,5)(0,6), bottom (11,5)(11,6)
Player spawn: (9,5)(9,6)
Fountain: (5,5)(5,6)
Upgrades: (4,4)(4,7)(6,4)(6,7)
No enemy anchors.

r\c  0 1 2 3 4 5 6 7 8 9 10 11
0   # # # # # D D # # #  #  #
1   # . . . . . . . . .  .  #
2   # . . . . . . . . .  .  #
3   # . . . . . . . . .  .  #
4   # . . . U . . U . .  .  #
5   # . . . . F F . . .  .  #
6   # . . . U . . U . .  .  #
7   # . . . . . . . . .  .  #
8   # . . . . . . . . .  .  #
9   # . . . . P P . . .  .  #
10  # . . . . . . . . .  .  #
11  # # # # # D D # # #  #  #
3) Elite Room (16×16) — ASCII Template

Doors: top (0,7)(0,8), bottom (15,7)(15,8)
Player spawn: (13,7)(13,8)
Reserved safe zone (4×4): rows 12–15, cols 6–9
Anchors (12):

(2,2), (2,13)

(4,4), (4,11)

(6,2), (6,13)

(8,4), (8,11)

(10,2), (10,13)

(5,8), (7,8)

r\c  0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
0   # # # # # # # D D #  #  #  #  #  #  #
1   # . . . . . . . . .  .  .  .  .  .  #
2   # . A . . . . . . .  .  .  .  A  .  #
3   # . . . . . . . . .  .  .  .  .  .  #
4   # . . . A . . . . .  .  A  .  .  .  #
5   # . . . . . . . A .  .  .  .  .  .  #
6   # . A . . . . . . .  .  .  .  A  .  #
7   # . . . . . . . A .  .  .  .  .  .  #
8   # . . . A . . . . .  .  A  .  .  .  #
9   # . . . . . . . . .  .  .  .  .  .  #
10  # . A . . . . . . .  .  .  .  A  .  #
11  # . . . . . . . . .  .  .  .  .  .  #
12  # . . . . . S S S S  .  .  .  .  .  #
13  # . . . . . S P P S  .  .  .  .  .  #
14  # . . . . . S S S S  .  .  .  .  .  #
15  # # # # # # # D D #  #  #  #  #  #  #

(Elite itself can spawn near center later; this template just locks anchors + safe zones.)

4) Mini Boss Room (16×16) — ASCII Template

Doors: top (0,7)(0,8), bottom (15,7)(15,8)
Player spawn: (13,7)(13,8)
Boss spawn 2×2: (7,7)(7,8)(8,7)(8,8)
Summon anchors (8): (3,3)(3,12)(5,3)(5,12)(10,3)(10,12)(12,5)(12,10)
Safe zone (4×4): rows 12–15, cols 6–9

r\c  0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
0   # # # # # # # D D #  #  #  #  #  #  #
1   # . . . . . . . . .  .  .  .  .  .  #
2   # . . . . . . . . .  .  .  .  .  .  #
3   # . . A . . . . . .  .  .  A  .  .  #
4   # . . . . . . . . .  .  .  .  .  .  #
5   # . . A . . . . . .  .  .  A  .  .  #
6   # . . . . . . . . .  .  .  .  .  .  #
7   # . . . . . . B B .  .  .  .  .  .  #
8   # . . . . . . B B .  .  .  .  .  .  #
9   # . . . . . . . . .  .  .  .  .  .  #
10  # . . A . . . . . .  .  .  A  .  .  #
11  # . . . . . . . . .  .  .  .  .  .  #
12  # . . . . A S S S S  A  .  .  .  .  #
13  # . . . . . S P P S  .  .  .  .  .  #
14  # . . . . . S S S S  .  .  .  .  .  #
15  # # # # # # # D D #  #  #  #  #  #  #

# BIOME 1 — Door Rules + Spawn Anchor Selection (Deterministic)

Tile size: 32×32  
All randomness uses the central seeded RNG.

---

## A) Door Rules (When doors open/close)

### A1) Common Door States
Each door can be in one of these states:

- **OPEN**: player can pass through
- **CLOSED**: blocks passage (visual: closed door)
- **LOCKED**: blocks passage during combat (visual: locked/seal door)

Door visuals use:
- `assets/tiles/doors/door_open_32x32.png`
- `assets/tiles/doors/door_closed_32x32.png`
- `assets/tiles/doors/door_locked_32x32.png`
- `assets/tiles/doors/door_safe_32x32.png` (for safe-room entrance only)

---

### A2) Start Room (Room 0)
- Doors are **OPEN** by default.
- No combat lock.
- Exit is always available.

---

### A3) Combat Room
On room enter:
- Entrance door becomes **CLOSED** for 0.25 sec (transition buffer)
- Then set all doors to **LOCKED**
- Spawn enemies (using anchor rules below)

During combat:
- Doors remain **LOCKED**

Clear condition:
- When `enemies_alive == 0`, doors switch to **OPEN**
- Optional: 0.2 sec delay + SFX

---

### A4) Ambush Room
On room enter:
- Doors become **LOCKED immediately**
- Ambush telegraph begins (tiles flash red)
- Enemies spawn after telegraph delay

Clear condition:
- When `enemies_alive == 0`, doors switch to **OPEN**

---

### A5) Safe Room
- Doors are always **OPEN**
- Entrance door uses **door_safe** visual (optional)
- No locking, no combat triggers

---

### A6) Elite Room
On room enter:
- Doors set to **LOCKED**
- Spawn elite + supporting enemies

Clear condition:
- When elite is defeated AND `enemies_alive == 0`, doors switch to **OPEN**

---

### A7) Mini Boss Room
On room enter:
- Entrance door becomes **LOCKED**
- Exit door is **LOCKED**
- Boss spawns in boss zone

Clear condition:
- When boss HP ≤ 0 and no enemies alive:
  - Exit door becomes **OPEN**
  - Entrance door can become **OPEN** or remain open (optional)
  - Reward drops spawn

---

## B) Spawn Anchor Selection Rules (Deterministic + Fair)

We define 8–12 anchor points per room template.
Seed controls *which* anchors are used.

---

### B1) Global Spawn Spacing Constraints

Minimum constraints:
- **Enemy ↔ Enemy**: ≥ 2 tiles apart
- **Enemy ↔ Player spawn**: ≥ 4 tiles away
- **Enemy ↔ Doors**: ≥ 2 tiles away
- **Enemy ↔ Safe zone**: cannot spawn inside reserved safe zone

If constraints fail:
- Select next anchor in deterministic order.

---

### B2) Anchor Selection Algorithm (Seeded)

Inputs:
- list of anchor positions from room template
- desired enemy count N (from encounter config / AI Director / RL params)
- seeded RNG

Steps:
1. Shuffle anchors deterministically using seed (or compute a seeded permutation).
2. Iterate anchors in that order:
   - If anchor passes spacing checks, accept it.
   - Else skip.
3. Stop when N anchors selected.
4. If not enough anchors:
   - reduce N to number selected (Biome 1 safety)
   - log event: `spawn_anchor_shortage`

This guarantees fairness and avoids overlap.

---

### B3) Spawn Timing Rules

#### Combat Room
- Spawn instantly when doors lock (no telegraph for Biome 1 combat).

#### Ambush Room
- Anchors are marked with telegraph:
  - flash red for 0.8 sec
- Spawn occurs after telegraph window

#### Elite Room
- Optional 0.5 sec elite “arrival” animation
- Supports spawn instantly or 0.3 sec stagger

#### Mini Boss Room
- Boss spawns in boss zone
- Summoned enemies (if any) use anchors with telegraph delay

---

### B4) Deterministic Guarantee
Given:
- same seed
- same room type
- same target enemy count
- same anchor list

Then:
- same anchor selection result
- same spawn positions
- same door behavior

This is required for debugging and RL training reproducibility.

---

## C) Logs Needed (for RL later)

For every room:
- seed
- room type
- selected anchors list
- rejected anchors list + reason (too close to player/enemy/door)
- enemy count requested vs spawned
- hazards % chosen
- clear time
- damage taken
- deaths

✅ 1️⃣ Lock Exact Telegraph Visuals + Timing (Red Tile Flash Rules)

We must make this identical everywhere (Combat, Ambush, Elite, Boss summons).

🔴 TELEGRAPH VISUAL STANDARD (Biome 1 Baseline)
A) Spawn Telegraph (All Enemy Types)

Visual:

Tile under spawn anchor flashes red overlay

Optional: small portal sprite (future enhancement)

Red overlay opacity: ~60%

Timing (LOCKED VALUES for Biome 1):

Stage	Duration
Red Tile Flash	0.6 sec
Enemy Idle Grace	0.4 sec
Total Player Reaction Time	1.0 sec

So:

0.6s red flash

Enemy spawns

Enemy remains idle for 0.4s

Then AI activates

This matches proposal idea (0.5 + 0.5 ≈ 1 sec) 

Requirements_Analysis _Proposal

 but makes it exact and clean.

🔴 Ambush Room Special Rule

Ambush must feel slightly more dramatic but still fair in Biome 1.

Ambush Timing:

Stage	Duration
Red Flash	0.8 sec
Idle Grace	0.4 sec
Total Reaction Window	1.2 sec

Extra clarity since room is smaller.

🔴 Elite / Mini Boss Summon Telegraph

When elite or boss summons:

Stage	Duration
Red Flash + Slight Gold Aura	0.8 sec
Spawn	immediate
Idle Grace	0.3 sec
🔴 Telegraph Hard Rules (Determinism)

Telegraph duration must use frame-based timers (no real-time jitter).

All enemies use the same telegraph duration inside same room type.

No random telegraph duration allowed.

Telegraph always rendered ABOVE hazards.

Enemies may NOT deal damage during idle grace.

✅ 2️⃣ Lock Safe-Zone Reservation Per Room Type (Exact Tiles)

We now formalize safe zone reservation per room type.

This must match:

ASCII templates

Hazard placement rules

Spawn anchor validation

AI Director fairness

🟢 Combat Room (12×12)

Reserved Safe Zone:

Rows: 8–10
Cols: 4–6

This 3×3 block is:

No hazards

No walls

No spawn anchors

No reinforcement spawn

No lava

No slow terrain

Minimum guaranteed reaction space.

🟠 Ambush Room (8×8)

Reserved Safe Zone:

Rows: 3–5
Cols: 2–4

Rules:

No spawn anchors

No hazards

No telegraph inside this zone

Player has 1.2 sec to reposition

🟢 Safe Room (12×12)

Safe Zone Definition:

Center 5×5 region (for clarity):

Rows: 4–8
Cols: 4–8

Rules:

No hazards

Fountain inside

Upgrade tiles inside

No clutter near spawn

🔴 Elite Room (16×16)

Reserved Spawn Safety Zone (4×4):

Rows: 12–15
Cols: 6–9

Rules:

No hazards

No elite spawn inside

No summon anchors inside

No wall segments intersecting

👑 Mini Boss Room (16×16)

Reserved Safety Zone:

Rows: 12–15
Cols: 6–9

Boss spawn zone (center 2×2) is separate.

Rules:

No hazards in safety zone

No summon anchors inside safety zone

After phase summon, at least one quadrant remains fully safe

🔒 Global Safe-Zone Enforcement (Engine-Level)

Before room validation passes:

Check safe zone tiles contain:

floor only

no hazards

no walls

no spawn anchors

Check safe zone reachable from spawn.

If violation:

Regenerate layout deterministically.

⚖️ Small Conflict Resolved

Proposal doc suggested:

Minimum safe distance from spawn: 128 px 

Requirements_Analysis _Proposal

With 32×32 tiles:

4 tiles = 128 px

So we lock:

Enemy spawn must be ≥ 4 tiles from player spawn center.

That now matches both documents cleanly.

# BIOME 1 — Enemy Composition Rules (Per Room Type, RL-Tunable)

Goal (Biome 1):
- Teach patterns + spacing.
- Avoid overwhelming swarms.
- Keep encounters readable and fair.
- Allow RL to tune counts/composition later within strict bounds.

Terminology:
- **Melee**: chases player + short-range hit
- **Ranged**: keeps distance + fires projectiles
- **Elite**: stronger variant with enhanced attack/HP
- **Mini Boss**: unique moveset + large HP bar

All compositions below are **baseline defaults** (MVP).
RL may tune within the ranges stated, but cannot violate fairness constraints.

---

## Global Composition Constraints (Biome 1)

### Spawn + spacing (hard rules)
- Min enemy-to-enemy spawn distance: **≥ 2 tiles**
- Min enemy-to-player spawn distance: **≥ 4 tiles**
- No spawns inside reserved safe zones
- Max simultaneous enemies on screen (Biome 1 cap): **6**

### Archetype caps (Biome 1 cap)
- Max ranged enemies at once: **2**
- Max “fast flankers” at once: **2**
- Elite room may include max **1 elite** (always exactly 1 in Biome 1)
- No summoning behavior in Biome 1 (elite + mini boss do NOT summon yet)

### RL tuning scope (allowed later)
RL may tune:
- Enemy count within bounds
- Which anchors are used
- Ratio of melee vs ranged (within caps)
- Minor stat multipliers (HP/Damage/Speed) within biome limits

RL may NOT:
- Exceed max simultaneous enemies
- Spawn ranged > 2 at once
- Spawn inside safe zones
- Remove telegraph grace rules

---

## Enemy Set (Biome 1 Roster)

Biome 1 uses a small roster for clarity:

1. **Melee Grunt** (basic chaser)
2. **Fast Flanker** (lighter HP, higher speed)
3. **Ranged Caster** (keeps distance, fires slow projectile)
4. **Elite Guardian** (elite variant: slower but stronger)
5. **Mini Boss: Biome 1 Guardian** (unique)

(Names can change; roles remain constant.)

---

## A) Start Room (Room 0 — Non-Combat)
- Enemies: **None**
- Optional: **Training Dummy** only (not hostile, infinite HP)

---

## B) Combat Room (12×12) — 3 rooms total

Purpose:
- Core fighting + movement learning.

### Baseline enemy counts (per Combat room)
- Total enemies: **3–5**
- Default target: **4**

### Allowed compositions
Pick one pattern per room (seeded):

**Pattern 1 (All Melee)**
- 3× Melee Grunt
- (+1 optional) Fast Flanker

**Pattern 2 (Mixed)**
- 2× Melee Grunt
- 1× Fast Flanker
- 1× Ranged Caster (max 1 ranged in this pattern)

**Pattern 3 (Ranged supported)**
- 3× Melee Grunt
- 1× Ranged Caster

### RL bounds (Combat)
RL may tune total enemies to: **3–5**
RL may tune ranged count to: **0–1** (Combat rooms only)
RL may tune flanker count to: **0–2**

---

## C) Ambush Room (8×8) — 1 room total

Purpose:
- Teach telegraph awareness + repositioning.

### Baseline enemy counts
- Total enemies: **3–4**
- Spawn as a single wave (Biome 1) with ambush telegraph.

### Allowed compositions
**Pattern A**
- 2× Melee Grunt
- 1× Fast Flanker

**Pattern B**
- 3× Melee Grunt

**Pattern C (harder but still fair)**
- 2× Melee Grunt
- 1× Ranged Caster

### RL bounds (Ambush)
RL may tune total enemies to: **3–4**
RL may tune ranged count to: **0–1**
RL may tune flanker count to: **0–1** (small room fairness)

---

## D) Safe Room (12×12) — 1 room total
- Enemies: **None**
- Interactables: Fountain + upgrades only

---

## E) Elite Room (16×16) — 1 room total

Purpose:
- A focused spike with one “featured” enemy.

### Baseline composition
- 1× Elite Guardian
- + 2× Melee Grunt
- + (optional) 1× Ranged Caster

Total: **3–4**

### RL bounds (Elite)
RL may tune supports to: **2–3**
RL may tune ranged to: **0–1**
Elite is always exactly **1**.

(No summoning in Biome 1.)

---

## F) Mini Boss Room (16×16) — Room 7

Purpose:
- End-of-biome skill check.

### Baseline composition
- 1× Mini Boss (Biome 1 Guardian)
- No adds in Biome 1 (for MVP fairness)

Optional (future enhancement after MVP):
- Adds only at boss HP thresholds (75/50/25), max 2 adds, with telegraph.

### RL bounds (Mini Boss)
For MVP:
- Adds: **0**
Later (optional):
- Adds: **0–2** per phase threshold, never > 2 alive simultaneously.

---

## Difficulty Ramp Within Biome 1 (Suggested)
Combat Room 1: 3–4 enemies, 0 ranged
Combat Room 2: 4 enemies, 0–1 ranged
Combat Room 3: 4–5 enemies, allow 1 ranged
Elite Room: elite + 2–3 supports
Mini Boss: boss only

Seed can swap compositions within bounds.
RL can tune counts within bounds later.

---

## Logging Required (for RL later)
For each room:
- room_type
- composition_id (pattern used)
- enemy_count_total
- count_melee / count_flanker / count_ranged / count_elite
- anchors_selected
- clear_time
- damage_taken
- deaths
- win/loss outcome

# BIOME 1 — Enemy Engage Distances + Attack Ranges (Locked Specs)

Tile size: 32×32 px  
All distances below are defined in both **tiles** and **pixels**.

Goal (Biome 1):
- Readable spacing
- Fair reaction windows
- Clear separation between melee vs ranged behavior
- Works with deterministic spawns + safe zones

---

## 1) Global Distance Definitions

### 1.1 Core Radii
| Concept | Tiles | Pixels |
|---|---:|---:|
| Enemy “Wake/Notice” radius | 8 tiles | 256 px |
| Enemy “Chase” radius | 7 tiles | 224 px |
| Enemy “Disengage” radius (hysteresis) | 10 tiles | 320 px |
| Minimum enemy spawn from player | 4 tiles | 128 px |
| Minimum enemy spawn from enemy | 2 tiles | 64 px |

Notes:
- “Disengage” > “Chase” prevents jitter (they don’t flip states constantly).
- If player is outside disengage radius, enemy returns to idle/patrol.

---

## 2) Player Attack Ranges (for tuning enemies around)

### 2.1 Player Short Attack (Left Click)
| Attribute | Value |
|---|---|
| Range | 1.5 tiles (48 px) |
| Arc | 90° forward cone |
| Wind-up | 0.12 sec |
| Active frames | 0.10 sec |
| Recovery | 0.18 sec |

### 2.2 Player Long Attack (Right Click)
| Attribute | Value |
|---|---|
| Range | 6 tiles (192 px) projectile |
| Projectile speed | 10 tiles/sec (320 px/sec) |
| Wind-up | 0.20 sec |
| Cooldown | 0.60 sec |
| Projectile lifetime | 0.9 sec |

(Exact numbers can be tuned later, but these are locked for Biome 1 baseline.)

---

## 3) Enemy Types — Engage + Attack Specs

## 3.1 Melee Grunt (basic chaser)

### Detection & chase
- Wake/Notice: 8 tiles (256 px)
- Chase: 7 tiles (224 px)
- Disengage: 10 tiles (320 px)

### Attack
| Attribute | Value |
|---|---|
| Attack trigger distance | ≤ 1.2 tiles (38 px) |
| Attack range (hit) | 1.3 tiles (42 px) |
| Wind-up | 0.25 sec (telegraph) |
| Active frames | 0.10 sec |
| Recovery | 0.40 sec |
| Attack cooldown | 1.2 sec |

Behavior:
- If within trigger distance and line-of-sight is clear → start wind-up.
- If player dashes away during wind-up → attack can whiff (good fairness).
- Uses simple pathing to close distance; does not strafe.

---

## 3.2 Fast Flanker (high-speed melee)

### Detection & chase
- Wake/Notice: 9 tiles (288 px)
- Chase: 8 tiles (256 px)
- Disengage: 11 tiles (352 px)

### Attack
| Attribute | Value |
|---|---|
| Attack trigger distance | ≤ 1.0 tile (32 px) |
| Attack range | 1.1 tiles (35 px) |
| Wind-up | 0.18 sec |
| Active frames | 0.08 sec |
| Recovery | 0.35 sec |
| Attack cooldown | 1.0 sec |

Behavior:
- Attempts to approach from side (simple “offset target”):
  - target_point = player_pos + perpendicular_dir * 1.5 tiles
- Never more than **2 flankers alive** in Biome 1 (composition cap).

---

## 3.3 Ranged Caster (kites + projectile)

### Preferred distance band (kiting band)
| Band | Tiles | Pixels |
|---|---:|---:|
| Too close (retreat) | < 4 tiles | < 128 px |
| Preferred distance | 4–6 tiles | 128–192 px |
| Too far (reposition closer) | > 7 tiles | > 224 px |

### Attack
| Attribute | Value |
|---|---|
| Fire trigger | Player within 4–7 tiles AND line-of-sight |
| Wind-up (telegraph) | 0.30 sec |
| Projectile speed | 8 tiles/sec (256 px/sec) |
| Projectile range | 7 tiles (224 px) |
| Cooldown | 1.6 sec |

Behavior:
- If player < 4 tiles → caster backpedals (retreat vector).
- If player in 4–6 tiles → stops briefly to cast.
- If player > 7 tiles → moves closer (no casting while closing).
- Max ranged alive at once: **2** (Biome 1 cap).

---

## 3.4 Elite Guardian (Elite Room)

Elite uses heavier telegraphs and slower, stronger hits.

### Detection & chase
- Wake: 10 tiles (320 px)
- Chase: 9 tiles (288 px)
- Disengage: 12 tiles (384 px)

### Attacks (2-move kit for Biome 1)
**Attack 1: Heavy Swing**
- Trigger distance: ≤ 1.5 tiles (48 px)
- Wind-up: 0.45 sec
- Active: 0.12 sec
- Recovery: 0.55 sec
- Cooldown: 1.8 sec
- Hit arc: 120°

**Attack 2: Ground Slam (small AOE)**
- Trigger distance: ≤ 2.0 tiles (64 px)
- Telegraph ring duration: 0.60 sec
- AOE radius: 2.2 tiles (70 px)
- Cooldown: 3.0 sec

Behavior:
- If player stays close too long → prefers Slam.
- No summoning in Biome 1.

---

## 3.5 Mini Boss (Biome 1 Guardian) — Baseline Kit

### Detection
- Always active once fight starts (boss arena lock)

### Attacks (3-phase-ready but only 1 phase in MVP)
**Attack 1: Double Swipe**
- Trigger distance: ≤ 1.8 tiles (58 px)
- Wind-up: 0.40 sec
- Hits: 2 (0.15 sec apart)
- Cooldown: 2.0 sec

**Attack 2: Dash Strike**
- Trigger distance: 3–6 tiles (96–192 px)
- Telegraph line: 0.55 sec
- Dash distance: 4 tiles (128 px)
- Cooldown: 3.2 sec

**Attack 3: Shockwave**
- Trigger: player within 5 tiles (160 px)
- Telegraph ring: 0.70 sec
- Radius: 4 tiles (128 px)
- Cooldown: 4.0 sec

MVP rule:
- No adds/summons in Biome 1.

---

## 4) Line-of-Sight (LOS) Rules (Locked)

- Melee enemies may chase without LOS (pathfinding).
- Ranged enemies require LOS to start casting.
- Walls block LOS.
- Lava/slow do not block LOS.

---

## 5) Determinism Requirements

- Distances use squared distance checks (avoid float drift).
- Timers are tick-based (frame dt accumulated).
- No random wind-up/cooldown variance in Biome 1.

---

## 6) Logging (for RL later)

For each enemy attack attempt:
- enemy_type
- distance_to_player_at_trigger
- attack_name
- windup_started_time
- did_hit (0/1)
- damage_dealt
- player_evade_action (dash/block/none)

# BIOME 1 — Enemy Movement Speeds + Steering Rules (LOCKED, RL-Tunable)

Tile size: 32×32 px

Design goals:
- Enemies feel readable (Hades-like clarity)
- No “clumping into the player”
- Deterministic movement + deterministic separation
- RL can tune *within bounds* later (counts/composition/small multipliers)

---

## 1) Movement Speeds (Biome 1 Baseline)

These match the Proposal + Parameter tables and are the baseline for Biome 1.  
(All values are px/sec; tiles/sec shown for convenience.)

| Enemy Type | Speed (px/sec) | Speed (tiles/sec) | RL Multiplier Range |
|---|---:|---:|---:|
| Swarm / Melee Grunt | 190 | 5.94 | 0.90× – 1.10× |
| Flanker (Fast) | 260 | 8.13 | 0.90× – 1.10× |
| Brute (Heavy Melee) | 120 | 3.75 | 0.90× – 1.10× |
| Heavy (Area Control) | 100 | 3.13 | 0.90× – 1.10× |
| Ranged | 150 | 4.69 | 0.90× – 1.10× |
| Mini Boss | 140 | 4.38 | 0.95× – 1.05× |
| Final Boss (Biome 4 reference) | 140 | 4.38 | (not used in Biome 1) |

Notes:
- These speeds come directly from the Proposal/Parameter tables (Swarm/Flanker/Brute/Heavy/Final Boss) and the “Ranged Suppressor” speed. :contentReference[oaicite:3]{index=3} :contentReference[oaicite:4]{index=4}
- Mini boss speed is set to 140 px/sec for Biome 1 guardian to align with “boss class” pacing while remaining fair. :contentReference[oaicite:5]{index=5}

---

## 2) Steering Model (Simple + Deterministic)

Biome 1 uses **velocity steering** with **no random jitter**.

### 2.1 Core steering forces (applied each tick)
Total movement vector:
- `v = normalize(chase_vector + separation_vector + avoidance_vector) * speed`

Where:
- chase_vector: toward target (player or kite position)
- separation_vector: keeps enemies from stacking/clumping
- avoidance_vector: avoids lava (soft) and walls (hard)

All calculations must use deterministic tick order:
- Sort enemies by stable ID before applying steering each frame.

---

## 3) No-Clumping / Separation Rule (Key Fix)

### 3.1 Separation radius (hard)
- Separation radius: **2 tiles (64 px)**
- If another enemy is within 64 px, apply repulsion.

### 3.2 Separation strength (Biome 1 baseline)
- Swarm: medium separation (so they still pressure, but don’t overlap)
- Flanker: higher separation (so they keep angles)
- Brute/Heavy: strong separation (large bodies should not pile-up)
- Ranged: strong separation (avoid “stacked turrets”)

Implementation note:
- Repulsion can be inverse-distance weighted, capped to avoid extreme spikes.

---

## 4) Turning / Acceleration Constraints (Prevents “teleport-feel”)

Even with constant speed, we lock a simple turn-rate cap.

### 4.1 Turn rate caps
| Enemy | Max turn rate (deg/sec) |
|---|---:|
| Swarm | 360 |
| Flanker | 480 |
| Brute | 180 |
| Heavy | 160 |
| Ranged | 240 |

Rule:
- Enemy cannot instantly flip direction. This prevents jitter at corners.

### 4.2 Acceleration cap (optional but recommended)
- Accel cap: **1200 px/sec²** for all non-boss enemies
- Boss accel cap: **900 px/sec²**

(Helps smooth movement and improves readability.)

---

## 5) Wall / Collision Handling (No Getting Stuck)

### 5.1 Wall blocking
- Walls fully block movement (slide along walls, do not clip through). :contentReference[oaicite:6]{index=6}

### 5.2 Door area buffer
- Enemies should not “camp” directly on door tiles:
  - Keep enemies ≥ **2 tiles** away from door tiles (anchors already avoid doors).

---

## 6) Hazard Interaction Movement Rules (Biome 1)

### 6.1 Lava (avoidance)
- Lava is damaging; enemies should avoid lava unless no path exists. :contentReference[oaicite:7]{index=7} :contentReference[oaicite:8]{index=8}
- Avoidance behavior:
  - Add avoidance_vector pushing away from lava tiles within **1 tile (32 px)** neighborhood.
- If crossing lava is required (rare in Biome 1), allow it but log it:
  - `enemy_crossed_lava = true`

### 6.2 Slow terrain
- Slow terrain reduces movement speed:
  - Player: 25% slow (Biome 1 spec) :contentReference[oaicite:9]{index=9}
  - Enemies: apply same 25% slow in Biome 1 (consistent) :contentReference[oaicite:10]{index=10}
- Dash movement ignores slow (player only). :contentReference[oaicite:11]{index=11}

---

## 7) Enemy-Specific Movement Behaviors

### 7.1 Swarm (Melee Grunt)
- Direct chase
- Separation ON
- No circling logic (Biome 1 simple)

### 7.2 Flanker
- Uses “offset target” (angle approach) for 0.8–1.2 sec circle time (deterministic window allowed as fixed constant in Biome 1: **1.0 sec**) :contentReference[oaicite:12]{index=12}
- Then lunge/dash
- Separation HIGH so multiple flankers don’t overlap

### 7.3 Brute / Heavy
- Slow approach
- Minimal steering (strong separation, low turn rate)
- They should feel heavy and predictable

### 7.4 Ranged
- Uses a kite band:
  - Retreat if player < 4 tiles
  - Hold/cast if 4–6 tiles
  - Reposition closer if > 7 tiles
- Separation HIGH (avoid stacked firing)

---

## 8) RL-Tunable Movement (Allowed Later)

RL can tune ONLY:
- Speed multiplier per enemy type within the “RL Multiplier Range”
- Separation strength scalar within ±15%
- Kite band thresholds within ±1 tile

RL cannot:
- Disable separation
- Remove turn caps
- Exceed speed bounds
- Change deterministic update ordering

---

## 9) Logging (For RL Later)

Per enemy, per room:
- avg_speed_used
- time_within_64px_of_other_enemy (clump metric)
- number_of_separation_pushes_applied
- time_in_slow_terrain
- lava_cross_count
- wall_slide_time

# BIOME 1 — Player Movement Spec (LOCKED, Deterministic)

Tile size: 32×32 px  
Goal:
- Crisp WASD movement (Hades-like)
- Reliable dash + i-frames (optional)
- Deterministic feel for testing + RL logs
- Consistent with enemy movement + hazards

Controls:
- Move: **W/A/S/D**
- Dash: **Space**
- Short attack: **Left click**
- Long attack: **Right click**
- Pause: **Esc**

---

## 1) Player Base Movement (Biome 1)

### 1.1 Movement Speed
| State | Speed (px/sec) | Speed (tiles/sec) |
|---|---:|---:|
| Normal move | 220 | 6.88 |
| On slow terrain | 165 (−25%) | 5.16 |
| While attacking | 170 (−23%) | 5.31 |

Notes:
- “While attacking” slowdown applies only during wind-up + active frames.
- Slow terrain applies only to normal movement (dash ignores slow).

---

## 2) Acceleration / Turning (Feels snappy but not jittery)

### 2.1 Movement Model
- Input vector = normalized(WASD)
- Velocity moves toward target velocity with accel cap.

### 2.2 Acceleration Cap
- Acceleration cap: **1600 px/sec²**
- Deceleration cap: **2000 px/sec²** (stops faster than starts)

### 2.3 Turn Responsiveness
- No explicit turn-rate limit needed for player.
- Player should respond instantly to direction changes, but accel cap smooths it.

---

## 3) Dash Spec (Biome 1)

### 3.1 Dash Distance & Time
| Attribute | Value |
|---|---|
| Dash distance | 4 tiles (128 px) |
| Dash duration | 0.18 sec |
| Dash speed | ~711 px/sec |
| Dash cooldown | 0.90 sec |

Dash ignores:
- Slow terrain speed penalty
- Minor collision friction (but not walls)

### 3.2 Dash Collision Handling
- Dash stops early if a wall is hit (no clipping).
- If dash would end inside wall: clamp to nearest valid position.

### 3.3 Invulnerability Frames (i-frames)
Biome 1 MVP recommendation:
- i-frames: **0.10 sec** (first half of dash)

Reason:
- Makes dash feel skill-based and forgiving without becoming “free escape”.

---

## 4) Player Hitbox + Collision

### 4.1 Hitbox
- Player collision circle radius: **14 px**
- Player hurtbox radius: **12 px** (slightly smaller for fairness)

### 4.2 Wall Collision
- Walls are solid; player slides along walls.

### 4.3 Door Collision
- Doors act as walls when closed/locked.
- Doors are passable only when open.

---

## 5) Hazard Interaction (Biome 1)

### 5.1 Lava
- Lava damage: **6 HP/sec**
- Damage tick: every **0.25 sec** (deterministic ticks)
- Lava does not slow; it only damages.

### 5.2 Slow Terrain
- Slow amount: **−25% move speed**
- Applies only to normal movement (not dash).
- Applies immediately on entry; removed immediately on exit.

---

## 6) Animation / Facing Rules (For Attacks)

### 6.1 Facing Direction
- Facing = last non-zero movement direction OR aim direction (mouse).
- Priority: if attacking, face toward mouse cursor.

### 6.2 Movement During Attack
- During wind-up/active frames:
  - allow movement at “While attacking” speed
  - dash is allowed if cooldown ready (dash cancels recovery)

---

## 7) Determinism Requirements

- Use fixed timestep update or dt accumulation with stable ordering.
- Movement uses float internally but positions can be snapped for collisions.
- Lava ticks are discrete (0.25 sec cadence).
- Dash distance is exact (clamped by collision).

---

## 8) Logging (for RL + debugging)

Per room:
- time_moving
- time_dashing
- dash_count
- damage_taken_from_lava
- time_in_slow_tiles
- hits_taken_total
- deaths
- room_clear_time

# BIOME 1 — Player Stat Scaling Rules (LOCKED for MVP, RL-Tunable Later)

Tile size: 32×32 px  
Goal:
- Simple, readable upgrades
- No runaway scaling in Biome 1
- Works with 4 pickup types:
  - Health Healing
  - Increase Attack
  - Increase Defence
  - Increase Speed

---

## 1) Base Player Stats (Biome 1 Defaults)

| Stat | Value |
|---|---:|
| Max HP | 100 |
| Base Attack Damage (Short Attack) | 10 |
| Base Attack Damage (Long Attack Projectile) | 8 |
| Base Defence | 0 |
| Base Move Speed | 220 px/sec |
| Dash Cooldown | 0.90 sec |

Notes:
- Defence starts at 0 and increases via pickups.
- Long attack is slightly weaker to keep melee meaningful.

---

## 2) Attack Scaling (Increase Attack Pickup)

### 2.1 Attack Level
- Player has `attack_level` (starts at 0).

### 2.2 Effect per pickup
Each pickup:
- `attack_level += 1`
- Damage multiplier increases by **+10%**

Formula:
- `attack_multiplier = 1.0 + 0.10 * attack_level`

Applied to:
- Short attack damage
- Long attack damage

Example:
- attack_level 0 → 1.00×
- attack_level 3 → 1.30×

Biome 1 cap:
- `attack_level <= 5` (max 1.50×)

---

## 3) Defence Scaling (Increase Defence Pickup)

### 3.1 Defence Level
- Player has `defence_level` (starts at 0).

### 3.2 Effect per pickup
Each pickup:
- `defence_level += 1`
- Adds flat Damage Reduction (DR) of **+6%**

Formula:
- `DR = min(0.06 * defence_level, 0.30)`

Biome 1 cap:
- Max DR = **30%** (defence_level 5)

Damage taken formula:
- `final_damage = incoming_damage * (1 - DR)`

Rules:
- DR applies to enemy attacks only.
- Lava damage is NOT reduced by defence (keeps hazards meaningful).

---

## 4) Speed Scaling (Increase Speed Pickup)

### 4.1 Speed Level
- Player has `speed_level` (starts at 0).

### 4.2 Effect per pickup
Each pickup:
- `speed_level += 1`
- Move speed increases by **+6%**

Formula:
- `move_speed = base_speed * (1.0 + 0.06 * speed_level)`

Biome 1 cap:
- `speed_level <= 5` (max +30%)

Dash interaction:
- Dash distance remains fixed (128 px).
- Dash duration scales slightly with speed for feel:
  - `dash_duration = base_dash_duration / (1.0 + 0.03 * speed_level)`
  - Cap: dash duration cannot go below 0.14 sec.

(So speed makes dash feel snappier, but not broken.)

---

## 5) Health Healing Pickup (Heal)

### 5.1 Heal amount
Each Heal pickup restores:
- **+25 HP**

Rules:
- Cannot exceed max HP.
- Heal pickups can appear in Safe Room only for Biome 1 MVP
  (Combat drop healing can be added later).

---

## 6) Safe Room Fountain (If used)

If you include a fountain interaction in Safe Room:

- Restores **40% of Max HP**
- Can only be used once per Safe Room

Formula:
- `heal = floor(max_hp * 0.40)`

---

## 7) Pickup Spawn Rules (Biome 1 MVP)

Safe Room upgrades:
- Spawn **2 upgrade pedestals** per safe room:
  - Choose 2 out of (Attack/Defence/Speed) without duplicates
- Spawn **1 heal pickup** near fountain

Player rules:
- Player can pick **only 1** of the 2 upgrades
- Heal can always be taken

---

## 8) RL Tuning (Allowed Later, With Bounds)

RL may tune:
- Upgrade spawn frequency (how often safe room appears — already fixed to 1 in Biome 1)
- Choice distribution (Attack vs Defence vs Speed frequency)
- Small scaling values within bounds:

| Parameter | Min | Max |
|---|---:|---:|
| Attack per level | 8% | 12% |
| Defence per level | 4% | 7% |
| Speed per level | 4% | 8% |
| Heal amount | 20 | 30 |
| Fountain heal % | 30% | 50% |

RL cannot:
- Remove caps
- Make DR apply to lava
- Increase any stat cap beyond Biome 1 limits

---

## 9) Logging (for RL later)

Per room and per run:
- attack_level / defence_level / speed_level
- total_damage_dealt
- total_damage_taken
- hp_before_safe_room / hp_after_safe_room
- upgrade_choice (Attack/Defence/Speed)
- heal_pickups_used

# BIOME 1 — Enemy HP + Damage Values (LOCKED for MVP, RL-Tunable Later)

Goal:
- Biome 1 teaches patterns without being lethal
- Encounters are readable and fair
- Upgrades (Attack/Defence/Speed) matter, but don’t break balance
- Works with:
  - Player base HP 100
  - Player short dmg 10, long dmg 8
  - Defence DR up to 30% (does NOT reduce lava)

All values below are for Biome 1 baseline.

---

## 1) Global Combat Rules (Biome 1)

### 1.1 Contact damage
- Enemies do **NOT** deal damage by touching the player.
- Damage only occurs via explicit attack hitboxes / projectiles.

### 1.2 Crits
- No critical hits in Biome 1 (keeps balance simple).

### 1.3 Damage numbers
- All damage values are integer.

---

## 2) Enemy HP (Biome 1)

| Enemy Type | HP |
|---|---:|
| Melee Grunt | 30 |
| Fast Flanker | 22 |
| Ranged Caster | 20 |
| Brute (if used) | 50 |
| Elite Guardian | 120 |
| Mini Boss (Biome 1 Guardian) | 320 |

Reasoning for feel:
- Grunt dies in ~3 short hits (10 dmg each).
- Flanker dies in ~2–3 hits.
- Ranged dies in ~2 hits (fragile).
- Elite lasts long enough to feel “featured”.
- Mini boss lasts long enough to show patterns + boss UI.

---

## 3) Enemy Damage (Biome 1)

### 3.1 Melee Grunt
- Basic swing damage: **10**
- Wind-up: 0.25s (already locked)
- Cooldown: 1.2s

### 3.2 Fast Flanker
- Quick strike damage: **8**
- Wind-up: 0.18s
- Cooldown: 1.0s

### 3.3 Ranged Caster
- Projectile damage: **9**
- Projectile speed: 256 px/sec
- Cooldown: 1.6s
- Projectile disappears on wall hit.

### 3.4 Brute (optional in Biome 1)
- Heavy hit damage: **14**
- Wind-up: 0.45s
- Cooldown: 2.2s
- Slow move speed keeps it fair.

### 3.5 Elite Guardian
Elite has 2 attacks (already locked):

- Heavy Swing damage: **16**
- Ground Slam damage: **18** (AOE)

### 3.6 Mini Boss (Biome 1 Guardian)
Boss has 3 attacks (already locked):

- Double Swipe: **12 per hit** (2 hits max = 24)
- Dash Strike: **18**
- Shockwave: **16**

Biome 1 rule:
- No adds/summons (MVP).

---

## 4) Status / Hazard Damage

### 4.1 Lava (player)
- Lava: **6 HP/sec**
- Tick: every 0.25s (1.5 HP per tick → round to 2 OR accumulate float internally)

Recommendation:
- Use float accumulation to avoid rounding bias.

### 4.2 Slow terrain
- Slow does **0 damage**
- Only reduces movement speed by 25%

---

## 5) Biome 1 Difficulty Targets (Sanity Check)

Expected outcomes for average player:
- Combat room: player takes ~10–25 total damage if sloppy
- Elite room: player takes ~20–40 damage if sloppy
- Mini boss: player takes ~30–60 damage if sloppy
- Safe room fountain/heal allows recovery without making run trivial

---

## 6) RL Tuning (Allowed Later, With Caps)

RL may tune these in offline training within bounds:

### 6.1 HP bounds
| Enemy | Min HP | Max HP |
|---|---:|---:|
| Grunt | 24 | 36 |
| Flanker | 18 | 28 |
| Ranged | 16 | 26 |
| Brute | 40 | 60 |
| Elite | 100 | 140 |
| Mini Boss | 280 | 380 |

### 6.2 Damage bounds
| Enemy | Min Dmg | Max Dmg |
|---|---:|---:|
| Grunt | 8 | 12 |
| Flanker | 6 | 10 |
| Ranged | 7 | 11 |
| Brute | 12 | 16 |
| Elite swing | 14 | 18 |
| Elite slam | 16 | 20 |
| Boss swipe (per hit) | 10 | 14 |
| Boss dash | 16 | 20 |
| Boss shockwave | 14 | 18 |

Hard rule:
- RL cannot increase multiple parameters simultaneously beyond caps in the same update step (to avoid instability).
- Keep a “change budget” per iteration (e.g., max +10% total difficulty delta).

---

## 7) Logging (for RL later)

Per room:
- enemies_spawned_by_type
- time_to_kill_per_enemy
- damage_dealt_by_enemy_type
- hits_taken_by_enemy_type
- deaths
- clear_time
- final_hp

# BIOME 1 — Enemy Hitboxes, Hurtboxes, and Projectile Specs (LOCKED)

Tile size: 32×32 px  
Goal:
- Fair hit detection (no “invisible hits”)
- Consistent melee spacing with player attack ranges
- Deterministic collision and damage logic

Definitions:
- **Hurtbox**: area that can take damage
- **Hitbox**: area that deals damage during an attack
- **Radius** values assume circle collision unless stated

---

## 1) Player Collision Reference (for fairness)

| Box | Radius |
|---|---:|
| Player collision radius | 14 px |
| Player hurtbox radius | 12 px |

(Used when checking enemy hitboxes/projectiles.)

---

## 2) Enemy Body Hurtboxes (Biome 1)

| Enemy Type | Hurtbox Radius |
|---|---:|
| Melee Grunt | 14 px |
| Fast Flanker | 12 px |
| Ranged Caster | 12 px |
| Brute | 18 px |
| Elite Guardian | 22 px |
| Mini Boss | 28 px |

Notes:
- Bigger enemies have bigger hurtboxes for readability.
- Hurtboxes are used for player melee hits + projectiles.

---

## 3) Enemy Melee Attack Hitboxes

### 3.1 Melee Grunt Swing
- Shape: arc/cone (recommended) OR circle at strike point (MVP)
- Effective hit radius: **20 px** from swing center
- Trigger distance: ≤ 38 px (already locked)
- Active frames: 0.10 sec

MVP implementation (simple):
- During active frames, create a circle hitbox:
  - center = enemy_pos + facing_dir * 20 px
  - radius = 20 px
- If circle overlaps player hurtbox → damage

---

### 3.2 Fast Flanker Strike
- Shape: smaller circle (precision feel)
- Hit radius: **16 px**
- Center offset: enemy_pos + facing_dir * 18 px
- Active frames: 0.08 sec

---

### 3.3 Brute Heavy Hit
- Hit radius: **26 px**
- Center offset: enemy_pos + facing_dir * 22 px
- Active frames: 0.12 sec
- Adds slight knockback (optional later)

---

## 4) Elite Attack Hitboxes

### 4.1 Elite Heavy Swing
- Hit arc: 120° (spec)
- Approx MVP circle method:
  - hit radius: **28 px**
  - center offset: enemy_pos + facing_dir * 24 px
- Active frames: 0.12 sec

### 4.2 Elite Ground Slam (AOE)
- Shape: circle AOE centered on elite
- Radius: **70 px** (≈ 2.2 tiles)
- Telegraph ring shows exact radius
- Damage applies only once per slam active frame window

---

## 5) Mini Boss Attack Hitboxes

### 5.1 Double Swipe
Each swipe:
- Hit radius: **30 px**
- Offset: boss_pos + facing_dir * 26 px
- Two swipes spaced 0.15 sec apart

### 5.2 Dash Strike
- During dash, boss body is damaging ONLY at end impact (Biome 1 fairness)
Impact hitbox:
- Circle radius: **40 px**
- Center: boss_pos at dash end
- Telegraph line indicates direction

### 5.3 Shockwave
- Shape: expanding ring OR instant circle (MVP)
MVP:
- Circle radius: **128 px** (4 tiles)
- Telegraph ring shows exact radius
- Damage applies once at activation

---

## 6) Ranged Projectiles (Enemy Caster)

### 6.1 Projectile Geometry
- Shape: circle
- Projectile radius: **6 px**
- Collision check: projectile circle vs player hurtbox circle

### 6.2 Projectile Behavior
- Speed: **256 px/sec**
- Lifetime / max range: **224 px** (7 tiles)
- Destroy conditions:
  - hits wall
  - hits player
  - exceeds range

### 6.3 Projectile Spawn Offset
- Spawn point: caster_pos + facing_dir * 18 px
- Prevents immediate self-collision with caster hurtbox

---

## 7) Player Projectile (Long Attack) Spec Alignment

Recommended projectile radius:
- **6 px** (same as enemy projectile for consistency)

Wall collision:
- projectile removed on wall hit

---

## 8) Hit Confirmation Rules (No multi-hit bugs)

- A single melee attack hitbox can damage the player **only once** per attack.
- A projectile can damage the player **only once**, then it is destroyed.
- If multiple hitboxes overlap in same frame:
  - Apply damage in deterministic order by enemy_id
  - Log total damage sources

---

## 9) Debug Rendering (Optional but extremely useful)

Add debug toggles (dev-only):
- Draw circles for hurtboxes/hitboxes
- Draw projectile circles
- Draw AOE telegraph rings

This helps fix “I can’t see why I got hit” issues quickly.

---

## 10) Logging (for RL later)

Per attack event:
- enemy_type
- attack_name
- hitbox_radius
- distance_to_player_at_hit
- did_hit (0/1)
- damage
- player_action (dash/none)

# BIOME 1 — Knockback + Stagger / Stun Rules (LOCKED for MVP)

Goal:
- Combat feels responsive
- Hits have impact
- No stun-lock abuse
- Biome 1 remains readable and fair

Tile size: 32×32 px

---

# 1️⃣ Global Philosophy (Biome 1)

- Player attacks cause **light knockback**
- Enemies do NOT permanently stun player
- No chain-stun loops allowed
- Elite + Boss have limited stagger rules

Biome 1 keeps crowd control simple.

---

# 2️⃣ Player → Enemy Knockback Rules

## 2.1 Short Attack (Melee)

On hit:
- Apply knockback distance: **18 px**
- Knockback duration: **0.08 sec**
- Direction: from enemy center away from player

Formula:
- `knock_dir = normalize(enemy_pos - player_pos)`
- `enemy_pos += knock_dir * knockback_force`

Rules:
- Knockback cannot push enemy through walls.
- Knockback does NOT interrupt elite heavy attacks (see below).
- Knockback does interrupt normal grunt attacks during wind-up.

---

## 2.2 Long Attack (Projectile)

On hit:
- Knockback distance: **12 px**
- Duration: **0.06 sec**
- Weaker than melee

Purpose:
- Keep ranged useful but not dominant.

---

# 3️⃣ Enemy → Player Knockback

Biome 1 minimal knockback to avoid frustration.

## 3.1 Melee Grunt
- Knockback: **10 px**
- Duration: 0.06 sec

## 3.2 Fast Flanker
- Knockback: **8 px**
- Very light

## 3.3 Ranged Projectile
- No knockback (just damage)

## 3.4 Brute Heavy Hit
- Knockback: **22 px**
- Duration: 0.10 sec

## 3.5 Elite Heavy Swing
- Knockback: **28 px**
- Duration: 0.12 sec

## 3.6 Mini Boss Attacks
- Double Swipe: 16 px per hit
- Dash Impact: 36 px
- Shockwave: 40 px radial push

All knockbacks:
- Respect walls
- Clamp to valid movement space
- Cannot push player outside map bounds

---

# 4️⃣ Stagger Rules (VERY Important)

## 4.1 Normal Enemies (Grunt, Flanker, Ranged)

They can be staggered.

Stagger trigger:
- On hit from player melee or projectile

Stagger duration:
- **0.12 sec**

Effects:
- Movement halted
- Attack wind-up canceled
- Cannot start new attack during stagger

Purpose:
- Makes combat feel responsive.

---

## 4.2 Brute (Optional in Biome 1)

Stagger resistance:
- Requires **2 hits within 0.4 sec** to stagger

Stagger duration:
- 0.10 sec

Prevents trivialization.

---

## 4.3 Elite Guardian

Elite stagger rule:
- Cannot be staggered by single hits.
- Requires cumulative damage of **15% of max HP within 1.2 sec**.

If threshold reached:
- Elite stagger duration: 0.20 sec
- Cooldown before next stagger: 3.0 sec

Prevents stun-locking.

---

## 4.4 Mini Boss

Mini Boss cannot be staggered in Biome 1 MVP.

Exception:
- During specific telegraphed attacks (optional later design), boss may have vulnerability window.

---

# 5️⃣ Player Stagger Rules

## 5.1 Player Hit Reaction

On taking damage:
- Micro flinch duration: **0.05 sec**
- Movement slowed briefly (not fully stopped)

No full stun in Biome 1.

Player cannot be stun-locked.

---

# 6️⃣ Stagger Immunity Window

To prevent chain-lock:

After stagger ends:
- Enemy gains **0.25 sec stagger immunity**

For Elite:
- 3.0 sec immunity (already defined)

---

# 7️⃣ Determinism Requirements

- Stagger timers are tick-based.
- Knockback uses fixed displacement, not physics simulation.
- No random knockback variance.
- All collisions resolved in stable enemy ID order.

---

# 8️⃣ Logging (For RL later)

Per enemy:
- stagger_count
- total_time_staggered
- damage_taken_between_staggers
- knockback_events
- player_knockback_distance_received

Per room:
- total_stagger_events
- time_enemies_spent_disabled

# BIOME 1 — Wrap-Up (Win Rate Target + Difficulty Curve + RL Metrics)

Biome 1 goal:
- Teach core combat + hazards + telegraphs
- Be fair and consistent (deterministic)
- Provide good logs for RL to tune later

---

## 1) 🎯 Target Win Rate for Biome 1 (Baseline Before RL)

We will define win rate targets for **two audiences**:

### 1.1 New / Average Player (first-time run)
- Target Biome 1 clear rate: **55% – 65%**
- This matches your project goal (win probability around 60–65%) and is a good balance target for RL later.

### 1.2 Skilled Player (knows mechanics)
- Target Biome 1 clear rate: **75% – 85%**
- Skilled players should consistently clear Biome 1 with good play.

These are *evaluation targets*, not runtime adjustments.

---

## 2) 📊 Difficulty Curve Across Rooms (Biome 1)

Biome 1 = Rooms 0–7  
(Seed can reorder room types within constraints, but difficulty still follows “early → mid → late” intent.)

### 2.1 Difficulty stages

#### Room 0 — Start (non-combat)
- No difficulty
- Tutorial + story + dummy

#### Stage 1: Early (Rooms 1–2)
**Purpose:** teach basics without ranged pressure

- Combat Room A:
  - 3–4 enemies
  - 0 ranged
  - hazards: low (lava 0–3%, slow 5–8%)
- Combat Room B:
  - 4 enemies
  - allow 0–1 flanker
  - hazards: low–medium

Target outcome:
- Player ends stage with **≥ 70 HP** on average.

---

#### Stage 2: Mid (Rooms 3–5)
**Purpose:** introduce ranged + ambush + resource decision

- Safe Room (exactly 1):
  - heal + upgrades (choose 1 of 2)
- Ambush Room:
  - 3–4 enemies, telegraph enforced
  - allow 0–1 ranged OR 0–1 flanker
  - smaller room means slightly higher tension
- Combat Room C:
  - 4–5 enemies
  - allow 1 ranged

Target outcome:
- After Safe Room, player should recover to **≥ 60–85 HP** depending on play.

---

#### Stage 3: Late (Rooms 6–7)
**Purpose:** spike challenge but fair

- Elite Room (Room 6 typically, but can vary):
  - Elite + 2–3 supports
  - allow 0–1 ranged
  - hazards medium but never choke-y
- Mini Boss Room (Room 7 fixed):
  - boss only (no adds in MVP)
  - cinematic boss HUD

Target outcome:
- Biome clear rate hits target 55–65% for new players.

---

### 2.2 Room difficulty “budget” (simple scoring)
Assign each room a difficulty score (for testing + RL reward shaping):

| Room Type | Difficulty Score |
|---|---:|
| Combat (early) | 2 |
| Combat (mid) | 3 |
| Ambush | 3 |
| Safe | 0 |
| Elite | 5 |
| Mini Boss | 6 |

Biome 1 total expected difficulty (typical run):
- 2 + 2 + 3 + 3 + 0 + 5 + 6 = **21**

Seed reordering must keep:
- Early rooms total difficulty ≤ 6 (first 2 rooms)
- Mid rooms total difficulty 6–9 (next 3 rooms)
- Late rooms total difficulty 10–12 (final 2 rooms)

This keeps the curve stable even if order changes.

---

## 3) 🧠 RL Optimization Metrics (Most Important)

RL is offline (headless simulation) and exports tuned parameters:
- enemy counts/compositions
- hazard percentages/placements within caps
- optional stat scaling within bounds
- (later) boss add timing

RL must optimize *more than win rate* so it doesn’t “cheat” by making runs boring.

---

### 3.1 Primary Objective (Core)
**Target win probability for Biome 1:** **60% ± 5%**  
Reward is highest when win rate falls in this band.

Example shaping:
- reward += +1 if win
- reward += +0.5 if win_rate in band (60 ±5)
- penalty if too easy or too hard

---

### 3.2 Secondary Objectives (Quality / Fun Constraints)

These are equally important, otherwise RL can produce bad gameplay.

#### A) Time-to-clear targets (pace)
- Target Biome 1 clear time (average): **6–9 minutes**
- Penalize runs that are too fast (< 4 min) or too slow (> 12 min)

Why:
- Too fast = trivial or low enemy density
- Too slow = boring or too tanky

---

#### B) Damage fairness (avoid unavoidable damage)
Track:
- average damage taken per room
- spike damage events (big hits)
- hits taken during telegraph grace window (should be near 0)

Penalize:
- high spike damage frequency
- repeated hits within 1 sec (burst death)

---

#### C) Encounter diversity (avoid monotony)
Across runs:
- penalize repeating same enemy pattern too often
- encourage variety across combat rooms:
  - (melee-only, mixed, ranged-supported)

---

#### D) Space quality metrics (no “bad layouts”)
Per room:
- number of failed validations (regen count)
- path length spawn→exit
- safe area ratio
- choke points count

Penalize:
- frequent regenerations
- narrow choke points
- low safe area

---

#### E) Clumping metric (your big issue)
Track:
- time enemies are within 64 px of each other
- number of separation pushes applied
- overlap events (should be 0)

Penalize:
- high clumping time
- repeated overlap collisions

---

### 3.3 Final RL Reward Function (Suggested)

Total reward per run:

**R = W + B + P + F**

Where:
- **W (Win band reward)**:
  - +1 for win
  - -1 for loss
  - additional band shaping based on overall win-rate target
- **B (Balance reward)**:
  - reward closeness to 60% target
- **P (Pace reward)**:
  - reward for clear time in 6–9 min band
- **F (Fairness/Quality penalties)**:
  - penalties for spike damage, clumping, regen failures, choke points

---

## 4) Metrics To Log Per Run (Minimum Set)

### Run-level
- seed
- room_order
- win/loss
- total_time
- total_damage_taken
- total_damage_dealt
- deaths
- final_hp
- upgrades chosen (attack/defence/speed levels)

### Room-level
- room_type
- hazards% (lava, slow)
- anchor list used
- enemy composition pattern ID
- room clear time
- damage taken in room
- number of telegraph hits received (should be low)

### Combat-level
- hits taken during telegraph grace (should be ~0)
- clumping metric
- choke points count
- regen attempts

---

## 5) What We “Lock” Now (Biome 1 Completed)

✅ Biome 1 room types + constraints  
✅ Door rules  
✅ Spawn anchors per room template  
✅ Safe-zone exact tiles  
✅ Telegraph timing (red tile flash rules)  
✅ Enemy composition bounds per room type  
✅ Engage ranges + attack ranges  
✅ HP + damage values  
✅ Hitboxes/projectiles  
✅ Player movement + dash  
✅ Stat scaling + upgrades  
✅ Knockback + stagger rules  
✅ RL metrics + reward shaping targets  

Biome 1 is now fully specified end-to-end.

## Biome 1 — Spawn Telegraph Visual + Timing (LOCKED SPEC)

This telegraph is used for:
- Ambush room spawns
- Elite/boss summons (later biomes)
- Optional reinforcements (not used in Biome 1 MVP except Ambush)

**Determinism rule:** Given the same seed + same anchor list, telegraph timing and visuals must be identical.

---

### 1) Telegraph Overlay Asset

**Tile overlay size:** `32×32 px` (exactly 1 tile)  
**Render layer:** above floor/hazards, below entities  
**Blend:** alpha blend (no additive bloom in MVP)

**Asset paths (recommended):**
- `assets/effects/telegraph/telegraph_tile_32x32.png` (static base)
- (optional) `assets/effects/telegraph/telegraph_tile_anim_32x32.png` (sprite sheet)

If using a sprite sheet:
- Frames: **6 frames**
- Frame size: **32×32**
- Layout: horizontal strip (192×32)

---

### 2) Telegraph Color (LOCKED)

Telegraph color is **pure red** with a slight warm tint:
- Base color: `RGB(255, 40, 40)`
- Edge highlight: `RGB(255, 120, 80)` (thin rim only)

No orange telegraph in Biome 1 (reserved for boss/elite later biomes).

---

### 3) Opacity + Pulse Animation (LOCKED)

**Opacity:** pulsing between:
- Min alpha: **0.35**
- Max alpha: **0.70**

**Pulse count:** **3 pulses** total  
**Pulse frequency:** **6 Hz** (i.e., 6 cycles/sec)  
**Animation function:**
- `alpha(t) = lerp(0.35, 0.70, (sin(2π * 6 * t) + 1)/2)`

(Any equivalent deterministic pulse is allowed.)

---

### 4) Timing (LOCKED at 60 FPS)

Game update assumed 60 FPS baseline.

**Telegraph duration:** **0.50 sec**
- Total frames: **30 frames**
- Telegraph starts at frame `0`
- Spawn happens at frame `30`

**After spawn: "Idle Grace"**
- Duration: **0.40 sec**
- Total frames: **24 frames**
- Enemy AI cannot attack or deal damage during this window

So total reaction window:
- **0.50 sec telegraph + 0.40 sec grace = 0.90 sec**

---

### 5) Movement / Collision / Damage Rules (LOCKED)

- Telegraph overlay **does NOT block movement**
- Telegraph overlay **has no collision**
- Telegraph overlay **does NOT deal damage**
- Player standing on telegraph tile is allowed
- Enemy spawns even if player is standing on it, BUT:
  - Spawn must **fail-safe** to nearest valid tile within 1-tile radius if overlap would occur
  - Log event: `spawn_overlap_resolved = true`

---

### 6) Spawn Conditions + Validations (LOCKED)

Before telegraph begins:
- Anchor tile must be:
  - Not a wall
  - Not inside reserved safe zone
  - Not within 2 tiles of a door
  - Not within 4 tiles of player spawn zone (Biome 1 fairness)

At spawn time (frame 30):
- If tile is blocked by wall/invalid:
  - Choose next valid anchor in deterministic order
  - Telegraph transfers to that tile instantly (no re-timer)
  - Log event: `telegraph_anchor_retargeted = true`

---

### 7) Ambush Room Special (Biome 1)

Ambush rooms always use telegraph.

**Ambush timing:**
- Telegraph: **0.80 sec** (48 frames)
- Grace: **0.40 sec** (24 frames)

Total: 1.20 sec reaction time (small room fairness).

---

### 8) Logging (Required for RL later)

For every telegraphed spawn:
- room_id
- room_type
- seed
- anchor_position (row,col)
- telegraph_start_frame
- spawn_frame
- grace_end_frame
- enemy_type
- spawn_overlap_resolved (0/1)
- telegraph_anchor_retargeted (0/1)

# How To Use In Pygame

If using sprite sheet:

Frame width: 32

Total frames: 6

Animation speed: 30 frames total duration

So change frame every 5 game frames (30 / 6)

Example logic:

frame_index = (current_frame // 5) % 6
source_rect = pygame.Rect(frame_index * 32, 0, 32, 32)

# BIOME 1 — Telegraph Timing Per Enemy Type (LOCKED) + Safe-Zone Tile Reservation (LOCKED)

FPS reference: 60 FPS  
Tile size: 32×32 px  
Determinism: All timers are frame-based (or dt-accumulated but snapped to these exact durations).

Telegraph assets (by danger level):
- Standard spawn (red): `assets/effects/telegraph/telegraph_tile_anim_32x32.png`
- Elite spawn (gold): `assets/effects/telegraph/telegraph_elite_gold_anim_32x32.png`
- AoE ring (red): `assets/effects/telegraph/telegraph_aoe_ring_anim_256x256.png`
- Boss AoE (purple): `assets/effects/telegraph/telegraph_boss_purple_anim_256x256.png`
- Line strike (crack): `assets/effects/telegraph/telegraph_ground_crack_anim_256x64.png`

---

## A) Telegraph Timing (Per Enemy Type)

### A1) Standard Enemy Spawn (Combat reinforcements / optional)
Used for:
- Any non-ambush telegraphed spawn (future biomes)
- Not typically used in Biome 1 combat rooms (Biome 1 combat = instant spawn)

**Timing (LOCKED):**
- Telegraph: **0.50 sec** = 30 frames
- Idle grace after spawn: **0.40 sec** = 24 frames
- Total reaction window: **0.90 sec**

**Rules:**
- No collision / no damage
- If player overlaps anchor at spawn time → relocate to nearest valid tile within 1-tile radius

---

### A2) Ambush Room Spawn (Biome 1 REQUIRED)
Used for:
- Ambush Room enemies only

**Timing (LOCKED):**
- Telegraph: **0.80 sec** = 48 frames
- Idle grace: **0.40 sec** = 24 frames
- Total: **1.20 sec**

Asset:
- red standard telegraph tile (32×32)

---

### A3) Ranged Caster Projectile Cast Telegraph
Used for:
- Ranged casting wind-up (not spawn)

**Timing (LOCKED):**
- Cast wind-up telegraph: **0.30 sec** = 18 frames
- Projectile fires at end of wind-up
- No “idle grace” (casting itself is the telegraph)

Visual:
- small red pulse under caster feet OR a subtle glow above caster sprite (optional)
(If no extra art, reuse standard telegraph tile at 50% alpha.)

---

### A4) Brute Heavy Hit Telegraph (Melee)
Used for:
- Brute heavy wind-up (if Brute appears in Biome 1 optionally)

**Timing (LOCKED):**
- Wind-up telegraph: **0.45 sec** = 27 frames
- Active: 0.12 sec (already locked)
- Recovery: 0.55 sec

Visual:
- ground-crack line telegraph if it’s a forward strike
- otherwise standard red pulse

---

### A5) Brute Slam AoE Telegraph (if used)
Used for:
- AoE slam telegraph ring

**Timing (LOCKED):**
- AoE ring telegraph: **0.60 sec** = 36 frames
- Damage triggers at end of telegraph (frame 36)
- No follow-up grace (AOE telegraph is the warning)

Asset:
- red AoE ring (256×256)
- Centered at slam origin
- Render radius must match the actual AoE radius (70 px in Biome 1 elite slam; for brute slam choose and match)

---

### A6) Elite Guardian Attacks Telegraph
**Elite Heavy Swing**
- Wind-up: **0.45 sec** (same as spec)
- Visual: elite gold pulse under elite (32×32) at 60% alpha

**Elite Ground Slam**
- AoE ring telegraph: **0.60 sec** = 36 frames
- Visual: red AoE ring (or gold AoE ring later)

---

### A7) Mini Boss Attacks Telegraph (Biome 1 Guardian)

**Double Swipe**
- Wind-up: **0.40 sec** = 24 frames
- Visual: gold pulse (boss “threat” but not purple ultimate)

**Dash Strike**
- Telegraph line (crack): **0.55 sec** = 33 frames
- Damage applies at dash impact (end), not during dash
- Visual: ground-crack line telegraph aligned to dash direction

**Shockwave**
- AoE ring telegraph: **0.70 sec** = 42 frames
- Visual: boss purple AoE ring for dramatic clarity

---

### A8) Universal Telegraph Hard Rules
- Telegraph never blocks movement
- Telegraph never causes damage
- Enemies cannot deal damage during “idle grace” after spawn
- Telegraph duration is NEVER randomized in Biome 1
- If anchor invalid → deterministic retarget to next anchor (log it)

---

## B) Safe-Zone Tile Reservation System (Exact Tiles, LOCKED)

Safe-zones are **reserved tiles** where:
- No hazards (lava/slow)
- No walls
- No spawn anchors
- No telegraph spawns
- Must remain reachable from player spawn

Coordinate system:
- (row, col), origin (0,0) top-left

---

### B1) Combat Room (12×12)
Player spawn: (9,5)(9,6)  
Doors: top (0,5)(0,6), bottom (11,5)(11,6)

**Reserved Safe Zone (3×3):**
- Rows **8–10**
- Cols **4–6**

Explicit tiles:
(8,4)(8,5)(8,6)
(9,4)(9,5)(9,6)
(10,4)(10,5)(10,6)

Additionally reserved:
- Door buffer (no hazards, no spawn):
  - All door tiles + 1-tile ring around them

---

### B2) Ambush Room (8×8)
Player spawn: (6,3)(6,4)  
Doors: top (0,3)(0,4), bottom (7,3)(7,4)

**Reserved Safe Zone (3×3):**
- Rows **3–5**
- Cols **2–4**

Explicit tiles:
(3,2)(3,3)(3,4)
(4,2)(4,3)(4,4)
(5,2)(5,3)(5,4)

Rule:
- No ambush anchors or telegraphs can occur inside this safe zone.

---

### B3) Safe Room (12×12)
Player spawn: (9,5)(9,6)  
Fountain: (5,5)(5,6)  
Upgrades: (4,4)(4,7)(6,4)(6,7)

**Reserved Safe Zone (5×5):**
- Rows **4–8**
- Cols **4–8**

Explicit tiles:
Rows 4..8 × Cols 4..8 (25 tiles)

No hazards in safe room (lava = 0% hard rule).
Slow tiles allowed only outside the 5×5 reserved zone (Biome 1: 0–5%).

---

### B4) Elite Room (16×16)
Player spawn: (13,7)(13,8)

**Reserved Spawn Safety Zone (4×4):**
- Rows **12–15**
- Cols **6–9**

Explicit tiles:
Rows 12..15 × Cols 6..9 (16 tiles)

Additionally reserved:
- Center readability zone (recommended “soft rule”):
  - Keep rows 6..9, cols 6..9 free of lava (walls ok at edges)

---

### B5) Mini Boss Room (16×16)
Player spawn: (13,7)(13,8)  
Boss spawn zone: rows 7..8, cols 7..8 (2×2)

**Reserved Spawn Safety Zone (4×4):**
- Rows **12–15**
- Cols **6–9**

Boss spawn zone is also reserved:
- No hazards inside boss 2×2 spawn zone
- No walls inside boss spawn zone

Additionally reserved:
- No telegraph spawns within 2 tiles of player safe zone

---

## C) Validation Checks (Must Pass)

For each room:
1. Safe-zone tiles are floor-only
2. Spawn tile is floor-only
3. Door tiles are floor-only
4. Path exists spawn → exit (or spawn → boss zone for mini boss)
5. No anchors exist inside safe zones
6. Hazard placement respects all reserved tiles

If any check fails:
- regenerate deterministically (seed + attempt index)
- log `room_regen_attempt += 1`

# BIOME 1 — Lock Attack Radius ↔ Telegraph Radius Mapping (LOCKED)

Goal:
- Telegraph visuals must match the *real* damage area.
- Player trust: if they stand outside the ring/line, they should not get hit.
- Deterministic rendering: same radius every time.

Units:
- Tiles are 32×32 px
- All radii below are in **pixels**, with tile equivalents.

---

## 1) General Mapping Rules (Hard)

### 1.1 Exact Match Rule
For any AoE or line attack:
- **Telegraph size == Damage size**
- No hidden padding beyond **+2 px** (only for rounding)

### 1.2 Hit Resolution Timing
- Damage is applied **exactly at telegraph end frame**
- Telegraph stays visible until the damage frame, then disappears.

### 1.3 Render Center / Direction
- Rings are centered at the attack origin (enemy center or impact point).
- Lines are aligned to the attack direction vector at telegraph start.
- If enemy rotates during telegraph, the telegraph direction does **not** change (locks direction).

---

## 2) AoE Ring Mapping (Circle Attacks)

### 2.1 Brute Slam (if used in Biome 1)
Damage AoE radius:
- **64 px** (2 tiles)

Telegraph asset:
- `telegraph_aoe_ring_anim_256x256.png`

Render scale rule:
- The 256×256 art is a *canvas*.  
- You draw the ring so the visible ring radius represents **64 px**.

Implementation convention (LOCKED):
- Treat the ring graphic as having a reference radius of **120 px** (visual outer ring).
- So scale factor:
  - `scale = damage_radius_px / 120`

For Brute Slam:
- scale = 64 / 120 = **0.5333×**

---

### 2.2 Elite Ground Slam (Biome 1 Elite)
Damage AoE radius:
- **70 px** (≈ 2.2 tiles)

Telegraph asset:
- `telegraph_elite_gold_aoe_anim_256x256.png` (preferred)
  - fallback: red AoE ring

Scale:
- scale = 70 / 120 = **0.5833×**

Damage application:
- single hit at telegraph end

---

### 2.3 Mini Boss Shockwave (Biome 1 Guardian)
Damage AoE radius:
- **128 px** (4 tiles)

Telegraph asset:
- `telegraph_boss_purple_anim_256x256.png`

Scale:
- scale = 128 / 120 = **1.0667×**

Rule:
- Shockwave does NOT hit outside the purple ring.

---

## 3) Line Telegraph Mapping (Dash / Charge Strikes)

Line telegraphs are rectangles (capsule-like), rendered using the 256×64 asset.

### 3.1 Boss Dash Strike (Mini Boss / Final Boss)
Telegraph asset:
- `telegraph_boss_purple_line_anim_256x64.png`

Damage shape (capsule rectangle):
- Length: **128 px** (4 tiles)
- Width: **40 px** (approx player width + fairness)

Mapping rule:
- The line graphic is a canvas of 256 px long.
- Reference length = **224 px** usable area (since margins exist).
- scale length so that usable area equals damage length.

ScaleX:
- scale_x = damage_length / 224

For 128 px dash length:
- scale_x = 128 / 224 = **0.5714×**

Width scaling:
- Reference width = **20 px** half-width in art
- scale_y = (damage_width/2) / 20 = 20 / 20 = **1.0×**

Damage timing:
- Damage occurs only at dash impact (end).
- During dash movement: no damage (Biome 1 fairness rule).

---

### 3.2 Flanker Dash Strike (if used)
Telegraph asset:
- `telegraph_ground_crack_anim_256x64.png`

Damage capsule:
- Length: **96 px** (3 tiles)
- Width: **32 px** (1 tile)

ScaleX:
- 96 / 224 = **0.4286×**
ScaleY:
- (32/2)/20 = 16/20 = **0.8×**

---

## 4) Melee Swings (Non-AoE, Non-Line)

Melee swings use *wind-up telegraph* (enemy animation / glow) but do not require rings/lines.

### 4.1 Melee Grunt Swing
Damage hit circle radius:
- **20 px**
No ring telegraph.
Telegraph is only:
- wind-up animation 0.25 sec

### 4.2 Flanker Strike
Damage hit circle radius:
- **16 px**
No ring telegraph.

### 4.3 Elite Heavy Swing
Damage circle radius:
- **28 px**
Telegraph:
- gold pulse under feet during 0.45 sec wind-up
No AoE ring.

---

## 5) Validation Rules (Must Pass)

### 5.1 Debug overlay check (dev-only)
When debug is ON:
- Draw the damage circle/rectangle outline in white
- Ensure it matches the telegraph ring/line

### 5.2 Unit tests (determinism)
For each attack:
- run with fixed seed
- confirm telegraph scaling equals expected scale factor
- confirm damage only applies within mapped area

---

## 6) Quick Reference Table

| Attack | Damage Shape | Damage Size | Telegraph Asset |
|---|---|---|---|
| Brute Slam | Circle | r=64 px | red AoE ring |
| Elite Slam | Circle | r=70 px | gold AoE ring |
| Boss Shockwave | Circle | r=128 px | purple AoE ring |
| Boss Dash | Capsule | L=128 px, W=40 px | purple line |
| Flanker Dash | Capsule | L=96 px, W=32 px | red crack line |
| Grunt Swing | Circle | r=20 px | no ring (anim only) |
| Flanker Strike | Circle | r=16 px | no ring (anim only) |
| Elite Swing | Circle | r=28 px | gold pulse tile |

# BIOME 1 — Safe-Zone Reservation System (Mathematically LOCKED)

Tile size: 32×32 px  
Coordinate system: (row, col), origin (0,0) top-left.  
Room grids are indexed 0..(H-1), 0..(W-1).

**Reserved tiles mean:**
- No hazards (lava/slow)
- No walls
- No enemy spawn anchors
- No telegraph spawns
- No pickups (unless explicitly allowed in Safe Room)
- Must remain reachable from player spawn

---

## 0) Global Reserved Rules (Apply to ALL Rooms)

### 0.1 Door Buffer (all rooms)
For every door tile `D`, reserve:
- the door tile itself
- plus 1-tile ring around it (Manhattan distance ≤ 1)

This prevents door camping, unfair hazard placement, and spawn clipping.

### 0.2 Player Spawn Buffer (all rooms)
Reserve:
- the player spawn tiles (2 tiles)
- plus 1-tile ring around the spawn center

(Combat/Ambush/Elite/MiniBoss also have larger safe zones defined below.)

---

## 1) Combat Room (12×12) — Safe Zones

### 1.1 Door positions (2-wide)
- Top door tiles: (0,5), (0,6)
- Bottom door tiles: (11,5), (11,6)

### 1.2 Player spawn (2-wide)
- Player spawn tiles: (9,5), (9,6)

### 1.3 Safe Zone A — Spawn Safety Zone (3×3) ✅
Rows 8..10, Cols 4..6 (3×3)

Explicit tiles:
- (8,4)(8,5)(8,6)
- (9,4)(9,5)(9,6)
- (10,4)(10,5)(10,6)

### 1.4 Reserved Exit Landing Zone ✅
Reserve a small landing zone just inside each door so the player never enters directly into hazards/enemies.

Top exit landing zone (2×2):
- (1,5)(1,6)
- (2,5)(2,6)

Bottom exit landing zone (2×2):
- (9,5)(9,6)  (already reserved by spawn)
- (10,5)(10,6) (already inside 3×3 zone)

### 1.5 Neutral Zone — Center Clarity (2×2) ✅
Purpose: keep the middle readable (avoid clutter + allow dodging).

Reserve center 2×2:
- (5,5)(5,6)
- (6,5)(6,6)

Rule:
- No hazards/walls/spawns here in Biome 1 combat rooms.

---

## 2) Ambush Room (8×8) — Safe Zones

### 2.1 Door positions
- Top door tiles: (0,3), (0,4)
- Bottom door tiles: (7,3), (7,4)

### 2.2 Player spawn (2-wide)
- Player spawn tiles: (6,3), (6,4)

### 2.3 Safe Zone A — Central Safety Zone (3×3) ✅
Rows 3..5, Cols 2..4 (3×3)

Explicit tiles:
- (3,2)(3,3)(3,4)
- (4,2)(4,3)(4,4)
- (5,2)(5,3)(5,4)

Rule:
- Ambush anchors cannot be inside this zone.
- Ambush telegraphs cannot occur inside this zone.

### 2.4 Exit Landing Zone ✅
Top landing (2×2):
- (1,3)(1,4)
- (2,3)(2,4)

Bottom landing (2×2):
- (5,3)(5,4)
- (6,3)(6,4) (spawn tiles already reserved)

---

## 3) Safe Room (12×12) — Safe Zones

Safe room is non-combat; its safe zone is larger and also reserves interactable placement.

### 3.1 Door positions
- Top door tiles: (0,5), (0,6)
- Bottom door tiles: (11,5), (11,6)

### 3.2 Player spawn (2-wide)
- Player spawn tiles: (9,5), (9,6)

### 3.3 Main Safe Zone — 5×5 Interaction Area ✅
Rows 4..8, Cols 4..8 (5×5)

Explicit tiles:
Rows 4..8 × Cols 4..8 (25 tiles)

### 3.4 Reserved Interactable Tiles ✅
Inside the 5×5 safe zone, reserve these for interactables (no hazards/walls):

- Fountain (2 tiles): (5,5), (5,6)
- Upgrade pedestals (4 tiles):
  - (4,4), (4,7), (6,4), (6,7)

Rule:
- Pickups may appear only in this 5×5 region (Biome 1 MVP).
- No lava in safe room (lava = 0% hard rule).
- Slow tiles allowed only outside the 5×5 region (0–5% optional).

---

## 4) Elite Room (16×16) — Safe Zones

### 4.1 Doors
- Top door tiles: (0,7), (0,8)
- Bottom door tiles: (15,7), (15,8)

### 4.2 Player spawn (2-wide)
- Player spawn tiles: (13,7), (13,8)

### 4.3 Safe Zone A — Spawn Safety Zone (4×4) ✅
Rows 12..15, Cols 6..9 (4×4)

Explicit tiles:
Rows 12..15 × Cols 6..9 (16 tiles)

### 4.4 Neutral Zone — Center Clarity (3×3) ✅
Reserve a 3×3 in the middle to ensure elite fights are readable.

Center 3×3:
Rows 7..9, Cols 7..9

Explicit tiles:
(7,7)(7,8)(7,9)
(8,7)(8,8)(8,9)
(9,7)(9,8)(9,9)

Rule:
- No lava/walls/spawns in this zone in Biome 1.
- (Slow tiles also not allowed here.)

---

## 5) Mini Boss Room (16×16) — Safe Zones

### 5.1 Doors
- Top door tiles: (0,7), (0,8)
- Bottom door tiles: (15,7), (15,8)

### 5.2 Player spawn
- Player spawn tiles: (13,7), (13,8)

### 5.3 Boss spawn zone ✅
Boss spawns in a reserved 2×2 center block:
Rows 7..8, Cols 7..8

Explicit tiles:
- (7,7)(7,8)
- (8,7)(8,8)

Rule:
- No hazards/walls/spawns inside boss spawn zone.

### 5.4 Safe Zone A — Player Safety Zone (4×4) ✅
Rows 12..15, Cols 6..9 (4×4)

Explicit tiles:
Rows 12..15 × Cols 6..9 (16 tiles)

### 5.5 Neutral Zone — Arena Clarity (5×5) ✅
To prevent unfair choke layouts, reserve an arena clarity square:

Rows 6..10, Cols 6..10 (5×5)

Rule:
- No walls inside this 5×5 in Biome 1 boss room.
- Hazards inside this 5×5 are NOT allowed in Biome 1 MVP.

(You can allow hazards in later biomes.)

---

## 6) Validation Checks (Must Pass)

Before room is accepted:
1. Reserved tiles contain floor only (no walls, no hazards).
2. No anchors lie inside reserved zones.
3. Path exists: spawn → exit (or spawn → boss zone).
4. Door buffer is clean.
5. If check fails → regenerate deterministically.

Log:
- `room_regen_attempt`
- `failed_rule_id` (e.g., SAFEZONE_BLOCKED, DOOR_BUFFER_VIOLATION)

---

## 7) Quick Summary Table

| Room Type | Size | Primary Safe Zone | Neutral Zone |
|---|---:|---|---|
| Combat | 12×12 | 3×3 at rows 8..10 cols 4..6 | center 2×2 at (5..6,5..6) |
| Ambush | 8×8 | 3×3 at rows 3..5 cols 2..4 | (none extra) |
| Safe | 12×12 | 5×5 at rows 4..8 cols 4..8 | interactables reserved |
| Elite | 16×16 | 4×4 at rows 12..15 cols 6..9 | center 3×3 at rows 7..9 cols 7..9 |
| Mini Boss | 16×16 | 4×4 at rows 12..15 cols 6..9 | arena 5×5 at rows 6..10 cols 6..10 + boss 2×2 |

## Biome 1 — Room Validation + Seeded Regeneration (Implementation Pseudocode)

This is the exact validation pipeline used after a room layout is generated
(walls + hazards + doors + anchors). If any check fails, the room regenerates
deterministically using the same seed + attempt index.

---

### 1) Deterministic RNG Setup (Per Room)

Each room uses a derived seed so that:
- Changing Room 3 does not change Room 4
- Regeneration attempts are deterministic

**Derived seed:**
- `room_seed = hash(run_seed, biome_id, room_index, room_type)`
- `attempt_seed = hash(room_seed, regen_attempt)`

Rule:
- All random calls inside that attempt use `attempt_seed`.

---

### 2) Reserved Tile Generation

Before validating, compute `reserved_tiles` as a set of (row,col).

Reserved tiles include:
- Door buffer tiles (door tiles + 1-tile ring)
- Player spawn tiles
- Room-type safe zone tiles (3×3 / 4×4 / 5×5 as locked)
- Neutral zones (combat center 2×2, elite center 3×3, boss arena 5×5)
- Boss spawn zone tiles (mini boss room only)

---

### 3) Validation Checks (Must Pass)

Checks are run in this exact order:

#### Rule V1 — Bounds
- All walls/hazards/doors/anchors must be within grid bounds.
- If fail: `FAIL_BOUNDS`

#### Rule V2 — Reserved Tiles are Floor-only
For each tile in `reserved_tiles`:
- Must be `FLOOR`
- Must NOT be `WALL`
- Must NOT be `LAVA`
- Must NOT be `SLOW`

If fail: `FAIL_RESERVED_BLOCKED`

#### Rule V3 — Door Buffer Clean
For each door tile and its 1-ring buffer:
- Must be floor-only
- Must not contain hazard or wall
- Must not contain anchor

If fail: `FAIL_DOOR_BUFFER`

#### Rule V4 — Anchor Validity
For each anchor in `spawn_anchors`:
- Must be floor tile
- Must not be in `reserved_tiles`
- Must not be in door buffer
- Must not overlap another anchor

If fail: `FAIL_ANCHOR_INVALID`

#### Rule V5 — Minimum Anchor Count
- Room must have ≥ `ANCHOR_MIN` anchors
- Biome 1 targets:
  - Combat (12×12): 10 anchors
  - Ambush (8×8): 8 anchors
  - Elite (16×16): 12 anchors
  - Mini Boss (16×16): 12 anchors
  - Safe: 0 anchors required

If fail: `FAIL_ANCHOR_COUNT`

#### Rule V6 — Path Connectivity (Spawn → Exit)
Run BFS/DFS on walkable tiles (floor + slow, but not walls/lava):
- Must reach at least one exit door landing zone.
- Mini Boss room: must reach boss zone and exit door.

If fail: `FAIL_PATH_BLOCKED`

#### Rule V7 — Safe Zone Reachability
- At least 80% of safe zone tiles must be reachable from spawn.
- This prevents “safe zone sealed by walls” edge cases.

If fail: `FAIL_SAFEZONE_UNREACHABLE`

#### Rule V8 — Hazard Caps (Biome 1)
Validate hazard percentages against room-type caps:
- Safe room: lava 0% (hard), slow 0–5% outside safe zone only
- Combat: lava 0–10%, slow 5–15%
- Ambush: lava 0–5%, slow 0–10%
- Elite: lava 0–8%, slow 5–15%
- Mini Boss: lava 0% in arena 5×5, slow 0–5% outside arena only

If fail: `FAIL_HAZARD_CAP`

---

### 4) Seeded Regeneration Loop


function generate_room_layout(run_seed, biome_id, room_index, room_type):
room_seed = hash(run_seed, biome_id, room_index, room_type)

for regen_attempt in range(0, MAX_REGEN_ATTEMPTS):
    rng = RNG(hash(room_seed, regen_attempt))

    layout = build_layout_with_rng(rng, room_type)
    reserved = compute_reserved_tiles(room_type)

    result = validate(layout, reserved, room_type)

    if result.ok:
        layout.meta.regen_attempt = regen_attempt
        return layout

    log_validation_failure(
        biome_id=biome_id,
        room_index=room_index,
        room_type=room_type,
        regen_attempt=regen_attempt,
        failed_rule_id=result.failed_rule_id
    )

# If repeated failures occur:
# fallback to a known-safe template layout for that room type
return load_fallback_template(room_type)

Recommended:
- `MAX_REGEN_ATTEMPTS = 12`
- If it still fails: fallback template ensures run never crashes.

---

### 5) Logging Fields (Required)

For each room:
- run_seed, room_seed
- biome_id, room_index, room_type
- regen_attempt_used
- failed_rule_id counts (aggregate)
- hazard_percent_lava, hazard_percent_slow
- anchor_count
- path_length_spawn_to_exit
- reserved_tile_count

This logging is RL-critical and also helps debugging.

---

### 6) Notes for Cursor / Implementation

- Keep `reserved_tiles` as a `set` for O(1) membership checks.
- Use deterministic ordering:
  - sort anchors and doors before validation logs
- BFS should treat:
  - floor + slow = walkable
  - wall + lava = blocked
- Validation must run BEFORE spawns/hazards are finalized for runtime.

# BIOME 1 — Template Spawn Anchor Coordinate Sets (LOCKED)

Tile size: 32×32 px  
Coordinate system: (row, col), origin (0,0) top-left.  
Anchor tiles are valid **only if** they are floor and not inside reserved zones.

Rules (apply to all room types):
- Anchors must NOT be in any reserved safe zone or door buffer
- Min enemy–enemy spawn distance: ≥ 2 tiles (64 px)
- Min enemy–player spawn distance: ≥ 4 tiles (128 px)
- If an anchor becomes invalid due to walls/hazards, it is skipped (deterministic)

---

## 1) Combat Room Anchors (12×12) — 10 anchors

Room: rows 0..11, cols 0..11  
Doors: top (0,5)(0,6), bottom (11,5)(11,6)  
Reserved: spawn safe zone rows 8..10 cols 4..6, center 2×2 rows 5..6 cols 5..6, door buffers.

**Anchor Set (LOCKED):**
- A1 (2,2)
- A2 (2,4)
- A3 (2,7)
- A4 (2,9)
- A5 (4,2)
- A6 (4,9)
- A7 (7,2)
- A8 (7,9)
- A9 (9,2)
- A10 (9,9)

Notes:
- Anchors avoid center and spawn safe zone.
- Anchors provide left/right symmetry and enough spacing.

---

## 2) Ambush Room Anchors (8×8) — 8 anchors

Room: rows 0..7, cols 0..7  
Doors: top (0,3)(0,4), bottom (7,3)(7,4)  
Reserved: safe zone rows 3..5 cols 2..4, door buffers.

**Anchor Set (LOCKED):**
- A1 (1,1)
- A2 (1,3)
- A3 (1,6)
- A4 (3,6)
- A5 (6,1)
- A6 (6,6)
- A7 (4,1)
- A8 (3,0)  *(edge anchor; only if floor and not wall)*

If A8 is invalid often, replace A8 with:
- A8_alt (2,5)

Ambush telegraphs use these anchors only.

---

## 3) Safe Room Anchors (12×12)
Safe room is non-combat.

**Anchor Set:**
- None required (anchors = 0)

(Interactables have their own reserved positions.)

---

## 4) Elite Room Anchors (16×16) — 12 anchors

Room: rows 0..15, cols 0..15  
Doors: top (0,7)(0,8), bottom (15,7)(15,8)  
Reserved:
- Player safe zone rows 12..15 cols 6..9
- Center clarity zone rows 7..9 cols 7..9
- Door buffers

**Anchor Set (LOCKED):**
- A1 (2,2)
- A2 (2,6)
- A3 (2,9)
- A4 (2,13)
- A5 (5,3)
- A6 (5,12)
- A7 (10,3)
- A8 (10,12)
- A9 (12,2)
- A10 (12,13)
- A11 (8,2)
- A12 (8,13)

Notes:
- Anchors avoid center 3×3 clarity zone.
- Anchors avoid player safe zone near bottom.
- Anchors include mid-left/right for reinforcement-style spacing.

---

## 5) Mini Boss Room Anchors (16×16) — 12 anchors

Room: rows 0..15, cols 0..15  
Reserved:
- Player safe zone rows 12..15 cols 6..9
- Boss spawn zone rows 7..8 cols 7..8
- Arena clarity zone rows 6..10 cols 6..10 (no walls/hazards)
- Door buffers

Mini boss room anchors are for:
- (Future) phase add spawns
- (Future) hazard spawns
In Biome 1 MVP: boss has no adds, but anchors are still defined for completeness.

**Anchor Set (LOCKED):**
- A1 (2,3)
- A2 (2,7)
- A3 (2,11)
- A4 (4,2)
- A5 (4,13)
- A6 (8,1)
- A7 (8,14)
- A8 (11,2)
- A9 (11,13)
- A10 (13,3)
- A11 (13,11)
- A12 (1,8)

Notes:
- Anchors are outside boss arena clarity zone.
- Anchors are away from player safe zone.

---

## 6) Deterministic Anchor Selection (Per Room)

When spawning N enemies:
1. Build `valid_anchors = [anchors not blocked AND not reserved]`
2. Sort anchors by fixed order A1..Ak
3. Choose anchors using seeded shuffle:
   - `rng.shuffle(valid_anchors)`
4. Pick first N anchors
5. Validate min-distance between chosen anchors:
   - if violation, skip anchor and pick next (deterministic)

Log:
- anchors_selected (list of (row,col))
- anchors_skipped_due_to_invalid
- anchors_skipped_due_to_distance

---

## 7) Quick Counts (Biome 1 Defaults)

| Room Type | Anchor Count | Typical Spawn Count |
|---|---:|---:|
| Combat 12×12 | 10 | 3–5 |
| Ambush 8×8 | 8 | 3–4 |
| Elite 16×16 | 12 | 3–4 |
| MiniBoss 16×16 | 12 | 0 (Biome 1 MVP) |

# BIOME 1 — ASCII Room Templates (LOCKED Layout Reference)

Legend:
- `#` = wall boundary (outer border)
- `.` = floor (walkable)
- `D` = door tile (2-wide)
- `S` = player spawn tiles (2 tiles)
- `R` = reserved safe-zone / reserved tiles (no hazards, no spawns)
- `N` = neutral clarity zone (reserved; no hazards/spawns)
- `B` = boss spawn zone (2×2)
- `A` = spawn anchor point (valid spawn candidate)

Coordinate note:
- These ASCII diagrams are conceptual references that match the locked coordinates.
- The generator may add interior walls/hazards elsewhere, but it must NOT change:
  - doors
  - reserved zones
  - spawn zone
  - neutral zones
  - anchor coordinates

---

## 1) Ambush Room (8×8)

Doors:
- Top: (0,3)(0,4)
- Bottom: (7,3)(7,4)

Spawn:
- (6,3)(6,4)

Reserved Safe Zone (3×3):
- rows 3..5, cols 2..4

Anchors (8):
(1,1) (1,3) (1,6) (3,6) (6,1) (6,6) (4,1) (3,0)*


row\col 0 1 2 3 4 5 6 7
0 # # # D D # # #
1 # A . A . . A #
2 # . . . . . . #
3 A . R R R . A #
4 # A R R R . . #
5 # . R R R . . #
6 # A . . S S A #
7 # # # D D # # #


Notes:
- `A` at (3,0) is the left-edge anchor and is allowed only if it’s floor.
- No ambush telegraph may occur on any `R` tile.

---

## 2) Safe Room (12×12)

Doors:
- Top: (0,5)(0,6)
- Bottom: (11,5)(11,6)

Spawn:
- (9,5)(9,6)

Reserved Interaction Zone (5×5):
- rows 4..8, cols 4..8

Fountain (2 tiles):
- (5,5)(5,6) inside reserved zone

Pedestals (4 tiles):
- (4,4) (4,7) (6,4) (6,7)

No anchors in safe room.


row\col 0 1 2 3 4 5 6 7 8 9 10 11
0 # # # # # D D # # # # #
1 # . . . . . . . . . . #
2 # . . . . . . . . . . #
3 # . . . . . . . . . . #
4 # . . . R R R R R . . #
5 # . . . R R R R R . . #
6 # . . . R R R R R . . #
7 # . . . R R R R R . . #
8 # . . . R R R R R . . #
9 # . . . . S S . . . . #
10 # . . . . . . . . . . #
11 # # # # # D D # # # # #


Notes:
- Fountain + pedestals are placed inside the `R` region.
- No lava anywhere in safe room (Biome 1 hard rule).

---

## 3) Elite Room (16×16)

Doors:
- Top: (0,7)(0,8)
- Bottom: (15,7)(15,8)

Spawn:
- (13,7)(13,8)

Reserved Spawn Safe Zone (4×4):
- rows 12..15, cols 6..9

Neutral Center Clarity Zone (3×3):
- rows 7..9, cols 7..9

Anchors (12):
(2,2)(2,6)(2,9)(2,13)(5,3)(5,12)(10,3)(10,12)(12,2)(12,13)(8,2)(8,13)


row 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
0 # # # # # # # D D # # # # # # #
1 # . . . . . . . . . . . . . . #
2 # . A . . . A . A . . . . A . #
3 # . . . . . . . . . . . . . . #
4 # . . . . . . . . . . . . . . #
5 # . . A . . . . . . . . A . . #
6 # . . . . . . . . . . . . . . #
7 # . . . . . . N N N . . . . . #
8 # . A . . . . N N N . . . A . #
9 # . . . . . . N N N . . . . . #
10 # . . A . . . . . . . . A . . #
11 # . . . . . . . . . . . . . . #
12 # . A . . . R R R R . . . A . #
13 # . . . . . R R S S . . . . . #
14 # . . . . . R R R R . . . . . #
15 # # # # # # # D D # # # # # # #


Notes:
- `R` zone protects spawn entry.
- `N` zone ensures the center stays readable (no hazards, no walls, no spawns).
- Elite enemy itself can spawn anywhere outside reserved zones, but supports use anchors.

---

## 4) Mini Boss Room (16×16)

Doors:
- Top: (0,7)(0,8)
- Bottom: (15,7)(15,8)

Player spawn:
- (13,7)(13,8)

Boss spawn zone (2×2):
- rows 7..8, cols 7..8

Reserved Player Safe Zone (4×4):
- rows 12..15, cols 6..9

Arena Clarity Zone (5×5):
- rows 6..10, cols 6..10 (no walls/hazards in Biome 1)

Anchors (12):
(2,3)(2,7)(2,11)(4,2)(4,13)(8,1)(8,14)(11,2)(11,13)(13,3)(13,11)(1,8)


row 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
0 # # # # # # # D D # # # # # # #
1 # . . . . . . . A . . . . . . #
2 # . . A . . . A . . . A . . . #
3 # . . . . . . . . . . . . . . #
4 # . A . . . . . . . . . . A . #
5 # . . . . . . . . . . . . . . #
6 # . . . . . . N N N N N . . . #
7 # . . . . . . N B B N N . . . #
8 # A . . . . . N B B N N . . A #
9 # . . . . . . N N N N N . . . #
10 # . . . . . . N N N N N . . . #
11 # . A . . . . . . . . . . A . #
12 # . . . . . R R R R . . . . . #
13 # . . . A . R R S S . . A . . #
14 # . . . . . R R R R . . . . . #
15 # # # # # # # D D # # # # # # #


Notes:
- `B` is the boss 2×2 spawn zone.
- `N` (arena clarity 5×5) must stay free of walls/hazards in Biome 1 MVP.
- Anchors exist for future adds (not used in Biome 1 MVP).

---

If you want next:
- I can generate the **Combat Room (12×12) ASCII template** too (with its center 2×2 neutral zone and the 10 anchors),
so your Requirements Analysis has all room types visually locked.

# BIOME 1 — Enemy Composition Rules (HARD-LOCKED, Deterministic-Bounded)

Goal:
- Biome 1 teaches melee pressure + flanking fundamentals
- No ranged pressure yet (keeps early game fair)
- Brute appears rarely as a “mini-lesson”
- Deterministic, seed-bounded selection per room type
- RL can tune within caps later, but cannot break these hard bounds in Biome 1 MVP

Enemy types available in Biome 1 MVP:
- `SWARM` (melee grunt)
- `FLANKER` (fast melee)
- `BRUTE` (heavy melee, optional)
Not allowed in Biome 1 MVP:
- `RANGED`
- `HEAVY`
- `SUPPRESSOR`
- Any other biome-specific enemies

---

## 1) Global Composition Constraints (Biome 1)

### 1.1 Global per-room limits (hard)
- Max BRUTE per room: **1**
- Max FLANKER per room: **2**
- Min SWARM per combat/ambush room: **1** (so room always has baseline melee)

### 1.2 Global biome-wide pacing (soft cap but enforced via room templates)
Across the full biome (rooms 1–7):
- Total BRUTES spawned: **0–2**
- Total FLANKERS spawned: **2–6**
- Total SWARMS spawned: remainder

This ensures variety without turning Biome 1 into “brute spam”.

---

## 2) Room-Type Composition (HARD CAPS)

### 2.1 Combat Room (12×12) — Biome 1
Allowed: SWARM, FLANKER, BRUTE  
Not allowed: RANGED, HEAVY

**Enemy Count:** **3–5** (hard)  
**Hard caps:**
- SWARM: **2–4**
- FLANKER: **0–2**
- BRUTE: **0–1**
- Total: **≤ 5**

**Required patterns (deterministic set):**
Combat room composition is selected from one of these pattern IDs:

| Pattern ID | SWARM | FLANKER | BRUTE | Total |
|---|---:|---:|---:|---:|
| C1 | 3 | 0 | 0 | 3 |
| C2 | 3 | 1 | 0 | 4 |
| C3 | 4 | 1 | 0 | 5 |
| C4 | 2 | 2 | 0 | 4 |
| C5 | 3 | 2 | 0 | 5 |
| C6 | 3 | 0 | 1 | 4 |
| C7 | 2 | 1 | 1 | 4 |
| C8 | 3 | 1 | 1 | 5 |

Biome 1 “early rooms” restriction:
- Rooms 1–2 cannot use patterns with BRUTE (C6–C8).

---

### 2.2 Ambush Room (8×8) — Biome 1
Allowed: SWARM, FLANKER  
BRUTE optional but **off by default** for MVP (recommended).

**Enemy Count:** **3–4** (hard)  
**Hard caps:**
- SWARM: **2–4**
- FLANKER: **0–1** (smaller room)
- BRUTE: **0** (MVP hard lock)

Ambush composition patterns:

| Pattern ID | SWARM | FLANKER | Total |
|---|---:|---:|---:|
| A1 | 3 | 0 | 3 |
| A2 | 3 | 1 | 4 |
| A3 | 4 | 0 | 4 |
| A4 | 2 | 1 | 3 |

Ambush timing:
- Uses telegraph spawns only (locked earlier).

---

### 2.3 Safe Room (12×12)
- No enemies (hard)

---

### 2.4 Elite Room (16×16) — Biome 1
Elite room is:
- 1 Elite Guardian + supports (no brute unless you want it)

Allowed supports: SWARM, FLANKER  
Not allowed: RANGED, HEAVY, BRUTE (MVP)

**Hard composition:**
- `ELITE_GUARDIAN`: **1** (always)
- Supports: **2–3** total (hard)

Support caps:
- SWARM: **1–3**
- FLANKER: **0–1**
- BRUTE: **0** (MVP)

Elite support patterns:

| Pattern ID | ELITE | SWARM | FLANKER | Total Enemies |
|---|---:|---:|---:|---:|
| E1 | 1 | 2 | 0 | 3 |
| E2 | 1 | 3 | 0 | 4 |
| E3 | 1 | 2 | 1 | 4 |

Rule:
- Elite always spawns at room center-ish (not in safe zones).
- Supports spawn at anchors with ≥2 tiles separation.

---

### 2.5 Mini Boss Room (16×16) — Biome 1
**Hard composition:**
- `MINI_BOSS_GUARDIAN`: **1**
- Adds: **0** (MVP hard lock)

(Anchors exist for future phases/biomes, but unused in Biome 1.)

---

## 3) Deterministic Pattern Selection (Seed-Bounded)

For each room:
1. Build the allowed pattern list based on room_type and room_index stage:
   - Stage Early (rooms 1–2): exclude BRUTE patterns
   - Stage Mid (rooms 3–5): allow all Combat patterns, allow Ambush patterns
   - Stage Late (rooms 6–7): Elite and MiniBoss fixed

2. Select pattern deterministically:
- `pattern_index = RNG(room_seed).randint(0, len(patterns)-1)`
- Choose that pattern ID

3. Spawn enemies using anchor selection rules:
- seeded shuffle anchors
- take first N anchors
- enforce min distance; skip invalid

Log:
- `room_seed`
- `pattern_id`
- `enemy_list` (types)
- `anchors_selected`

---

## 4) RL Tuning (Allowed Later, But Bounded)

RL may tune:
- Probability weights of patterns (e.g., more C2 than C5)
- Whether BRUTE appears 0–2 times across Biome 1 (still respecting early-room restriction)
- Enemy counts only by choosing from existing patterns

RL cannot:
- Add RANGED/HEAVY in Biome 1
- Exceed caps (e.g., 2 brutes, 3 flankers in one room)
- Change MiniBoss adds rule in MVP

---

## 5) Quick Summary Table

| Room Type | Allowed | Total Enemies | Hard Caps |
|---|---|---:|---|
| Combat | Swarm, Flanker, Brute | 3–5 | Flanker≤2, Brute≤1 |
| Ambush | Swarm, Flanker | 3–4 | Flanker≤1, Brute=0 |
| Safe | None | 0 | N/A |
| Elite | Elite + (Swarm/Flanker) | 3–4 | Flanker≤1, Brute=0 |
| MiniBoss | Boss only | 1 | Adds=0 |

# BIOME 1 — Room Order, Type Distribution & Deterministic Path (FULLY LOCKED)

Biome 1 Goal:
- Teach melee fundamentals
- Introduce flanking pressure
- Introduce brute as “lesson spike”
- Deliver clean elite + mini boss finish
- Keep win rate baseline ~70–75% before RL tuning

Total Rooms in Biome 1: **8**

Room Index Meaning:
- R0 = Start Room (non-combat, already locked)
- R1–R7 = Biome 1 gameplay rooms
- R8 = Mini Boss Room

So gameplay path:

R0 → R1 → R2 → R3 → R4 → R5 → R6 → R7 → R8

---

# 1️⃣ Fixed Room Count Per Type (HARD LOCK)

Biome 1 must contain:

- Combat Rooms: **4**
- Ambush Rooms: **2**
- Safe Room: **1**
- Elite Room: **1**
- Mini Boss Room: **1**

Total = 8 gameplay rooms

---

# 2️⃣ Hard Positional Constraints

## 2.1 Absolute Locks

- R1: Combat (never safe, never ambush, never brute)
- R8: Mini Boss (always)
- Exactly 1 Safe Room in R3–R6 range
- Elite Room must be after Safe Room
- Mini Boss always final

## 2.2 Early Protection Rule

Rooms R1–R2:
- No BRUTE allowed
- No Elite
- No Ambush in R1
- R2 may be Ambush

---

# 3️⃣ Deterministic Room Type Distribution

Biome 1 uses this deterministic slot model:

Room Slots:

| Room Index | Type Candidates |
|------------|-----------------|
| R1 | Combat |
| R2 | Combat or Ambush |
| R3 | Combat or Ambush |
| R4 | Safe or Combat |
| R5 | Combat or Elite |
| R6 | Combat or Elite |
| R7 | Elite or Combat |
| R8 | Mini Boss |

Hard rules:
- Exactly 2 Ambush rooms total (R2–R5 range only)
- Exactly 1 Safe room (R3–R6)
- Exactly 1 Elite room (R5–R7)

---

# 4️⃣ Room Order Resolution Algorithm (Seeded)

Given run_seed:

Step 1: Assign R1 = Combat

Step 2: Choose Safe Room
- Choose 1 index from {R3, R4, R5, R6}
- `safe_index = seeded_choice([3,4,5,6])`

Step 3: Choose Elite Room
- Must be > safe_index
- Choose from remaining in {5,6,7}
- `elite_index = seeded_choice(valid_indices_after_safe)`

Step 4: Choose 2 Ambush Rooms
- Choose from R2–R5
- Cannot overlap safe_index
- Cannot overlap elite_index
- R1 excluded
- `ambush_indices = seeded_sample(valid_indices, 2)`

Step 5: Remaining non-assigned rooms become Combat.

This guarantees:
- Early pacing
- Safe before Elite
- Deterministic but varied runs

---

# 5️⃣ Example Valid Distributions

Example A:
R1 Combat  
R2 Ambush  
R3 Combat  
R4 Safe  
R5 Combat  
R6 Elite  
R7 Combat  
R8 MiniBoss  

Example B:
R1 Combat  
R2 Combat  
R3 Ambush  
R4 Combat  
R5 Safe  
R6 Combat  
R7 Elite  
R8 MiniBoss  

Example C:
R1 Combat  
R2 Ambush  
R3 Combat  
R4 Safe  
R5 Ambush  
R6 Combat  
R7 Elite  
R8 MiniBoss  

All obey constraints.

---

# 6️⃣ Difficulty Curve Across Rooms (LOCKED)

Room Difficulty Rating (Baseline)

| Room | Difficulty Level |
|------|------------------|
| R1 | 1/10 |
| R2 | 2/10 |
| R3 | 3/10 |
| R4 | 2/10 (if Safe) or 4/10 |
| R5 | 4/10 |
| R6 | 5/10 |
| R7 | 6/10 (Elite) |
| R8 | 8/10 (Mini Boss) |

No sudden spike > +2 difficulty between consecutive rooms.

---

# 7️⃣ Biome 1 Target Win Rate (Before RL)

Target:
- **70–75% player win rate** (first-time player)

Mini Boss target clear rate:
- 60–65%

Elite room survival rate:
- 75–80%

---

# 8️⃣ RL Tuning Scope (Allowed Later)

RL may:
- Adjust pattern weights inside each room type
- Adjust hazard percentages within caps
- Adjust enemy HP ±10%
- Adjust spawn count within defined patterns
- Slightly reorder Ambush/Combat within allowed slots

RL may NOT:
- Move Safe after Elite
- Add extra Elite
- Add Ranged enemies
- Change MiniBoss position
- Increase total rooms
- Exceed enemy caps

---

# 9️⃣ Final Biome 1 Structure Summary

Biome 1 is now:

✔ Deterministic-bounded  
✔ Seed-reorderable  
✔ Early-player protected  
✔ No hidden spikes  
✔ RL-ready  
✔ Mathematically locked  

---

Biome 1 is now structurally complete.

If you want next, we can:

A) Lock hazard percentage curve per room index  
B) Lock enemy stat scaling curve per room index  
C) Lock Mini Boss exact attack timings & HP  
D) Move to Biome 2 philosophy  

Your call.

## Biome 1 — Room Plan Skeleton (HARD-LOCKED)

**Indexing (locked):**
- **Room 1 = Start Room (non-combat)**  
- **Biome 1 gameplay rooms = Rooms 2–8**
- **Room 8 = Mini Boss Room (end of Biome 1, fixed)**

Total rooms in Biome 1 segment including start: **8 rooms (1–8)**

---

### A) Room Type Counts (Rooms 2–8 only)

Biome 1 must contain exactly:

- **Combat Rooms:** 4  
- **Ambush Rooms:** 2  
- **Safe Room:** 1  
- **Elite Room:** 1  
- **Mini Boss Room:** 1 (fixed at Room 8)

Note: counts above include rooms 2–8 (7 rooms), where Elite + Safe + Ambush + Combat are arranged under constraints.

---

### B) Hard Order Rules (Deterministic Constraints)

These rules must always hold:

1. **Room 1 is always Start Room** (non-combat, tutorial/story/dummy).
2. **Room 8 is always Mini Boss Room** (fixed).
3. **Safe Room appears exactly once** in Rooms **3–6** (never Room 2, never Room 7).
4. **Elite Room appears exactly once** in Rooms **6–7** (and must be after the Safe Room).
5. **Room 2 cannot be Safe** (it is always Combat or Ambush).
6. **No more than 2 Ambush rooms** in Biome 1, and both must be in Rooms **2–5**.
7. **Early protection:** Rooms **2–3** cannot use BRUTE patterns (composition rule already locked).

---

### C) Flexible Slots (Combat vs Ambush) — Director/Seed Allowed

Rooms with flexible type (eligible for Combat/Ambush selection):

- **Room 2:** Combat or Ambush  
- **Room 3:** Combat or Ambush  
- **Room 4:** Combat or Ambush *(unless it is chosen as Safe)*  
- **Room 5:** Combat or Ambush  

Fixed-type rooms (not flexible):
- **Room 1:** Start
- **Room 8:** Mini Boss
- **Safe Room:** fixed once chosen (Room 3–6)
- **Elite Room:** fixed once chosen (Room 6–7)

---

### D) Deterministic Seed-Based Assignment (Room Type Schedule)

Given `run_seed`, assign room types using this deterministic algorithm:

**Step 1 — Lock fixed rooms**
- Room 1 = Start
- Room 8 = Mini Boss

**Step 2 — Choose Safe Room index**
- Choose 1 from `{3,4,5,6}`
- `safe_index = seeded_choice([3,4,5,6])`

**Step 3 — Choose Elite Room index**
- Elite must be after Safe
- Choose 1 from `{6,7}` but only those `> safe_index`
- `elite_index = seeded_choice(valid_elite_indices)`

**Step 4 — Choose Ambush Rooms**
- Ambush must be exactly 2 total
- Choose 2 unique indices from `{2,3,4,5}` excluding `safe_index`
- `ambush_indices = seeded_sample(valid_ambush_indices, 2)`

**Step 5 — Remaining unassigned rooms become Combat**
- Any room in `{2..7}` that is not Safe/Elite/Ambush becomes Combat

This produces deterministic but varied Biome 1 schedules while respecting all constraints.

---

### E) Allowed Permutations (Examples)

Example A:
- 1 Start
- 2 Combat
- 3 Ambush
- 4 Safe
- 5 Combat
- 6 Ambush
- 7 Elite
- 8 Mini Boss

Example B:
- 1 Start
- 2 Ambush
- 3 Combat
- 4 Ambush
- 5 Safe
- 6 Combat
- 7 Elite
- 8 Mini Boss

Example C:
- 1 Start
- 2 Combat
- 3 Ambush
- 4 Combat
- 5 Ambush
- 6 Safe
- 7 Elite
- 8 Mini Boss

---

### F) Director Policy (Optional but Compatible)

- Seed defines the schedule above.
- Director may tune:
  - enemy compositions within room-type caps
  - hazard percent within room-type caps
- Director may NOT:
  - move Safe after Elite
  - change Elite/Mini Boss positions
  - exceed ambush count
  - introduce ranged/heavy enemies in Biome 1 MVP

  ## Biome 1 — Room Clear & Door Unlock Rules (HARD-LOCKED)

This section defines exactly when a room is considered “cleared” and when doors unlock.
Applies to: Combat, Ambush, Elite rooms in Biome 1 (Safe + Start are always unlocked; Mini Boss unlocks after boss defeat).

---

### A) Definitions (Runtime Counters)

A room maintains these counters/sets:

- **Active Enemies**: enemies that currently exist in the room world state and are alive  
  - Includes: normal enemies, elite supports, summoned adds (if any), and elite itself  
  - Excludes: dead enemies (HP ≤ 0)

- **Pending Telegraph Spawns**: telegraph events that have started but have not spawned yet  
  - Each has: `telegraph_start_frame`, `spawn_frame`, `grace_end_frame`, `anchor`, `enemy_type`

- **Pending Reinforcement Waves**: reinforcement waves that are scheduled but not yet fully spawned  
  - Wave is considered “pending” if:
    - wave is not started yet OR
    - wave is currently telegraphing OR
    - wave has unspawned enemies remaining

- **Room Lock State**: `LOCKED` during combat, `UNLOCKING_DELAY` after clear check passes, `UNLOCKED` when doors open

---

### B) What Counts as “Enemy Remaining”?

✅ **Summoned enemies count** as active enemies until killed.  
✅ **Elite enemies count** until killed.  
✅ **Minions/adds count** (if boss/elite summons in later biomes).  
❌ Telegraph overlays do NOT count as enemies (they are only “pending spawns”).

---

### C) Room Clear Condition (HARD)

A room is “cleared” only when ALL of these are true at the same moment:

1) **Active Enemies = 0**  
2) **Pending Telegraph Spawns = 0**  
3) **Pending Reinforcement Waves = 0**  
4) **No enemy spawn is scheduled in the future** (i.e., no future wave timers)

Then the room enters an unlock delay state.

---

### D) Unlock Delay (HARD)

After the clear condition becomes true:

- Start **Unlock Delay Timer: 0.50 sec** (30 frames at 60 FPS)
- During this delay:
  - No new spawns may be scheduled
  - If any enemy appears (should not happen if rules above are correct), cancel unlock and return to LOCKED

When unlock delay completes:
- Doors become **UNLOCKED**
- Door visuals change to “open”
- Player may exit

---

### E) When Does a Room Become Locked?

Room locks at the moment the player crosses the entry threshold.

**Combat Room:**
- Locks instantly when player enters
- All enemies spawn immediately (no telegraph in Biome 1 combat by default)

**Ambush Room:**
- Locks instantly when player enters
- Enemies spawn via telegraph (pending telegraph spawns > 0)

**Elite Room:**
- Locks instantly when player enters
- Elite spawns immediately + supports spawn (may be immediate or telegraphed depending on design; both supported by this rule set)

---

### F) Special Room Types

#### Start Room (Room 1)
- Always unlocked (no combat lock)
- Doors always open (player can leave anytime)

#### Safe Room
- Always unlocked
- No enemies
- Doors always open

#### Mini Boss Room (Room 8)
- Locks on entry
- Clear condition is:
  - Boss HP ≤ 0
  - Active Enemies = 0 (adds count if present in future)
  - Pending Telegraph Spawns = 0
  - Pending Reinforcement Waves = 0
- Then 0.50 sec unlock delay, then doors open

---

### G) Edge Cases (HARD)

1) **Enemy dies during telegraph spawn**
- No effect; telegraph is independent.
- Clear cannot happen until pending telegraph spawns = 0.

2) **Telegraph retargeted due to invalid tile**
- Still counts as pending telegraph spawn until it spawns or is canceled.

3) **Waves scheduled but canceled**
- If a wave is canceled, it must be removed from pending waves list immediately.
- Clear condition uses the current list state only.

---

### H) Logging (Required)

For every room:
- `room_lock_frame`
- `room_unlock_start_frame`
- `room_unlock_frame`
- `clear_condition_first_true_frame`
- `active_enemies_peak`
- `telegraph_spawns_count_total`
- `reinforcement_waves_total`
- `unlock_delay_canceled_count` (should be 0)

This is important for debugging and RL training.

## Biome 1 — Difficulty Curve (Mathematically LOCKED Baseline Before RL)

Purpose:
- Provide a deterministic “difficulty slope” across Biome 1 rooms.
- Seed may reorder room types within the allowed skeleton, but the **intensity budget** must still follow this curve.
- RL later tunes parameters *within caps*, but must respect this baseline curve shape.

Indexing (locked):
- **Room 1 = Start Room**
- **Rooms 2–8 = Biome 1 gameplay**
- **Room 8 = Mini Boss (fixed)**

---

### A) Difficulty Scale + Room Intensity Budget

We define a discrete intensity scale `I` per room:
- `I ∈ {0,1,2,3,4,5}`
- 0 = none, 5 = peak

Each room type maps to a base intensity:

| Room Type | Base Intensity `I_base` |
|---|---:|
| Start | 0 |
| Safe | 0 |
| Combat (early) | 1 |
| Combat (mid) | 2 |
| Ambush | 2 |
| Combat (late) | 3 |
| Elite | 4 |
| Mini Boss | 5 |

---

### B) Locked Baseline Curve by Room Index (Target Intensities)

This is the required curve (baseline), regardless of seed permutation:

| Room Index | Target Intensity `I_target` | Notes |
|---:|---:|---|
| 1 | 0 | Start room, non-combat |
| 2 | 1 | First fight is easy (no brute) |
| 3 | 1–2 | Still easy; ambush allowed but must stay ≤2 |
| 4 | 0–2 | Safe may appear here (0), otherwise a mild fight |
| 5 | 2–3 | Mid difficulty begins |
| 6 | 2–4 | Safe or mid/late fight; Elite may appear (if after Safe) |
| 7 | 3–4 | Late fight or Elite (high) |
| 8 | 5 | Mini Boss peak |

**Hard slope rule (anti-spike):**
- Between consecutive rooms, intensity cannot increase by more than **+2**
  - `I_room(k) - I_room(k-1) ≤ 2`

---

### C) Room-Type Assignment Must Respect Intensity Bands

Given the room skeleton (Safe once in 3–6, Elite once in 6–7, Ambush twice in 2–5):

#### C1) Early rooms (Rooms 2–3)
- Must be **I ≤ 2**
- BRUTE patterns forbidden (already locked)
- Enemy count must stay in “early range”:
  - Combat patterns allowed: C1–C5 only (no brute)
  - Ambush patterns allowed: A1–A4

#### C2) Mid rooms (Rooms 5–6)
- Must be **I ∈ [2,3]** unless one is Elite (4) or Safe (0)
- If Safe occurs here, the *next* room may be Elite (4) because slope still ≤ +2 from 0 → 2/3/4

#### C3) Late room (Room 7)
- Must be **I ∈ [3,4]**
- If Elite is Room 7, it is **I = 4**

#### C4) Mini Boss (Room 8)
- Always **I = 5**

---

### D) Deterministic Difficulty Budget (Numbers You Can Implement)

For each intensity level, we lock a parameter budget range.
RL later can tune inside these bounds.

#### D1) Enemy Count Budget by Intensity
| Intensity | Allowed Total Enemies (Combat/Ambush) |
|---:|---|
| 1 | 3–4 |
| 2 | 3–5 |
| 3 | 4–5 |
| 4 (Elite room) | Elite + 2–3 supports |
| 5 (Mini Boss) | Boss only |

#### D2) Hazard Budget by Intensity (Biome 1 caps, room-type aware)
| Intensity | Lava % | Slow % |
|---:|---:|---:|
| 1 | 0–3% | 5–8% |
| 2 | 0–6% | 5–12% |
| 3 | 0–10% | 5–15% |
| 4 (Elite) | 0–8% | 5–15% |
| 5 (Mini Boss) | 0% in arena (hard) | 0–5% outside arena only |

Safe room:
- Lava = 0% (hard), Slow = 0–5% outside interaction zone only

---

### E) Baseline Progression Example (Canonical)

This is the canonical “easy-to-peak” example (one valid schedule):

| Room | Type | Intensity |
|---:|---|---:|
| 1 | Start | 0 |
| 2 | Combat | 1 |
| 3 | Combat | 1 |
| 4 | Safe | 0 |
| 5 | Combat | 2 |
| 6 | Ambush | 2 |
| 7 | Elite | 4 |
| 8 | Mini Boss | 5 |

Other schedules are allowed, but must satisfy the intensity bands and slope rule.

---

### F) RL Note (Baseline Before RL)

Before RL, we balance Biome 1 so average player clear rate ~60–70% (project target band can be adjusted later).
RL optimizes within caps:
- pattern weights
- hazard % inside ranges
- small stat scalers
But RL must preserve:
- Safe before Elite
- Anti-spike slope rule
- No ranged/heavy enemies in Biome 1 MVP

## Biome 1 — RL Logging System (HARD-LOCKED: Frequency, Format, Resolution, Storage)

Purpose:
- Enable offline RL / tuning later without changing gameplay logic.
- Ensure logs are deterministic, complete, and easy to parse.

This is the authoritative logging contract for Biome 1.

---

### A) Log Frequency (What gets logged and when)

We log at **three levels**:

#### A1) Run-level (1 record per run)
Logged:
- **At run start**
- **At run end** (victory/defeat/quit)

#### A2) Room-level (1 record per room)
Logged:
- **On room entry**
- **On room clear / exit**
- **On room death** (if player dies inside room)

#### A3) Encounter/Wave-level (0..N per room)
Logged:
- **Each spawn event** (including ambush telegraph spawn and reinforcement wave spawn)
- **Each wave start / wave end** (if waves exist)

Biome 1 MVP note:
- Combat rooms may have “single wave” only (still logged as wave 0).
- Ambush rooms always log telegraph spawns.

---

### B) Logging Resolution (Time + Frame)

Hard lock:
- Primary time resolution = **frame index** at **60 FPS**
- Each log event includes:
  - `frame`: integer frame count since run start
  - `t_sec`: float time seconds = `frame / 60.0`

Reason:
- Deterministic replay/debugging + matches telegraph timing spec.

---

### C) Output Format (File Format + Storage)

Hard lock:
- **JSON Lines** format (`.jsonl`)
  - One JSON object per line
  - Append-only (safe for crashes)

File naming:
```plaintext
logs/runs/run_<UTC_ISO>_<seed>.jsonl

Example:

logs/runs/run_2026-02-23T21-15-02Z_seed123456.jsonl

Why JSONL:

Easy to stream/write during play

Easy to parse in Python for RL

Doesn’t break if partial write occurs

Optional (post-processing):

Convert JSONL → CSV after run completes (offline script)

D) Director Snapshot Storage (Where “director state” goes)

Hard lock:

Director state is stored as a nested object inside each room-level and wave-level log record.

Additionally, store a lightweight director “heartbeat” snapshot:

once every 5 seconds (300 frames)

only while in combat rooms (not in safe/start)

This ensures RL can correlate outcomes with director decisions over time.

E) Log Event Types (Schema)

Every JSON object must include:

E1) Common header fields (present in ALL events)
{
  "schema_version": "biome1_v1",
  "run_id": "run_2026-02-23T21-15-02Z_seed123456",
  "seed": 123456,
  "biome_id": 1,
  "room_index": 2,
  "room_type": "combat",
  "event_type": "room_enter",
  "frame": 840,
  "t_sec": 14.0
}
F) Required Event Records
F1) run_start

Logged once at run start.
Fields:

player_base_stats

starting_loadout

initial_director_state

F2) run_end

Logged once at end.
Fields:

end_reason: "victory" | "defeat" | "quit"

final_room_index

total_time_sec

summary_metrics (see Section H)

F3) room_enter

Fields:

room_seed

regen_attempt_used

hazard_percent_lava

hazard_percent_slow

anchors_available_count

doors_locked: true/false

director_state (snapshot)

F4) room_exit

Fields:

clear_time_sec

clear_time_frames

damage_taken_in_room

heals_used_in_room

deaths_in_room (0/1)

enemies_spawned_total

telegraph_spawns_total

waves_total

unlock_frame

director_state (snapshot)

F5) room_death

Fields:

cause: "enemy" | "hazard" | "boss"

damage_source_id (enemy type or hazard type)

frame_of_death

room_progress_pct (0..1)

director_state (snapshot)

F6) wave_start

Fields:

wave_id (0..N)

spawn_plan (enemy list by type)

spawn_anchor_list

pending_telegraphs_count

director_state

F7) spawn_event

Logged per enemy spawn (including telegraph-based spawns).
Fields:

spawn_id

spawn_method: "immediate" | "telegraph_tile" | "telegraph_ring" | "telegraph_line"

telegraph_start_frame (if telegraph)

telegraph_spawn_frame (if telegraph)

spawn_anchor (row,col)

enemy_type

enemy_max_hp

enemy_params (speed, attack_cd, damage)

F8) wave_end

Fields:

wave_id

wave_duration_frames

wave_damage_to_player

enemies_killed_in_wave

director_state

F9) director_heartbeat (every 300 frames in combat)

Fields:

director_state

active_enemies

player_hp_pct

room_intensity_target

G) Director State Object (Locked Fields)

director_state must include:

{
  "intensity_target": 2,
  "difficulty_band": "mid",
  "allowed_enemy_types": ["swarm","flanker"],
  "pattern_id": "C2",
  "hazard_budget": {"lava_pct": 4, "slow_pct": 10},
  "spawn_caps": {"max_brute": 1, "max_flanker": 2, "total_cap": 5},
  "recent_outcomes": {"rooms_cleared": 3, "rooms_failed": 0}
}

This snapshot is the minimum RL needs to learn what the director was trying to do.

H) Run Summary Metrics (Required at run_end)

summary_metrics:

rooms_cleared

avg_clear_time_sec

total_damage_taken

total_healing_gained

telegraph_avoid_rate (fraction of telegraphed spawns where player not hit within 1 sec after spawn)

death_count

win (true/false)

I) Storage Path (Project)

Hard lock log location:

logs/runs/
logs/index.json   (optional)

Implementation note:

Ensure logs/runs/ exists at startup.

Append logs line-by-line during runtime to avoid losing data.

J) RL Training Export (Later, Offline)

Offline scripts can generate:

runs.csv (one line per run)

rooms.csv (one line per room)

spawns.csv (one line per spawn_event)

waves.csv (one line per wave_start/end)

But the in-game runtime format stays JSONL (hard lock).

## Biome 1 — AI Director Flexible Slot Rule (HARD-LOCKED)

Purpose:
- Keep Biome 1 deterministic and bounded
- Allow *limited* director choice (Combat vs Ambush) without breaking structure
- Seed defines which rooms are eligible; Director chooses within hard constraints

---

### A) Definitions

**Fixed Rooms (never change):**
- Start Room (Room 1)
- Mini Boss Room (Room 8)
- Safe Room (the chosen safe_index)
- Elite Room (the chosen elite_index)

**Flexible Slot:**
A room index that is eligible to be either:
- `Combat`
- `Ambush`

Flexible slots are **marked by the seed** and **resolved by the AI Director at runtime**.

---

### B) Hard Constraints (Biome 1)

#### B1) Maximum flexible slots allowed
- **Max Flexible Slots per Biome 1 run: 1** (HARD)

#### B2) What Director is allowed to change
Director may only choose:
- **Combat vs Ambush** for that one flexible room.

Director may NOT:
- Change room count totals
- Change room sizes
- Change doors, anchors, or safe zones

#### B3) Rooms that can never be overridden (HARD)
Director cannot override these rooms under any condition:
- Start (Room 1)
- Mini Boss (Room 8)
- Safe Room (safe_index)
- Elite Room (elite_index)

#### B4) Flexible slot eligibility window (HARD)
Flexible slot must be in:
- **Room 3, Room 4, or Room 5**
And must NOT equal:
- safe_index
- elite_index

So eligible candidates = `{3,4,5} - {safe_index, elite_index}`

#### B5) Ambush cap rule (HARD)
Biome 1 total ambush rooms must remain:
- **exactly 2** (as locked in composition skeleton)

So Director can only choose Ambush if it does NOT exceed:
- `ambush_count_target = 2`

---

### C) Seed Marking Rule (Deterministic)

At biome generation time (from run_seed):

1. Generate the room schedule using the deterministic skeleton:
   - safe_index chosen
   - elite_index chosen
   - ambush_indices chosen (2 rooms)
   - remaining become combat
   - Room 8 fixed as mini boss

2. Determine if a flexible slot exists:
   - Candidate set = `{3,4,5} - {safe_index, elite_index}`
   - If candidate set is empty → **no flexible slot this run**
   - Otherwise seed selects exactly 1:
     - `flex_index = seeded_choice(candidate_set)`
     - Mark `flex_index` with `is_flexible = true`

Hard lock:
- At most 1 `flex_index` per run.

---

### D) Runtime Director Choice Logic (Combat vs Ambush)

When the player is about to enter `flex_index` room:

Director evaluates recent metrics (last 1–2 rooms only):
- player HP%
- damage taken last room
- time-to-clear last room
- death count this run

Director chooses:
- `Combat` OR `Ambush`

Hard lock decision gate:
- If choosing Ambush would violate biome ambush target counts → force Combat.

---

### E) Logging (Required)

When a flexible slot is resolved, log:

Event: `director_flex_resolve`
Fields:
- `flex_index`
- `seed_marked_type` (what the skeleton initially assigned)
- `director_choice_type` (combat/ambush)
- `reason_codes` (e.g., LOW_HP, HIGH_CLEAR_SPEED, NEED_VARIETY)
- `ambush_count_before`, `ambush_count_after`

---

### F) Summary (Biome 1)

✅ Seed may mark **0 or 1** flexible slot per run  
✅ Director may only toggle **Combat ↔ Ambush**  
❌ Director cannot override **Start, Safe, Elite, Mini Boss**  
❌ Director cannot change total room counts or reorder rooms  
✅ Deterministic + bounded + RL-ready  

## Biome 1 — Visual Identity Lock (Palette + Tints + Lighting + Particles)

Goal:
Give Biome 1 a consistent “Hades-like dungeon” mood without requiring dynamic lighting.
This is a hard-locked art direction contract for all Biome 1 rooms.

Resolution context:
- Target screen: 1920×1080
- Tile size: 32×32
- Sprites: silhouette-forward, high-contrast readability

---

### A) Core Palette (Biome 1)

Biome 1 theme: **“Ash Dungeon / Warm Torchlight”**

Hard-locked palette (HEX):
- **Base Shadow (deep):** `#0B0E14`
- **Dungeon Floor (base):** `#2A2C32`
- **Dungeon Floor (highlight):** `#3A3D45`
- **Dungeon Walls (base):** `#3B3330`
- **Dungeon Walls (edge highlight):** `#5A4A42`
- **Torch Warm Light:** `#E0A24A`
- **Accent Ember Red:** `#B93B2D`
- **UI Gold Accent:** `#D6B35A`

Hazards (locked):
- **Lava core:** `#FF5A1F`
- **Lava mid:** `#D63B1E`
- **Lava dark:** `#6B1A12`
- **Slow terrain tint:** `#3E4A3B` (mud/lichen feel)

Telegraphs (locked, consistent with earlier):
- Standard spawn telegraph: **Red** `#FF2B2B`
- Elite telegraph: **Gold** `#FFD24A`
- Boss telegraph: **Purple** `#B05CFF`

---

### B) Floor Tint + Variation Rules

Biome 1 floor must be:
- Neutral dark gray base with subtle warm highlights
- No high saturation (keeps silhouettes readable)

Variation rule (optional but recommended):
- Use **3–5 floor variants** (same palette family)
- Scatter at **10–20%** placement probability
- Never place variant tiles inside reserved safe-zones if they reduce readability

---

### C) Wall Tint + Edge Rules

Walls must be:
- Slightly warmer than floor (brown-gray)
- Stronger edge highlight on top/inner edges for readability

Hard rules:
- Wall outline contrast must be visible against floor at a glance
- Corners must read cleanly at 32×32 scale

---

### D) Lava Visual Tone (Biome 1)

Lava should read as:
- **bright molten orange core**
- **dark crust edges**
- minimal animation (3–4 frames loop)

Hard rules:
- Lava must visually “pop” more than floor (danger clarity)
- Lava animation must not shift tile edges (seamless tiling)

---

### E) Lighting / Color Grading (No Dynamic Lighting)

Biome 1 uses a static global color grade overlay:

**Global grade overlay:**
- Warm vignette (subtle)
- Opacity: **12–18%**
- Tint: `#E0A24A` (torch warmth)
- Vignette strength: mild (do not hide corners)

Hard rule:
- No dynamic lights required in MVP.
- Grade overlay is applied uniformly per room.

File (recommended):
```plaintext
assets/lighting/biome1_grade_overlay_1920x1080.png
F) Ambient Particles (Yes/No + Locked)

Ambient particles: YES (locked)

Biome 1 particle style:

small ember dust / ash motes

slow upward drift

low density

Hard-locked settings:

Particle count: 18–28 on screen

Speed: 8–14 px/sec upward drift

Alpha: 20–40%

Size: 2–4 px

Spawn region: random across screen (not tied to player)

Layer: behind entities, above floor

File (optional sprites):

assets/effects/particles/ember_01_4x4.png
assets/effects/particles/ember_02_4x4.png
assets/effects/particles/ash_01_4x4.png

If you don’t want particle sprites:

render as simple circles with alpha (still allowed)

G) Biome 1 Room Mood Summary

Biome 1 should feel:

dark and claustrophobic but readable

warm torch tint

clear hazards (lava bright)

high-contrast silhouettes for player/enemies

subtle ash/embers for atmosphere

This locks Biome 1 visual personality for implementation and asset creation.
