# Class Diagram Verification

## Scope and Sources

Verified against:

- `src/` implementation (primary source of truth)
- Existing class diagram source:
  - `design_docs/SRS/srs_fig_puml_code/uml.puml` (original SRS figure; many names outdated)
- Supplemental architecture diagrams:
  - `design_docs/SRS/srs_fig_puml_code/architecture.puml`
  - `design_docs/SRS/srs_fig_puml_code/context.puml`

Prompt packs reviewed for subsystem scope alignment:

- `prompts/ai_prompts/ai_director_prompts/`
- `prompts/ai_prompts/seed_generation_prompts/`

---

## Diagram Scope Used for Verification

Submission-ready class diagram should represent major runtime architecture:

- Scene orchestration (`SceneManager`, scene classes, especially `GameScene`)
- Dungeon/room flow (`RoomController`, `Room`, `RoomType`, door/hazard systems)
- AI runtime stack (`AIDirector`, `PlayerModel`, `MetricsTracker`, difficulty params)
- Core gameplay entities (`Player`, `EnemyBase` family, bosses, `Projectile`)
- Core systems (`SpawnSystem`, combat events/resolution, VFX, debug overlay)
- Deterministic seed/runtime boundaries (`game.rng` module and seed sequence modules)
- RL runtime integration boundary (`DungeonEnv` and wrappers) at high level if in scope

---

## What Is Already Correct in Original SRS `uml.puml`

From `design_docs/SRS/srs_fig_puml_code/uml.puml`, several high-level intentions are still conceptually valid:

- Layered separation exists (game orchestration, AI, dungeon generation, logging)
- Deterministic RNG and read-only runtime parameter ideas are represented
- AI Director and metrics concept are represented
- Room/boss/enemy families are represented at a conceptual level

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
  - `AIDirector` (+ `EncounterDirective`, `EncounterDirectorSnapshot`, etc.)
  - `PlayerModel`, `PlayerStateClass`, `PlayerClassificationResult`, `PlayerModelSummaryInput`
  - `MetricsTracker`, `RunMetrics`, `RoomMetrics`, `RoomResult`
  - `DifficultyParams` family and loader functions
  - `AILogger`

- **Seed/determinism runtime**
  - Module-level seeded API in `game/rng.py` (`initialize_run_seed`, `derive_seed`, room/channel helpers)
  - Deterministic sequence/spec modules: `dungeon/srs_biome_order.py`, `dungeon/seeded_encounter_specs.py`

- **Gameplay entities/systems**
  - `Player`
  - `EnemyBase` + `Swarm`, `Flanker`, `Brute`, `Heavy`, `Ranged`
  - Standalone boss-like classes: `MiniBoss`, `MiniBoss2`, `Biome3MiniBoss`, `FinalBoss` (not subclasses of `EnemyBase`)
  - `TrainingDummy` (standalone)
  - `Projectile`, `SpawnSystem`, `SpawnSlot`
  - combat `DamageEvent`
  - `VfxManager`
  - `DebugOverlay`

- **RL runtime boundary**
  - `DungeonEnv`
  - wrappers: `TimeoutPenaltyWrapper`, `CurriculumSuccessWrapper`, `CurriculumScenarioSamplerWrapper` (optional on diagram)

---

## Acceptability Assessment

`design_docs/SRS/srs_fig_puml_code/uml.puml` is **not acceptable as-is** for final submission against the current implementation.

Reason:

- Many diagram classes do not exist in code (e.g., `GameController`, `RoomFlowManager`, `SeedManager`, `RNGModule`, `DungeonGenerator`, `EncounterManager`, `CombatResolver`, `RunLogger`)
- Key implemented classes are missing (`SceneManager`, `GameScene`, `RoomController`, `PlayerModel`, `AILogger`, `SpawnSystem`, `DungeonEnv`, etc.)
- Multiple represented relationships no longer match implementation structure

Conclusion:

- Diagram needs revision to a lean, implementation-accurate class diagram focused on major runtime classes and relationships.

---

## Updated Artifacts Produced (this folder)

| Artifact | Purpose |
|----------|---------|
| `Class_Diagram_Verification.md` | This verification summary |
| `Class_Diagram_Mismatches.md` | Detailed mismatch list (including §6 follow-up) |
| `Updated_Class_Diagram.puml` | Compact implementation-aligned diagram (relationships + packages) |
| `Updated_Class_Diagram.png` | Rendered image (same folder) |
| `Core_Class_Diagram_SRS_Figure.puml` | **SRS-style** figure: packages, **+ / −** visibility, «property»/«dataclass», key methods |
| `Core_Class_Diagram_SRS_Figure.png` | Rendered image |

**PNG generation:** Images were produced with the public PlantUML server (`plantuml` Python package → `http://www.plantuml.com/plantuml/img/`). To regenerate offline, install Graphviz + PlantUML JAR and run:

`java -jar plantuml.jar Core_Class_Diagram_SRS_Figure.puml`

Or use the VS Code **PlantUML** extension with local Java.

---

## Relationship to `Updated_Class_Diagram` vs `Core_Class_Diagram_SRS_Figure`

- **`Updated_Class_Diagram.puml`**: smaller, fast to read; corrected boss/training dummy note (no false `EnemyBase` inheritance for bosses).
- **`Core_Class_Diagram_SRS_Figure.puml`**: submission-style detail — visibility legend, accessors, and a more complete API surface for core classes; use this when the assignment asks for SRS figure conventions.

See **`Class_Diagram_Mismatches.md` §6** for the boss/`EnemyBase` correction and API naming notes.

---

## Final verification pass (sync with current `src/`)

The following were checked against the codebase and reflected in **`Core_Class_Diagram_SRS_Figure.puml`** / PNG:

| Area | Change |
|------|--------|
| **GameScene** | Uses public **`player_model`**, **`ai_director`**, **`ai_logger`**; private **`_metrics`** (not `_metrics_tracker`); lists **`_projectiles`**; RL flags **`_rl_skip_draw`**. |
| **SceneManager → DifficultyParams** | Loaded in `SceneManager.__init__` and held as **`difficulty_params`**. |
| **Door / DoorState** | **`CLOSED`** state added; **`Door.is_safe_door`**, **`world_x` / `world_y`**, **`can_pass()`** aligned with `door_system.py`. |
| **AILogger** | Public **`logs`**, **`run_seed`**, **`file_path`**, etc. (not a private `_records` only). |
| **DebugOverlay** | **`enabled`**, **`game_scene`**, **`_font`** per `debug_overlay.py`. |
| **Combat** | **`GameScene ..> DamageEvent`** — events come from **`systems.combat`** (`apply_*` functions). |
| **Ranged → Projectile** | **`Ranged ..> Projectile`** — ranged enemies fire projectiles. |
| **SpawnSlot → EnemyBase** | **`SpawnSlot ..> EnemyBase`** — `enemy_cls` typically subclasses **`EnemyBase`**. |
| **RL** | **`RewardState`**, **`RewardSnapshot`**; **`DungeonEnv`** holds **`_prev_reward_snapshot`**; **`TimeoutPenaltyWrapper`** wraps the env for training; reward math in **`rl/reward.py`**. |

**Intentionally light or omitted** (to keep the figure readable): `game.asset_loader` / `game.logger` (module-level APIs), biome-specific `*_director_spawn.py` helpers, `curriculum_wrappers` beyond **`TimeoutPenaltyWrapper`**, and full **`RewardSnapshot`** field list (see note on diagram + **`rl/reward.py`**).
