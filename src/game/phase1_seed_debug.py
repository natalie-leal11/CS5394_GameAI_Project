"""
Deterministic seed verification logger.

Creates one file per run:
  logs/seed_run_<timestamp>.txt
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

PHASE1_SEED_DEBUG_ENABLED: bool = True

_ACTIVE_LOG_PATH: Path | None = None
_RUN_TIMESTAMP: str | None = None
_ROOM_LOGGED_ONCE: set[int] = set()


def _enabled() -> bool:
    if not PHASE1_SEED_DEBUG_ENABLED:
        return False
    return os.environ.get("PHASE1_SEED_DEBUG", "1").strip().lower() not in ("0", "false", "no", "off")


def _project_logs_dir() -> Path:
    from game.config import PROJECT_ROOT

    return Path(PROJECT_ROOT) / "logs"


def _new_run_path() -> Path:
    global _RUN_TIMESTAMP
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    _RUN_TIMESTAMP = ts
    logs = _project_logs_dir()
    logs.mkdir(parents=True, exist_ok=True)
    base = logs / f"seed_run_{ts}.txt"
    if not base.exists():
        return base
    # If restarted within same second, make deterministic suffix.
    i = 1
    while True:
        p = logs / f"seed_run_{ts}_{i}.txt"
        if not p.exists():
            return p
        i += 1


def _ensure_active_log() -> Path:
    global _ACTIVE_LOG_PATH
    if _ACTIVE_LOG_PATH is None:
        _ACTIVE_LOG_PATH = _new_run_path()
    return _ACTIVE_LOG_PATH


def _write(lines: list[str]) -> None:
    if not _enabled():
        return
    p = _ensure_active_log()
    with p.open("a", encoding="utf-8", newline="\n") as f:
        for ln in lines:
            f.write(ln.rstrip("\n") + "\n")


def _biome_orders(seed: int) -> dict[int, list[str]]:
    from game.config import (
        USE_BIOME2,
        USE_BIOME3,
        USE_BIOME4,
    )
    from dungeon.srs_biome_order import (
        room_order_biome1_srs,
        room_order_biome2_srs,
        room_order_biome3_srs,
        room_order_biome4_srs,
    )

    out = {1: [x.value for x in room_order_biome1_srs(seed)]}
    if USE_BIOME2:
        out[2] = [x.value for x in room_order_biome2_srs(seed)]
    if USE_BIOME3:
        out[3] = [x.value for x in room_order_biome3_srs(seed)]
    if USE_BIOME4:
        out[4] = [x.value for x in room_order_biome4_srs(seed)]
    return out


def _safe_idx(order: list[str]) -> int:
    try:
        return order.index("SAFE")
    except ValueError:
        return -1


def _door_positions_for_room(room: Any) -> list[tuple[float, float]]:
    from dungeon.room_controller import _place_doors_for_room
    from game.config import TILE_SIZE

    doors = _place_doors_for_room(room)
    by_target: dict[int, list[Any]] = {}
    for d in doors:
        t = int(getattr(d, "target_room_index", -1))
        by_target.setdefault(t, []).append(d)
    out: list[tuple[float, float]] = []
    for _target, group in by_target.items():
        txs = [int(g.tile_x) for g in group]
        tys = [int(g.tile_y) for g in group]
        min_tx, max_tx = min(txs), max(txs)
        min_ty, max_ty = min(tys), max(tys)
        cx = (min_tx + max_tx + 1) / 2.0 * TILE_SIZE
        cy = (min_ty + max_ty + 1) / 2.0 * TILE_SIZE
        out.append((cx, cy))
    return out


def _spawn_specs_for_room(room_index: int, room_type: Any, run_seed: int) -> tuple[list[tuple[Any, bool, float, Any]], str]:
    from dungeon.room import RoomType
    from game.config import BIOME3_START_INDEX, BIOME4_START_INDEX
    from entities.swarm import Swarm
    from entities.flanker import Flanker
    from entities.brute import Brute
    from entities.heavy import Heavy
    from entities.ranged import Ranged
    from entities.mini_boss import MiniBoss
    from entities.mini_boss_2 import MiniBoss2
    from entities.biome3_miniboss import Biome3MiniBoss
    from dungeon.biome1_rooms import get_biome1_spawn_specs, get_biome1_spawn_pattern
    from dungeon.biome2_rooms import get_biome2_spawn_specs, get_biome2_spawn_pattern
    from dungeon.biome3_rooms import get_biome3_spawn_specs, get_biome3_spawn_pattern
    from dungeon.biome4_rooms import get_biome4_spawn_specs, get_biome4_spawn_pattern

    rtype = room_type if isinstance(room_type, RoomType) else RoomType(str(room_type))
    if room_index >= BIOME4_START_INDEX:
        specs = get_biome4_spawn_specs(
            room_index - BIOME4_START_INDEX, rtype, Swarm, Flanker, Brute, Heavy, Ranged, seed=run_seed
        )
        pat = get_biome4_spawn_pattern(rtype)
        return specs, f"biome4:{pat}" if pat else "none"
    if room_index >= BIOME3_START_INDEX:
        specs = get_biome3_spawn_specs(
            room_index - BIOME3_START_INDEX, rtype, Swarm, Flanker, Brute, Heavy, Ranged, Biome3MiniBoss, seed=run_seed
        )
        pat = get_biome3_spawn_pattern(rtype)
        return specs, f"biome3:{pat}" if pat else "none"
    if room_index >= 8:
        specs = get_biome2_spawn_specs(
            room_index - 8, rtype, Swarm, Flanker, Brute, Heavy, MiniBoss2, seed=run_seed
        )
        pat = get_biome2_spawn_pattern(rtype)
        return specs, f"biome2:{pat}" if pat else "none"

    specs = get_biome1_spawn_specs(room_index, rtype, Swarm, Flanker, Brute, MiniBoss, seed=run_seed)
    pat = get_biome1_spawn_pattern(rtype)
    return specs, f"biome1:{pat}" if pat else "none"


def _spawn_positions_for_room(room: Any, room_index: int, spawn_specs: list[tuple[Any, bool, float, Any]], pattern: str, run_seed: int) -> list[tuple[float, float]]:
    import random
    from dungeon.room import RoomType
    from systems.spawn_helper import (
        generate_valid_spawn_position,
        spawn_ambush,
        spawn_spread,
        spawn_triangle,
    )
    from dungeon.biome4_rooms import BIOME4_AMBUSH_RADIUS_PX, BIOME4_TRIANGLE_OFFSET_PX
    from game.config import BIOME3_START_INDEX, BIOME4_START_INDEX

    if not spawn_specs:
        return []
    player_center = room.world_pos_for_tile(room.spawn_tile[0], room.spawn_tile[1])
    rng = random.Random(int(run_seed) + int(room.room_index) * 10000)
    doors = _door_positions_for_room(room)
    rtype = room.room_type

    if room_index >= BIOME4_START_INDEX:
        if "triangle" in pattern:
            return spawn_triangle(room, player_center, is_elite=True, rng=rng, door_positions=doors, offset_px=BIOME4_TRIANGLE_OFFSET_PX)
        if "ambush" in pattern:
            return spawn_ambush(room, player_center, len(spawn_specs), rng=rng, radius_px=BIOME4_AMBUSH_RADIUS_PX)
        if "spread" in pattern:
            return spawn_spread(room, player_center, len(spawn_specs), is_elite=(rtype == RoomType.ELITE), rng=rng, door_positions=doors)
        return []
    if room_index >= BIOME3_START_INDEX:
        if "triangle" in pattern:
            return spawn_triangle(room, player_center, is_elite=True, rng=rng, door_positions=doors)
        if "ambush" in pattern:
            return spawn_ambush(room, player_center, len(spawn_specs), rng=rng)
        if "single" in pattern:
            return [generate_valid_spawn_position(room, player_center, [], is_elite=False, rng=rng)]
        if "spread" in pattern:
            return spawn_spread(room, player_center, len(spawn_specs), is_elite=(rtype == RoomType.ELITE), rng=rng, door_positions=doors)
        return []
    if room_index >= 8:
        if "triangle" in pattern:
            return spawn_triangle(room, player_center, is_elite=True, rng=rng, door_positions=doors)
        if "ambush" in pattern:
            return spawn_ambush(room, player_center, len(spawn_specs), rng=rng)
        if "single" in pattern:
            out: list[tuple[float, float]] = []
            for _ in spawn_specs:
                out.append(generate_valid_spawn_position(room, player_center, out, is_elite=False, rng=rng))
            return out
        if "spread" in pattern:
            return spawn_spread(room, player_center, len(spawn_specs), is_elite=(rtype == RoomType.ELITE), rng=rng, door_positions=doors)
        return []
    # Biome 1
    if "triangle" in pattern:
        return spawn_triangle(room, player_center, is_elite=True, rng=rng, door_positions=doors)
    if "ambush" in pattern:
        return spawn_ambush(room, player_center, len(spawn_specs), rng=rng)
    if "single" in pattern:
        return [generate_valid_spawn_position(room, player_center, [], is_elite=False, rng=rng)]
    if "spread" in pattern:
        return spawn_spread(room, player_center, len(spawn_specs), is_elite=False, rng=rng, door_positions=doors)
    return []


def _log_projected_all_rooms(run_seed: int) -> None:
    from dungeon.room import generate_room, total_campaign_rooms, TILE_LAVA, TILE_SLOW

    global _ROOM_LOGGED_ONCE
    lines: list[str] = ["=== PROJECTED FULL RUN (ALL ROOMS) ==="]
    total = total_campaign_rooms()
    _ROOM_LOGGED_ONCE = set()
    for room_index in range(total):
        room = generate_room(room_index, run_seed)
        specs, pattern = _spawn_specs_for_room(room_index, room.room_type, run_seed)
        positions = _spawn_positions_for_room(room, room_index, specs, pattern, run_seed)
        lava = sum(row.count(TILE_LAVA) for row in room.tile_grid)
        slow = sum(row.count(TILE_SLOW) for row in room.tile_grid)
        hazard_pct = float(getattr(room, "hazard_percentage", 0.0))

        lines.extend(
            [
                "=== ROOM DETAIL ===",
                f"room_index: {room_index}",
                f"biome_index: {int(room.biome_index)}",
                f"room_type: {room.room_type.value}",
            ]
        )

        if room.room_type.value == "SAFE":
            lines.extend(
                [
                    "enemy_count: 0",
                    "enemy_types: []",
                    "spawn_details: []",
                ]
            )
        elif room.room_type.value == "FINAL_BOSS":
            lines.extend(
                [
                    "boss_type: FinalBoss",
                    "enemy_count: 1",
                    "enemy_types: [FinalBoss]",
                    "spawn_details: []",
                    "(no seed-controlled changes)",
                ]
            )
        elif room.room_type.value == "MINI_BOSS":
            boss_type = specs[0][0].__name__ if specs else "MiniBoss"
            add_types = [s[0].__name__ for s in specs[1:]] if len(specs) > 1 else []
            lines.extend(
                [
                    f"boss_type: {boss_type}",
                    "adds:",
                    f"  - count: {max(0, len(specs) - 1)}",
                    f"  - types: {add_types}",
                ]
            )
        else:
            enemy_types = [s[0].__name__ for s in specs]
            lines.extend(
                [
                    f"spawn_pattern: {pattern}",
                    f"enemy_count: {len(specs)}",
                    f"enemy_types: {enemy_types}",
                    "spawn_details:",
                ]
            )
            for i, spec in enumerate(specs):
                cls, elite, start_t, _tele = spec
                pos = positions[i] if i < len(positions) else (-1.0, -1.0)
                lines.extend(
                    [
                        f"  - enemy_type: {cls.__name__}",
                        f"    is_elite: {elite}",
                        f"    spawn_time: {float(start_t):.1f}",
                        f"    spawn_position (x,y): ({pos[0]:.2f}, {pos[1]:.2f})",
                    ]
                )

        lines.extend(
            [
                "",
                "=== HAZARDS ===",
                f"room_index: {room_index}",
                f"lava_tiles: {lava}",
                f"slow_tiles: {slow}",
                f"hazard_pct: {hazard_pct:.6f}",
                "",
                "=== RNG ===",
                f"room_index: {room_index}",
                f"base_seed: {run_seed}",
                f"derived_spawn_seed: {run_seed + room_index * 10000}",
                "derived_hazard_seed: N/A (hazards deterministic by biome_index + room_type)",
                "",
            ]
        )
        _ROOM_LOGGED_ONCE.add(int(room_index))
    _write(lines)


def log_phase1_app_launch() -> None:
    # Keep hook; no output until a run starts.
    return


def log_run_start(procedural_seed: int) -> None:
    if not _enabled():
        return
    global _ACTIVE_LOG_PATH, _ROOM_LOGGED_ONCE
    _ACTIVE_LOG_PATH = _new_run_path()
    _ROOM_LOGGED_ONCE = set()

    from game.rng import get_run_seed, get_variant_id
    from game.config import (
        BIOME2_START_INDEX,
        BIOME3_START_INDEX,
        BIOME4_START_INDEX,
    )

    run_seed = int(get_run_seed())
    variant_id = int(get_variant_id())
    now = datetime.now().isoformat(timespec="seconds")
    orders = _biome_orders(int(procedural_seed))

    lines: list[str] = [
        "=== RUN START ===",
        f"timestamp: {now}",
        f"run_seed: {run_seed}",
        f"variant_id (run_seed % 3): {variant_id}",
        f"log_file: {_ACTIVE_LOG_PATH.resolve()}",
        "",
        "=== DUNGEON STRUCTURE ===",
        "fixed rooms:",
        "  START = 0",
        "  MINI_BOSS = 7, 15, 23",
        "  FINAL_BOSS = 29",
        "",
    ]

    b1 = orders.get(1, [])
    lines.extend(
        [
            "Biome 1:",
            "  room indices: 0–7",
            f"  SAFE room index: {_safe_idx(b1)}",
            f"  room order: {b1}",
            "",
        ]
    )
    if 2 in orders:
        b2 = orders[2]
        lines.extend(
            [
                "Biome 2:",
                f"  room indices: {BIOME2_START_INDEX}–{BIOME3_START_INDEX - 1}",
                f"  SAFE room index: {BIOME2_START_INDEX + _safe_idx(b2)}",
                f"  room order: {b2}",
                "",
            ]
        )
    if 3 in orders:
        b3 = orders[3]
        lines.extend(
            [
                "Biome 3:",
                f"  room indices: {BIOME3_START_INDEX}–{BIOME4_START_INDEX - 1}",
                f"  SAFE room index: {BIOME3_START_INDEX + _safe_idx(b3)}",
                f"  room order: {b3}",
                "",
            ]
        )
    if 4 in orders:
        b4 = orders[4]
        lines.extend(
            [
                "Biome 4:",
                f"  room indices: {BIOME4_START_INDEX}–29",
                f"  SAFE room index: {BIOME4_START_INDEX + _safe_idx(b4)}",
                f"  room order: {b4}",
                "",
            ]
        )

    lines.extend(
        [
            "=== DETERMINISM CHECK HELPER ===",
            "Compare two run files manually:",
            "  - same run_seed -> files should match except timestamp/file path",
            "  - different run_seed -> only seed-controlled sections should differ",
            "",
        ]
    )
    _write(lines)
    _log_projected_all_rooms(run_seed)


def log_room_loaded(campaign_index: int, room: Any, controller_seed: int) -> None:
    if not _enabled():
        return
    if int(campaign_index) in _ROOM_LOGGED_ONCE:
        return
    from dungeon.room import TILE_LAVA, TILE_SLOW
    from game.rng import get_run_seed

    lava = sum(row.count(TILE_LAVA) for row in room.tile_grid)
    slow = sum(row.count(TILE_SLOW) for row in room.tile_grid)
    hazard_pct = float(getattr(room, "hazard_percentage", 0.0))
    base_seed = int(get_run_seed())
    derived_spawn_seed = base_seed + int(campaign_index) * 10000

    lines = [
        "=== ROOM DETAIL ===",
        f"room_index: {campaign_index}",
        f"biome_index: {room.biome_index}",
        f"room_type: {room.room_type.value}",
        "",
        "=== HAZARDS ===",
        f"room_index: {campaign_index}",
        f"lava_tiles: {lava}",
        f"slow_tiles: {slow}",
        f"hazard_pct: {hazard_pct:.6f}",
        "",
        "=== RNG ===",
        f"room_index: {campaign_index}",
        f"base_seed: {base_seed}",
        f"derived_spawn_seed: {derived_spawn_seed}",
        "derived_hazard_seed: N/A (hazards deterministic by biome_index + room_type)",
        "",
    ]
    _write(lines)


def log_spawn_setup(
    *,
    procedural_seed: int,
    room_index: int,
    room_type_name: str,
    biome_index: int,
    spawn_legacy_seed: int,
    spawn_specs_summary: list[str],
    positions_world: list[tuple[float, float]],
    spawn_pattern_label: str,
    room: Any | None = None,
    player_center_world: tuple[float, float] | None = None,
    spawn_specs: list[tuple[Any, bool, float, Any]] | None = None,
) -> None:
    if not _enabled():
        return
    if int(room_index) in _ROOM_LOGGED_ONCE:
        return

    specs = spawn_specs or []
    enemy_types = [s[0].__name__ for s in specs]
    enemy_count = len(specs)
    lines: list[str] = []

    if room_type_name == "SAFE":
        lines.extend(
            [
                "=== ROOM DETAIL ===",
                f"room_index: {room_index}",
                f"biome_index: {biome_index}",
                "room_type: SAFE",
                "enemy_count: 0",
                "enemy_types: []",
                "spawn_details: []",
                "",
            ]
        )
        _write(lines)
        return

    if room_type_name in ("COMBAT", "AMBUSH", "ELITE", "START"):
        lines.extend(
            [
                "=== ROOM DETAIL ===",
                f"room_index: {room_index}",
                f"biome_index: {biome_index}",
                f"room_type: {room_type_name}",
                f"spawn_pattern: {spawn_pattern_label}",
                f"enemy_count: {enemy_count}",
                f"enemy_types: {enemy_types}",
                "spawn_details:",
            ]
        )
        for i, spec in enumerate(specs):
            cls, elite, start_t, _tele = spec
            pos = positions_world[i] if i < len(positions_world) else (-1.0, -1.0)
            lines.extend(
                [
                    f"  - enemy_type: {cls.__name__}",
                    f"    is_elite: {elite}",
                    f"    spawn_time: {float(start_t):.1f}",
                    f"    spawn_position (x,y): ({pos[0]:.2f}, {pos[1]:.2f})",
                ]
            )
        lines.extend(
            [
                "",
                "=== RNG ===",
                f"room_index: {room_index}",
                f"base_seed: {procedural_seed}",
                f"derived_spawn_seed: {spawn_legacy_seed}",
                "derived_hazard_seed: N/A (hazards deterministic by biome_index + room_type)",
                "",
            ]
        )
        _write(lines)
        return

    if room_type_name == "MINI_BOSS":
        boss_type = specs[0][0].__name__ if specs else "MiniBoss"
        adds = specs[1:] if len(specs) > 1 else []
        add_types = [a[0].__name__ for a in adds]
        lines.extend(
            [
                "=== ROOM DETAIL ===",
                f"room_index: {room_index}",
                f"biome_index: {biome_index}",
                "room_type: MINI_BOSS",
                f"boss_type: {boss_type}",
                "adds:",
                f"  - count: {len(adds)}",
                f"  - types: {add_types}",
                f"spawn_pattern: {spawn_pattern_label}",
                f"spawn_count: {enemy_count}",
                "",
            ]
        )
        _write(lines)
        return

    if room_type_name == "FINAL_BOSS":
        lines.extend(
            [
                "=== ROOM DETAIL ===",
                f"room_index: {room_index}",
                f"biome_index: {biome_index}",
                "room_type: FINAL_BOSS",
                "boss_type: FinalBoss",
                "enemy_count: 1",
                "enemy_types: [FinalBoss]",
                "spawn_details: []",
                "(no seed-controlled changes)",
                "",
            ]
        )
        _write(lines)


def log_spawn_skipped(reason: str, *, procedural_seed: int) -> None:
    if not _enabled():
        return
    _write(
        [
            "=== ROOM DETAIL ===",
            f"spawn_skipped_reason: {reason}",
            f"base_seed: {procedural_seed}",
            "",
        ]
    )


def log_end_run_summary() -> None:
    if not _enabled():
        return
    _write(
        [
            "=== RUN END ===",
            f"timestamp: {datetime.now().isoformat(timespec='seconds')}",
            "",
        ]
    )
