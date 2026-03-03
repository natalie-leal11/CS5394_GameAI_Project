# Adaptive AI Dungeon — Requirements Analysis (Rebuilt)

**Group Members:** Natalie Cristina Leal Blanco, Maham Asif  
**Last rebuilt:** 2026-02-23 (UTC)

---

## Table of Contents
1. Scope and Goals
2. Game Launch & UI Flow
3. Controls & Input Mapping
4. Settings & Save System
5. Run Structure (Roguelike Rules)
6. Rendering, Camera, and Resolution
7. Asset Directory Contract (Authoritative)
8. Room 0 — Start Room (Story + Dummy)
9. Biome 1 — Structure, Difficulty Curve, Visual Identity
10. Biome 1 — Rooms (Templates + Safe Zones + Anchors)
11. Biome 1 — Hazards (Placement + Damage + Slow)
12. Biome 1 — Spawning System (Telegraphs + Portal FX)
13. Biome 1 — Enemy Composition (Hard Caps Per Room Type)
14. Combat System (Player + Enemy Ranges + Timing)
15. Room Clear Rule (Hard-Locked)
16. AI Director (Flexible Slot Rule + Bounds)
17. Logging for RL (JSONL Contract)
18. Optional LLM Features (Story Generation)
19. Determinism & Seeds (No seed display)
20. Open Items / Asset TODO Checklist
---

## 1) Scope and Goals

- Deterministic roguelike dungeon crawler with seeded procedural content.
- MVP scope: full UI start flow, Room 0, and complete Biome 1.
- RL is offline/analysis-first: logs gameplay, later tunes bounded parameters.
- Optional LLM: story flavor text with deterministic fallback.

---

## 2) Game Launch & UI Flow

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
│ ├── controls_bg.pngR
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

# 💀 PLAYER DEATH SEQUENCE CONTRACT (MANDATORY)

Player death must be cinematic and time-controlled.
It must NOT instantly reset the game.

---

## 1️⃣ Death Animation Duration

- Player death animation duration: 3–4 seconds total.
- Animation must play fully before any scene transition.
- Animation speed must be slowed (dramatic effect).

Player cannot move or attack during this period.

---

## 2️⃣ Enemy Behavior During Player Death

When player HP reaches 0:

- Enemies must immediately stop attacking.
- Enemies may step backward slightly (retreat behavior).
- No further damage is applied.
- Combat logic pauses.

This creates visual space for the death animation.

---

## 3️⃣ Death Freeze & Delay

After death animation completes:

- Freeze screen for 1–2 seconds.
- Optional: fade screen slightly darker.

---

## 4️⃣ Game Over Message Timing

- Display “Game Over” overlay.
- Overlay must remain visible for 3–5 seconds.
- Player input disabled during this period.

---

## 5️⃣ Scene Transition

After Game Over delay:

- Transition to Main Menu (StartScene).
- New seed generated for next run.

Total time from HP=0 → Main Menu:
Minimum 6 seconds.
Maximum 10 seconds.

Instant reset is NOT allowed.


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

---

## 7) Asset Directory Contract (Authoritative)

### 7.1 Assets present in `assets.zip`

