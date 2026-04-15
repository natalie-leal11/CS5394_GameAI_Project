# Recommended Test Additions

Prioritized additions only (highest value for final submission confidence).

## Priority 1 (Add First)

1. **Checkpoint respawn progression integration test**
   - Cover `GameScene` checkpoint update after mini-boss clears (7/15/23 -> 8/16/24), life-loss respawn at checkpoint, and HP tier handling.
   - Why first: high gameplay risk and currently uncovered.

2. **Seeded encounter specs concrete variant tests**
   - Replace current smoke/skips with deterministic assertions per biome and per variant (0/1/2), including invariant checks.
   - Why first: seed prompt pack core requirement and currently weak/uncovered.

3. **Safe-room biome upgrade behavior integration test**
   - Validate one-choice selection rule, biome-specific pick counts/options, and Director bias not forcing final selection.
   - Why first: explicitly required by prompt pack and currently uncovered.

4. **Final boss phase/revive deterministic sequence test**
   - Validate phase threshold, revive timing, cooldown/telegraph multiplier behavior, and deterministic cycle progression.
   - Why first: final-submission critical path; current tests are mostly smoke.

5. **Seed replayability log-consistency test**
   - Run same seed twice, compare procedural summaries (room order/specs/spawn summaries), verify fixed milestones unchanged and logs deterministic.
   - Why first: directly ties to seed determinism prompt requirements.

---

## Priority 2 (Add Next)

6. **PlayerModel boundary and life-phase override unit tests**
   - Threshold edges + life-index override checks.

7. **MetricsTracker rolling-window + room lifecycle tests**
   - Last-3 behavior, reinforcement metadata, and end-room result classification edges.

8. **Ranged AI behavior unit tests**
   - Kiting/spacing/cooldown/projectile cadence beyond smoke.

9. **AI logger content completeness tests**
   - Validate required fields for Director/seed analysis and no runtime feedback loop.

10. **RL runtime boundary policy tests**
   - Verify no online-learning runtime imports and deterministic config-loading pathway constraints.

---

## Suggested Minimal Implementation Strategy

- Keep additions focused and deterministic (no broad harness rewrite).
- Prefer:
  - 2-3 high-value integration tests (`GameScene`/campaign flow)
  - 4-6 tight unit tests (`seeded_encounter_specs`, `player_model`, `final_boss`, `ranged`)
- Defer large end-to-end scenario only after Priority 1 is green.
