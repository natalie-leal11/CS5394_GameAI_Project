# Biome 1 — Complete Requirements Breakdown (Authoritative)

This document consolidates what is currently expected to be implemented for Biome 1 (MVP + current fixes). **It is intended for Cursor AI to follow exactly.**

---

## 0) Global Constants

### Rendering & Grid

- **TILE_SIZE_PX = 32**
- All tile-based placement must align to the 32px grid.
- Walls/doors must align to tile edges.
- World-space rectangles (player/enemies/doors) must be consistent (avoid mixing screen-space vs world-space).

### Player Sprite

- **PLAYER_SIZE = (96, 96)**

---

## 1) Room System

### 1.1 Room fills the viewport

- Rooms must be sized to fill the current game window using tile sizing:
  - `cols = screen_width // 32`
  - `rows = screen_height // 32`
- The playable room is defined by this **rows × cols** grid (not a smaller "box inside the screen").

### 1.2 Wall border thickness by room type

- Walls are a border around the room and should not consume most of the playable area.
- **Standard rooms** (Combat, Safe): wall thickness **B = 2 tiles**
- **Small/tight rooms** (Ambush): wall thickness **B = 4 tiles**
- Walls are formed by placing wall tiles on the border area. Interior is floor.
- **Playable interior bounds** (tile indices):
  - Rows: `[B .. rows - B - 1]`
  - Cols: `[B .. cols - B - 1]`

### 1.3 No floor outside room bounds

- Do not render normal floor outside the room grid.
- Outside the room should be:
  - empty/void (black), or
  - clipped away (not visible), or
  - a distinct void tile (not normal floor)

---

## 2) Wall Tiles

### 2.1 Wall tile assets (32×32 only)

Use:

- `assets/tiles/walls/wall_top.png`
- `assets/tiles/walls/wall_bottom.png`
- `assets/tiles/walls/wall_left.png`
- `assets/tiles/walls/wall_right.png`
- `assets/tiles/walls/wall_corner_tl.png`
- `assets/tiles/walls/wall_corner_tr.png`
- `assets/tiles/walls/wall_corner_bl.png`
- `assets/tiles/walls/wall_corner_br.png`

### 2.2 Placement rules

- Top border: wall_top + corner tiles at ends
- Bottom border: wall_bottom + corner tiles at ends
- Left border: wall_left (skip corners)
- Right border: wall_right (skip corners)

### 2.3 Collision rules

- All wall tiles are solid:
  - player/enemies cannot pass through
  - wall collision should match tile area

---

## 3) Doors

### 3.1 Door assets (32×32 sprites scaled)

Door assets:

- `assets/tiles/doors/door_open_32x32.png`
- `assets/tiles/doors/door_closed_32x32.png`
- `assets/tiles/doors/door_locked_32x32.png`
- `assets/tiles/doors/door_safe_32x32.png` (optional use if needed)

### 3.2 Door visual size

- Door must be visually comparable to the player:
- **Door sprite must render at 96×96 px** (scale 3×).

### 3.3 Door logic by room

- **Room 0 (Training/Dummy Room):** door is OPEN by default (no enemy dependency)
- **All combat rooms:** door starts CLOSED
  - door opens ONLY after all enemies are defeated
  - after enemies cleared, wait **2–3 seconds** (recommended **2.5s**) then open

### 3.4 Door transition condition (no angle)

Transition must occur as soon as:

- `door_state == OPEN`
- AND `player.rect.colliderect(door.trigger_rect)`

**No facing checks. No angle checks.**

### 3.5 Doorway carving MUST be wall-thickness aware

**This is critical for B=4 rooms.**

- Let wall thickness = **B** tiles.
- A doorway must be carved through the **entire** wall thickness, not just the outermost wall tile.

**Example (BOTTOM door, 2 tiles wide):**

- Choose `door_col_start` (centered)
- For depth `d` from `0..B-1`, set tiles:
  - `row = rows - 1 - d`
  - `col = door_col_start` and `door_col_start + 1`
- to **FLOOR** and remove collision.

This ensures the player can reach the doorway even when B=4.

### 3.6 Door placement rule (inner-face)

- Doors must be **reachable** from the playable interior.
- Place the door aligned to the **inner face** of the wall border, not beyond it.

### 3.7 Trigger rect alignment

- Door sprite is 96×96
- Door rect must be centered on the doorway opening
- Trigger rect should be slightly smaller and centered:
  - `door.trigger_rect = door_rect.inflate(-20, -20)`

### 3.8 Debug overlays (required while fixing)

Add a debug mode to draw:

- wall collision rects (**blue**)
- door.trigger_rect (**green**)
- player.rect (**red**)

This is **mandatory** until doors work reliably for both B=2 and B=4 rooms.

---

## 4) Player Directional Animations

- **New asset root:** `assets/entities/player/directional/`
- **Folders:**
  - `idle/` (only frame_01.png currently)
  - `walk_up/`, `walk_down/`, `walk_left/`, `walk_right/` (frames 01–02)
  - `attack_up/`, `attack_down/`, `attack_left/`, `attack_right/` (frames 01–02)
- **Rules:**
  - Track player facing direction (up/down/left/right).
  - Use correct directional folder for walk/attack.
  - If folder has 1 frame, treat as static (no animation crash).

---

## 5) Combat & Hit Detection (Applies to ALL enemies + dummy)

### 5.1 Authoritative melee hit detection