- `assets/backgrounds/controls_bg.png`
- `assets/backgrounds/main_menu_bg.png`
- `assets/backgrounds/room0_bg.png`
- `assets/backgrounds/settings_bg.png`
- `assets/backgrounds/story_intro_bg.png`
- `assets/effects/particles/ash_01_4x4.png`
- `assets/effects/particles/ember_01_4x4.png`
- `assets/effects/particles/ember_02_4x4.png`
- `assets/effects/telegraphs/telegraph_aoe_ring_256x256.png`
- `assets/effects/telegraphs/telegraph_aoe_ring_anim_256x256.png`
- `assets/effects/telegraphs/telegraph_boss_purple_256x256.png`
- `assets/effects/telegraphs/telegraph_boss_purple_anim_256x256.png`
- `assets/effects/telegraphs/telegraph_boss_purple_line_256x64.png`
- `assets/effects/telegraphs/telegraph_boss_purple_line_anim_256x64.png`
- `assets/effects/telegraphs/telegraph_elite_gold_32x32.png`
- `assets/effects/telegraphs/telegraph_elite_gold_anim_32x32.png`
- `assets/effects/telegraphs/telegraph_elite_gold_aoe_256x256.png`
- `assets/effects/telegraphs/telegraph_elite_gold_aoe_anim_256x256.png`
- `assets/effects/telegraphs/telegraph_ground_crack_256x64.png`
- `assets/effects/telegraphs/telegraph_ground_crack_anim_256x64.png`
- `assets/effects/telegraphs/telegraph_tile_32x32.png`
- `assets/effects/telegraphs/telegraph_tile_anim_32x32.png`
- `assets/effects/vfx/parry_flash/frame_01.png`
- `assets/effects/vfx/parry_flash/frame_02.png`
- `assets/effects/vfx/parry_flash/frame_03.png`
- `assets/entities/enemies/brute/death/frame_01.png`
- `assets/entities/enemies/brute/death/frame_02.png`
- `assets/entities/enemies/brute/death/frame_03.png`
- `assets/entities/enemies/brute/death/frame_04.png`
- `assets/entities/enemies/brute/death/frame_05.png`
- `assets/entities/enemies/brute/death/frame_06.png`
- `assets/entities/enemies/brute/hit/frame_01.png`
- `assets/entities/enemies/brute/hit/frame_02.png`
- `assets/entities/enemies/brute/idle/frame_01.png`
- `assets/entities/enemies/brute/idle/frame_02.png`
- `assets/entities/enemies/brute/idle/frame_03.png`
- `assets/entities/enemies/brute/idle/frame_04.png`
- `assets/entities/enemies/brute/recovery/frame_01.png`
- `assets/entities/enemies/brute/recovery/frame_02.png`
- `assets/entities/enemies/brute/recovery/frame_03.png`
- `assets/entities/enemies/brute/slam/frame_01.png`
- `assets/entities/enemies/brute/slam/frame_02.png`
- `assets/entities/enemies/brute/slam/frame_03.png`
- `assets/entities/enemies/brute/slam/frame_04.png`
- `assets/entities/enemies/brute/walk/frame_01.png`
- `assets/entities/enemies/brute/walk/frame_02.png`
- `assets/entities/enemies/brute/walk/frame_03.png`
- `assets/entities/enemies/brute/walk/frame_04.png`
- `assets/entities/enemies/brute/walk/frame_05.png`
- `assets/entities/enemies/brute/walk/frame_06.png`
- `assets/entities/enemies/brute/windup/frame_01.png`
- `assets/entities/enemies/brute/windup/frame_02.png`
- `assets/entities/enemies/brute/windup/frame_03.png`
- `assets/entities/enemies/brute/windup/frame_04.png`
- `assets/entities/enemies/elite_guardian/death/frame_03.png`
- `assets/entities/enemies/elite_guardian/death/frame_04.png`
- `assets/entities/enemies/elite_guardian/death/frame_05.png`
- `assets/entities/enemies/elite_guardian/death/frame_06.png`
- `assets/entities/enemies/elite_guardian/death/frame_07.png`
- `assets/entities/enemies/elite_guardian/death/frame_08.png`
- `assets/entities/enemies/elite_guardian/hit/frame_01.png`
- `assets/entities/enemies/elite_guardian/hit/frame_02.png`
- `assets/entities/enemies/elite_guardian/idle/frame_01.png`
- `assets/entities/enemies/elite_guardian/idle/frame_02.png`
- `assets/entities/enemies/elite_guardian/idle/frame_03.png`
- `assets/entities/enemies/elite_guardian/idle/frame_04.png`
- `assets/entities/enemies/elite_guardian/recovery/frame_01.png`
- `assets/entities/enemies/elite_guardian/recovery/frame_02.png`
- `assets/entities/enemies/elite_guardian/recovery/frame_03.png`
- `assets/entities/enemies/elite_guardian/slam/frame_01.png`
- `assets/entities/enemies/elite_guardian/slam/frame_02.png`
- `assets/entities/enemies/elite_guardian/slam/frame_03.png`
- `assets/entities/enemies/elite_guardian/slam/frame_04.png`
- `assets/entities/enemies/elite_guardian/walk/frame_01.png`
- `assets/entities/enemies/elite_guardian/walk/frame_02.png`
- `assets/entities/enemies/elite_guardian/walk/frame_03.png`
- `assets/entities/enemies/elite_guardian/walk/frame_04.png`
- `assets/entities/enemies/elite_guardian/walk/frame_05.png`
- `assets/entities/enemies/elite_guardian/walk/frame_06.png`
- `assets/entities/enemies/elite_guardian/windup/frame_01.png`
- `assets/entities/enemies/elite_guardian/windup/frame_02.png`
- `assets/entities/enemies/elite_guardian/windup/frame_03.png`
- `assets/entities/enemies/elite_guardian/windup/frame_04.png`
- `assets/entities/enemies/flanker/attack/frame_01.png`
- `assets/entities/enemies/flanker/attack/frame_02.png`
- `assets/entities/enemies/flanker/attack/frame_03.png`
- `assets/entities/enemies/flanker/attack/frame_04.png`
- `assets/entities/enemies/flanker/dash/frame_01.png`
- `assets/entities/enemies/flanker/dash/frame_02.png`
- `assets/entities/enemies/flanker/dash/frame_03.png`
- `assets/entities/enemies/flanker/dash/frame_04.png`
- `assets/entities/enemies/flanker/death/frame_01.png`
- `assets/entities/enemies/flanker/death/frame_02.png`
- `assets/entities/enemies/flanker/death/frame_03.png`
- `assets/entities/enemies/flanker/death/frame_04.png`
- `assets/entities/enemies/flanker/death/frame_05.png`
- `assets/entities/enemies/flanker/death/frame_06.png`
- `assets/entities/enemies/flanker/hit/frame_01.png`
- `assets/entities/enemies/flanker/hit/frame_02.png`
- `assets/entities/enemies/flanker/idle/frame_01.png`
- `assets/entities/enemies/flanker/idle/frame_02.png`
- `assets/entities/enemies/flanker/idle/frame_03.png`
- `assets/entities/enemies/flanker/idle/frame_04.png`
- `assets/entities/enemies/flanker/walk/frame_01.png`
- `assets/entities/enemies/flanker/walk/frame_02.png`
- `assets/entities/enemies/flanker/walk/frame_03.png`
- `assets/entities/enemies/flanker/walk/frame_04.png`
- `assets/entities/enemies/flanker/walk/frame_05.png`
- `assets/entities/enemies/flanker/walk/frame_06.png`
- `assets/entities/enemies/mini_boss/attack_01/frame_01.png`
- `assets/entities/enemies/mini_boss/attack_01/frame_02.png`
- `assets/entities/enemies/mini_boss/attack_01/frame_03.png`
- `assets/entities/enemies/mini_boss/attack_01/frame_04.png`
- `assets/entities/enemies/mini_boss/attack_02/frame_01.png`
- `assets/entities/enemies/mini_boss/attack_02/frame_02.png`
- `assets/entities/enemies/mini_boss/attack_02/frame_03.png`
- `assets/entities/enemies/mini_boss/attack_02/frame_04.png`
- `assets/entities/enemies/mini_boss/dash/frame_01.png`
- `assets/entities/enemies/mini_boss/dash/frame_02.png`
- `assets/entities/enemies/mini_boss/dash/frame_03.png`
- `assets/entities/enemies/mini_boss/dash/frame_04.png`
- `assets/entities/enemies/mini_boss/death/frame_01.png`
- `assets/entities/enemies/mini_boss/death/frame_02.png`
- `assets/entities/enemies/mini_boss/death/frame_03.png`
- `assets/entities/enemies/mini_boss/death/frame_04.png`
- `assets/entities/enemies/mini_boss/death/frame_05.png`
- `assets/entities/enemies/mini_boss/death/frame_06.png`
- `assets/entities/enemies/mini_boss/death/frame_07.png`
- `assets/entities/enemies/mini_boss/death/frame_08.png`
- `assets/entities/enemies/mini_boss/death/frame_09.png`
- `assets/entities/enemies/mini_boss/death/frame_10.png`
- `assets/entities/enemies/mini_boss/hit/frame_01.png`
- `assets/entities/enemies/mini_boss/hit/frame_02.png`
- `assets/entities/enemies/mini_boss/idle/frame_01.png`
- `assets/entities/enemies/mini_boss/idle/frame_02.png`
- `assets/entities/enemies/mini_boss/idle/frame_03.png`
- `assets/entities/enemies/mini_boss/idle/frame_04.png`
- `assets/entities/enemies/mini_boss/move/frame_01.png`
- `assets/entities/enemies/mini_boss/move/frame_02.png`
- `assets/entities/enemies/mini_boss/move/frame_03.png`
- `assets/entities/enemies/mini_boss/move/frame_04.png`
- `assets/entities/enemies/mini_boss/move/frame_05.png`
- `assets/entities/enemies/mini_boss/move/frame_06.png`
- `assets/entities/enemies/mini_boss/phase_change/frame_01.png`
- `assets/entities/enemies/mini_boss/phase_change/frame_02.png`
- `assets/entities/enemies/mini_boss/phase_change/frame_03.png`
- `assets/entities/enemies/mini_boss/phase_change/frame_04.png`
- `assets/entities/enemies/mini_boss/phase_change/frame_05.png`
- `assets/entities/enemies/mini_boss/phase_change/frame_06.png`
- `assets/entities/enemies/mini_boss/windup/frame_01.png`
- `assets/entities/enemies/mini_boss/windup/frame_02.png`
- `assets/entities/enemies/mini_boss/windup/frame_03.png`
- `assets/entities/enemies/mini_boss/windup/frame_04.png`
- `assets/entities/enemies/swarm/attack/frame_01.png`
- `assets/entities/enemies/swarm/attack/frame_02.png`
- `assets/entities/enemies/swarm/attack/frame_03.png`
- `assets/entities/enemies/swarm/attack/frame_04.png`
- `assets/entities/enemies/swarm/death/frame_01.png`
- `assets/entities/enemies/swarm/death/frame_02.png`
- `assets/entities/enemies/swarm/death/frame_03.png`
- `assets/entities/enemies/swarm/death/frame_04.png`
- `assets/entities/enemies/swarm/death/frame_05.png`
- `assets/entities/enemies/swarm/death/frame_06.png`
- `assets/entities/enemies/swarm/hit/frame_01.png`
- `assets/entities/enemies/swarm/hit/frame_02.png`
- `assets/entities/enemies/swarm/idle/frame_01.png`
- `assets/entities/enemies/swarm/idle/frame_02.png`
- `assets/entities/enemies/swarm/idle/frame_03.png`
- `assets/entities/enemies/swarm/idle/frame_04.png`
- `assets/entities/enemies/swarm/walk/frame_01.png`
- `assets/entities/enemies/swarm/walk/frame_02.png`
- `assets/entities/enemies/swarm/walk/frame_03.png`
- `assets/entities/enemies/swarm/walk/frame_04.png`
- `assets/entities/enemies/swarm/walk/frame_05.png`
- `assets/entities/enemies/swarm/walk/frame_06.png`
- `assets/entities/player/attack_long/frame_01.png`
- `assets/entities/player/attack_long/frame_02.png`
- `assets/entities/player/attack_long/frame_03.png`
- `assets/entities/player/attack_long/frame_04.png`
- `assets/entities/player/attack_long/frame_05.png`
- `assets/entities/player/attack_short/frame_01.png`
- `assets/entities/player/attack_short/frame_02.png`
- `assets/entities/player/attack_short/frame_03.png`
- `assets/entities/player/attack_short/frame_04.png`
- `assets/entities/player/block/frame_01.png`
- `assets/entities/player/block/frame_02.png`
- `assets/entities/player/block/frame_03.png`
- `assets/entities/player/dash/frame_01.png`
- `assets/entities/player/dash/frame_02.png`
- `assets/entities/player/dash/frame_03.png`
- `assets/entities/player/dash/frame_04.png`
- `assets/entities/player/death/frame_01.png`
- `assets/entities/player/death/frame_02.png`
- `assets/entities/player/death/frame_03.png`
- `assets/entities/player/death/frame_04.png`
- `assets/entities/player/death/frame_05.png`
- `assets/entities/player/death/frame_06.png`
- `assets/entities/player/hit/frame_01.png`
- `assets/entities/player/hit/frame_02.png`
- `assets/entities/player/idle/frame_01.png`
- `assets/entities/player/idle/frame_02.png`
- `assets/entities/player/idle/frame_03.png`
- `assets/entities/player/idle/frame_04.png`
- `assets/entities/player/walk/frame_01.png`
- `assets/entities/player/walk/frame_02.png`
- `assets/entities/player/walk/frame_03.png`
- `assets/entities/player/walk/frame_04.png`
- `assets/entities/player/walk/frame_05.png`
- `assets/entities/player/walk/frame_06.png`
- `assets/fonts/PixelifySans-Variable.ttf`
- `assets/props/altar_book.png`
- `assets/props/door_open.png`
- `assets/props/training_dummy.png`
- `assets/tiles/corridor/corridor_floor_32x32.png`
-`assets/tiles/corridor/corridor_wall_top_32x32.png`
-`assets/tiles/corridor/corridor_wall_bottom_32x32.png`
-`assets/tiles/corridor/corridor_wall_left_32x32.png`
-`assets/tiles/corridor/corridor_wall_right_32x32.png`
-`assets/tiles/corridor/corridor_corner_tl_32x32.png`
-`assets/tiles/corridor/corridor_corner_tr_32x32.png`
-`assets/tiles/corridor/corridor_corner_bl_32x32.png`
-`assets/tiles/corridor/corridor_corner_br_32x32.png`
-`assets/tiles/corridor/corridor_corners_sheet.png`
-`assets/tiles/corridor/torch_32x32.png`
-`assets/tiles/corridor/corridor_shadow_overlay.png`
- `assets/tiles/doors/door_closed_32x32.png`
- `assets/tiles/doors/door_locked_32x32.png`
- `assets/tiles/doors/door_open_32x32.png`
- `assets/tiles/doors/door_safe_32x32.png`
- `assets/tiles/floor/floor_tile.png`
- `assets/tiles/hazards/lava_tile_32x32.png`
- `assets/tiles/hazards/lava_tile_anim_32x32.png`
- `assets/tiles/hazards/slow_tile_32x32.png`
- `assets/tiles/powerups/boost_attack_32x32.png`
- `assets/tiles/powerups/boost_defence_32x32.png`
- `assets/tiles/powerups/boost_speed_32x32.png`
- `assets/tiles/powerups/heal_health_32x32.png`
- `assets/tiles/walls/wall_bottom_32x32.png`
- `assets/tiles/walls/wall_corner_bl_32x32.png`
- `assets/tiles/walls/wall_corner_tl_32x32.png`
- `assets/tiles/walls/wall_corner_tr_32x32.png`
- `assets/tiles/walls/wall_left_32x32.png`
- `assets/tiles/walls/wall_right_32x32.png`
- `assets/ui/buttons/btn_apply.png`
- `assets/ui/buttons/btn_back.png`
- `assets/ui/buttons/btn_controls.png`
- `assets/ui/buttons/btn_play.png`
- `assets/ui/buttons/btn_play_hover.png`
- `assets/ui/buttons/btn_play_pressed.png`
- `assets/ui/buttons/btn_quit.png`
- `assets/ui/buttons/btn_settings.png`
- `assets/tiles/doors/indicators/door_exit_arrow_32x32.png`
- `assets/tiles/doors/indicators/door_locked_icon_32x32.png`
- `assets/tiles/doors/indicators/door_unlocked_icon_32x32.png`
- `assets/tiles/doors/overlays/door_glow_overlay_32x32.png`
- `assets/tiles/doors/overlays/door_lock_overlay_32x32.png`
- `assets/tiles/doors/prompts/door_interact_prompt_bg.png`
- `assets/tiles/doors/prompts/door_interact_prompt_key_e.png`
- `assets/ui/hud/boss_hp_chunk_divider_8x60.png`
- `assets/ui/hud/boss_intro_splash_panel_900x300.png`
- `assets/ui/hud/boss_lava_cracks_overlay_780x36.png`
- `assets/ui/hud/boss_nameplate_panel_600x80.png`
- `assets/ui/hud/boss_phase_marker_20x40.png`
- `assets/ui/hud/final_boss_burning_overlay_800x60.png`
- `assets/ui/hud/final_boss_health_fill_780x36.png`
- `assets/ui/hud/final_boss_health_frame_800x60.png`
- `assets/ui/hud/health_bar_damage_flash_clean_192x32.png`
- `assets/ui/hud/health_bar_fill_190x26.png`
- `assets/ui/hud/health_bar_frame_192x32.png`
- `assets/ui/hud/health_bar_lowhp_glow_clean_192x32.png`
- `assets/ui/hud/icon_attack_24x24.png`
- `assets/ui/hud/icon_defence_24x24.png`
- `assets/ui/hud/icon_health_24x24.png`
- `assets/ui/hud/icon_speed_24x24.png`
- `assets/ui/hud/mini_boss_health_fill_396x24.png`
- `assets/ui/hud/mini_boss_health_frame_400x40.png`
- `assets/ui/hud/phase_change_flash_fullscreen_1920x1080.png`
- `assets/ui/hud/stat_panel_bg_84x32.png`
- `assets/ui/hud/xp_bar_fill_178x12.png`
- `assets/ui/hud/xp_bar_frame_180x16.png`
- `assets/ui/panels/story_panel.png`
- ... (8 more files in assets.zip)


