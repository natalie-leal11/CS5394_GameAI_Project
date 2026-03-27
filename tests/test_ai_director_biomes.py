"""
AI Director + biome-specific spawn helpers (Biomes 1–4).

Pure logic / determinism tests; no GameScene or full combat loop.
"""

from __future__ import annotations

import pytest

from dungeon.room import RoomType
from game.ai.ai_director import AIDirector
from game.ai.biome1_director_spawn import (
    adjust_biome1_spawn_specs,
    biome1_director_spawn_eligible,
    biome1_effective_heal_drop_chance,
)
from game.ai.biome2_director_spawn import (
    adjust_biome2_spawn_specs,
    biome2_director_spawn_eligible,
    biome2_effective_heal_drop_chance,
    biome2_safe_room_heal_multiplier,
    biome2_spawn_pattern_params,
)
from game.ai.biome3_director_spawn import (
    adjust_biome3_spawn_specs,
    apply_biome3_ranged_position_offsets,
    biome3_director_spawn_eligible,
    biome3_effective_heal_drop_chance,
    biome3_safe_room_heal_multiplier,
    biome3_spawn_pattern_params,
)
from game.ai.biome4_director_spawn import (
    adjust_biome4_spawn_specs,
    biome4_director_spawn_eligible,
    biome4_effective_heal_drop_chance,
    biome4_pacing_spacing_mult,
    biome4_safe_room_heal_multiplier,
    biome4_spawn_pattern_params,
)
from game.ai.metrics_tracker import MetricsTracker
from game.ai.player_model import PlayerStateClass
from game.config import BIOME3_START_INDEX, BIOME4_START_INDEX


# Distinct stand-ins for spawn spec rows (identity matters for composition logic).
class Swarm:
    __name__ = "Swarm"


class Flanker:
    __name__ = "Flanker"


class Brute:
    __name__ = "Brute"


class Heavy:
    __name__ = "Heavy"


class Ranged:
    __name__ = "Ranged"


class MiniBoss2:
    __name__ = "MiniBoss2"


class Biome3MiniBoss:
    __name__ = "Biome3MiniBoss"


def _freeze_specs(specs: list) -> list[tuple]:
    """Normalize for stable equality checks."""
    out = []
    for row in specs:
        cls, elite, t, tele = row
        name = getattr(cls, "__name__", str(cls))
        out.append((name, bool(elite), round(float(t), 6), tele))
    return out


# ---------------------------------------------------------------------------
# AIDirector: player state -> all biome outputs
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "state, exp",
    [
        (
            PlayerStateClass.STRUGGLING,
            dict(
                difficulty_modifier=0.85,
                enemy_adjustment=-1,
                reinforcement_chance=0.0,
                composition_bias="lighter",
                pressure_level="low",
                composition_bias_b2="lighter",
                reinforcement_chance_b2=0.05,
                hazard_tune_factor_b2=0.88,
                composition_bias_b3="safe",
                ranged_bias_b3="low",
                reinforcement_chance_b3=0.05,
                hazard_tune_factor_b3=0.85,
                composition_bias_b4="safe",
                boss_pressure="low",
                pacing_bias="relaxed",
                reinforcement_chance_b4=0.05,
                hazard_tune_factor_b4=0.85,
            ),
        ),
        (
            PlayerStateClass.STABLE,
            dict(
                difficulty_modifier=1.0,
                enemy_adjustment=0,
                reinforcement_chance=0.1,
                composition_bias="normal",
                pressure_level="medium",
                composition_bias_b2="balanced",
                reinforcement_chance_b2=0.15,
                hazard_tune_factor_b2=1.0,
                composition_bias_b3="balanced",
                ranged_bias_b3="medium",
                reinforcement_chance_b3=0.15,
                hazard_tune_factor_b3=1.0,
                composition_bias_b4="balanced",
                boss_pressure="medium",
                pacing_bias="normal",
                reinforcement_chance_b4=0.15,
                hazard_tune_factor_b4=1.0,
            ),
        ),
        (
            PlayerStateClass.DOMINATING,
            dict(
                difficulty_modifier=1.15,
                enemy_adjustment=1,
                reinforcement_chance=0.3,
                composition_bias="harder",
                pressure_level="high",
                composition_bias_b2="aggressive",
                reinforcement_chance_b2=0.35,
                hazard_tune_factor_b2=1.12,
                composition_bias_b3="aggressive",
                ranged_bias_b3="high",
                reinforcement_chance_b3=0.35,
                hazard_tune_factor_b3=1.15,
                composition_bias_b4="aggressive",
                boss_pressure="high",
                pacing_bias="intense",
                reinforcement_chance_b4=0.35,
                hazard_tune_factor_b4=1.15,
            ),
        ),
    ],
)
def test_ai_director_update_maps_player_state_to_all_biomes(state, exp):
    d = AIDirector()
    d.update(state)
    for key, val in exp.items():
        assert getattr(d, key) == val, f"{key}: expected {val}, got {getattr(d, key)}"
    assert d.last_player_state_name == state.name


