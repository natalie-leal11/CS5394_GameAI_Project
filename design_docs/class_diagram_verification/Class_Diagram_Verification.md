# Class Diagram Verification

## Scope and Sources

Verified against:
- `src/` implementation (primary source of truth)
- existing class diagram source:
  - `SRS/srs_fig_puml_code/uml.puml` (class diagram)
- supplemental architecture diagrams:
  - `SRS/srs_fig_puml_code/architecture.puml`
  - `SRS/srs_fig_puml_code/context.puml`

Prompt packs reviewed for subsystem scope alignment:
- `ai_prompts/ai_director_prompts/`
- `ai_prompts/seed_generation_prompts/`
- `ai_prompts/rl_integration_prompts/`

---

## Diagram Scope Used for Verification

Submission-ready class diagram should represent major runtime architecture:
- scene orchestration (`SceneManager`, scene classes, especially `GameScene`)
- dungeon/room flow (`RoomController`, `Room`, `RoomType`, door/hazard systems)
- AI runtime stack (`AIDirector`, `PlayerModel`, `MetricsTracker`, difficulty params)
- core gameplay entities (`Player`, `EnemyBase` family, bosses, `Projectile`)
- core systems (`SpawnSystem`, combat events/resolution, VFX, debug overlay)
- deterministic seed/runtime boundaries (`game.rng` module and seed sequence modules)
- RL runtime integration boundary (`DungeonEnv` and wrappers) at high level if in scope

---

## What Is Already Correct in Existing Diagram

From `uml.puml`, several high-level intentions are still conceptually valid:
- layered separation exists (game orchestration, AI, dungeon generation, logging)
- deterministic RNG and read-only runtime parameter ideas are represented
- AI Director and metrics concept are represented
- room/boss/enemy families are represented at a conceptual level

These are directionally correct, but class names and relationships are largely outdated versus actual code.

---

## Major Subsystems Confirmed in Current Implementation

- **Scene/runtime orchestration**
  - `SceneManager`
  - `BaseScene`, `StartScene`, `ControlsScene`, `SettingsScene`, `GameScene`

- **Dungeon/room control**
  - `RoomController`
  - `Room`, `RoomType`
  - `DoorSystem`, `Door`, `DoorState`
  - `HazardSystem`

- **AI runtime**
  - `AIDirector`
  - `PlayerModel`, `PlayerStateClass`, `PlayerClassificationResult`
  - `MetricsTracker`, `RunMetrics`, `RoomMetrics`, `RoomResult`
  - `DifficultyParams` family and loader functions
  - `AILogger`

- **Seed/determinism runtime**
  - module-level seeded API in `game/rng.py` (`initialize_run_seed`, `derive_seed`, room/channel helpers)
  - deterministic sequence/spec modules (function-based): `dungeon/srs_biome_order.py`, `dungeon/seeded_encounter_specs.py`

- **Gameplay entities/systems**
  - `Player`
  - `EnemyBase` + `Swarm`, `Flanker`, `Brute`, `Heavy`, `Ranged`
  - `MiniBoss`, `MiniBoss2`, `Biome3MiniBoss`, `FinalBoss`
  - `Projectile`, `TrainingDummy`
  - `SpawnSystem`, `SpawnSlot`
  - combat `DamageEvent`
  - `VfxManager`
  - `DebugOverlay`

- **RL runtime boundary**
  - `DungeonEnv`
  - wrappers: `TimeoutPenaltyWrapper`, `CurriculumSuccessWrapper`, `CurriculumScenarioSamplerWrapper`

---

## Acceptability Assessment

`SRS/srs_fig_puml_code/uml.puml` is **not acceptable as-is** for final submission against the current implementation.

Reason:
- many diagram classes do not exist in code (e.g., `GameController`, `RoomFlowManager`, `SeedManager`, `RNGModule`, `DungeonGenerator`, `EncounterManager`, `CombatResolver`, `RunLogger`)
- key implemented classes are missing (`SceneManager`, `GameScene`, `RoomController`, `PlayerModel`, `AILogger`, `SpawnSystem`, `DungeonEnv`, etc.)
- multiple represented relationships no longer match implementation structure

Conclusion:
- diagram needs revision to a lean, implementation-accurate class diagram focused on major runtime classes and relationships.

---

## Updated Artifacts Produced

- `design_docs/class_diagram_verification/Class_Diagram_Verification.md`
- `design_docs/class_diagram_verification/Class_Diagram_Mismatches.md`
- `design_docs/class_diagram_verification/Updated_Class_Diagram.puml`

`Updated_Class_Diagram.png` was not generated in this environment because the `plantuml` CLI is not installed.