### 7.2 Assets referenced in this Requirements Analysis

- `assets/backgrounds/controls_bg.png`
- `assets/backgrounds/main_menu_bg.png`
- `assets/backgrounds/room0_bg.png`
- `assets/backgrounds/settings_bg.png`
- `assets/backgrounds/story_intro_bg.png`
- `assets/effects/telegraphs/telegraph_aoe_ring_anim_256x256.png`
- `assets/effects/telegraphs/telegraph_boss_purple_anim_256x256.png`
- `assets/effects/telegraphs/telegraph_elite_gold_anim_32x32.png`
- `assets/effects/telegraphs/telegraph_ground_crack_anim_256x64.png`
- `assets/effects/telegraphs/telegraph_tile_32x32.png`
- `assets/effects/telegraphs/telegraph_tile_anim_32x32.png`
- `assets/fonts/PixelifySans-Variable.ttf`
- `assets/props/altar_book.png`
- `assets/props/door_open.png`
- `assets/props/training_dummy.png`
- `assets/tiles/doors/door_closed_32x32.png`
- `assets/tiles/doors/door_locked_32x32.png`
- `assets/tiles/doors/door_open_32x32.png`
- `assets/tiles/doors/door_safe_32x32.png`
- `assets/ui/buttons/btn_apply.png`
- `assets/ui/buttons/btn_back.png`
- `assets/ui/buttons/btn_controls.png`
- `assets/ui/buttons/btn_play.png`
- `assets/ui/buttons/btn_quit.png`
- `assets/ui/buttons/btn_settings.png`
- `assets/ui/panels/story_panel.png`
- `assets/ui/prompts/interact_prompt_bg.png`
- `assets/ui/sliders/slider_knob.png`
- `assets/ui/sliders/slider_track.png`


