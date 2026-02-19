# Adaptive AI Dungeon — Final Parameters (Master Combined Specification)

**Group Members:** Natalie Cristina Leal Blanco, Maham Asif  

---

# GAME BEGINNING

## 1. Main Menu Structure

When the game launches, it opens directly to the **Main Menu**.

### Main Menu Options

- **Play**  
  Starts a new run and loads the player into **Room 0 (Start Room)**.

- **Controls**  
  Opens a screen showing the full control mapping (movement, attacks, dash, pause) and includes a **Back** option to return to the Main Menu.

- **Settings**  
  Opens a screen to adjust basic game settings (audio and display). Includes **Apply/Save** and **Back** buttons.

- **Quit**  
  Exits and closes the game application immediately.

---

## 2. Controls Screen

### Title
**Controls**

### Control Scheme (Keyboard + Mouse)

- **Movement:** W / A / S / D  
- **Short Attack:** Left Mouse Click  
- **Long Attack:** Right Mouse Click  
- **Dash:** Space  
- **Pause / Menu:** Esc  

### UI Elements

- Title: “Controls”
- List of bindings (as shown above)
- **Back** button (returns to Main Menu)

---

## 3. Settings Screen

The Settings screen allows the player to adjust audio and display preferences.  
These settings do not affect gameplay mechanics or difficulty.

### Audio Settings

- **Master Volume (0–100 slider)**  
  Controls the overall volume of the game, including music and sound effects.

- **Music Volume (0–100 slider)**  
  Controls only the background music volume.

- **SFX Volume (0–100 slider)**  
  Controls all in-game sound effects (attacks, enemy sounds, UI clicks, etc.).

---

### Display Settings

- **Display Mode (Toggle: Windowed / Fullscreen)**  
  Allows the player to switch between windowed mode and fullscreen mode.

---

### Settings Screen Buttons

- **Apply / Save**  
  Saves the selected settings.

- **Back**  
  Returns to the Main Menu without starting a run.

---

### Design Constraints

- No gameplay-affecting settings.
- No difficulty slider.
- No seed display.
- No debug options available to the player.

## 4. Main Menu Background

The Main Menu background shall be a **subtle animated dungeon scene** rendered in 2D top-down pixel style.  
The background is non-interactive and purely visual.

---

### 4.1 Background Type

- Subtle animated dungeon environment
- No gameplay logic active
- No enemies or player character visible
- Static camera (no panning or movement)

---

### 4.2 Allowed Animation Elements

The following subtle animations are permitted:

- Torch flame flicker (slow, looping)
- Lava glow with soft pulsing effect (if visible)
- Light drifting fog
- Minimal dust or ambient particle effects

Animations must be:
- Slow
- Looping
- Non-distracting
- Low intensity

The following are **not allowed**:

- Explosions
- Fast flashing lights
- Camera shake
- Sudden or aggressive movement

---

### 4.3 Visual Theme

- Dark dungeon stone textures
- Deep grey base tones
- Warm accent lighting (orange/red torch glow)
- Soft ambient shadows
- Strong contrast to ensure menu text readability

Menu text must remain clearly visible at all times.

---

### 4.4 Performance Constraints

- Background animation must not impact gameplay performance.
- No dynamic real-time lighting engine.
- Particle count must remain low.
- No heavy shader usage.

---

### 4.5 Architectural Constraint

- Background belongs strictly to the Rendering Layer.
- It contains no gameplay logic.
- It does not use seeded randomness.
- It must not affect determinism.
- It is purely cosmetic.

## 5. Game Start Flow (After Clicking "Play")

When the player clicks **Play**, the following sequence occurs:

---

### 5.1 Fade Transition

- The Main Menu fades out smoothly (light fade-to-dark transition).
- Duration: ~1.0–1.5 seconds.
- Background music transitions into low ambient dungeon sound.

---

### 5.2 Story Introduction Screen

After the fade, a short narrative introduction appears on screen.

