# AI Director Prompt Pack Summary

This pack isolates AI Director responsibilities from the larger system integration prompts and keeps biome execution split into separate phases.

---

## Scope Captured

The pack defines:
- what the Director controls (bounded high-level adaptation)
- what inputs it uses (metrics, player model state, params, seed-driven context)
- what it does not control (boss mechanics, UI flow, core combat, architecture redesign)
- deterministic and logging boundaries (offline analysis only; no runtime feedback loop)

---

## Phase Map

1. `Phase1_AI_Director_Overview.md`
2. `Phase2_Metrics_and_PlayerModel.md`
3. `Phase3_Director_Core_Decision_Logic.md`
4. `Phase4_Biome1_Director_Behavior.md`
5. `Phase5_Biome2_Director_Behavior.md`
6. `Phase6_Biome3_Director_Behavior.md`
7. `Phase7_Biome4_Director_Behavior.md`
8. `Phase8_Encounter_and_SafeRoom_Adjustments.md`
9. `Phase9_Logging_and_Determinism.md`
10. `AI_Director_Summary.md`

---

## Biome Phase Differences

- Biome 1: foundational adaptation with `Swarm`/`Flanker`/`Brute`, light bounded adjustments
- Biome 2: adds `Heavy` and stronger pressure/composition/reinforcement shaping
- Biome 3: adds `Ranged` and hazard/ranged-pressure-aware adaptation, limited mini-boss nudges only
- Biome 4: highest bounded pressure, pacing bias, and small legal final-boss tuning with fairness constraints

---

## Final Validation Questions

- Are all Director decisions deterministic and bounded?
- Are biome phases separate and aligned with documented enemy/room constraints?
- Is safe-room influence bias-only with one player-selected upgrade preserved?
- Are boss mechanics and non-AI systems untouched?
- Do logs support offline analysis without influencing runtime gameplay?
