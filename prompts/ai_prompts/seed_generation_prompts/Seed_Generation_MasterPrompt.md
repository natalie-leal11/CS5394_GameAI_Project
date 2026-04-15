# MASTER PROMPT — Seed Generation Integration Pack (Seed-Only Scope)

Use this prompt pack to implement or verify seed-controlled procedural variation only.
Do not modify this document while executing the phases.

This pack is scoped to:
- deterministic run-seed initialization and variant mapping
- deterministic room-order variation within fixed biome constraints
- deterministic encounter composition/spawn realization variation
- deterministic replay/logging verification for seed behavior

This pack is not for gameplay redesign.

---

## Source of Truth and Scope

Use existing implementation and seed-related project prompts/documents as source of truth.
If docs and code differ, preserve current repository behavior and existing SRS-aligned constraints.

Seed scope remains bounded to already implemented/documented behavior:
- finite variant model (`TOTAL_SEED_VARIANTS = 3`)
- fixed room structure constraints
- bounded room-order/encounter/spawn/hazard realization variation

---

## Seed System Contract

The seed system controls:
- run seed initialization and storage
- deterministic variant mapping (`variant_id = run_seed % 3`)
- deterministic per-room/per-channel derivation streams
- bounded procedural variation in legal slots

The seed system does not control:
- total room count
- fixed milestone positions (`START`, `MINI_BOSS`, `FINAL_BOSS`)
- room size/grid dimensions/core layout algorithms
- boss identity, boss phases, or core combat systems
- UI/menu/scene flow redesign

---

## Required Phase Order

Execute phases in order:
1. `Phase1_Seed_Overview.md`
2. `Phase2_Base_Seed_Architecture.md`
3. `Phase3_Seed_Variation_1.md`
4. `Phase4_Seed_Variation_2.md`
5. `Phase5_Seed_Variation_3.md`
6. `Phase6_Gameplay_Impact.md`
7. `Phase7_Determinism_and_Replayability.md`
8. `Phase8_Logging_and_Testing.md`
9. `Seed_Generation_Summary.md`

Stop after each phase and verify existing game behavior remains intact.

---

## Global Success Criteria

The pack is complete only if all are true:
- seed architecture is deterministic and centralized
- three implemented seed variants remain distinct
- room-order variation stays within fixed biome/milestone constraints
- encounter variation stays within allowed biome pools and count bounds
- safe-room placement/flow remains constrained and deterministic
- same seed + same input path yields same procedural outcomes
- logging supports offline verification and does not affect runtime decisions