The story is presented as centered text with subtle fade-in animation.

Example narrative (LLM-generated or template-based):

> "You awaken in the depths of a forgotten dungeon.  
> Thirty chambers stand between you and freedom.  
> Powerful guardians watch each biome.  
> Survive the trials. Defeat the bosses.  
> Escape to the outside world."

Player can:
- Press any key to continue.

---

### 5.3 LLM Integration (Optional Narrative Enhancement)

An LLM may be integrated to dynamically generate short narrative introductions based on:

- Biome theme
- Dungeon variation
- Difficulty state
- Prior player performance

LLM Usage Constraints:
- LLM generates narrative text only.
- It does not influence gameplay mechanics.
- It does not modify dungeon structure.
- It does not affect determinism.

If LLM is unavailable, the system falls back to a predefined story template.

---

### 5.4 Transition to Gameplay

After the player continues:

- Screen fades into gameplay.
- Player spawns in **Room 0 (Start Room)**.
- Controls become active.
- Run officially begins.

A) Global Questions (apply to all rooms)

Spawn Safety Rules

What is the minimum safe distance from player spawn where enemies can appear? (Example: ≥ 4 tiles / ≥ 128px)

What is the minimum distance between enemies at spawn so they don’t overlap or “struggle”? (Example: ≥ 2 tiles)

Should we enforce “no spawn on hazards” (lava/slow)? Always?

Engage Rules

When does enemy AI become active?

Immediately on room entry?

After a 0.5–1.0 sec “entry grace” like Hades?

Attack Distance Rules

From what distance can the player short attack hit? (You already have 50px—confirm final)

From what distance can the player long attack hit? (Projectile range depends on lifetime+speed—confirm effective range)

What is the melee enemy attack range? (tile-based: 1 tile? 1.5 tiles?)

Spawn Visualization

Do all spawns use a telegraph?

Red tile marker?

Shadow circle?

Small “portal” effect?

How long is telegraph duration? (Example: 0.6s)

Deterministic Spawn Points

Do we predefine a set of spawn anchor points per room template (like Hades arenas)?

Or do we generate random points but constrained by rules (min distances, safe tiles, not overlapping)?

B) Room 0 (Start Room) — Questions

Purpose

Is Room 0 strictly a non-combat tutorial/safe intro?

Story Interaction

Do you want a “story object” (book/altar) the player interacts with?

If yes: is it optional or required?

Does it show tutorial text + run goal?

Allowed Actions

Can player practice attacks/dash in Room 0?

Exit Condition

Is the exit always open? Or opens after interacting with the book?

C) Combat Room — Questions (Room 1+ typical)

Enemy Spawn Moment

Do enemies spawn:

Already standing in place when player enters?

Or spawn with telegraph after entry?

Enemy Initial State

Should enemies:

idle for 0.3–0.6s then engage?

engage instantly?

Positions

Should enemies spawn in:

A ring around player?

Corners?

Mixed anchor points?

No-Clumping Rule

Do we enforce “separation” at spawn only, or also during movement (simple steering)?

Room Lock

When player enters combat room:

Doors close immediately?

Doors close after telegraph finishes?

D) Ambush Room — Questions (Hades-like)

Ambush Trigger

Ambush triggers immediately on entry or after player moves to center?

Spawn Style

Enemies appear via:

Red tiles → pop up

Portals

Falling from ceiling (visual only)

Ambush Wave Structure

One wave only? Or 2 waves max?

Player Fairness

Must there be an entry safe zone (3×3) with no spawns for 1–2 seconds?

E) Safe / Rest Room — Questions

Healing Format

Healing appears as:

A “healing fountain” object?

Pickups on floor?

Both?

Pickup Rules

Can player pick multiple healing items or only one?

Preview UI

When player approaches item:

Show tooltip: “Heal +20 HP” / “Speed +10%”?

Placement

Where do drops spawn?

Near center?

Near edges?

