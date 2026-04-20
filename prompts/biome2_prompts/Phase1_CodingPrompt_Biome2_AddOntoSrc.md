# Phase 1 — Incremental Coding Prompt
# Additive Heavy Enemy Support in `src/`

Implement **only** the following. Do not add Biome 2 room progression or mini boss logic yet. Stop when this phase is complete.

---

## 1. Scope

- **Phase 1 deliverables:** additive Biome 2 **Heavy** enemy support inside the existing `src/` codebase.
- **Source of truth:** `Biome2_Rooms_And_Rules_Reference.md`.
- **Architecture rule:** preserve the existing Biome 1 engine and add only what is necessary for Heavy support.

---

## 2. Additive-only implementation rule

You must preserve the existing Biome 1 behavior.

Preferred approach:
- add a new enemy file such as `src/entities/heavy.py`
- add any narrow config constants needed for Heavy
- extend existing enemy registries/maps only if unavoidable
- do not rewrite player, movement, combat, or rendering systems

Any edits to existing files must be tiny, additive, and backwards-compatible.

---

## 3. Heavy enemy requirements

Add a new Biome 2 enemy type:

- **Type:** Heavy
- **Class name:** `Heavy`
- **Base HP:** 60
- **Base damage:** 16
- **Size:** 88×88
- **Role:** Heavy armored enemy

Reference values come directly from the Biome 2 reference.

---

## 4. Behavior requirements

Heavy should reuse the existing enemy architecture and conventions already used in `src/entities/`.

Implement Heavy so that it:
- fits into the same enemy update/render/combat flow as existing enemies
- has a stable `enemy_type` identifier such as `"heavy"`
- exposes the same expected surface API as other enemies
- uses existing animation-loading conventions from `src/entities/enemy_base.py`
- supports elite mode if the current base enemy system supports elite modifiers generically

Do not invent a brand-new enemy framework.

---

## 5. Asset-loading rule

Use the same asset-loading pipeline already used by the existing enemy classes in `src/`.

Do not invent new loader logic.
Do not add direct `pygame.image.load` calls outside the centralized loader pattern already used by the codebase.

If the Heavy asset directory is not present, preserve the project’s existing fallback behavior.

---

## 6. Config/constants rule

Add only the Heavy-specific constants needed for compatibility with the current architecture, following the naming style already present in `src/game/config.py`.

Examples of the kinds of constants that may be needed:
- size
- base HP
- base damage
- move speed
- stop distance
- attack radius
- attack offset
- attack cooldown

Do not rebalance existing Swarm, Flanker, Brute, or Mini Boss values in this phase.

---

## 7. Registration rule

If the existing codebase uses:
- enemy type tuples
- enemy priority maps
- separation maps
- per-type size/stat lookup helpers
- import registries

then extend them minimally to include Heavy.

Do not remove or rename existing entries.

---

## 8. Out of scope for this phase

Do **not** implement any of the following yet:
- Biome 2 room sequence
- room 8–15 progression
- safe room pickup logic
- mini boss room logic
- mini boss adds
- Biome 2-specific spawn tables

This phase is only for additive Heavy support.

---

## 9. Checklist

- [ ] `src/entities/heavy.py` exists
- [ ] Heavy is compatible with the existing enemy framework in `src/`
- [ ] Heavy constants are added minimally and cleanly
- [ ] Existing enemy behavior is preserved
- [ ] Any registry/helper changes are additive only
- [ ] No Biome 2 room sequence or mini boss code is added yet

---

**Stop after Phase 1. Wait for user confirmation before proceeding to Phase 2.**