def test_ai_director_none_like_stable_without_stable_label():
    d = AIDirector()
    d.update(None)
    assert d.difficulty_modifier == 1.0
    assert d.reinforcement_chance_b3 == 0.15
    assert d.last_player_state_name is None


def test_ai_director_biome_debug_helpers_match_fields():
    d = AIDirector()
    d.update(PlayerStateClass.DOMINATING)
    b1 = d.get_biome1_debug()
    assert b1["composition_bias"] == "harder"
    assert b1["reinforcement_chance"] == 0.3
    b2 = d.get_biome2_debug()
    assert b2["composition_bias"] == "aggressive"
    assert b2["reinforcement_chance"] == 0.35
    b3 = d.get_biome3_debug()
    assert b3["composition_bias"] == "aggressive"
    assert b3["ranged_bias"] == "high"
    assert b3["hazard_bias"] == 1.15
    b4 = d.get_biome4_debug()
    assert b4["boss_pressure"] == "high"
    assert b4["pacing_bias"] == "intense"
    assert b4["hazard_tune_factor_b4"] == 1.15


# ---------------------------------------------------------------------------
# Eligibility (Biomes 1–4)
# ---------------------------------------------------------------------------


def test_biome1_spawn_eligible_only_campaign_0_7_combat_biome1():
    assert biome1_director_spawn_eligible(
        room_idx=3, biome_index=1, room_type=RoomType.COMBAT, beginner_test_mode=False
    )
    assert not biome1_director_spawn_eligible(
        room_idx=8, biome_index=1, room_type=RoomType.COMBAT, beginner_test_mode=False
    )
    assert not biome1_director_spawn_eligible(
        room_idx=3, biome_index=2, room_type=RoomType.COMBAT, beginner_test_mode=False
    )
    assert not biome1_director_spawn_eligible(
        room_idx=3, biome_index=1, room_type=RoomType.SAFE, beginner_test_mode=False
    )
    assert not biome1_director_spawn_eligible(
        room_idx=3, biome_index=1, room_type=RoomType.COMBAT, beginner_test_mode=True
    )


def test_biome2_spawn_eligible_rooms_8_to_15_biome2_only():
    assert biome2_director_spawn_eligible(
        room_idx=8, biome_index=2, room_type=RoomType.COMBAT, beginner_test_mode=False
    )
    assert biome2_director_spawn_eligible(
        room_idx=15, biome_index=2, room_type=RoomType.ELITE, beginner_test_mode=False
    )
    assert not biome2_director_spawn_eligible(
        room_idx=7, biome_index=2, room_type=RoomType.COMBAT, beginner_test_mode=False
    )
    assert not biome2_director_spawn_eligible(
        room_idx=16, biome_index=2, room_type=RoomType.COMBAT, beginner_test_mode=False
    )
    assert not biome2_director_spawn_eligible(
        room_idx=10, biome_index=3, room_type=RoomType.COMBAT, beginner_test_mode=False
    )


