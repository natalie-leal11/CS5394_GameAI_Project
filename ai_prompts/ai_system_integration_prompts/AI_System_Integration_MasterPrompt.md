# MASTER PROMPT — Existing `src` Integration for AI Director + Seed-Controlled Variation + Player Model
# STRICT SRS-FIRST INTEGRATION PACK

Open and execute the repo file
AI_System_Integration_MasterPrompt.md
exactly as written. Do not modify this document.

You are integrating three systems into an EXISTING Python/Pygame codebase that already runs:
1. AI Director
2. Seed-Controlled Variation
3. Player Model

This prompt pack is for INTEGRATION ONLY.
Do NOT rebuild the game.
Do NOT replace the current architecture.
Do NOT redesign the menu, controls, room art, start screen, victory screen, room types, biome visuals, boss assets, or existing player/combat systems unless a change is directly required to integrate the three AI systems.

---

## OFFICIAL SOURCE OF TRUTH

If the documents disagree:
1. `AI_Dungeon_ProjSRS.md` has final authority.
2. `AI_Dungeon_ProjGuide(v2).md` is secondary guidance.
3. `AI_Dungeon_Parameters_discuss_FULL.md` is supporting detail.

---

## EXISTING REPOSITORY CONTRACT (MANDATORY)

This pack MUST work off the existing `src` code already present in Cursor.

The existing repository already contains paths such as:
- `src/game/main.py`
- `src/game/scene_manager.py`
- `src/game/scenes/game_scene.py`
- `src/dungeon/room_controller.py`
- `src/systems/spawn_system.py`
- `src/entities/...`

You MUST preserve the existing playable game loop and integrate into it.

### Preserve all existing non-AI systems
The following are OUT OF SCOPE for redesign:
- asset paths and asset bindings
- room art / props / backgrounds
- start screen / controls / settings screens
- existing room types
- existing biome sequence and milestone positions
- existing boss art / boss room visuals
- existing player controls and core attacks
- unrelated UI polish

Only edit them when strictly necessary to hook in:
- AI Director
- Seed-Controlled Variation
- Player Model
- logging/determinism verification

---

## ARCHITECTURAL RULES

1. Integrate with the existing `src` structure. Do not introduce a second parallel game architecture.
2. Prefer adding small focused modules and wiring them into existing classes.
3. Preserve current imports and run command conventions already used by the repo.
4. Do not rename major existing files.
5. Do not mass-refactor unrelated gameplay systems.
6. New AI systems must be deterministic.
7. AI Director must be high-level only; it must not directly control per-enemy AI behavior.
8. Runtime RL is forbidden. Runtime may only load fixed parameters.
9. Seed-controlled variation must not change:
   - total room count
   - milestone positions
   - hazard caps
   - room type support
10. Safe-room upgrade resolution must remain:
   - present multiple options
   - player selects exactly one

---

## IMPLEMENTATION GOAL

Add the three AI-related systems so that the current game keeps its existing behavior everywhere else, while gaining:

- deterministic seed-derived encounter variation
- deterministic player metrics tracking
- deterministic player state classification
- deterministic AI Director decisions
- bounded encounter/safe-room adaptation
- offline-only logging for later tuning

---

## PHASE EXECUTION ORDER

Execute these files in this exact order and stop after each one:

1. `Phase0_Repository_Contract_and_NonAI_Preservation.md`
2. `Phase1_Seed_RNG_Adapter.md`
3. `Phase2_Metrics_and_PlayerModel_Integration.md`
4. `Phase3_AIDirector_Foundation_Integration.md`
5. `Phase4_Encounter_and_SafeRoom_Wiring.md`
6. `Phase5_Logging_Determinism_Verification.md`

After each phase:
- run the game using the same existing command/environment that already works in this repository
- fix any runtime/import errors before continuing
- do not proceed if the game no longer launches

---

## SUCCESS CRITERIA

The integration is complete only if all are true:

- existing game still launches and plays
- room count remains 30
- room 0 remains start
- room 29 remains final boss
- existing non-AI screens and assets still work
- same seed + same inputs produce identical AI-side decisions
- AI Director decisions are bounded and deterministic
- player state classification is deterministic
- safe room logic remains one-upgrade-selected by the player
- logging exists for offline analysis only
- no online learning occurs

STOP AFTER READING THIS MASTER PROMPT.
Then begin PHASE 0 only.