- Damage is applied **ONLY** using directional rectangle hitboxes.
- **No angle checks. No distance-circle-only damage.**
- **Condition:** If `attack_rect.colliderect(enemy.hurtbox_rect or enemy.rect)` → apply damage

### 5.2 Short Attack (close, wide)

- Range forward: **48 px**
- Thickness: **70 px**
- Active duration: ~0.10s
- **Rect examples:**
  - RIGHT: `Rect(player.right, player.centery-35, 48, 70)`
  - LEFT: `Rect(player.left-48, player.centery-35, 48, 70)`
  - UP: `Rect(player.centerx-35, player.top-48, 70, 48)`
  - DOWN: `Rect(player.centerx-35, player.bottom, 70, 48)`

### 5.3 Long Attack ("ranged slash": far, thinner, slower)

- Range forward: **192 px**
- Thickness: **50 px**
- Active duration: ~0.12s
- Slightly higher wind-up + cooldown than short

### 5.4 One-hit-per-swing rule

- During one attack swing, each enemy may only be damaged **once**.
- Track a set like `damaged_enemies_this_swing`.

### 5.5 Dummy is damageable

- Training dummy is treated like an enemy:
  - has HP
  - has rect/hurtbox
  - receives damage via same attack system

---

## 6) Attack Range Visualization (Debug Only)

- Keep range indicator circles as **debug visual only**
- **Must not** control damage logic
- **Radii:** Short = 48 px, Long = 192 px
- Must be toggleable: `DEBUG_DRAW_ATTACK_RANGE = True/False`
- **Recommended debug visuals:**
  - draw attack_rect (red)
  - draw enemy hurtbox rect (green)
  - optionally draw range circles

---

## 7) Health Bars

### 7.1 Player health bar (HUD at bottom)

- **Position:** bottom center (20 px above bottom)
- **Size:** ~300×18 px
- **Background:** dark gray
- **Border:** 2 px
- **Color thresholds** based on HP%:
  - 50%: Blue
  - 10%–50%: Orange
  - <10%: Red
- If HP can exceed 100% (overheal), bar must visually handle up to **130%** (e.g., clamp display or extend overlay region).

### 7.2 Enemy health bars (above enemies)

- **Size:** 40×6 px
- Above enemy sprite (about 12 px offset)
- Distinct palette from player
- Hide when dead

---

## 8) Safe Room Requirements

### 8.1 Safe room contents

- No enemies
- No hazards
- Doors open immediately (no combat lock)
- Has a **mandatory heal pickup/altar** (see below)

### 8.2 Mandatory heal pickup

- **Asset:** `assets/tiles/powerups/heal_health_32x32.png`
- **Placement:**
  - Place in corner of safe room interior
  - Visually glowing/pulsing
- **Interaction:**
  - When player is close, show: **Press [H] to gain Health Upgrade (+30%)**
- **Heal behavior:**
  - Adds 30% of base max HP
  - Overheal allowed up to 130% cap
  - No timed decay; it decreases only when taking damage normally
- **Formula:**
  - `heal_amount = base_max_hp * 0.30`
  - `cap = base_max_hp * 1.30`
  - `current_hp = min(current_hp + heal_amount, cap)`
- **Limit:** usable **once per room visit** (then disappears/dims)

---

## 9) Enemy Spawning (No corners, no doors, no overlaps)

### 9.1 Global spawn constraints

Enemies must **NOT** spawn:

- near player spawn (min **150 px** away)
- near doors (min **3 tiles** away)
- near walls (min **3 tiles** away)
- in corners
- overlapping each other (min **90 px** spacing; +extra spacing for elite)

### 9.2 Adaptive spacing

- Elite rooms should have extra spacing: `MIN_DISTANCE_BETWEEN_ENEMIES += 60`

### 9.3 Pattern support (optional but implemented)

- Spawn modes: Spread (default combat), Triangle (elite), Ambush ring (ambush rooms)
- Must still validate not inside walls/doors

---

## 10) Mini Boss Behavior

### 10.1 No teleport / no side flip bug

- Mini boss must **NOT**:
  - instantly jump to opposite side of the player
  - snap x/y position around player during attacks
- Movement must be **continuous via velocity per frame**.
- **Facing rule:** face right if `boss.centerx < player.centerx` else face left

---

## 11) Training Room (Room 0)

- Large full-screen play area (same sizing rules)
- **Contains:**
  - training dummy (damageable)
  - tutorial/interaction object (book pedestal ok)
  - door is **OPEN** by default
- No combat locking required

---

## 12) Debugging Aids (Must be available)

Add toggles for:

- draw wall collision rects
- draw player rect
- draw enemy rect/hurtbox
- draw door trigger rect
- draw attack hitbox rect
- draw attack range circles (48/192)

These are **required** until all collisions/transitions/hits are stable.

---

## Acceptance Checklist (Quick Tests)

- [ ] Room fills screen; only border walls; no extra outside floor.
- [ ] B=2 and B=4 rooms both have working doors and transitions.
- [ ] Door opens only after enemy clear + 2.5s delay (except Room 0).
- [ ] Player transitions on overlap with open door (no angle issues).
- [ ] Dummy/enemies take damage reliably with attack rectangles.
- [ ] Enemies do not spawn in corners/doors/walls; do not overlap each other.
- [ ] Safe room heal works on H, adds +30% and allows up to 130%.
