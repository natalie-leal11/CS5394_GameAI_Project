# PHASE 2 — Integrate Overlay Into GameScene

## Modify

```
src/game/scenes/game_scene.py
```

## IMPORT

```
from game.debug.debug_overlay import DebugOverlay
```

## INITIALIZATION

Inside GameScene.__init__ add:

```
self._debug_overlay = DebugOverlay(self)
```

## INPUT HANDLING

Inside handle_event():

```
if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
    self._debug_overlay.toggle()
```

## DRAWING

At the end of GameScene.draw():

```
self._debug_overlay.draw(screen)
```

Ensure this occurs AFTER all other drawing calls.

## STOP AFTER IMPLEMENTATION