def test_biome3_spawn_eligible_rooms_16_to_23_biome3_combat_family():
    assert biome3_director_spawn_eligible(
        room_idx=BIOME3_START_INDEX,
        biome_index=3,
        room_type=RoomType.COMBAT,
        beginner_test_mode=False,
    )
    assert not biome3_director_spawn_eligible(
        room_idx=BIOME3_START_INDEX,
        biome_index=3,
        room_type=RoomType.MINI_BOSS,
        beginner_test_mode=False,
    )
    assert not biome3_director_spawn_eligible(
        room_idx=BIOME4_START_INDEX,
        biome_index=3,
        room_type=RoomType.COMBAT,
        beginner_test_mode=False,
    )
    assert not biome3_director_spawn_eligible(
        room_idx=20, biome_index=2, room_type=RoomType.COMBAT, beginner_test_mode=False
    )


def test_biome4_spawn_eligible_rooms_24_to_28_not_final_boss():
    assert biome4_director_spawn_eligible(
        room_idx=BIOME4_START_INDEX,
        biome_index=4,
        room_type=RoomType.COMBAT,
        beginner_test_mode=False,
    )
    assert biome4_director_spawn_eligible(
        room_idx=28, biome_index=4, room_type=RoomType.ELITE, beginner_test_mode=False
    )
    assert not biome4_director_spawn_eligible(
        room_idx=29, biome_index=4, room_type=RoomType.COMBAT, beginner_test_mode=False
    )
    assert not biome4_director_spawn_eligible(
        room_idx=26, biome_index=3, room_type=RoomType.COMBAT, beginner_test_mode=False
    )


# ---------------------------------------------------------------------------
# Deterministic spawn adjustments
# ---------------------------------------------------------------------------


def test_biome1_adjust_spawn_specs_deterministic():
    base = [
        (Swarm, False, 0.0, None),
        (Flanker, False, 0.4, None),
        (Brute, False, 0.8, None),
    ]
    a = adjust_biome1_spawn_specs(
        list(base),
        room_type=RoomType.COMBAT,
        room_idx=2,
        biome_index=1,
        difficulty_modifier=1.0,
        enemy_adjustment=0,
        reinforcement_chance=0.5,
        composition_bias="normal",
        Swarm=Swarm,
        Flanker=Flanker,
        Brute=Brute,
    )
    b = adjust_biome1_spawn_specs(
        list(base),
        room_type=RoomType.COMBAT,
        room_idx=2,
        biome_index=1,
        difficulty_modifier=1.0,
        enemy_adjustment=0,
        reinforcement_chance=0.5,
        composition_bias="normal",
        Swarm=Swarm,
        Flanker=Flanker,
        Brute=Brute,
    )
    assert _freeze_specs(a) == _freeze_specs(b)


def test_biome2_adjust_spawn_specs_deterministic():
    base = [
        (Swarm, False, 0.0, None),
        (Heavy, False, 0.4, None),
        (Flanker, False, 0.8, None),
    ]
    kwargs = dict(
        room_type=RoomType.COMBAT,
        room_idx=10,
        biome_index=2,
        difficulty_modifier=1.0,
        enemy_adjustment=0,
        reinforcement_chance_b2=0.0,
        pressure_level="medium",
        composition_bias_b2="balanced",
        player_state_name="STABLE",
        Swarm=Swarm,
        Flanker=Flanker,
        Brute=Brute,
        Heavy=Heavy,
    )
    a, m1 = adjust_biome2_spawn_specs(list(base), **kwargs)
    b, m2 = adjust_biome2_spawn_specs(list(base), **kwargs)
    assert _freeze_specs(a) == _freeze_specs(b)
    assert m1 == m2


def test_biome3_adjust_spawn_specs_deterministic():
    base = [
        (Swarm, False, 0.0, None),
        (Ranged, False, 0.4, None),
        (Brute, False, 0.8, None),
    ]
    kwargs = dict(
        room_type=RoomType.COMBAT,
        room_idx=18,
        biome_index=3,
        difficulty_modifier=1.0,
        enemy_adjustment=0,
        reinforcement_chance_b3=0.0,
        pressure_level="medium",
        composition_bias_b3="balanced",
        ranged_bias_b3="medium",
        player_state_name="STABLE",
        hazard_tune_factor=1.0,
        Swarm=Swarm,
        Flanker=Flanker,
        Brute=Brute,
        Heavy=Heavy,
        Ranged=Ranged,
    )
    a, m1 = adjust_biome3_spawn_specs(list(base), **kwargs)
    b, m2 = adjust_biome3_spawn_specs(list(base), **kwargs)
    assert _freeze_specs(a) == _freeze_specs(b)
    assert m1 == m2
    assert "hazard_tune_effective" in m1


