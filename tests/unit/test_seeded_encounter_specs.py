"""Concrete tests for seeded encounter variant behavior and bounds."""

from __future__ import annotations

from dungeon import seeded_encounter_specs as ses
from dungeon.room import RoomType


class Swarm:
    pass


class Flanker:
    pass


class Brute:
    pass


class Heavy:
    pass


class Ranged:
    pass


class MiniBoss:
    pass


class MiniBoss2:
    pass


class Biome3MiniBoss:
    pass


def _names(specs):
    return [row[0].__name__ for row in specs]


def _times(specs):
    return [float(row[2]) for row in specs]


def _assert_staggered_by_slot_delay(specs):
    # Current implementation uses _stagger_specs with SPAWN_SLOT_DELAY_SEC.
    times = _times(specs)
    for i, t in enumerate(times):
        assert t == 0.4 * i


def test_variant_mapping_is_seed_mod_three_deterministic():
    assert ses._variant(0) == 0
    assert ses._variant(1) == 1
    assert ses._variant(2) == 2
    assert ses._variant(3) == 0
    assert ses._variant(42) == 0
    assert ses._variant(43) == 1
    assert ses._variant(44) == 2
    assert ses._variant(42) == ses._variant(42)


def test_biome1_combat_variants_balanced_pressure_spike_are_concrete():
    # Balanced / baseline: v0 => Swarm, Flanker, Brute
    s0 = ses.build_biome1_spawn_specs(0, RoomType.COMBAT, campaign_index=1, seed=0, Swarm=Swarm, Flanker=Flanker, Brute=Brute, MiniBoss=MiniBoss)
    assert _names(s0) == ["Swarm", "Flanker", "Brute"]
    _assert_staggered_by_slot_delay(s0)

    # Combat-heavy / pressure: v1 => Swarm, Flanker (lighter count in current implementation)
    s1 = ses.build_biome1_spawn_specs(0, RoomType.COMBAT, campaign_index=1, seed=1, Swarm=Swarm, Flanker=Flanker, Brute=Brute, MiniBoss=MiniBoss)
    assert _names(s1) == ["Swarm", "Flanker"]
    _assert_staggered_by_slot_delay(s1)

    # Ambush-heavy / spike: v2 => parity-dependent but deterministic and legal.
    s2_even = ses.build_biome1_spawn_specs(0, RoomType.COMBAT, campaign_index=2, seed=2, Swarm=Swarm, Flanker=Flanker, Brute=Brute, MiniBoss=MiniBoss)
    s2_odd = ses.build_biome1_spawn_specs(0, RoomType.COMBAT, campaign_index=3, seed=2, Swarm=Swarm, Flanker=Flanker, Brute=Brute, MiniBoss=MiniBoss)
    assert _names(s2_even) == ["Swarm", "Swarm", "Flanker"]
    assert _names(s2_odd) == ["Swarm", "Flanker", "Brute"]
    _assert_staggered_by_slot_delay(s2_even)
    _assert_staggered_by_slot_delay(s2_odd)


def test_seeded_builders_are_deterministic_for_same_inputs():
    kwargs = dict(
        room_idx=0,
        room_type=RoomType.ELITE,
        campaign_index=11,
        seed=5,
        Swarm=Swarm,
        Flanker=Flanker,
        Brute=Brute,
        Heavy=Heavy,
        Ranged=Ranged,
    )
    a = ses.build_biome3_spawn_specs(MiniBoss=Biome3MiniBoss, **kwargs)
    b = ses.build_biome3_spawn_specs(MiniBoss=Biome3MiniBoss, **kwargs)
    assert a == b


