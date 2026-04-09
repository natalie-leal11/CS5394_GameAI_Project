"""
Discrete action → gameplay controls. Central map for RL (edit here only).

See DungeonEnv.action_space (Discrete(17)).
"""

from __future__ import annotations

import pygame

# Action indices (must match DungeonEnv.action_space = Discrete(17))
ACTION_NOOP = 0
ACTION_MOVE_UP = 1
ACTION_MOVE_DOWN = 2
ACTION_MOVE_LEFT = 3
ACTION_MOVE_RIGHT = 4
ACTION_SHORT_ATTACK = 5
ACTION_LONG_ATTACK = 6
ACTION_DASH = 7
ACTION_BLOCK = 8
ACTION_PARRY = 9
# Interaction (same gameplay as manual KEYDOWN in GameScene.handle_event)
ACTION_INTERACT = 10  # E — altar / close story panel / confirm-style uses
ACTION_SAFE_ROOM_HEAL = 11  # F — safe-room heal pickup when near prompt
ACTION_RESERVE_HEAL = 12  # H — consume reserve heal if available
ACTION_SAFE_CHOICE_1 = 13  # 1 — safe-room upgrade choice
ACTION_SAFE_CHOICE_2 = 14  # 2
ACTION_SAFE_CHOICE_3 = 15  # 3
ACTION_SAFE_CHOICE_4 = 16  # 4

ACTION_COUNT = 17

ACTION_NAMES: dict[int, str] = {
    0: "noop",
    1: "move_up",
    2: "move_down",
    3: "move_left",
    4: "move_right",
    5: "short_attack",
    6: "long_attack",
    7: "dash",
    8: "block",
    9: "parry",
    10: "interact",
    11: "safe_room_heal",
    12: "reserve_heal",
    13: "safe_choice_1",
    14: "safe_choice_2",
    15: "safe_choice_3",
    16: "safe_choice_4",
}


def movement_keys_for_action(action: int) -> set[int]:
    """Return a set of pygame key constants for held movement (WASD subset)."""
    a = int(action)
    keys: set[int] = set()
    if a == ACTION_MOVE_UP:
        keys.add(pygame.K_w)
    elif a == ACTION_MOVE_DOWN:
        keys.add(pygame.K_s)
    elif a == ACTION_MOVE_LEFT:
        keys.add(pygame.K_a)
    elif a == ACTION_MOVE_RIGHT:
        keys.add(pygame.K_d)
    return keys


def attack_flags_for_action(action: int) -> tuple[bool, bool]:
    """(short_attack_requested, long_attack_requested) for one frame."""
    a = int(action)
    return (a == ACTION_SHORT_ATTACK, a == ACTION_LONG_ATTACK)


def dash_requested_for_action(action: int) -> bool:
    return int(action) == ACTION_DASH


def block_parry_for_action(action: int) -> tuple[bool, bool]:
    """
    Match manual semantics for one frame: block = hold J, parry = tap K (one-shot request).

    # RL-only path: used when GameScene._rl_controlled — not read from keyboard/mouse.
    """
    a = int(action)
    if a == ACTION_BLOCK:
        return (True, False)
    if a == ACTION_PARRY:
        return (False, True)
    return (False, False)


def interaction_key_for_action(action: int) -> int | None:
    """
    If action is an interaction-only index, return the pygame key for handle_event(KEYDOWN).
    Movement/combat actions return None (handled separately).
    """
    a = int(action)
    if a == ACTION_INTERACT:
        return pygame.K_e
    if a == ACTION_SAFE_ROOM_HEAL:
        return pygame.K_f
    if a == ACTION_RESERVE_HEAL:
        return pygame.K_h
    if a == ACTION_SAFE_CHOICE_1:
        return pygame.K_1
    if a == ACTION_SAFE_CHOICE_2:
        return pygame.K_2
    if a == ACTION_SAFE_CHOICE_3:
        return pygame.K_3
    if a == ACTION_SAFE_CHOICE_4:
        return pygame.K_4
    return None
