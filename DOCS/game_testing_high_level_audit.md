# High-Level Game Codebase Audit — Testing Coverage Map

## 1. CORE GAME ENTITIES

### Component: Player (`entities/player.py`)

- **Responsibility:** Player avatar: HP, lives, movement, combat actions, dash/block/parry, facing, life-index progression, damage and healing intake.
- **Key Behaviors to Test:** HP bounds; life loss on death; respawn/life transitions; cooldowns for dash and attacks; state transitions (movement, attack, block, parry, hurt); invulnerability windows; interaction with hazards and enemy hits.
- **Possible Edge Cases:** HP at 0; healing at full HP; simultaneous damage and heal; last life; frame-boundary damage.
- **Testing Type Tag:** UNIT, INTEGRATION, REGRESSION

### Component: Enemy base & shared enemy contracts (`entities/enemy_base.py` and subclasses)

- **Responsibility:** Common enemy lifecycle: HP, activation, death, contact with player/projectiles, AI hooks.
- **Key Behaviors to Test:** Spawn alive; take damage; die and remove from combat set; elite/normal distinctions if applicable.
- **Possible Edge Cases:** Kill on same frame as room transition; damage after death; zero-HP enemies.
- **Testing Type Tag:** UNIT, INTEGRATION, REGRESSION

### Component: Swarm (`entities/swarm.py`)

- **Responsibility:** Swarm-type enemy behavior and parameters.
- **Key Behaviors to Test:** Movement, attack patterns, damage to player, death handling.
- **Possible Edge Cases:** Many instances; overflow spawn counts.
- **Testing Type Tag:** UNIT, INTEGRATION

### Component: Flanker (`entities/flanker.py`)

- **Responsibility:** Flanker-type positioning and attack behavior.
- **Key Behaviors to Test:** Approach logic, attack timing, damage application.
- **Possible Edge Cases:** Stuck on geometry; rapid oscillation near player.
- **Testing Type Tag:** UNIT, INTEGRATION

### Component: Brute (`entities/brute.py`)

- **Responsibility:** Brute-type heavy melee behavior.
- **Key Behaviors to Test:** Attack windup/cooldowns, damage zones, HP pool.
- **Possible Edge Cases:** Overlapping hitboxes with other entities.
- **Testing Type Tag:** UNIT, INTEGRATION

### Component: Heavy (`entities/heavy.py`)

- **Responsibility:** Heavy-type enemy (armor/tank role per design).
- **Key Behaviors to Test:** Reduced damage or extended HP behavior; attack patterns.
- **Possible Edge Cases:** Elite modifiers stacking with base stats.
- **Testing Type Tag:** UNIT, INTEGRATION

### Component: Ranged (`entities/ranged.py`)

- **Responsibility:** Ranged enemy attacks and projectile interaction.
- **Key Behaviors to Test:** Firing cadence, projectile spawn, collision with player/environment.
- **Possible Edge Cases:** Projectiles after shooter death; off-screen firing.
- **Testing Type Tag:** UNIT, INTEGRATION, REGRESSION

### Component: Projectile (`entities/projectile.py`)

- **Responsibility:** Projectile movement, lifetime, collision, damage.
- **Key Behaviors to Test:** Travel, despawn, hit registration, friendly/enemy ownership.
- **Possible Edge Cases:** Multiple hits one frame; despawn same frame as collision.
- **Testing Type Tag:** UNIT, INTEGRATION, CONCURRENCY

### Component: MiniBoss (`entities/mini_boss.py`)

- **Responsibility:** Biome 1 (or primary) mini-boss encounter entity.
- **Key Behaviors to Test:** Phase or pattern behavior; defeat condition; rewards tied to clear.
- **Possible Edge Cases:** Defeat during room transition; duplicate spawn.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: MiniBoss2 (`entities/mini_boss_2.py`)

- **Responsibility:** Secondary mini-boss variant.
- **Key Behaviors to Test:** Same class of tests as MiniBoss with variant-specific patterns.
- **Possible Edge Cases:** Wrong biome/room pairing.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: Biome3MiniBoss (`entities/biome3_miniboss.py`)

