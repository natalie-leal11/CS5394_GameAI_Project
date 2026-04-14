"""One-off generator for tests/prompts/prompt_XX.md — run from repo root: python tests/prompts/_generate_prompts.py"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIT = "docs/game_testing_high_level_audit.md"

PROMPTS = []

def p(n, title, objective, files, cases, conc="", dead="", audit_refs=""):
    body = f"""## Prompt Title: {title}

### CRITICAL REQUIREMENTS ###
- **MANDATORY:** ONLY write test code (pytest).
- **CRITICAL:** DO NOT modify production code.
- **CRITICAL:** DO NOT change game logic.
- Tests must be additive and isolated under `tests/`.
- Use deterministic seeds where the audit requires reproducibility.
- Source coverage: `{AUDIT}` — components: {audit_refs}

---

### OBJECTIVE ###
{objective}

---

### FILES TO CREATE ###
{files}

---

### TEST CASES (MANDATORY) ###
{cases}

---

### CONCURRENCY / TIMING TESTS (IF APPLICABLE) ###
{conc or "- Not applicable for this prompt (unit-only scope)." }

---

### DEADLOCK SAFETY (IF APPLICABLE) ###
{dead or "- Not applicable unless noted." }

---

### ACCEPTANCE CRITERIA ###
- **MANDATORY:** Tests pass without editing `src/` except test utilities if already allowed by project.
- **CRITICAL:** No flaky tests; fixed seeds for RNG-dependent assertions.
- **CRITICAL:** Same seed + inputs ⇒ same observable outcomes.

---

### CRITICAL REMINDER ###
ONLY create or extend test files listed above.
NO production code edits.
NO refactoring.
NO design changes.

---

### CRITICAL END ###
Execute this prompt as a single Cursor task; then run `pytest` on new tests.
"""
    PROMPTS.append((n, body))


# --- Build 40 prompts from audit ---

p(1, "Player — HP, lives, and damage intake (`entities/player.py`)",
  "Unit and focused integration tests for HP bounds, life loss, respawn transitions, healing at full HP, last life, and frame-boundary damage per audit §1 Player.",
  "- `tests/unit/test_player_hp_lives.py`",
  """- `test_hp_never_exceeds_max_when_clamped`
- `test_damage_reduces_hp_monotonically`
- `test_life_decrement_on_run_failure_if_applicable`
- `test_heal_at_full_hp_is_noop_or_clamped`
- `test_edge_last_life_death`""",
  "- N/A unless multi-step update harness used.",
  "- N/A",
  "§1 Player")

p(2, "Player — Cooldowns, dash, block, parry, attack states",
  "Unit tests for dash/attack cooldown timers and state transitions (movement, attack, block, parry, hurt) per audit §1 Player.",
  "- `tests/unit/test_player_combat_states.py`",
  """- `test_dash_cooldown_counts_down`
- `test_attack_cooldown_respects_config`
- `test_block_parry_mutual_exclusion_if_designed`
- `test_invulnerability_window_monotonic`""",
  "- Timer expiry exactly once per tick.",
  "- N/A",
  "§1 Player")

p(3, "Enemy base — lifecycle, HP, death, elite/normal",
  "Tests for `entities/enemy_base.py` and shared contracts: spawn alive, take damage, die, removal from combat set.",
  "- `tests/unit/test_enemy_base_lifecycle.py`",
  """- `test_enemy_starts_alive_with_positive_hp`
- `test_damage_reduces_hp`
- `test_at_zero_hp_marks_dead_or_triggers_removal_hook`
- `test_no_damage_after_death`""",
  "- N/A",
  "- N/A",
  "§1 Enemy base")

p(4, "Swarm & Flanker enemies",
  "Tests for `entities/swarm.py` and `entities/flanker.py`: movement/attack patterns and damage to player (mocked) per audit.",
  "- `tests/unit/test_swarm_flanker.py`",
  """- `test_swarm_instantiation_and_update_smoke`
- `test_flanker_approach_smoke`
- `test_edge_many_swarm_instances_no_overflow_invariants`""",
  "- N/A",
  "- N/A",
  "§1 Swarm, Flanker")

p(5, "Brute & Heavy enemies",
  "Tests for `entities/brute.py` and `entities/heavy.py`: windups, HP pools, elite stacking edge cases per audit.",
  "- `tests/unit/test_brute_heavy.py`",
  """- `test_brute_attack_timing_smoke`
