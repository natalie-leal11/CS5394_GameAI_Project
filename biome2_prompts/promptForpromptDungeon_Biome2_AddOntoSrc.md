# MASTER PROMPT — Dungeon Geeks (Biome 2 Add-On for `src/`)
# STRICT ADDITIVE GENERATION SYSTEM

You are generating structured, incremental coding prompts for adding **Biome 2 content** onto the existing `src/` codebase.

You MUST strictly follow the official Biome 2 reference document.
You MUST NOT invent gameplay systems, room rules, enemy timings, or healing behavior outside the reference.
You MUST preserve the existing Biome 1 engine behavior.
You MUST prefer **new files and additive registrations** over rewriting existing systems.
You MUST generate phase-based prompts only.

This is a graded academic project.

---

# 📘 OFFICIAL SOURCE OF TRUTH

All implementation must align with:

- `Biome2_Rooms_And_Rules_Reference.md`
- the existing `src/` architecture already present in the repository

If any ambiguity exists:
1. Follow `Biome2_Rooms_And_Rules_Reference.md`
2. Reuse the already-working Biome 1 engine patterns from `src/`
3. Prefer additive extension points rather than replacing existing behavior

---

# 🎯 IMPLEMENTATION GOAL

Biome 2 is an **extension pack** for the existing game, not a second engine.

Implement only the new Biome 2 content needed to support:

- the **Heavy** enemy type
- the **Biome 2 room sequence** (rooms 8–15)
- the **Biome 2 mini boss**, including **adds** support

Do **not** rebuild player, camera, rendering, menu flow, or basic combat architecture.
Reuse the existing `src/` systems wherever possible.

---

# 🚫 HARD CONSTRAINTS

You MUST:

- work inside `src/`, not `src2/`
- preserve existing Biome 1 behavior
- avoid broad rewrites
- avoid renaming existing files or folders
- avoid changing existing balance unless required for Biome 2 support
- avoid inventing asset paths not already implied by the current codebase
- keep deterministic seed behavior intact
- keep room progression deterministic when `BEGINNER_TEST_MODE = True`

You MUST NOT:

- create a second engine
- redesign the scene system
- redesign the movement system
- redesign the combat system
- modify unrelated Biome 1 gameplay code
- replace working Biome 1 enemy classes

---

# 🧱 ADDITIVE-ONLY RULE

Prefer the following order:

1. Add a new file
2. Add a new helper/registry/module
3. Add a narrow import/registration hook only if required
4. Touch existing code only when a tiny integration point is unavoidable

If an existing file must be touched, the change must be:
- minimal
- additive
- backwards-compatible
- clearly isolated to Biome 2 support

Do not refactor unrelated logic.

---

# 🧩 BIOME 2 CONTENT REQUIRED

From the reference document, Biome 2 must support:

- fixed beginner order for rooms **8–15**:
  - 8 Combat
  - 9 Combat
  - 10 Ambush
  - 11 Safe
  - 12 Combat
  - 13 Elite
  - 14 Ambush
  - 15 Mini Boss
- Heavy enemy in Combat 2 and Combat 3
- Mini Boss room at room 15
- Mini Boss defeat unlock delay = 0.5 s
- Safe room heal pickup rules
- clear-heal drop rules
- room-type wall border thickness rules
- room-type spawn pattern rules
- Biome 2 enemy roster and sizes

Use the exact values from the reference document.

---

# 🧩 PHASED GENERATION ORDER

PHASE 1 → Heavy enemy additive implementation for `src/`
PHASE 2 → Biome 2 room sequence / room-data additive implementation for `src/`
PHASE 3 → Biome 2 mini boss additive implementation for `src/`, including adds support

After each phase:
STOP.
Wait for user confirmation.

---

# OUTPUT RULE

Generate ONLY the coding prompt for the next phase.
Do not output explanations.
Do not output analysis.
Do not output the entire game.