- **Responsibility:** Biome 3 mini-boss entity.
- **Key Behaviors to Test:** Biome-specific patterns; victory/defeat hooks.
- **Possible Edge Cases:** State desync with room controller.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: FinalBoss (`entities/final_boss.py`)

- **Responsibility:** Final boss encounter logic and end-of-run conditions.
- **Key Behaviors to Test:** Win/lose linkage to campaign end; phase transitions if any; damage gates.
- **Possible Edge Cases:** Early kill exploits; timeout vs boss death ordering.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: TrainingDummy (`entities/training_dummy.py`)

- **Responsibility:** Non-hostile or test target for combat calibration.
- **Key Behaviors to Test:** Damage absorption without breaking invariants; optional reset.
- **Possible Edge Cases:** Counted as kill incorrectly in metrics.
- **Testing Type Tag:** UNIT, REGRESSION

---

## 2. GAMEPLAY SYSTEMS

### Component: Combat system (`systems/combat.py`)

- **Responsibility:** Resolves attacks, hit detection, damage application between player and enemies.
- **Key Behaviors to Test:** Hitbox overlap; damage amounts; attack cooldown interaction; kill registration.
- **Possible Edge Cases:** Double-hit one swing; hits after entity removal list mutation.
- **Testing Type Tag:** UNIT, INTEGRATION, CONCURRENCY, REGRESSION

### Component: Collisions (`systems/collisions.py`)

- **Responsibility:** Broad/narrow phase collision between game objects and world.
- **Key Behaviors to Test:** Wall sliding; entity–entity overlap rules; trigger volumes.
- **Possible Edge Cases:** Tunneling at high speed; corner cases on tile boundaries.
- **Testing Type Tag:** UNIT, INTEGRATION

### Component: Movement (`systems/movement.py`)

- **Responsibility:** Position updates, speed modifiers, dash integration.
- **Key Behaviors to Test:** Velocity caps; slow tiles vs dash; facing updates.
- **Possible Edge Cases:** Movement during stun/hitstop if present.
- **Testing Type Tag:** UNIT, INTEGRATION

### Component: Animation (`systems/animation.py`)

- **Responsibility:** Sprite/frame timing for entities.
- **Key Behaviors to Test:** Frame index bounds; loop vs one-shot; sync with combat frames.
- **Possible Edge Cases:** Animation end vs state exit race.
- **Testing Type Tag:** UNIT, REGRESSION

### Component: VFX (`systems/vfx.py`)

- **Responsibility:** Visual effects spawning and lifetime (non-gameplay-critical but tied to events).
- **Key Behaviors to Test:** Spawn on hit/death; cleanup; no gameplay side effects if documented.
- **Possible Edge Cases:** VFX leak if scene ends mid-effect.
- **Testing Type Tag:** UNIT, INTEGRATION

### Component: Health system (player + enemies via entity HP)

- **Responsibility:** HP changes, healing, death transitions.
- **Key Behaviors to Test:** Clamp HP to max; healing orbs; safe-room heal; life decrement vs HP.
- **Possible Edge Cases:** Overheal; heal on death frame; fractional HP if used.
- **Testing Type Tag:** UNIT, INTEGRATION, REGRESSION

### Component: Gameplay reward / metrics hooks (kills, room clear, victory/defeat)

- **Responsibility:** `MetricsTracker` and game scene tie combat outcomes and progression to logged metrics and RL-related counters.
- **Key Behaviors to Test:** Increment on kill; room clear event; victory/defeat flags; no double-count.
- **Possible Edge Cases:** Kill credited after room unload; reinforcement kill attribution.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: RL step reward (`rl/reward.py`) — gameplay-facing

- **Responsibility:** Computes dense per-step reward from game snapshots for training (not manual play mutation).
- **Key Behaviors to Test:** Breakdown sums; terminal once-only; stall penalty; interact/heal success counters feeding reward.
- **Possible Edge Cases:** Reward on reset boundary; timeout truncation vs `TimeoutPenaltyWrapper` ordering.
- **Testing Type Tag:** UNIT, INTEGRATION, REGRESSION

---

## 3. GAME STATE & LOGIC

### Component: Player state model — DOMINATING / STABLE / STRUGGLING (`game/ai/player_model.py`)

