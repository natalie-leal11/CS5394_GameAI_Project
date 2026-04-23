# Missing Test Cases

## Unit-Level Gaps

### AI Director / Biome helpers

- Verify clamping at all boundary values for:
  - enemy count offsets
  - reinforcement caps
  - pacing/spacing multipliers
- Validate all forbidden-room filters (SAFE, MINI_BOSS, FINAL_BOSS where applicable) for every biome helper.
- Add deterministic idempotence tests for identical input snapshots across helper functions with edge inputs (empty/min/max specs).

### Player model / metrics

- Add threshold-boundary tests around `player_model` decision cutoffs (critical HP, weak HP, clean-clear minimum, fast clear average).
- Add explicit tests for life-phase override behavior (`life_index`, `recent_life_loss_flag`) beyond base v3 classification.
- Add stronger unit tests for `MetricsTracker`:
  - start/end room state transitions
  - last-3 rolling windows
  - reinforcement metadata append behavior
  - update-time accumulation (idle/hazard/near-far enemy splits)

### Seed determinism / variants

- Replace smoke/skipped tests in `tests/unit/test_seeded_encounter_specs.py` with concrete assertions for each biome builder.
- Add direct tests for `make_room_rng`, `sample_seeded_choice`, `sample_seeded_shuffle`, `sample_seeded_uniform`, `sample_seeded_int`.
- Add explicit variant identity tests (`run_seed % 3`) that verify distinct outputs for variant 0/1/2 while keeping invariants fixed.

### Ranged tuning

- Add unit tests for `Ranged.update`:
  - cooldown and projectile emission cadence
  - close/far/ideal-band movement mode transitions (kite/approach/strafe)
  - behavior under overlap/unstuck constraints

### Final boss internals

- Add unit tests for `FinalBoss`:
  - phase change at 50%
  - revive wait + invulnerability timing
  - deterministic cycle transitions
  - AI multiplier effects on telegraph/cooldown/recovery values

---

## Integration-Level Gaps

### Checkpoint and respawn

- Test mini-boss clear updates checkpoint:
  - room 7 -> checkpoint 8
  - room 15 -> checkpoint 16
  - room 23 -> checkpoint 24
- Test life-loss respawn reloads checkpoint room and applies expected life-tier HP behavior.
- Test checkpoint retry count/log fields update consistently after respawns.

### Safe-room upgrade flow

- Verify one-choice enforcement in safe room upgrade selection across Biome 3/4 flows.
- Verify biome-specific upgrade pick counts and allowed options.
- Verify Director bias changes option ordering/weights without forcing final choice.

### Seed replayability

- Integration check that two runs with same seed produce identical:
  - biome room order
  - encounter specs
  - spawn realization summaries
- Integration check that differing seeds alter only seed-controlled sections while fixed milestones remain constant.

### AI logger / deterministic trace

- Verify per-room logger entries include required fields from prompt packs:
  - seed, room/biome/type, player state, directive snapshot
- Verify logger output does not affect runtime behavior (no readback loop).

### RL runtime boundaries

- Add integration policy tests to ensure runtime scene path does not import/execute online training code paths.
- Verify runtime uses parameter loading contract and remains deterministic under fixed seeds.

---

## System-Level Gaps

- End-to-end deterministic replay scenario:
  - same seed + scripted action path -> identical AI/seed side decisions and terminal summary
- Long-run campaign transition scenario:
  - checkpoint progression, safe-room behavior, mini-boss transitions, final boss path
- Submission-level scenario test:
  - validates combined constraints from AI Director + seed generation + RL runtime guardrails in one report-producing run