Always away from door?

Upgrade Choice

Upgrades appear as:

3 choices like Hades?

2 choices?

Does AI Director bias which choices appear?

F) Corridor / Transition Room — Questions

Purpose

Is it non-combat always?

Choices

Does it offer a fork choice (two doors)?

Or just a pacing buffer room?

Loot

Can small loot appear here or never?

G) Elite Room — Questions

Elite Entry

Elite appears:

Alone with reinforcements?

Or elite + 2–4 normal enemies?

Telegraph

Does elite spawn with a stronger telegraph effect (gold aura + marker)?

Summon Rule

When elite summons:

Trigger at 50% HP?

Timer-based?

Director-based?

Summon Spawn

Do summons appear:

From red tiles (like ambush)?

From portals near edges?

Caps

When summoning, do we always respect MAX_ACTIVE_ENEMIES_PER_ROOM = 10?

H) Biome-by-Biome Questions (because you changed Elite counts)
Biome 1 (Rooms 0–7)

What enemy types are allowed? (Swarm + basic flanker only?)

Do we allow ambush here at all? (Spec says soft ambush only)

Hazard low: Should spawns avoid hazards completely?

Biome 2 (Rooms 8–15)

You set Elite = 2. Are these:

2 elite rooms, or 2 elite enemies across biome?

Are ambushes now “hard ambush” or still soft?

Biome 3 (Rooms 16–23)

You set Elite = 3. Is that too many for pacing?

Should enemies get faster/more aggressive patterns here?

Biome 4 (Rooms 24–29)

You set Elite = 4. Confirm: elite rooms or elite occurrences?

Should the checkpoint Safe Room be fixed at a specific index (e.g., Room 27/28)?

I) Enemy-by-Enemy Questions (behavior + spacing)
Swarm (Small Melee)

Attack range (in tiles/pixels)?

Do they “surround” by trying different angles, or just chase directly?

How many can spawn at once per room?

Flanker

How long do they circle before lunging?

What is dash distance and dash telegraph?

Brute

Slam radius (already 70px in heavy, brute has small AoE—confirm value)

Slam telegraph: red circle on ground? duration?

Heavy

AoE slam: should it push player back?

Does heavy have armor phase or just high HP?

Ranged (if used)

Minimum distance it tries to keep from player?

Projectile speed and telegraph?

J) Mini Boss Questions (end of each biome)

Arena Setup

Does mini boss always spawn center?

Or enters from a gate?

Summon at 50%

When summon happens, how many enemies appear? (2–4 swarms already suggested)

Where do they appear? edges? red tiles?

Phase / Pattern

Does mini boss have 2 patterns (simple) or 3?

Reward

Does mini boss drop guaranteed healing + upgrade?

K) Final Boss Questions (Room 29)

Spawn & Intro

Boss appears immediately or after a short cinematic?

Phase Transition

During 2s invulnerability: what does the boss do? (roar + glow)

Summon Rule

Final boss summons once at phase 2 start (per your spec). Confirm again.

Summon Type

Does boss summon:

2 elites? or 1 elite + 2 normal? or only normal?

Summon Placement

Red tiles at edges?

Always opposite side of player?

Fairness

Guarantee at least one safe zone remains in boss arena after summons?

L) Healing Drops & Loot Questions (combat rooms)

Do healing drops appear:

only in Safe Rooms?

or sometimes after combat clears?

Drop type:

small heal vs big heal?

Pickup rule:

instant pickup on overlap?

or press key to pick up (prevents accidental pickup)?

UI preview:

tooltip on hover/near?

M) Implementation Questions (to avoid “random mess”)

Do we want a spawn-point system per room template?

Example: each room has 8–12 predefined spawn anchors.

Do we want spawn groups?

Example: “Group A = 3 swarms in triangle”, “Group B = brute + flankers”.

Do we want a deterministic function:

choose_spawn_points(seed, room_template_id, enemy_count)?