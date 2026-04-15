# Seed Generation Prompt Pack Summary

This pack isolates seed-controlled procedural variation from broader AI integration prompts and keeps seed-variation execution split into separate phases.

---

## Scope Captured

The pack defines:
- what the seed system controls (bounded deterministic variation)
- what it does not control (fixed structure, bosses, core systems)
- base run-seed + variant architecture
- three separate implemented variant phases
- gameplay impact, determinism/replay, and logging/testing boundaries

---

## Phase Map

1. `Phase1_Seed_Overview.md`
2. `Phase2_Base_Seed_Architecture.md`
3. `Phase3_Seed_Variation_1.md` (`Balanced`)
4. `Phase4_Seed_Variation_2.md` (`Combat-heavy / Pressure`)
5. `Phase5_Seed_Variation_3.md` (`Ambush-heavy / Spike`)
6. `Phase6_Gameplay_Impact.md`
7. `Phase7_Determinism_and_Replayability.md`
8. `Phase8_Logging_and_Testing.md`
9. `Seed_Generation_Summary.md`

---

## Variation Differences

- `Balanced`: baseline implementation-aligned ordering/composition tendencies
- `Combat-heavy / Pressure`: stronger pressure-forward tendencies within legal bounds
- `Ambush-heavy / Spike`: stronger ambush/spike tendencies within legal bounds

All variants remain deterministic and constrained by biome pools, room-type bounds, and fixed structural invariants.

---

## Final Validation Questions

- Are all seed outputs deterministic for same seed and input path?
- Are fixed structure constraints preserved?
- Are variant phases separate and meaningfully distinct?
- Are logs sufficient for offline replay verification only?