- **Responsibility:** Classifies player situation from HP loss bands and related inputs for AI Director.
- **Key Behaviors to Test:** Threshold crossings; stable boundary cases; deterministic classification for same inputs.
- **Possible Edge Cases:** Exact threshold equality; single-frame spike damage; missing metrics.
- **Testing Type Tag:** UNIT, REGRESSION

### Component: MetricsTracker (`game/ai/metrics_tracker.py`)

- **Responsibility:** Aggregates run/room stats: damage, clears, RL interact/heal counts, director-relevant fields.
- **Key Behaviors to Test:** Monotonicity where defined; reset on new run; per-room vs run totals.
- **Possible Edge Cases:** Double increment on same event; reset partially applied.
- **Testing Type Tag:** UNIT, INTEGRATION, REGRESSION

### Component: Game progression — `RoomController` (`dungeon/room_controller.py`)

- **Responsibility:** Current room index, transitions, door linkage, campaign flow across biomes/sequences.
- **Key Behaviors to Test:** Advance to next room; boss room flags; prevent skip; sync with scene.
- **Possible Edge Cases:** Transition during combat active; duplicate advance.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: Room definitions — biome rooms & sequences (`dungeon/biome*_rooms.py`, `dungeon/biome*_sequence.py`, `dungeon/srs_biome_order.py`)

- **Responsibility:** Data/layout for room order, types, and biome boundaries per SRS.
- **Key Behaviors to Test:** Expected room count; type assignment; seed reproducibility for generation paths.
- **Possible Edge Cases:** Off-by-one last room; missing safe room where required.
- **Testing Type Tag:** UNIT, INTEGRATION, REGRESSION

### Component: Seeded encounter specs (`dungeon/seeded_encounter_specs.py`)

- **Responsibility:** Deterministic encounter parameters from seed.
- **Key Behaviors to Test:** Same seed → same spec; bounds on enemy counts/types.
- **Possible Edge Cases:** Seed edge values; missing spec fallback.
- **Testing Type Tag:** UNIT, REGRESSION

### Component: Victory / defeat / death phases (`game/scenes/game_scene.py` integration)

- **Responsibility:** Ends run on player death or final victory; drives scene transitions.
- **Key Behaviors to Test:** Single terminal outcome; correct trigger on boss defeat vs player death.
- **Possible Edge Cases:** Victory and death same frame; pause during terminal state.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: Safe room logic (`dungeon/room.py`, safe-room flows in `game_scene` / upgrades)

- **Responsibility:** Safe room entry, heal offers, upgrade choice, door unlock after rules.
- **Key Behaviors to Test:** Heal percentage; upgrade selection persistence; door state when leaving.
- **Possible Edge Cases:** Choice spam; full HP heal attempt; overlapping safe-room triggers.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: Game config (`game/config.py`)

- **Responsibility:** Global tuning: cooldowns, HP, timings, campaign constants.
- **Key Behaviors to Test:** Values within expected ranges; hot-reload not assumed—load once consistency.
- **Possible Edge Cases:** Zero or negative if misconfigured.
- **Testing Type Tag:** UNIT, REGRESSION

---

## 4. AI / DIRECTOR SYSTEM

### Component: AIDirector (`game/ai/ai_director.py`)

- **Responsibility:** Maps `PlayerModel` state and params to difficulty knobs: modifiers, enemy adjustments, reinforcement chances, biome-specific snapshot fields.
- **Key Behaviors to Test:** Deterministic outputs for fixed inputs; snapshot immutability during room; update only at defined boundaries.
- **Possible Edge Cases:** Unknown player state; neutral default snapshot.
- **Testing Type Tag:** UNIT, INTEGRATION, REGRESSION

### Component: DifficultyParams & JSON load (`game/ai/difficulty_params.py`, `config/difficulty_params.json`)

- **Responsibility:** Typed schema and load of runtime difficulty configuration.
- **Key Behaviors to Test:** Parse valid JSON; reject or clamp invalid; frozen/immutable usage where specified.
- **Possible Edge Cases:** Missing keys; extra keys; path resolution from different CWD.
- **Testing Type Tag:** UNIT, REGRESSION

### Component: Biome spawn helpers (`game/ai/biome1_director_spawn.py` … `biome4_director_spawn.py`)

