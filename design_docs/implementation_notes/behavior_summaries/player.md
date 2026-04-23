---
# Player — Behavior Implementation Summary

## Overview

The player is implemented as a finite state machine. At any given game tick the
player occupies exactly one of the following states:

`idle` · `walk` · `dash` · `attack_short` · `attack_long` · `block` · `parry` · `hit` · `death`

The active state controls which animation plays, whether new input is accepted,
and whether movement is allowed. Transitions between states are governed by a
strict priority chain evaluated top-to-bottom inside `_run_update_body()` every
frame.

---

## State Machine — Priority Order

Each frame, `_run_update_body()` evaluates the following in order and returns
early on the first match:

1. **Death entry** — if `hp <= 0` and not already in `death`, transition to `death`.
2. **Death active** — advance death animation; set `inactive = True` when finished.
3. **Dash active** — call `apply_player_movement()`, return when dash ends.
4. **Hit stun** — advance hit animation, block all movement until it finishes.
5. **Attack active** — advance attack animation; movement is still allowed during
   attacks so the player can strike on the move. Transition to `idle` on finish.
6. **Block / parry drop** — exit `block` or `parry` if `parry_window_timer` has
   expired and the block key is not held.
7. **Short attack** — consume `_pending_short_attack` or fresh request if cooldown
   is clear. Transition to `attack_short`.
8. **Parry** — a K-tap sets `parry_window_timer` and transitions to `parry`.
9. **Long attack** — right mouse / long attack flag triggers `attack_long`.
10. **Block** — J held while not attacking transitions to `block`.
11. **Movement / idle** — WASD held → `walk`; nothing held → `idle`.

---

## Input Buffering

Short attack inputs received while the player is in a locking state
(`attack_short`, `attack_long`, `dash`, `hit`, `death`) are stored in
`_pending_short_attack`. The pending flag is consumed and executed the moment
the locking state ends, so fast clicks are never silently dropped.

Dash can interrupt almost any state (except `hit` and `death`) because it is
checked before most of the priority chain. This makes dash feel instant regardless
of what the player was doing.

---

## Damage and Invulnerability

Taking a hit:
- Reduces `hp` by the incoming damage amount.
- Starts `damage_flash_timer` (visual feedback).
- Grants `invulnerable_timer` for a fixed window to prevent double-hits.
- Transitions to `hit` state which locks input until the animation finishes.

Parry: if a hit is received while `parry_window_timer > 0`, the hit is negated
and a parry success event fires instead of the normal damage path.

---

## RL Integration

The player's `update()` method accepts all inputs as explicit boolean arguments
rather than reading from `pygame.key.get_pressed()` directly. `GameScene`
assembles those booleans from either the real keyboard state (human play) or the
integer stored in `gs._rl_action` (RL agent). This means the RL agent drives
the exact same player code path a human uses — no parallel simulation.

---

## Primary File Locations

| File | Contents |
|---|---|
| `src/entities/player.py` | `Player` class, `update()` shell, `_run_update_body()`, all state logic |
| `src/systems/player_movement.py` | `apply_player_movement()`, dash physics, velocity integration |
| `src/systems/player_combat.py` | Attack hitbox generation, damage application, parry resolution |
| `src/systems/collisions.py` | `hitbox_overlap()` used by combat and hazard systems |
| `src/game/config.py` | All player constants: speed, HP, cooldown durations, dash timing, invulnerability window |
