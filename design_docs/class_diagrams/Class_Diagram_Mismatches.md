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

---

## 6) Additional mismatches found (post–`Updated_Class_Diagram` review)

Verified against `src/entities/*.py`, `src/dungeon/door_system.py`, `src/dungeon/hazard_system.py`, `src/game/ai/ai_director.py`.

### 6.1 Boss / training classes are not `EnemyBase` subclasses

The earlier high-level diagram implied **all** combat entities extend `EnemyBase`. In code:

- **`Swarm`, `Flanker`, `Brute`, `Heavy`, `Ranged`** inherit **`EnemyBase`** (`src/entities/*.py`).
- **`MiniBoss`**, **`MiniBoss2`**, **`Biome3MiniBoss`**, **`FinalBoss`** are **standalone** classes: they define `enemy_type`, `world_pos`, `hp`, `update`/`draw`, etc., but **do not** subclass `EnemyBase` (`mini_boss.py`, `mini_boss_2.py`, `biome3_miniboss.py`, `final_boss.py`).
- **`TrainingDummy`** is also **standalone** (`training_dummy.py`), not `EnemyBase`.

`GameScene` treats these as compatible “enemy-like” instances for lists and combat hooks (duck typing), not via a shared base class for bosses.

### 6.2 `AIDirector` public API names

Prefer diagram labels:

- **`update(player_state: PlayerStateClass | None)`** — not `update_from_player_state`.
- **`capture_encounter_snapshot() -> EncounterDirectorSnapshot`** — not `snapshot()`.
- **`update_room_context(room_idx, biome_index)`** for room/biome context.

### 6.3 `DoorSystem` / `HazardSystem` method signatures

- **`DoorSystem.update(dt: float)`** — does not take `player_rect` / `Room` in `update` (player/door collision is handled elsewhere, e.g. `GameScene`).
- **`HazardSystem`**: **`set_room(room)`**, **`update(dt)`**; tile queries **`is_lava_tile`**, **`is_slow_tile`**, **`tile_at_world`** — not a single `bind_room` + `update(dt, player, room_rect)` as in some generic diagrams.

### 6.4 `SpawnSystem` entry points

Primary API includes **`add_spawn(...)`**, **`update(...)`**, **`all_spawns_completed()`** — not necessarily a method named `schedule_spawns`.

### 6.5 `DifficultyParams` root fields (JSON schema)

`DifficultyParams` includes **`player_model`**, **`director`**, **`rewards`**, **`metrics`**, **`combat`** (`src/game/ai/difficulty_params.py`) — not only “thresholds” blobs; nested types are `PlayerModelParams`, `DirectorParams`, etc.

### 6.6 SRS archive path

Legacy class diagram source lives at **`design_docs/SRS/srs_fig_puml_code/uml.puml`** (not `SRS/` at repo root in this project layout).