- **Responsibility:** Biome-specific spawn composition using director snapshot and seeds.
- **Key Behaviors to Test:** Spawn counts within bounds; elite/ranged bias application; deterministic with seed.
- **Possible Edge Cases:** Snapshot stale vs current room; zero enemies.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: AI logger (`game/ai/ai_logger.py`)

- **Responsibility:** Structured logging for director/metrics for offline analysis.
- **Key Behaviors to Test:** Log lines emitted on key events; no crash on missing optional fields.
- **Possible Edge Cases:** High-frequency spam; disk failure not required in unit scope.
- **Testing Type Tag:** INTEGRATION

### Component: Offline RL dataset / reward eval (`game/rl/dataset_export.py`, `reward_eval.py`, `offline_tuning_spec.py`)

- **Responsibility:** Export and evaluate logged data for offline tuning (not runtime learning).
- **Key Behaviors to Test:** CSV/JSONL shape; deterministic scores on fixed input files.
- **Possible Edge Cases:** Empty logs; malformed rows.
- **Testing Type Tag:** UNIT, REGRESSION

---

## 5. ENVIRONMENT / WORLD

### Component: Room model (`dungeon/room.py`)

- **Responsibility:** Room metadata: index, type, hazards, dimensions, controller hooks.
- **Key Behaviors to Test:** Type enum consistency; hazard percentage bounds; pixel size positive.
- **Possible Edge Cases:** Invalid room type string; zero size.
- **Testing Type Tag:** UNIT, REGRESSION

### Component: Door system (`dungeon/door_system.py`)

- **Responsibility:** Locked/unlocked state, delay after clear, forward progression linkage.
- **Key Behaviors to Test:** Locked during combat; unlock after clear with delay; safe-room door variant behavior if distinct.
- **Possible Edge Cases:** Clear signal twice; player at door before unlock.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: Hazard system (`dungeon/hazard_system.py`)

- **Responsibility:** Lava/slow tiles, damage per second, placement by room.
- **Key Behaviors to Test:** Damage ticks; animation FPS; slow factor application; seed-stable layout.
- **Possible Edge Cases:** Standing on tile boundary; hazard off during transition.
- **Testing Type Tag:** UNIT, INTEGRATION, REGRESSION

### Component: Spawn system (`systems/spawn_system.py`, `spawn_helper.py`)

- **Responsibility:** Instantiates enemies from directives; timing/delay profiles.
- **Key Behaviors to Test:** Spawn list matches spec; reinforcements; despawn on clear.
- **Possible Edge Cases:** Spawn during pause; max enemy cap overflow.
- **Testing Type Tag:** INTEGRATION, CONCURRENCY, REGRESSION

### Component: Biome4 visuals (`dungeon/biome4_visuals.py`)

- **Responsibility:** Visual layering for biome 4 rooms (non-logic or minimal logic).
- **Key Behaviors to Test:** Assets resolve; no exception on valid room.
- **Possible Edge Cases:** Missing asset fallback.
- **Testing Type Tag:** UNIT, REGRESSION

### Component: Asset loader (`game/asset_loader.py`)

- **Responsibility:** Loads sprites/sounds paths for scenes.
- **Key Behaviors to Test:** Cached load; missing file behavior.
- **Possible Edge Cases:** Case sensitivity on paths.
- **Testing Type Tag:** UNIT, REGRESSION

### Component: Scene manager (`game/scene_manager.py`)

- **Responsibility:** Switches scenes; drives update loop entry.
- **Key Behaviors to Test:** Single active scene; transition ordering.
- **Possible Edge Cases:** Re-entrant transition request.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: GameScene (`game/scenes/game_scene.py`)

- **Responsibility:** Main gameplay: entities list, update order, RL hooks, metrics, win/loss.
- **Key Behaviors to Test:** Update order player→enemies→combat; enemy list consistency; RL `rl_step` path vs keyboard path.
- **Possible Edge Cases:** Modify enemy list while iterating (documented iteration safety).
- **Testing Type Tag:** INTEGRATION, CONCURRENCY, REGRESSION

### Component: RNG (`game/rng.py`)