def test_biome4_adjust_spawn_specs_deterministic():
    base = [
        (Swarm, False, 0.0, None),
        (Heavy, False, 0.4, None),
        (Ranged, False, 0.8, None),
    ]
    kwargs = dict(
        room_type=RoomType.COMBAT,
        room_idx=26,
        biome_index=4,
        difficulty_modifier=1.0,
        enemy_adjustment=0,
        reinforcement_chance_b4=0.0,
        pressure_level="medium",
        composition_bias_b4="balanced",
        pacing_bias="normal",
        player_state_name="STABLE",
        hazard_tune_factor=1.0,
        Swarm=Swarm,
        Flanker=Flanker,
        Brute=Brute,
        Heavy=Heavy,
        Ranged=Ranged,
    )
    a, m1 = adjust_biome4_spawn_specs(list(base), **kwargs)
    b, m2 = adjust_biome4_spawn_specs(list(base), **kwargs)
    assert _freeze_specs(a) == _freeze_specs(b)
    assert m1 == m2


def test_biome3_safe_composition_caps_extra_ranged():
    base = [
        (Ranged, False, 0.0, None),
        (Ranged, False, 0.4, None),
        (Swarm, False, 0.8, None),
    ]
    out, _mods = adjust_biome3_spawn_specs(
        list(base),
        room_type=RoomType.COMBAT,
        room_idx=17,
        biome_index=3,
        difficulty_modifier=1.0,
        enemy_adjustment=0,
        reinforcement_chance_b3=0.0,
        pressure_level="medium",
        composition_bias_b3="safe",
        ranged_bias_b3="low",
        player_state_name="STRUGGLING",
        hazard_tune_factor=1.0,
        Swarm=Swarm,
        Flanker=Flanker,
        Brute=Brute,
        Heavy=Heavy,
        Ranged=Ranged,
    )
    names = [getattr(r[0], "__name__", "") for r in out]
    assert names.count("Ranged") <= 1


def test_biome4_safe_composition_reduces_heavy_ranged_pressure():
    base = [
        (Heavy, False, 0.0, None),
        (Ranged, False, 0.4, None),
        (Brute, False, 0.8, None),
    ]
    out, _ = adjust_biome4_spawn_specs(
        list(base),
        room_type=RoomType.COMBAT,
        room_idx=25,
        biome_index=4,
        difficulty_modifier=1.0,
        enemy_adjustment=0,
        reinforcement_chance_b4=0.0,
        pressure_level="low",
        composition_bias_b4="safe",
        pacing_bias="relaxed",
        player_state_name="STRUGGLING",
        hazard_tune_factor=0.9,
        Swarm=Swarm,
        Flanker=Flanker,
        Brute=Brute,
        Heavy=Heavy,
        Ranged=Ranged,
    )
    names = [getattr(r[0], "__name__", "") for r in out]
    assert "Heavy" not in names
    assert names.count("Ranged") <= 1


# ---------------------------------------------------------------------------
# Pattern params & ranged offsets
# ---------------------------------------------------------------------------


def test_biome2_spawn_pattern_params_pressure():
    low = biome2_spawn_pattern_params("low")
    assert low["ambush_radius_px"] > 0
    high = biome2_spawn_pattern_params("high")
    assert high["ambush_radius_px"] < low["ambush_radius_px"]
    assert biome2_spawn_pattern_params("medium") == {}


def test_biome3_spawn_pattern_params_include_ranged_dist_mult():
    m = biome3_spawn_pattern_params("high", "high")
    assert m["ranged_spawn_dist_mult"] == 0.9


