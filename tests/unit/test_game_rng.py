"""Prompt 37: RNG."""
import pytest
from game.rng import derive_seed, channel_key

def test_same_seed_same_sequence():
    a = derive_seed(42, channel_key("x"))
    b = derive_seed(42, channel_key("x"))
    assert a == b

def test_different_seeds_differ_with_high_probability():
    a = derive_seed(1, channel_key("x"))
    b = derive_seed(2, channel_key("x"))
    assert a != b