- **Responsibility:** Seeded randomness for variation.
- **Key Behaviors to Test:** Same seed → same stream; independence of sub-streams if designed.
- **Possible Edge Cases:** Seed None behavior.
- **Testing Type Tag:** UNIT, REGRESSION

---

## 6. RL / CONTROL LAYER

### Component: DungeonEnv (`rl/env.py`)

- **Responsibility:** Gymnasium API: reset, step, render modes, episode termination linkage to game.
- **Key Behaviors to Test:** Headless no display; observation shape/dtype; info dict keys; terminated on win/loss.
- **Possible Edge Cases:** Double reset; step after terminal without reset.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: Observation builder (`rl/obs.py`)

- **Responsibility:** Fixed-size vector from `GameScene` state.
- **Key Behaviors to Test:** No NaN/inf; stable length; normalization bounds.
- **Possible Edge Cases:** No enemies; final room; uninitialized scene.
- **Testing Type Tag:** UNIT, REGRESSION

### Component: Action map (`rl/action_map.py`)

- **Responsibility:** Discrete actions to game inputs including interact/heal extensions.
- **Key Behaviors to Test:** Index bounds; mapping stable across versions.
- **Possible Edge Cases:** Action during invalid UI state.
- **Testing Type Tag:** UNIT, REGRESSION

### Component: PPO training/eval/demo scripts (`rl/train_ppo.py`, `eval_ppo.py`, `demo_ppo.py`)

- **Responsibility:** SB3 training, evaluation, human demo entrypoints.
- **Key Behaviors to Test:** Resume loads weights; eval seeds; TimeLimit alignment.
- **Possible Edge Cases:** Missing model path; zero timesteps.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: Wrappers (`rl/wrappers.py`)

- **Responsibility:** Timeout penalty after `TimeLimit` truncation for training/eval.
- **Key Behaviors to Test:** Penalty only when `truncated`; reward breakdown key present.
- **Possible Edge Cases:** Wrapper order with `TimeLimit`.
- **Testing Type Tag:** UNIT, INTEGRATION, REGRESSION

### Component: Curriculum wrappers (`rl/curriculum_wrappers.py`)

- **Responsibility:** Scenario selection; curriculum success detection via metrics; min-step gating before success bonus/termination.
- **Key Behaviors to Test:** Correct scenario in `info`; success fires once; bonus applied.
- **Possible Edge Cases:** Success on step 1 vs min steps; wrong scenario string.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: Best progression callback (`rl/best_progress_callback.py`)

- **Responsibility:** Eval callback saving best checkpoint by progression metric; optional early stop.
- **Key Behaviors to Test:** Saves on improvement; patience decrement; no save when eval off.
- **Possible Edge Cases:** Tie scores; eval fails mid-run.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: Experiment layout (`rl/experiment_layout.py`, `curriculum_layout.py`)

- **Responsibility:** Paths for models/logs per experiment/stage.
- **Key Behaviors to Test:** Resolved paths exist parent dirs; no path traversal.
- **Possible Edge Cases:** Special characters in experiment name.
- **Testing Type Tag:** UNIT, REGRESSION

### Component: Headless mode (`rl/headless.py`)

- **Responsibility:** Suppresses display updates for RL.
- **Key Behaviors to Test:** No display calls when headless; logic still runs.
- **Possible Edge Cases:** Toggle mid-session if unsupported.
- **Testing Type Tag:** INTEGRATION, REGRESSION

---

## 7. CONCURRENCY / TIMING

### Component: Main game loop ordering (`scene_manager` + `game_scene.update`)

- **Responsibility:** Single-threaded frame update; order of physics, combat, AI, cleanup.
- **Key Behaviors to Test:** Deterministic frame order for fixed inputs; no partial updates exposed to player.
- **Possible Edge Cases:** Deferred removals; list copy during enemy update.
- **Testing Type Tag:** CONCURRENCY, INTEGRATION

### Component: Shared mutable collections — enemy list / projectile list

- **Responsibility:** Runtime lists mutated during update; combat may remove entities.
- **Key Behaviors to Test:** Iterator safety patterns; no use-after-remove.
- **Possible Edge Cases:** Nested removal; spawn mid-iteration.
- **Testing Type Tag:** CONCURRENCY, INTEGRATION, REGRESSION

### Component: Cooldown and timer systems (player + enemies + global delays)

