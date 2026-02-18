"""
Centralized RNG. No other file may import or use Python's random module.
All game randomness must go through this module.
"""
import random

_rng: random.Random = random.Random()


def set_seed(seed: int) -> None:
    """Set the global seed for reproducible runs."""
    _rng.seed(seed)


def randint(a: int, b: int) -> int:
    """Return random integer N such that a <= N <= b."""
    return _rng.randint(a, b)


def choice(seq):
    """Return a random element from non-empty sequence seq."""
    return _rng.choice(seq)


def shuffle(seq) -> None:
    """Shuffle sequence in place."""
    _rng.shuffle(seq)