- `test_heavy_damage_mitigation_or_hp_pool`
- `test_edge_overlapping_hitboxes_no_double_count_same_frame`""",
  "- N/A",
  "- N/A",
  "§1 Brute, Heavy")

p(6, "Ranged enemy & Projectile",
  "Tests for `entities/ranged.py` and `entities/projectile.py`: firing, travel, despawn, hit registration, projectile after shooter death per audit.",
  "- `tests/unit/test_ranged_projectile.py`",
  """- `test_ranged_spawn_projectile_smoke`
- `test_projectile_despawn_on_lifetime`
- `test_edge_projectile_after_shooter_death_no_ghost_owner`
- `test_multiple_hits_same_frame_documented`""",
  "- Projectile update order vs collision in one frame.",
  "- N/A",
  "§1 Ranged, Projectile")

p(7, "MiniBoss & MiniBoss2",
  "Integration-style tests for `entities/mini_boss.py` and `entities/mini_boss_2.py`: defeat conditions and room pairing per audit.",
  "- `tests/integration/test_miniboss_variants.py`",
  """- `test_miniboss_defeat_sets_expected_flags`
- `test_miniboss2_distinct_from_miniboss_smoke`
- `test_edge_defeat_during_transition_no_double_reward`""",
  "- N/A",
  "- N/A",
  "§1 MiniBoss, MiniBoss2")

p(8, "Biome3MiniBoss & FinalBoss",
  "Integration tests for `entities/biome3_miniboss.py` and `entities/final_boss.py`: campaign end linkage and phase hooks per audit.",
  "- `tests/integration/test_bosses_biome3_final.py`",
  """- `test_biome3_miniboss_defeat_smoke`
- `test_final_boss_defeat_triggers_victory_path_smoke`
- `test_edge_timeout_vs_boss_death_ordering_mocked`""",
  "- N/A",
  "- N/A",
  "§1 Biome3MiniBoss, FinalBoss")

p(9, "TrainingDummy",
  "Unit tests for `entities/training_dummy.py`: damage absorption; not counted as kill in metrics if applicable per audit.",
  "- `tests/unit/test_training_dummy.py`",
  """- `test_dummy_accepts_damage_without_invalid_state`
- `test_dummy_not_in_kill_count_if_metrics_wired`""",
  "- N/A",
  "- N/A",
  "§1 TrainingDummy")

p(10, "Combat system (`systems/combat.py`)",
  "Unit/integration tests for hit detection, damage amounts, kill registration; double-hit and list-mutation edge cases per audit §2.",
  "- `tests/unit/test_combat_resolution.py`",
  """- `test_hitbox_overlap_applies_damage`
- `test_kill_increments_once`
- `test_edge_double_hit_one_swing_if_forbidden`
- `test_edge_hit_after_removal_from_list`""",
  "- Combat pass order vs removal list.",
  "- N/A",
  "§2 Combat system")

p(11, "Collisions & Movement",
  "Tests for `systems/collisions.py` and `systems/movement.py`: wall sliding, velocity caps, slow vs dash per audit.",
  "- `tests/unit/test_collisions_movement.py`",
  """- `test_movement_respects_velocity_cap`
- `test_collision_no_tunnel_smoke`
- `test_edge_corner_tile_boundary`""",
  "- N/A",
  "- N/A",
  "§2 Collisions, Movement")

p(12, "Animation & VFX",
  "Tests for `systems/animation.py` and `systems/vfx.py`: frame bounds, cleanup, no gameplay mutation from VFX per audit.",
  "- `tests/unit/test_animation_vfx.py`",
  """- `test_animation_frame_index_stays_in_range`
- `test_vfx_cleanup_after_lifetime`
- `test_edge_scene_end_clears_vfx_references`""",
  "- N/A",
  "- N/A",
  "§2 Animation, VFX")

p(13, "Health system (player & enemy HP)",
  "Tests for HP clamp, healing orbs, safe-room heal, life vs HP per audit §2 Health system.",
  "- `tests/unit/test_health_system.py`",
  """- `test_hp_clamped_to_max`
- `test_overheal_rejected_or_clamped`
- `test_heal_on_death_frame_rejected`""",
  "- N/A",
  "- N/A",
  "§2 Health system")

p(14, "Gameplay metrics hooks — kills, room clear, victory/defeat",
  "Integration tests tying combat outcomes to metrics / scene flags per audit §2 Gameplay reward/metrics hooks.",
  "- `tests/integration/test_gameplay_metrics_hooks.py`",
  """- `test_kill_increments_metric_once`