---

## 8) Room 0 — Start Room (Story + Dummy)

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

---

## 9) Biome 1 — Structure, Difficulty Curve, Visual Identity

### 9.1 Difficulty Curve (Mathematically Locked Baseline)

Biome 1 must follow a bounded difficulty slope. Seed may reorder within allowed skeleton, but the intensity budget must follow this curve.

**Intensity scale:** `I ∈ {0,1,2,3,4,5}`

| Room | Target Intensity |
|---:|---:|
| 1 (Start) | 0 |
| 2 | 1 |
| 3 | 1–2 |
| 4 | 0–2 |
| 5 | 2–3 |
| 6 | 2–4 |
| 7 | 3–4 |
| 8 (Mini Boss) | 5 |

**Anti-spike rule (Hard):** Consecutive rooms cannot increase by more than **+2** intensity.



### 9.2 Visual Identity Lock (Biome 1)

Theme: **Ash Dungeon / Warm Torchlight** (Hades-like contrast, readable silhouettes)

**Palette (HEX):**
- Base Shadow: `#0B0E14`
- Floor Base: `#2A2C32`
- Floor Highlight: `#3A3D45`
- Wall Base: `#3B3330`
- Wall Edge Highlight: `#5A4A42`
- Torch Warm Light: `#E0A24A`
- Accent Ember Red: `#B93B2D`
- UI Gold Accent: `#D6B35A`

