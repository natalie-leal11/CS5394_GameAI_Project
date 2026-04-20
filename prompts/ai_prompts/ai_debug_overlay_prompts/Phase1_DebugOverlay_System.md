# PHASE 1 — Debug Overlay System

## Goal

Implement a lightweight AI debug overlay.

## CREATE FILE

```
src/game/debug/debug_overlay.py
```

## CLASS

DebugOverlay

## Constructor

DebugOverlay(game_scene)

Store the GameScene reference.

## STATE

self.enabled = False

Initialize font:

```
pygame.font.SysFont("consolas", 16)
```

## METHODS


toggle()

Flip enabled state.

draw(screen)

If overlay is disabled return immediately.

Otherwise draw the following values if available:

Seed
Room index
Player model state
AI Director difficulty modifier
Enemy adjustment
Reinforcement chance

## Example display

```
AI DEBUG
Seed: 12345
Room: 17
Player State: STABLE
Director Difficulty: 1.10
Enemy Adjustment: +1
Reinforcement Chance: 0.32
```

## Rendering rules

Text color: (0,255,0)
Line spacing: 18 pixels

Draw a semi‑transparent background rectangle
behind the text.

Color: black
Alpha: 120
Padding: 8 pixels

Render overlay in the top-left corner.

## STOP AFTER FILE CREATION