def test_non_combat_room_legality_is_preserved_across_biomes():
    # SAFE must be empty everywhere.
    assert ses.build_biome1_spawn_specs(0, RoomType.SAFE, 0, 0, Swarm, Flanker, Brute, MiniBoss) == []
    assert ses.build_biome2_spawn_specs(0, RoomType.SAFE, 0, 0, Swarm, Flanker, Brute, Heavy, MiniBoss2) == []
    assert ses.build_biome3_spawn_specs(0, RoomType.SAFE, 0, 0, Swarm, Flanker, Brute, Heavy, Ranged, Biome3MiniBoss) == []
    assert ses.build_biome4_spawn_specs(0, RoomType.SAFE, 0, 0, Swarm, Flanker, Brute, Heavy, Ranged) == []

    # Final boss room in biome 4 must be empty (boss handled elsewhere).
    assert ses.build_biome4_spawn_specs(0, RoomType.FINAL_BOSS, 0, 2, Swarm, Flanker, Brute, Heavy, Ranged) == []

    # Mini-boss rows use explicit mini-boss entry where implemented.
    b1_mb = ses.build_biome1_spawn_specs(0, RoomType.MINI_BOSS, 0, 0, Swarm, Flanker, Brute, MiniBoss)
    assert len(b1_mb) == 1 and b1_mb[0][0] is MiniBoss and b1_mb[0][2] == 2.0
    b3_mb = ses.build_biome3_spawn_specs(0, RoomType.MINI_BOSS, 0, 0, Swarm, Flanker, Brute, Heavy, Ranged, Biome3MiniBoss)
    assert len(b3_mb) == 1 and b3_mb[0][0] is Biome3MiniBoss and b3_mb[0][2] == 2.0


def test_biome_enemy_pools_and_count_caps_remain_within_implemented_bounds():
    # Explicitly sample each variant id by seed 0/1/2.
    for seed in (0, 1, 2):
        # Biome 1 bounds (combat-family): 2..3 in current builder, pool swarm/flanker/brute.
        for rt in (RoomType.COMBAT, RoomType.AMBUSH, RoomType.ELITE):
            specs = ses.build_biome1_spawn_specs(0, rt, campaign_index=6, seed=seed, Swarm=Swarm, Flanker=Flanker, Brute=Brute, MiniBoss=MiniBoss)
            names = set(_names(specs))
            assert 2 <= len(specs) <= 3
            assert names <= {"Swarm", "Flanker", "Brute"}

        # Biome 2 bounds: combat 3..4, ambush 3, elite 2..3; includes Heavy.
        b2c = ses.build_biome2_spawn_specs(0, RoomType.COMBAT, 10, seed, Swarm, Flanker, Brute, Heavy, MiniBoss2)
        b2a = ses.build_biome2_spawn_specs(0, RoomType.AMBUSH, 10, seed, Swarm, Flanker, Brute, Heavy, MiniBoss2)
        b2e = ses.build_biome2_spawn_specs(0, RoomType.ELITE, 10, seed, Swarm, Flanker, Brute, Heavy, MiniBoss2)
        assert 3 <= len(b2c) <= 4
        assert len(b2a) == 3
        assert 2 <= len(b2e) <= 3
        assert set(_names(b2c) + _names(b2a) + _names(b2e)) <= {"Swarm", "Flanker", "Brute", "Heavy"}

        # Biome 3 bounds: combat 3..4, ambush 3..4, elite 3; includes Ranged.
        b3c = ses.build_biome3_spawn_specs(0, RoomType.COMBAT, 18, seed, Swarm, Flanker, Brute, Heavy, Ranged, Biome3MiniBoss)
        b3a = ses.build_biome3_spawn_specs(0, RoomType.AMBUSH, 18, seed, Swarm, Flanker, Brute, Heavy, Ranged, Biome3MiniBoss)
        b3e = ses.build_biome3_spawn_specs(0, RoomType.ELITE, 18, seed, Swarm, Flanker, Brute, Heavy, Ranged, Biome3MiniBoss)
        assert 3 <= len(b3c) <= 4
        assert 3 <= len(b3a) <= 4
        assert len(b3e) == 3
        assert set(_names(b3c) + _names(b3a) + _names(b3e)) <= {"Swarm", "Flanker", "Brute", "Heavy", "Ranged"}

        # Biome 4 bounds: combat 3..4, ambush 3..4, elite 2..3; includes Ranged/Heavy.
        b4c = ses.build_biome4_spawn_specs(0, RoomType.COMBAT, 26, seed, Swarm, Flanker, Brute, Heavy, Ranged)
        b4a = ses.build_biome4_spawn_specs(0, RoomType.AMBUSH, 26, seed, Swarm, Flanker, Brute, Heavy, Ranged)
        b4e = ses.build_biome4_spawn_specs(0, RoomType.ELITE, 26, seed, Swarm, Flanker, Brute, Heavy, Ranged)
        assert 3 <= len(b4c) <= 4
        assert 3 <= len(b4a) <= 4
        assert 2 <= len(b4e) <= 3
        assert set(_names(b4c) + _names(b4a) + _names(b4e)) <= {"Swarm", "Flanker", "Brute", "Heavy", "Ranged"}