**Hazards:**
- Lava core: `#FF5A1F`
- Lava mid: `#D63B1E`
- Lava dark: `#6B1A12`
- Slow terrain tint: `#3E4A3B`

**Ambient particles:** YES (ember/ash)
- Count: 18–28
- Size: 2–4 px
- Alpha: 20–40%
- Speed: 8–14 px/sec upward drift


---

## 10–14) Biome 1 Gameplay Specs (Rooms, Hazards, Spawns, Enemies, Combat)

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

# ⚔ ENEMY–PLAYER SEPARATION & ATTACK RANGE CONTRACT (MANDATORY)

Enemies must NOT visually overlap with the player during combat.

## 1️⃣ Minimum Separation Distance

Each enemy must maintain a minimum distance from the player:

- Swarm: stop at 40 px
- Flanker: stop at 50 px
- Brute: stop at 60 px
- Mini Boss: stop at 80 px

Enemies must switch from "move" to "attack/windup" when inside their attack radius.

Enemies must NOT continue moving once inside attack range.

---

## 2️⃣ Collision Resolution

If enemy and player rectangles overlap:

- Apply deterministic push-back resolution
- Resolve overlap by moving enemy outward along collision normal
- No random displacement allowed

---

## 3️⃣ Attack Trigger Rule

Enemy attack may only trigger if:

distance_to_player ≤ attack_radius  
AND attack_cooldown_ready == True

Enemy cannot deal damage by standing inside the player.

---

## 4️⃣ Contact Damage Rule

If contact damage type enemy:

- Damage applies at fixed interval (0.5 sec)
- Damage interval must be frame-based
- Overlap does NOT increase damage frequency

---

## 5️⃣ Rendering Order

If overlap visually occurs momentarily:
- Player sprite must render above enemy sprite
- Mini Boss renders above all standard enemies

# 🛡 ENEMY–ENEMY SEPARATION CONTRACT (MANDATORY)

Enemies must NOT visually or physically overlap with each other at any time.

---

## 1️⃣ Minimum Separation Distance

Each enemy must maintain a minimum spacing from other enemies:

- Swarm ↔ Swarm: 30 px
- Swarm ↔ Flanker: 35 px
- Swarm ↔ Brute: 40 px
- Flanker ↔ Flanker: 40 px
- Flanker ↔ Brute: 45 px
- Brute ↔ Brute: 50 px
- Mini Boss ↔ Any: 80 px

If distance_between_enemies < required_min_distance:
- Apply deterministic separation push force.

---

## 2️⃣ Collision Resolution Rule

When enemy rectangles overlap:

- Resolve using push-back vector along collision normal.
- Both enemies must be adjusted (not only one).
- Resolution must be deterministic.
- No random displacement allowed.

Enemies must NEVER stack visually.

---

## 3️⃣ Movement Priority Rule

Mini Boss has highest priority:
- Smaller enemies must move away if collision occurs.

Brute has higher priority than Flanker.
Flanker has higher priority than Swarm.

Lower-priority enemy yields position.

---

## 4️⃣ Death State Behavior

When player dies:

- Enemies must stop forward movement.
- Separation logic must still remain active.
- Enemies must not cluster on player body.

---

## 5️⃣ Rendering Rule

Even if two enemies are close:
- Their center points must never be identical.
- Visible sprite stacking is not allowed.

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

<!-- NOTE: Biome section trimmed to first 3000 lines for rebuild output size. Keep adding remaining sections here as you iterate. -->


---

## 15) Biome 1 — Room Clear Rule (Hard-Locked)

A room is cleared when:
- Active enemies = 0
- Pending telegraph spawns = 0
- Pending reinforcement waves = 0
- No future spawn timers remain

Then unlock doors after:
- **0.50 sec delay** (30 frames at 60 FPS)

Notes:
- Summoned enemies count as active enemies until killed.
- Telegraph overlays do **not** count as enemies (they count as pending spawns).
- If a new enemy appears during unlock delay, cancel unlock and re-lock.


---

## 16) AI Director — Flexible Slot Rule (Hard-Locked for Biome 1)

- Seed may mark **0 or 1** flexible slot per Biome 1 run.
- **Max flexible slots per run: 1**
- Eligible indices: **Room 3, 4, or 5**
- Director can choose: **Combat vs Ambush** only for that slot.

Director cannot override:
- Start (Room 1)
- Safe room (safe_index)
- Elite room (elite_index)
- Mini Boss (Room 8)

Log event: `director_flex_resolve` with (flex_index, chosen_type, reason_codes).


---

## 17) Logging for RL (Hard-Locked JSONL Contract)

**Format:** JSON Lines (.jsonl), append-only  
**Path:** `logs/runs/run_<UTC_ISO>_<seed>.jsonl`

**Resolution:** frame index at **60 FPS** + `t_sec = frame/60.0`

**Frequency:**
- Run-level: start + end
- Room-level: enter + exit (+ death)
- Wave/spawn-level: wave start/end, every spawn_event (including telegraph spawns)
- Director heartbeat: every **300 frames** during combat rooms

Director state snapshot is stored inside each room/wave record as `director_state`.


---

## 18) Optional LLM Features

- LLM is optional. If disabled/unavailable, use the static story text.
- All LLM outputs must be capped (<180 words) and must not include mechanics.


---

## 19) Determinism & Seeds

- Seed drives procedural generation and flexible-slot marking.
- Seed must **never** be displayed in UI.


---

## 20) Asset TODO Checklist

- Enemy sprites (swarm/flanker/brute/elite/mini boss) with hit/death animations
- Spawn portal animation frames (if not present)
- Slash VFX + hit impact effects
- Lava animation frames (optional)
- Corridor tileset (optional)
- UI door indicators/overlays if `assets/tiles/doors/` is used

# SECTION — Biome 1 Asset Binding Contract (Authoritative)

This section defines:

- Exact folder structure
- Required PNG names
- Frame counts
- Sprite dimensions
- Animation FPS
- Gameplay linkage
- Fallback rules

This section overrides any ambiguity elsewhere.

---

## 1️⃣ Global Rendering Rules

- Tile size: **32×32**
- Entity sprite size: **64×64**
- Brute optional size: **80×80**
- Mini Boss size: **96×96**
- Final Boss size: **128×128**
- Anchor point: **center alignment**
- Transparent PNG required
- Engine baseline: **60 FPS**
- Animations loop unless explicitly marked non-loop
- All assets load from `assets/`
- Missing asset → load `assets/placeholders/missing.png`
- Game must NOT crash on missing asset

---

## 2️⃣ Player Asset Contract

**Base Path:**  
`assets/entities/player/`

| Folder        | Frames | FPS | Loop |
|---------------|--------|-----|------|
| idle          | 2–4    | 6   | Yes  |
| walk          | 4–6    | 8   | Yes  |
| attack_short  | 4      | 10  | No   |
| attack_long   | 6      | 10  | No   |
| dash          | 2–3    | 12  | No   |
| block         | 1–2    | Static | Yes |
| parry         | 2      | 12  | No   |
| hit           | 1      | 0.1 sec | No |
| death         | 3–4    | 6   | No   |

After death animation completes → entity removed.

Sprite size: **64×64 px**

---

## 3️⃣ Enemy Asset Contract — Biome 1

Base path pattern:


assets/entities/enemies/<enemy_type>/


---

### 3.1 Swarm (64×64)

`assets/entities/enemies/swarm/`

| Animation | Frames | FPS | Loop |
|-----------|--------|-----|------|
| idle      | 2      | 6   | Yes  |
| walk      | 4      | 8   | Yes  |
| attack    | 3      | 10  | No   |
| hit       | 1      | Flash | No |
| death     | 2      | 8   | No   |

Elite variant uses overlay (see Section 4).

---

### 3.2 Flanker (64×64)

`assets/entities/enemies/flanker/`

| Animation | Frames | FPS |
|-----------|--------|-----|
| idle      | 2      | 6   |
| walk      | 4      | 10  |
| dash      | 3      | 14  |
| attack    | 3      | 12  |
| death     | 2      | 8   |

---

### 3.3 Brute (64×64 or 80×80)

`assets/entities/enemies/brute/`

| Animation | Frames | FPS |
|-----------|--------|-----|
| idle      | 2      | 5   |
| walk      | 4      | 6   |
| windup    | 2      | 6   |
| slam      | 3      | 10  |
| death     | 3      | 6   |

---

## 4️⃣ Elite Modifier Overlay

Path:


assets/entities/enemies/elite/


Required files:

- `elite_glow_overlay.png`
- `elite_aura_01.png`
- `elite_aura_02.png`

Rules:

- +40% HP
- +20% Damage
- Aura loops at 6 FPS
- Overlay rendered above base sprite
- Elite telegraph uses gold variant

---

## 5️⃣ Mini Boss (Biome 1)

Path:


assets/entities/enemies/mini_boss/


Sprite size: **96×96**

| Animation     | Frames | FPS |
|---------------|--------|-----|
| idle          | 3      | 5   |
| move          | 4      | 6   |
| attack_01     | 4      | 10  |
| attack_02     | 4      | 10  |
| dash          | —      | —   |
| windup        | —      | —   |
| phase_change  | —      | —   |
| hit           | —      | —   |
| death         | 4      | 6   |

Death → spawn reward → unlock doors after delay.

Health Bar Assets:


assets/ui/hud/mini_boss_health_frame_400x40.png
assets/ui/hud/mini_boss_health_fill_396x24.png


---

## 6️⃣ Spawn Effects

### 6.1 Telegraph Tiles

Path:


assets/effects/telegraphs/


Required:

- `telegraph_tile_32x32.png`
- `telegraph_tile_anim_32x32.png`
- `telegraph_elite_gold_32x32.png`
- `telegraph_elite_gold_anim_32x32.png`

Duration: 0.5 sec  
Pulses: 3  
No collision  
Spawn at frame 30  

---

### 6.2 AoE Telegraph

- `telegraph_aoe_ring_256x256.png`
- `telegraph_elite_gold_aoe_256x256.png`
- `telegraph_boss_purple_line_256x64.png`

Animate at **12 FPS**

---

### 6.3 Spawn Portal

Path:


assets/effects/spawn_portal/


Files:

- `frame_01.png`
- `frame_02.png`
- `frame_03.png`
- `frame_04.png`
- `frame_05.png`
- `frame_06.png`

6 frames  
12 FPS  
Spawn occurs at final frame  

---

## 7️⃣ Player Attack VFX

Path:


assets/effects/slash/


- `slash_short_01.png`
- `slash_short_02.png`
- `slash_long_01.png`
- `slash_long_02.png`

Hit Impact:


assets/effects/hit/


- `hit_spark_01.png`
- `hit_spark_02.png`

---

## 8️⃣ Damage Numbers


assets/ui/damage_numbers/font_damage.ttf


Rules:

- Red → damage taken
- Yellow → damage dealt
- Float duration: 0.6 sec
- Fade to 0 alpha

---

