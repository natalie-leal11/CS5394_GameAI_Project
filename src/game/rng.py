# Central seeded RNG for AI-side and future seed-controlled variation (Phases 0–1).
# Existing dungeon/spawn code continues using config.SEED + local random.Random until later phases.
# All new AI Director / Player Model randomness must use this module only.

from __future__ import annotations

import random
import time
from typing import Sequence, TypeVar
from game.config import SEED

_T = TypeVar("_T")

# Global run seed (set at run start / reset from game config).
_run_seed: int = int(SEED)
TOTAL_SEED_VARIANTS: int = 3
_variant_id: int = int(SEED) % TOTAL_SEED_VARIANTS


def initialize_run_seed(raw_seed: int | None = None) -> int:
    """
    Initialize one run seed at run start.
    If raw_seed is omitted, use system time in milliseconds per seed_determinism.md.
    """
    if raw_seed is None:
        raw_seed = int(time.time() * 1000)
    set_run_seed(int(raw_seed))
    return int(_run_seed)


def set_run_seed(seed: int) -> None:
    """Initialize the AI/run RNG stream from the same source as procedural dungeon SEED."""
    global _run_seed, _variant_id
    _run_seed = int(seed)
    _variant_id = int(_run_seed) % TOTAL_SEED_VARIANTS


def get_run_seed() -> int:
    return int(_run_seed)


def get_variant_id() -> int:
    return int(_variant_id)


def derive_seed(*parts: int) -> int:
    """
    Deterministically mix integer parts into a 32-bit non-negative seed for random.Random.
    Same parts → same output on all platforms.
    """
    x = 0x9E3779B9
    for p in parts:
        x ^= int(p) & 0xFFFFFFFF
        x = (x * 0x01000193) & 0xFFFFFFFF
    x ^= (len(parts) * 0x85EBCA6B) & 0xFFFFFFFF
    return x if x != 0 else 0x1A2B3C4D


def _channel_key(channel: str) -> int:
    h = 2166136261
    for c in channel:
        h ^= ord(c)
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def channel_key(channel: str) -> int:
    """Stable string → int for derive_seed (same input → same int on all runs)."""
    return _channel_key(channel)


def get_stream(name: str, offset: int = 0) -> random.Random:
    """Named global stream derived from run seed (AI systems not tied to a single room)."""
    return random.Random(derive_seed(_run_seed, _channel_key(name), int(offset)))


def make_room_rng(room_index: int, channel: str, biome_index: int = 1) -> random.Random:
    """
    Per-room deterministic stream: same run seed + biome + campaign room index + channel → identical draws.
    `biome_index` should match `Room.biome_index` (1–4) when available.
    """
    return random.Random(
        derive_seed(
            _run_seed,
            int(biome_index) & 0xFFFF,
            int(room_index) & 0xFFFF,
            _channel_key(channel),
        )
    )


def sample_seeded_choice(
    seq: Sequence[_T],
    room_index: int,
    channel: str,
    biome_index: int = 1,
) -> _T:
    if not seq:
        raise ValueError("sample_seeded_choice: empty sequence")
    rng = make_room_rng(room_index, channel, biome_index)
    return rng.choice(seq)


def sample_seeded_shuffle(
    seq: Sequence[_T],
    room_index: int,
    channel: str,
    biome_index: int = 1,
) -> list[_T]:
    rng = make_room_rng(room_index, channel, biome_index)
    out = list(seq)
    rng.shuffle(out)
    return out


def sample_seeded_uniform(
    a: float,
    b: float,
    room_index: int,
    channel: str,
    biome_index: int = 1,
) -> float:
    rng = make_room_rng(room_index, channel, biome_index)
    return rng.uniform(a, b)


def sample_seeded_int(
    a: int,
    b: int,
    room_index: int,
    channel: str,
    biome_index: int = 1,
) -> int:
    rng = make_room_rng(room_index, channel, biome_index)
    return rng.randint(a, b)