- `test_room_clear_event_fires_once`
- `test_victory_and_defeat_mutually_exclusive`""",
  "- N/A",
  "- N/A",
  "§2 Gameplay reward / metrics hooks")

p(15, "RL step reward (`rl/reward.py`)",
  "Unit tests for reward breakdown sum, terminal once-only, stall, interact/heal terms; wrapper ordering assumptions per audit §2 RL reward + §7 snapshot timing.",
  "- `tests/unit/test_rl_reward_breakdown.py`",
  """- `test_breakdown_components_sum_to_step_reward`
- `test_terminal_reward_paid_once`
- `test_stall_penalty_threshold`
- `test_edge_reset_boundary_zero_reward_consistency`""",
  "- Snapshot before/after update ordering.",
  "- N/A",
  "§2 RL reward, §7 Metrics/reward snapshot")

p(16, "PlayerModel — DOMINATING / STABLE / STRUGGLING",
  "Unit tests for `game/ai/player_model.py`: threshold boundaries, deterministic classification per audit §3.",
  "- `tests/unit/test_player_model_classification.py`",
  """- `test_same_inputs_same_state_deterministic`
- `test_boundary_equality_struggling_vs_stable`
- `test_spike_damage_single_frame`""",
  "- N/A",
  "- N/A",
  "§3 Player state model")

p(17, "MetricsTracker (`game/ai/metrics_tracker.py`)",
  "Unit/integration tests for aggregates, reset on new run, no double increment per audit §3.",
  "- `tests/unit/test_metrics_tracker.py`",
  """- `test_reset_clears_run_counters`
- `test_increment_idempotent_where_required`
- `test_rl_interact_counters_separate_from_success`""",
  "- N/A",
  "- N/A",
  "§3 MetricsTracker")

p(18, "RoomController — progression",
  "Integration tests for `dungeon/room_controller.py`: advance room, boss flags, no duplicate advance per audit §3.",
  "- `tests/integration/test_room_controller.py`",
  """- `test_advance_increments_room_index`
- `test_cannot_skip_boss_room_if_blocked`
- `test_edge_transition_mid_combat_documented`""",
  "- N/A",
  "- N/A",
  "§3 RoomController")

p(19, "Biome rooms, sequences, `srs_biome_order`",
  "Unit tests for room counts, types, biome order consistency per audit §3 Room definitions.",
  "- `tests/unit/test_biome_room_sequences.py`",
  """- `test_expected_room_count_matches_srs_smoke`
- `test_biome_order_list_coherent`
- `test_edge_off_by_one_last_room`""",
  "- N/A",
  "- N/A",
  "§3 Room definitions")

p(20, "Seeded encounter specs (`dungeon/seeded_encounter_specs.py`)",
  "Unit tests: same seed ⇒ same spec; bounds on counts per audit §3.",
  "- `tests/unit/test_seeded_encounter_specs.py`",
  """- `test_deterministic_seed_produces_same_spec`
- `test_enemy_count_within_bounds`
- `test_edge_seed_extremes`""",
  "- N/A",
  "- N/A",
  "§3 Seeded encounter specs")

p(21, "Victory / defeat / death — GameScene integration",
  "Integration tests for terminal outcomes from `game/scenes/game_scene.py` per audit §3.",
  "- `tests/integration/test_game_scene_terminal_states.py`",
  """- `test_player_death_ends_run_smoke`
- `test_final_victory_single_terminal`
- `test_edge_death_and_victory_same_frame_rejected_or_ordered`""",
  "- N/A",
  "- N/A",
  "§3 Victory/defeat")

p(22, "Safe room logic",
  "Integration tests for heal offers, upgrade choice, door state per audit §3 Safe room.",
  "- `tests/integration/test_safe_room_flow.py`",
  """- `test_heal_percent_applied`
- `test_full_hp_heal_noop`
- `test_choice_spam_does_not_corrupt_state`""",
  "- N/A",
  "- N/A",
  "§3 Safe room logic")

p(23, "Game config (`game/config.py`)",
  "Unit tests that key constants are positive / in valid ranges; load consistency per audit §3.",
  "- `tests/unit/test_game_config_sanity.py`",
  """- `test_cooldowns_positive`
