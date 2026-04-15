# Class Diagram Mismatches

## Priority Mismatches (Most Important for Submission)

## 1) Missing Major Implemented Classes

These are central runtime classes in `src` but absent from `SRS/srs_fig_puml_code/uml.puml`:

- `SceneManager`
- `BaseScene`
- `GameScene`
- `StartScene`
- `ControlsScene`
- `SettingsScene`
- `RoomController`
- `DoorSystem`, `Door`, `DoorState`
- `HazardSystem`
- `PlayerModel` (+ `PlayerStateClass`, `PlayerClassificationResult`)
- `MetricsTracker` (+ `RunMetrics`, `RoomMetrics`, `RoomResult`)
- `AILogger`
- `SpawnSystem`, `SpawnSlot`
- `EnemyBase` (as actual base class)
- `FinalBoss`, `Biome3MiniBoss`, `MiniBoss2` (in addition to `MiniBoss`)
- `Projectile`
- `DebugOverlay`
- `DungeonEnv` (if RL runtime boundary is in scope)

---

## 2) Missing Critical Relationships

Implemented relationships that should be represented:

- `SceneManager` aggregates scene instances (`GameScene`, `StartScene`, `ControlsScene`, `SettingsScene`)
- `GameScene` inherits `BaseScene`
- `GameScene` composes/uses:
  - `RoomController`
  - `Player`
  - `MetricsTracker`
  - `PlayerModel`
  - `AIDirector`
  - `AILogger`
  - `SpawnSystem`
  - `VfxManager`
  - `DebugOverlay`
- `RoomController` composes `DoorSystem` and `HazardSystem`
- `PlayerModel` depends on `MetricsTracker` summary models and difficulty params
- `AIDirector` depends on difficulty params and player state output from `PlayerModel`
- `EnemyBase` is base for `Swarm`, `Flanker`, `Brute`, `Heavy`, `Ranged`
- `DungeonEnv` uses `SceneManager`/`GameScene` as runtime simulation backend

---

## 3) Outdated or Incorrect Diagram Elements

Classes in `uml.puml` that do not correspond to current implementation class names/structure:

- `GameController` (not implemented as class)
- `RoomFlowManager` (not implemented as class)
- `SeedManager` (seed control is module-level functions in `game/rng.py`)
- `RNGModule` (same issue; no RNG class)
- `DungeonGenerator` (generation is function-based via `generate_room` and sequence modules)
- `EncounterManager` (not a standalone class; logic distributed in `GameScene` + spawn/director helpers)
- `CombatResolver` (combat is module-level functions in `systems/combat.py`)
- `Enemy` as base class name (actual base is `EnemyBase`)
- `RunLogger`/`LogWriter`/`DifficultyParamsLoader` class forms are not current class implementations

Outdated relationships:
- many arrows from `RoomFlowManager` are invalid because this class does not exist
- seed/dungeon relationships are class-modeled where code is functional module-level

---

## 4) Implemented but Optional to Exclude for Readability

For a clean final class diagram, these can be excluded or grouped:

- Fine-grained dataclasses/DTOs:
  - `EncounterDirective`, `SafeRoomDirective`, `VariationDirective`, `EncounterDirectorSnapshot`
  - `RewardSnapshot`, `RewardState`, etc.
- Specialized helper modules:
  - biome-specific director spawn helper modules
  - spawn helper utility functions
  - seed sequence/spec function modules as classes (better represented as notes/modules)
- RL training/evaluation tooling classes (`PPOConfig`, callbacks) unless submission scope explicitly includes RL toolchain internals
- Prompt/test utility files

---

## 5) Suggested High-Value Revisions

For submission-ready clarity, prioritize:

1. Replace fictional orchestration classes with real scene/runtime classes (`SceneManager`, `GameScene`, `RoomController`)
2. Update AI section to real stack (`AIDirector`, `PlayerModel`, `MetricsTracker`, difficulty params)
3. Update gameplay entity hierarchy to `EnemyBase`-based inheritance and include bosses/projectile
4. Represent seed as deterministic module/service note (not fake classes), tied to `GameScene` + room sequence/spec modules
5. Include RL runtime boundary as one class (`DungeonEnv`) connected to `SceneManager`/`GameScene` if RL scope is claimed