def test_biome4_pacing_and_spawn_pattern():
    assert biome4_pacing_spacing_mult("normal") == 1.0
    assert biome4_pacing_spacing_mult("relaxed") > 1.0
    assert biome4_pacing_spacing_mult("intense") < 1.0
    m = biome4_spawn_pattern_params("high", "intense")
    assert "ambush_radius_px" in m


def test_apply_biome3_ranged_position_offsets_changes_ranged_only():
    specs = [
        (Swarm, False, 0.0, None),
        (Ranged, False, 0.4, None),
    ]
    positions = [(100.0, 100.0), (200.0, 100.0)]
    player_center = (100.0, 100.0)
    before = list(positions)
    apply_biome3_ranged_position_offsets(positions, specs, player_center, "low")
    assert positions[0] == before[0]
    assert positions[1] != before[1]


# ---------------------------------------------------------------------------
# Heal / safe-room helpers (used with AI Director player state)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fn, struggling, dominating, neutral",
    [
        (biome1_effective_heal_drop_chance, 0.35, 0.15, 0.25),
        (biome2_effective_heal_drop_chance, 0.37, 0.13, 0.25),
        (biome3_effective_heal_drop_chance, 0.37, 0.15, 0.25),
        (biome4_effective_heal_drop_chance, 0.39, 0.11, 0.25),
    ],
)
def test_biome_heal_drop_helpers_struggling_vs_dominating(fn, struggling, dominating, neutral):
    base = 0.25
    assert fn(base, "STRUGGLING") == pytest.approx(struggling)
    assert fn(base, "DOMINATING") == pytest.approx(dominating)
    assert fn(base, "STABLE") == pytest.approx(neutral)
    assert fn(base, None) == pytest.approx(neutral)


def test_safe_room_heal_multipliers_biome_2_3_4():
    assert biome2_safe_room_heal_multiplier("STRUGGLING") > 1.0
    assert biome2_safe_room_heal_multiplier("DOMINATING") < 1.0
    assert biome3_safe_room_heal_multiplier("STRUGGLING") > 1.0
    assert biome4_safe_room_heal_multiplier("STRUGGLING") > biome3_safe_room_heal_multiplier("STRUGGLING")


# ---------------------------------------------------------------------------
# Metrics: hazard damage (feeds room-history relief wiring)
# ---------------------------------------------------------------------------


def test_metrics_hazard_lava_increments_damage_from_hazards():
    m = MetricsTracker()
    m.start_run(42)
    m.start_room(room_index=20, biome_index=3, hp_percent=100.0)
    m.record_damage_taken(5.0, "hazard_lava")
    assert m._room is not None
    assert m._room.damage_from_hazards == pytest.approx(5.0)
    assert m.run.damage_from_hazards == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# Final boss + Biome 3 mini-boss director hooks (entity layer)
# ---------------------------------------------------------------------------


def test_final_boss_stores_ai_director_scaling_kwargs():
    from entities.final_boss import FinalBoss

    boss = FinalBoss(
        (0.0, 0.0),
        room_index=29,
        ai_telegraph_mult=1.1,
        ai_cooldown_mult=0.95,
        ai_recovery_mult=1.02,
        ai_post_revive_delay_sec=1.25,
    )
    assert boss._ai_telegraph_mult == pytest.approx(1.1)
    assert boss._ai_post_revive_delay_sec == pytest.approx(1.25)
    # Cooldown / telegraph helpers apply multipliers
    cd = boss._cooldown_sec()
    assert cd > 0
    assert boss._telegraph_fireball_sec() > 0


def test_configure_biome3_miniboss_director_clamps_and_resets():
    import entities.biome3_miniboss as b3m

    b3m.configure_biome3_miniboss_director(fireball_cd_mult=1.2, fireball_telegraph_mult=1.1)
    assert b3m._DIRECTOR_FIREBALL_CD_MULT == pytest.approx(1.2)
    b3m.configure_biome3_miniboss_director(fireball_cd_mult=1.0, fireball_telegraph_mult=1.0)
    assert b3m._DIRECTOR_FIREBALL_CD_MULT == pytest.approx(1.0)