- `test_hp_values_positive`
- `test_edge_no_negative_durations`""",
  "- N/A",
  "- N/A",
  "§3 Game config")

p(24, "AIDirector (`game/ai/ai_director.py`)",
  "Unit tests for deterministic mapping from PlayerModel + params to snapshot; immutability during encounter per audit §4.",
  "- `tests/unit/test_ai_director.py`",
  """- `test_fixed_input_fixed_output`
- `test_snapshot_fields_within_expected_ranges`
- `test_neutral_default_snapshot`""",
  "- N/A",
  "- N/A",
  "§4 AIDirector")

p(25, "DifficultyParams & JSON load",
  "Unit tests for `game/ai/difficulty_params.py` + `config/difficulty_params.json`: parse, missing key handling, immutability per audit §4.",
  "- `tests/unit/test_difficulty_params_load.py`",
  """- `test_load_default_json_succeeds`
- `test_reject_or_clamp_invalid_values`
- `test_frozen_dataclass_no_mutation`""",
  "- N/A",
  "- N/A",
  "§4 DifficultyParams")

p(26, "Biome spawn helpers (biome1–biome4)",
  "Integration tests for spawn composition bounds and seed determinism per audit §4 Biome spawn helpers.",
  "- `tests/integration/test_biome_director_spawns.py`",
  """- `test_spawn_count_non_negative`
- `test_same_seed_same_composition_smoke`
- `test_zero_enemy_edge_if_allowed`""",
  "- N/A",
  "- N/A",
  "§4 Biome spawn helpers")

p(27, "AI logger (`game/ai/ai_logger.py`)",
  "Integration tests: logging calls do not crash; optional fields per audit §4.",
  "- `tests/integration/test_ai_logger.py`",
  """- `test_log_event_with_minimal_fields`
- `test_missing_optional_field_no_crash`""",
  "- N/A",
  "- N/A",
  "§4 AI logger")

p(28, "Offline RL — dataset export & reward eval",
  "Unit tests for `game/rl/dataset_export.py`, `reward_eval.py`, `offline_tuning_spec.py` with temp files per audit §4.",
  "- `tests/unit/test_offline_rl_tools.py`",
  """- `test_export_produces_parseable_rows`
- `test_evaluate_deterministic_on_fixed_csv`
- `test_empty_input_handled_gracefully`""",
  "- N/A",
  "- N/A",
  "§4 Offline RL dataset / reward eval")

p(29, "Room model (`dungeon/room.py`)",
  "Unit tests for room metadata, hazard percentage bounds, dimensions positive per audit §5.",
  "- `tests/unit/test_room_model.py`",
  """- `test_hazard_percent_in_0_100`
- `test_pixel_dimensions_positive`
- `test_invalid_room_type_rejected`""",
  "- N/A",
  "- N/A",
  "§5 Room model")

p(30, "Door system (`dungeon/door_system.py`)",
  "Integration/regression tests: locked during combat, unlock after clear + delay per audit §5 + §8 door unlock.",
  "- `tests/integration/test_door_system.py`",
  """- `test_doors_locked_while_enemies_alive`
- `test_unlock_after_clear_with_delay`
- `test_edge_last_enemy_and_player_death_same_frame`""",
  "- Unlock timer vs frame order.",
  "- N/A",
  "§5 Door system, §8 Door unlock")

p(31, "Hazard system (`dungeon/hazard_system.py`)",
  "Unit/integration tests for lava DPS, slow tiles, boundary standing per audit §5.",
  "- `tests/unit/test_hazard_system.py`",
  """- `test_lava_applies_dps_over_time`
- `test_slow_reduces_speed_factor`
- `test_edge_tile_boundary`""",
  "- N/A",
  "- N/A",
  "§5 Hazard system")

p(32, "Spawn system & spawn_helper — timing and reinforcements",
  "Integration + concurrency-oriented tests for spawn lists, reinforcements, cap per audit §5 Spawn system + §7 spawn delay.",
  "- `tests/integration/test_spawn_system.py`",
  """- `test_spawn_matches_directive`
- `test_reinforcement_only_when_flag_set`
- `test_no_spawn_after_room_clear`
- `test_edge_max_enemy_cap`""",
  "- Spawn mid-frame vs update order; reinforcement timing.",
  "- N/A",
  "§5 Spawn system, §7 Spawn delay")

p(33, "Biome4 visuals (`dungeon/biome4_visuals.py`)",
  "Unit/smoke tests: valid room does not raise; asset paths resolve per audit §5.",
  "- `tests/unit/test_biome4_visuals.py`",
  """- `test_build_visuals_for_valid_room_smoke`
