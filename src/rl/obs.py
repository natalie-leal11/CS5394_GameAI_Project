"""
Fixed-size observation vector for DungeonEnv (Step 2).

# RL-only path — safe to remove if RL is abandoned

Reads from GameScene and nested objects only; does not mutate gameplay state.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from dungeon.room import TILE_LAVA, TILE_SLOW, RoomType, total_campaign_rooms
from game.config import (
    LOGICAL_H,
    LOGICAL_W,
    PLAYER_DASH_COOLDOWN_SEC,
    PLAYER_LONG_ATTACK_COOLDOWN_SEC,
    PLAYER_LIVES_INITIAL,
    PLAYER_MAX_HP_BY_LIFE,
    PLAYER_MOVE_SPEED,
    RESERVE_HEAL_USE_COOLDOWN_SEC,
    SAFE_ROOM_OVERHEAL_CAP_RATIO,
)

# ---------------------------------------------------------------------------
# Vector layout: 36 features (see README_step2.md). All float32.
# ---------------------------------------------------------------------------
OBS_DIM = 36

# Stable RoomType order for normalization (enum iteration order is definition order in room.py).
_ROOM_TYPE_LIST: tuple[RoomType, ...] = tuple(RoomType)

# Stable enemy identity buckets: string key from enemy_type or class name.
_ENEMY_KEYS_ORDER: tuple[str, ...] = (
    "swarm",
    "flanker",
    "brute",
    "heavy",
    "ranged",
    "mini_boss",
    "MiniBoss",
    "MiniBoss2",
    "Biome3MiniBoss",
    "FinalBoss",
    "TrainingDummy",
    "other",
)
_ENEMY_KEY_TO_ID: dict[str, int] = {k: i for i, k in enumerate(_ENEMY_KEYS_ORDER)}

# Normalization scales (documented; not gameplay constants).
# Max HP: per-life ceiling * overheal cap (config) * slack for safe-room / upgrade effective HP (clamp in [0,1]).
_MAX_PLAYER_HP_UPPER = float(max(PLAYER_MAX_HP_BY_LIFE)) * float(SAFE_ROOM_OVERHEAL_CAP_RATIO) * 1.2
_MAX_VELOCITY_PX_S = float(PLAYER_MOVE_SPEED * 3.0)  # dash / mult headroom
_DISTANCE_SCALE_PX = float(math.hypot(LOGICAL_W, LOGICAL_H))  # diagonal of logical view
_INVULN_CAP_SEC = 3.0  # cap for invulnerable_timer normalization
# Simultaneous combat enemies (reinforcements, boss adds): safe upper bound; clamp ratio to [0,1].
_MAX_ALIVE_ENEMIES_CAP = 24.0
# Swarm density: same radius scale as GameScene "near enemy" (~280 px).
_LOCAL_SWARM_RADIUS_PX = 280.0
_MAX_LOCAL_ENEMIES_CAP = 12.0  # normalize in-radius count (mini-boss adds can exceed; still clamped)


def _clamp01(x: float) -> float:
    return float(np.clip(x, 0.0, 1.0))


def _clamp_m11(x: float) -> float:
    return float(np.clip(x, -1.0, 1.0))


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
        if not math.isfinite(v):
            return default
        return v
    except (TypeError, ValueError):
        return default


def room_type_to_norm(room_type: RoomType | None) -> float:
    """Map RoomType to [0, 1]. Unknown / None -> 0."""
    if room_type is None:
        return 0.0
    try:
        idx = _ROOM_TYPE_LIST.index(room_type)
    except ValueError:
        return 0.0
    return _clamp01(idx / max(1, len(_ROOM_TYPE_LIST) - 1))


def enemy_type_to_norm(enemy: Any) -> float:
    """Map enemy instance to [0, 1] using stable key table."""
    key = getattr(enemy, "enemy_type", None)
    if isinstance(key, str) and key in _ENEMY_KEY_TO_ID:
        idx = _ENEMY_KEY_TO_ID[key]
    else:
        name = type(enemy).__name__
        idx = _ENEMY_KEY_TO_ID.get(name, _ENEMY_KEY_TO_ID["other"])
    return _clamp01(idx / max(1, len(_ENEMY_KEYS_ORDER) - 1))


def _is_combat_enemy(e: Any) -> bool:
    if getattr(e, "inactive", False):
        return False
    if getattr(e, "is_training_dummy", False):
        return False
    hp = getattr(e, "hp", None)
    if hp is not None and float(hp) <= 0.0:
        return False
    st = getattr(e, "state", None)
    if st == "death":
        return False
    return True


def _nearest_enemy(enemies: list[Any], px: float, py: float) -> tuple[Any | None, float]:
    best: Any | None = None
    best_d = float("inf")
    for e in enemies:
        if not _is_combat_enemy(e):
            continue
        ex, ey = getattr(e, "world_pos", (0.0, 0.0))
        d = math.hypot(float(ex) - px, float(ey) - py)
        if d < best_d:
            best_d = d
            best = e
    if best is None:
        return None, 0.0
    return best, best_d


def _enemies_within_radius(
    enemies: list[Any],
    px: float,
    py: float,
    radius_px: float,
) -> int:
    """Count combat-relevant enemies within radius of player (Manhattan circle in Euclidean distance)."""
    r2 = radius_px * radius_px
    n = 0
    for e in enemies:
        if not _is_combat_enemy(e):
            continue
        ex, ey = getattr(e, "world_pos", (0.0, 0.0))
        dx = float(ex) - px
        dy = float(ey) - py
        if dx * dx + dy * dy <= r2:
            n += 1
    return n


def _hazard_flags(
    room: Any | None,
    hazard_system: Any | None,
    px: float,
    py: float,
) -> tuple[float, float]:
    """
    Returns (near_hazard, in_hazard_tile) each in {0,1}.
    near_hazard: neighbor tile (8-neighborhood) has lava or slow, current may or may not.
    in_hazard_tile: current tile is lava or slow.
    """
    if room is None or hazard_system is None:
        return 0.0, 0.0
    tx, ty = room.tile_at_world(px, py)
    try:
        tt = room.get_tile_type(tx, ty)
    except Exception:
        tt = ""
    in_hazard = 1.0 if tt in (TILE_LAVA, TILE_SLOW) else 0.0
    near = 0.0
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            ntx, nty = tx + dx, ty + dy
            try:
                nt = room.get_tile_type(ntx, nty)
            except Exception:
                continue
            if nt in (TILE_LAVA, TILE_SLOW):
                near = 1.0
                break
        if near:
            break
    return near, in_hazard


def build_observation(game_scene: Any) -> np.ndarray:
    """
    Build OBS_DIM float32 vector. Missing objects use safe zeros; never NaN/inf.

    Feature order matches README_step2.md (A–D + E local density).
    """
    out = np.zeros((OBS_DIM,), dtype=np.float32)
    gs = game_scene

    p = getattr(gs, "_player", None)
    rc = getattr(gs, "_room_controller", None)
    room = rc.current_room if rc is not None else None
    enemies = list(getattr(gs, "_enemies", []) or [])

    # --- A: Player (0..15) ---
    if p is not None:
        max_hp = max(_safe_float(getattr(p, "max_hp", 1.0), 1.0), 1e-6)
        hp = _safe_float(getattr(p, "hp", 0.0))
        out[0] = _clamp01(hp / max_hp)
        out[1] = _clamp01(_safe_float(getattr(p, "max_hp", 0.0)) / max(_MAX_PLAYER_HP_UPPER, 1e-6))
        out[2] = _clamp01(_safe_float(getattr(p, "lives", 0)) / float(max(1, PLAYER_LIVES_INITIAL)))
        li = int(getattr(p, "life_index", 0))
        max_li = max(0, len(PLAYER_MAX_HP_BY_LIFE) - 1)
        out[3] = _clamp01(float(li) / float(max(1, max_li)))

        px, py = getattr(p, "world_pos", (LOGICAL_W * 0.5, LOGICAL_H * 0.5))
        px, py = _safe_float(px), _safe_float(py)
        if room is not None:
            pw = float(room.pixel_width)
            ph = float(room.pixel_height)
            out[4] = _clamp01(px / max(pw, 1.0))
            out[5] = _clamp01(py / max(ph, 1.0))
        else:
            out[4] = _clamp01(px / float(LOGICAL_W))
            out[5] = _clamp01(py / float(LOGICAL_H))

        vx, vy = getattr(p, "velocity_xy", (0.0, 0.0))
        out[6] = _clamp_m11(_safe_float(vx) / _MAX_VELOCITY_PX_S)
        out[7] = _clamp_m11(_safe_float(vy) / _MAX_VELOCITY_PX_S)

        fx, fy = getattr(p, "facing", (1.0, 0.0))
        out[8] = _clamp_m11(_safe_float(fx))
        out[9] = _clamp_m11(_safe_float(fy))

        out[10] = 1.0 if bool(getattr(p, "dash_active", False)) else 0.0
        out[11] = _clamp01(_safe_float(getattr(p, "dash_cooldown_timer", 0.0)) / max(PLAYER_DASH_COOLDOWN_SEC, 1e-6))
        out[12] = _clamp01(
            _safe_float(getattr(p, "long_attack_cooldown_timer", 0.0)) / max(PLAYER_LONG_ATTACK_COOLDOWN_SEC, 1e-6)
        )
        # Public helpers (preferred).
        try:
            out[13] = 1.0 if p.is_blocking() else 0.0
        except Exception:
            out[13] = 1.0 if getattr(p, "state", "") == "block" else 0.0
        try:
            out[14] = 1.0 if p.is_parry_active() else 0.0
        except Exception:
            out[14] = 1.0 if getattr(p, "state", "") == "parry" else 0.0
        out[15] = _clamp01(_safe_float(getattr(p, "invulnerable_timer", 0.0)) / _INVULN_CAP_SEC)
    else:
        # Defaults already zero.
        pass

    # --- B: Room / progression (16..24) ---
    total_rooms = max(1, total_campaign_rooms())
    if rc is not None:
        cri = int(getattr(rc, "current_room_index", 0))
        # Campaign position: 0 at first room, 1 at last (0-based index normalized).
        out[16] = _clamp01(float(cri) / float(max(1, total_rooms - 1)))
    if room is not None:
        bi = int(getattr(room, "biome_index", 1))
        out[17] = _clamp01(float(bi) / 4.0)  # biomes 1..4 in this project
        rt = getattr(room, "room_type", None)
        if isinstance(rt, RoomType):
            out[18] = room_type_to_norm(rt)
        else:
            out[18] = 0.0

    alive_n = sum(1 for e in enemies if _is_combat_enemy(e))
    out[19] = _clamp01(float(alive_n) / max(_MAX_ALIVE_ENEMIES_CAP, 1e-6))

    room_cleared = bool(getattr(gs, "_room_cleared_flag", False))
    doors_unlocked = bool(getattr(gs, "_doors_unlocked", False))
    out[20] = 1.0 if (room_cleared or doors_unlocked) else 0.0

    is_boss_room = 0.0
    if room is not None:
        rt = getattr(room, "room_type", None)
        if rt in (RoomType.MINI_BOSS, RoomType.FINAL_BOSS):
            is_boss_room = 1.0
    out[21] = is_boss_room

    if rc is not None:
        cri = int(getattr(rc, "current_room_index", 0))
        # Progress along campaign length (1-based fraction): distinct from raw index in [16].
        out[22] = _clamp01(float(cri + 1) / float(max(1, total_rooms)))

    out[23] = 1.0 if bool(getattr(gs, "_victory_phase", False)) else 0.0
    out[24] = 1.0 if getattr(gs, "_death_phase", None) is not None else 0.0

    # --- C: Nearest enemy (25..31) ---
    if p is not None:
        px, py = getattr(p, "world_pos", (0.0, 0.0))
        px, py = _safe_float(px), _safe_float(py)
        ne, dist = _nearest_enemy(enemies, px, py)
        if ne is None:
            out[25] = 0.0
            # 26..31 stay 0
        else:
            out[25] = 1.0
            out[26] = _clamp01(dist / max(_DISTANCE_SCALE_PX, 1e-6))
            ex, ey = getattr(ne, "world_pos", (px, py))
            ex, ey = _safe_float(ex), _safe_float(ey)
            out[27] = _clamp_m11((ex - px) / max(_DISTANCE_SCALE_PX, 1e-6))
            out[28] = _clamp_m11((ey - py) / max(_DISTANCE_SCALE_PX, 1e-6))
            mhp = max(_safe_float(getattr(ne, "max_hp", 1.0), 1.0), 1e-6)
            ehp = _safe_float(getattr(ne, "hp", 0.0))
            out[29] = _clamp01(ehp / mhp)
            out[30] = enemy_type_to_norm(ne)
            # Near-threat flag: 1 if nearest combat enemy is within engagement distance (~400 px).
            out[31] = 1.0 if dist < 400.0 else 0.0

    # --- D: Hazard / reserve (32..34) ---
    if p is not None and rc is not None:
        px, py = getattr(p, "world_pos", (0.0, 0.0))
        px, py = _safe_float(px), _safe_float(py)
        hs = getattr(rc, "hazard_system", None)
        near_hz, in_hz = _hazard_flags(room, hs, px, py)
        out[32] = near_hz
        out[33] = in_hz

    if p is not None:
        rcd = _safe_float(getattr(p, "reserve_heal_cooldown_timer", 0.0))
        out[34] = _clamp01(rcd / max(RESERVE_HEAL_USE_COOLDOWN_SEC, 1e-6))

    # --- E: Local enemy density (35) — appended Step 2.1 ---
    if p is not None:
        px, py = getattr(p, "world_pos", (0.0, 0.0))
        px, py = _safe_float(px), _safe_float(py)
        local_n = _enemies_within_radius(enemies, px, py, _LOCAL_SWARM_RADIUS_PX)
        out[35] = _clamp01(float(local_n) / max(_MAX_LOCAL_ENEMIES_CAP, 1e-6))

    # Final sanitize
    out = np.nan_to_num(out, nan=0.0, posinf=1.0, neginf=-1.0)
    out = np.clip(out, -1.0, 1.0).astype(np.float32)
    return out
