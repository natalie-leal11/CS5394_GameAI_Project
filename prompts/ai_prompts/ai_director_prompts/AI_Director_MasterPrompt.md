# MASTER PROMPT — AI Director Integration Pack (Director-Only Scope)

Use this prompt pack to implement or verify AI Director behavior only.
Do not modify this document while executing the phases.

This pack is scoped to:
- deterministic AI Director planning
- deterministic use of metrics and player state
- bounded encounter and safe-room directives
- deterministic logging and verification boundaries

This pack is not for redesigning the game.

---

## Source of Truth and Scope

Use existing project implementation and prompts as source of truth.
If source documents disagree, prioritize repository behavior and SRS-aligned constraints already used by this project.

Keep scope limited to AI Director responsibilities already documented:
- high-level encounter and safe-room adaptation
- no per-enemy AI behavior control
- no runtime learning

---

## Core Director Contract

The AI Director:
- reads game context, metrics summaries, player model state, fixed parameters, and seed-driven helpers
- outputs bounded high-level directives
- stays deterministic for same seed and same input path

The AI Director does not:
- redesign room flow, UI flow, assets, bosses, or core combat systems
- alter dungeon structure, milestone positions, or hazard caps outside allowed bounded adjustments
- run online learning
- use unseeded randomness

---

## Required Phase Order

Execute phases in order:
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

Stop after each phase and verify existing game behavior remains intact.

---

## Global Success Criteria

The pack is complete only if all are true:
- AI Director remains a high-level deterministic meta-layer
- directives are bounded and parameter-driven
- biome-specific behavior remains separated by biome phase and uses existing enemy sets/room constraints
- safe-room influence remains biasing, not forced selection
- same seed + same input path gives same AI-side directives
- logs support offline analysis and do not affect gameplay