- `test_missing_asset_fallback_if_implemented`""",
  "- N/A",
  "- N/A",
  "§5 Biome4 visuals")

p(34, "Asset loader (`game/asset_loader.py`)",
  "Unit tests for cache and missing file behavior per audit §5.",
  "- `tests/unit/test_asset_loader.py`",
  """- `test_load_twice_uses_cache_if_implemented`
- `test_missing_file_raises_or_placeholder`""",
  "- N/A",
  "- N/A",
  "§5 Asset loader")

p(35, "Scene manager (`game/scene_manager.py`)",
  "Integration tests for single active scene and transition ordering per audit §5.",
  "- `tests/integration/test_scene_manager.py`",
  """- `test_only_one_scene_updates_per_frame`
- `test_double_transition_second_ignored_or_queued_documented`""",
  "- N/A",
  "- N/A",
  "§5 Scene manager")

p(36, "GameScene — update order & enemy list safety",
  "Integration + concurrency tests for `game/scenes/game_scene.py`: player→enemies→combat order; list mutation safety per audit §5 + §7.",
  "- `tests/integration/test_game_scene_update_order.py`",
  """- `test_update_order_documented`
- `test_enemy_list_no_modify_during_iteration_violation`
- `test_rl_rl_step_path_smoke_headless`""",
  "- Deferred removal; copy-while-iterate patterns.",
  "- N/A",
  "§5 GameScene, §7 Shared collections, §7 Main loop")

p(37, "RNG (`game/rng.py`)",
  "Unit tests for seed reproducibility and None-seed behavior per audit §5.",
  "- `tests/unit/test_game_rng.py`",
  """- `test_same_seed_same_sequence`
- `test_different_seeds_differ_with_high_probability`""",
  "- N/A",
  "- N/A",
  "§5 RNG")

p(38, "DungeonEnv (`rl/env.py`)",
  "Integration tests for Gymnasium API: reset, step, obs shape, terminal flags per audit §6.",
  "- `tests/integration/test_rl_dungeon_env.py`",
  """- `test_reset_returns_valid_obs`
- `test_step_after_terminal_requires_reset`
- `test_headless_no_display_smoke`""",
  "- N/A",
  "- N/A",
  "§6 DungeonEnv")

p(39, "Observation builder & action map (`rl/obs.py`, `rl/action_map.py`)",
  "Unit tests: no NaN/inf, fixed length, action indices in range per audit §6.",
  "- `tests/unit/test_rl_obs_action_map.py`",
  """- `test_build_observation_shape_dtype`
- `test_all_action_indices_map_defined`
- `test_no_nan_inf_for_empty_enemy_case`""",
  "- N/A",
  "- N/A",
  "§6 obs, action_map")

p(40, "RL wrappers, curriculum, headless, experiment layout, PPO CLI smoke, deadlock guard",
  "Tests for `rl/wrappers.py`, `rl/curriculum_wrappers.py`, `rl/headless.py`, `rl/experiment_layout.py`, `rl/best_progress_callback.py`; argparse smoke for train/eval/demo **without** long training; static check for no threading locks in hot path per audit §6 + §7 threading.",
  "- `tests/unit/test_rl_wrappers_and_layout.py`\n- `tests/unit/test_rl_cli_smoke.py`\n- `tests/unit/test_no_deadlock_primitives_in_gameloop.py`",
  """- `test_timeout_penalty_only_when_truncated`
- `test_curriculum_success_requires_min_steps`
- `test_experiment_paths_no_path_traversal`
- `test_train_ppo_help_exits_zero`
- `test_no_threading_lock_import_in_game_scene_hot_path_static`""",
  "- Wrapper order TimeLimit then TimeoutPenalty.",
  "- **CRITICAL:** No `acquire()` blocking in game loop; infinite loop guard on eval callback patience smoke with mocks.",
  "§6 Wrappers, curriculum, headless, experiment_layout, best_progress, train/eval/demo, §7 Threading/locks")


def main():
    for n, body in PROMPTS:
        path = ROOT / f"prompt_{n:02d}.md"
        path.write_text(body, encoding="utf-8")
    print(f"Wrote {len(PROMPTS)} files to {ROOT}")


if __name__ == "__main__":
    main()