- **Responsibility:** Frame-based or dt-based countdowns for attacks, door unlock, hazard tick.
- **Key Behaviors to Test:** Monotonic decrease; expiry exactly once; pause behavior if any.
- **Possible Edge Cases:** Large dt spike; zero dt.
- **Testing Type Tag:** UNIT, INTEGRATION, REGRESSION

### Component: Spawn delay / reinforcement timing

- **Responsibility:** Late spawns during combat; reinforcement waves.
- **Key Behaviors to Test:** Triggers only after conditions; cap on living enemies.
- **Possible Edge Cases:** Reinforcement after room clear flag.
- **Testing Type Tag:** INTEGRATION, CONCURRENCY, REGRESSION

### Component: RL environment step vs real-time

- **Responsibility:** Fixed dt steps for RL; no wall-clock coupling.
- **Key Behaviors to Test:** Identical steps for identical actions/seed.
- **Possible Edge Cases:** Floating-point dt accumulation.
- **Testing Type Tag:** UNIT, REGRESSION

### Component: Threading / locks (current architecture)

- **Responsibility:** Core gameplay loop is single-threaded; training usually separate process.
- **Key Behaviors to Test:** Absence of blocking waits between game entities in one frame; no re-entrant lock on update path if any lock exists in libraries.
- **Possible Edge Cases:** Future multithreaded asset streaming or RL inference thread.
- **Testing Type Tag:** DEADLOCK

### Component: Metrics / reward snapshot timing (`rl/reward.py` before/after update)

- **Responsibility:** Snapshots bracket `SceneManager.update` for reward deltas.
- **Key Behaviors to Test:** Consistent pre/post snapshots; breakdown matches step reward.
- **Possible Edge Cases:** Mismatch if update throws; partial update.
- **Testing Type Tag:** INTEGRATION, REGRESSION

---

## 8. KNOWN EDGE CASES / BUG-PRONE AREAS

### Component: Enemy removal / disappearance

- **Responsibility:** Enemies leave combat set on death; cleanup from lists and AI targeting.
- **Key Behaviors to Test:** No ghost hits; minimap/count consistency.
- **Possible Edge Cases:** Death animation longer than removal; reference held elsewhere.
- **Testing Type Tag:** INTEGRATION, REGRESSION, CONCURRENCY

### Component: Door unlock vs combat state

- **Responsibility:** Doors remain locked until room clear conditions met.
- **Key Behaviors to Test:** Cannot exit while enemies alive; unlock after delay post-clear.
- **Possible Edge Cases:** Last enemy dies same frame as player death.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: Overlapping events (damage + heal + hazard)

- **Responsibility:** Order of application affects final HP and metrics.
- **Key Behaviors to Test:** Documented precedence; single net HP change per substep if applicable.
- **Possible Edge Cases:** Healing orb + lava same frame.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: State inconsistency — director snapshot vs current room

- **Responsibility:** Snapshot for **next** room should not mutate mid-fight for **current** room.
- **Key Behaviors to Test:** Frozen snapshot during encounter; update only at room boundaries.
- **Possible Edge Cases:** Player state flips mid-room affecting wrong spawn set.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: RL interact / safe-heal metrics vs gameplay UI

- **Responsibility:** Counters for E/F success must align with actual game events (story, heal applied).
- **Key Behaviors to Test:** Failed spam increments separate counters; success increments once per real event.
- **Possible Edge Cases:** Curriculum eval vs full-game action distribution mismatch.
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: Curriculum merge / transfer checkpoints

- **Responsibility:** Policies trained under one distribution may fail on full-game eval (observed in project eval artifacts).
- **Key Behaviors to Test:** Smoke eval after merge; action histogram sanity.
- **Possible Edge Cases:** Degenerate policy (single action dominance).
- **Testing Type Tag:** INTEGRATION, REGRESSION

### Component: Debug overlay (`game/debug/debug_overlay.py`)

- **Responsibility:** Optional visualization of AI/debug state.
- **Key Behaviors to Test:** Toggle does not alter gameplay RNG or state when disabled.
- **Possible Edge Cases:** Overlay on during screenshots affecting performance only.
- **Testing Type Tag:** INTEGRATION, REGRESSION
