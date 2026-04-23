# Test Coverage Audit

## Scope Reviewed

- Implementation: `src/`
- Tests: `tests/`
- Prompt packs:
  - `ai_prompts/ai_director_prompts/`
  - `ai_prompts/seed_generation_prompts/`
  - `ai_prompts/rl_integration_prompts/` (runtime boundary relevance)

Status labels used:
- `Covered`: meaningful assertions on implemented behavior
- `Partially Covered`: mostly smoke, shallow, or missing key edge assertions
- `Uncovered`: no direct tests found for implemented behavior

---

## Feature-to-Test Mapping

| Feature Area | Implementation Signals | Existing Tests | Status | Notes |
|---|---|---|---|---|
| AI Director state mapping (struggling/stable/dominating -> knobs) | `src/game/ai/ai_director.py` | `tests/test_ai_director_biomes.py` | Covered | Strong paramized checks across biome fields and debug helpers. |
| AI Director bounded biome spawn helpers | `src/game/ai/biome*_director_spawn.py` | `tests/test_ai_director_biomes.py`, `tests/integration/test_biome_director_spawns.py` | Partially Covered | Core helper behavior covered; integration file is mostly smoke and weak assertions. |
| AI Director determinism/logging boundaries (prompt phase 9) | `src/game/ai/ai_logger.py`, `src/game/scenes/game_scene.py` | `tests/integration/test_ai_logger.py` | Partially Covered | Logger API smoke exists; no robust deterministic replay assertions for director decision sequence. |
| Metrics tracker room/run interactions | `src/game/ai/metrics_tracker.py` | `tests/integration/test_gameplay_metrics_hooks.py`, `tests/test_ai_director_biomes.py` | Partially Covered | Good targeted checks for kill/room/death/hazard; `tests/unit/test_metrics_tracker.py` is mostly trivial. |
| Player model deterministic classification | `src/game/ai/player_model.py` | `tests/unit/test_player_model_classification.py` | Partially Covered | Determinism smoke present, but threshold boundary/override behavior mostly skipped. |
| Player model + metrics integration into gameplay loop | `src/game/scenes/game_scene.py` hooks | `tests/integration/test_gameplay_metrics_hooks.py` | Partially Covered | Hook-level coverage exists; no strong end-to-end state-transition assertions through gameplay phases. |
| Seed RNG core helpers | `src/game/rng.py` | `tests/unit/test_game_rng.py` | Partially Covered | `derive_seed` basic checks exist; little coverage for room/channel helper APIs and variant lifecycle. |
| Seed room-order variation by variant | `src/dungeon/srs_biome_order.py` | `tests/unit/test_biome_room_sequences.py` | Partially Covered | Sequence tests exist, but no comprehensive variant-difference matrix and invariant assertions per biome. |
| Seed encounter variation by variant | `src/dungeon/seeded_encounter_specs.py` | `tests/unit/test_seeded_encounter_specs.py` | Uncovered | File contains mostly smoke + skipped tests; no concrete builder assertions. |
| Seed determinism/replay logging | `src/game/phase1_seed_debug.py`, `src/game/scenes/game_scene.py` | No robust tests found | Uncovered | Prompt requires reproducibility checks from logs; currently untested. |
| Safe-room heal and bounded behavior | `src/game/scenes/game_scene.py`, biome helper multipliers | `tests/integration/test_safe_room_flow.py`, `tests/test_ai_director_biomes.py` | Partially Covered | Heal formula/multipliers tested; one-choice upgrade path and biome-specific offering behavior not deeply verified. |
| Biome-specific safe room upgrade behavior | `src/game/scenes/game_scene.py` upgrade flow | No direct deep tests found | Uncovered | No clear assertions for biome 3/4 pick counts, option biasing, or one-choice enforcement under all states. |
| Checkpoint respawn after mini-boss clears | `src/game/scenes/game_scene.py` (`_update_checkpoint_from_mini_boss_clear`, `_respawn_player_at_checkpoint`) | No direct tests found | Uncovered | This implementation is significant and currently lacks explicit tests. |
| Final boss phase/revive behavior | `src/entities/final_boss.py` | `tests/integration/test_bosses_biome3_final.py`, `tests/test_ai_director_biomes.py` | Partially Covered | Mostly smoke; no deep validation of phase transitions, revive timing, cooldown/telegraph scaling sequence. |
| Short attack buffering | `src/entities/player.py`, `src/game/scenes/game_scene.py` | `tests/test_short_attack_buffer_gameplay.py`, `tests/test_phase4_combat.py` | Covered | Strong scenario-based coverage for buffering semantics and pause clearing. |
| Ranged enemy tuning and projectile behavior | `src/entities/ranged.py`, `src/entities/projectile.py`, biome3 helpers | `tests/unit/test_ranged_projectile.py`, `tests/test_ai_director_biomes.py` | Partially Covered | Ranged-position helper tests are good; direct ranged AI/cooldown/kiting behavior is mostly smoke-level. |
| RL runtime boundaries (read-only params, no online learning in runtime path) | `src/game/ai/difficulty_params.py`, `src/rl/*`, `tools/rl/*` | `tests/unit/test_rl_*`, `tests/integration/test_rl_dungeon_env.py` | Partially Covered | RL env/wrapper smoke coverage exists; explicit guardrail verification against forbidden runtime mutations is limited. |

---

## Prompt-Pack Alignment Check

### AI Director Prompt Pack

Expected by prompts:
- deterministic bounded directives
- biome-specific behavior preserved separately
- safe-room biasing without forced choice
- deterministic logging/replay checks

Observed test alignment:
- Strongest alignment: deterministic directive mapping and biome helper behaviors (`tests/test_ai_director_biomes.py`)
- Gaps: safe-room upgrade decision path assertions, end-to-end deterministic replay checks from logs, final boss tuning validation depth

### Seed Generation Prompt Pack

Expected by prompts:
- three distinct seed variants
- bounded variation in room order and encounter composition
- deterministic replayability and logging verification

Observed test alignment:
- Some alignment: RNG basics and sequence checks
- Major gap: concrete variant-specific composition tests for `seeded_encounter_specs`, deterministic replay/log output checks, explicit seed-variation difference assertions

### RL Integration Prompt Pack (runtime boundaries)

Expected by prompts:
- runtime parameter contract is deterministic and read-only
- no online/runtime learning imported into gameplay path
- guardrails against forbidden gameplay mutations

Observed test alignment:
- RL env/wrapper smoke is present
- Guardrail verification is mostly not asserted in tests as policy checks

---

## Test Suite Quality Notes

- Several files under `tests/unit/` are placeholders or minimal smoke and include `pytest.skip(...)`.
- `tests/prompts/` and `tests/prompts_out/` are prompt artifacts and not evidence of implemented behavior coverage.
- The strongest behavior-focused tests currently are:
  - `tests/test_ai_director_biomes.py`
  - `tests/test_short_attack_buffer_gameplay.py`
  - `tests/test_phase4_combat.py`
  - selected integration tests (`test_gameplay_metrics_hooks.py`, `test_safe_room_flow.py`)