## 9️⃣ Hazard Tiles

Path:


assets/tiles/


Required:

- `floor_tile.png`
- `lava_tile_32x32.png`
- `lava_tile_anim_32x32.png`
- `slow_tile_32x32.png`

Wall tiles (if used):

- `wall_top_32x32.png`
- `wall_bottom_32x32.png`
- `wall_left_32x32.png`
- `wall_right_32x32.png`
- `wall_corner_tl_32x32.png`
- `wall_corner_tr_32x32.png`
- `wall_corner_bl_32x32.png`
- `wall_corner_br_32x32.png`

Lava Animation:

- 3-frame loop
- 6 FPS
- **Damage: 6 HP/sec**

---

## 🔟 Doors

Path:


assets/tiles/doors/


- `door_closed_32x32.png`
- `door_locked_32x32.png`
- `door_open_32x32.png`
- `door_safe_32x32.png`

Locked during combat  
Unlock delay → 0.5 sec  

---

## 1️⃣1️⃣ HUD

Path:


assets/ui/hud/


- `health_bar_frame_192x32.png`
- `health_bar_fill_190x26.png`
- `health_bar_damage_flash_clean_192x32.png`
- `health_bar_lowhp_glow_clean_192x32.png`
- `icon_attack_24x24.png`
- `icon_defence_24x24.png`
- `icon_speed_24x24.png`

Boss:

- `final_boss_health_frame_800x60.png`
- `boss_phase_marker_20x40.png`
- `boss_nameplate_panel_600x80.png`

---

## 1️⃣2️⃣ Corridor Tileset

Path:


assets/tiles/corridor/


- `corridor_floor_32x32.png`
- `corridor_wall_top_32x32.png`
- `corridor_wall_bottom_32x32.png`
- `corridor_wall_left_32x32.png`
- `corridor_wall_right_32x32.png`
- `corridor_corner_tl_32x32.png`
- `corridor_corner_tr_32x32.png`
- `corridor_corner_bl_32x32.png`
- `corridor_corner_br_32x32.png`
- `corridor_corners_sheet.png`
- `torch_32x32.png`
- `corridor_shadow_overlay.png`

Corridor width: 2–3 tiles

---

## 1️⃣3️⃣ Ambient Particles

Path:


assets/effects/particles/


- `ember_01_4x4.png`
- `ember_02_4x4.png`
- `ash_01_4x4.png`

Spawn: 18–28  
Alpha: 20–40%  
Upward drift  

---

## 1️⃣4️⃣ LLM Story Panel (Optional)

Path:


assets/ui/story/


- `story_panel_bg.png`
- `story_continue_button.png`

If LLM unavailable → use static story text  
Skip via Enter  

---

## 1️⃣5️⃣ Mandatory Asset Checklist (Biome 1 MVP)

You MUST have:

- Player sprites
- Swarm
- Flanker
- Brute
- Mini Boss
- Elite overlay
- Telegraph assets
- Spawn portal
- Slash VFX
- Hit sparks
- Lava tile
- Doors
- HUD
- Damage numbers font

If any missing → load placeholder, log warning, continue execution.

Hi Cursor — I’m facing multiple issues with the Swarm enemy. Please address the following:

1️⃣ Swarm Enemy Overlaps Player (No Separation)

Problem:

Swarm enemy overlaps the player sprite.

It does not maintain proper minimum distance.

It feels like it sits inside the player.

Required Fix:

Enforce minimum separation distance between swarm enemy and player.

Swarm enemy should stop moving when within a small radius (e.g., 40–50 px).

Do not allow rect overlap with player.

Implement simple pushback or collision resolution if overlapping.

Example idea:

if swarm.rect.colliderect(player.rect):
    resolve_overlap()

Or enforce:

if distance_to_player <= stop_radius:
    stop_moving()
2️⃣ Swarm Enemy Not Taking Damage

Problem:

When I attack left or right, swarm enemy does not lose HP.

Damage detection seems inconsistent.

Likely hitbox too small or wrong rect.

Required Fix:

Increase swarm enemy hitbox rectangle.

Ensure damage uses rect.colliderect(attack_rect) only.

No angle-based filtering.

If attack_rect overlaps enemy.rect → apply damage.

Please verify:

if attack_rect.colliderect(swarm.rect):
    swarm.take_damage(damage)
3️⃣ Swarm Teleports to Opposite Side During Attack

Problem:

If swarm is on left and I attack left,

It suddenly appears on right side.

This causes attack to miss.

This suggests:

Position update happening after attack

Or direction-based reposition logic bug

Or incorrect rect center assignment

Required Fix:

Prevent swarm from switching sides instantly.

Movement should be continuous.

Remove any forced side-flipping logic.

Ensure position updates occur BEFORE collision checks.

Add debug logging for:

Swarm position before update

Swarm position after update

Attack rect coordinates

4️⃣ Debug Mode Request

Please temporarily:

Draw swarm.rect in green

Draw attack_rect in red

Print HP change when damage applied

This will help visually confirm collisions.

🎯 Expected Result

Swarm maintains minimum distance.

Swarm does not overlap player.

Swarm takes damage when in correct attack rectangle.

Swarm does not teleport or flip sides during attack.

