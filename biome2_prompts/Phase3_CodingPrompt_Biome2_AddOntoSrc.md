# Phase 3 — Incremental Coding Prompt
# Additive Biome 2 Mini Boss Support in `src/`, Including Adds

Implement **only** the following. Stop when this phase is complete.

---

## 1. Scope

- **Phase 3 deliverables:** additive Biome 2 mini boss support inside `src/`, including support for **adds** during the Biome 2 mini boss encounter.
- **Source of truth:** `Biome2_Rooms_And_Rules_Reference.md`.
- **Architecture rule:** extend the existing mini boss / spawn / room-clear pipeline rather than replacing it.

---

## 2. Additive-only implementation rule

Preferred approach:
- add a dedicated Biome 2 mini boss module if needed, such as `src/entities/biome2_mini_boss.py`
- or extend the existing mini boss through a narrowly-scoped Biome 2 variant/config path
- add a dedicated Biome 2 boss encounter helper if needed
- add only small, backwards-compatible hooks into existing spawn/room-clear logic

Do not rewrite the current Biome 1 mini boss behavior unless a tiny shared extension point is required.

---

## 3. Mini Boss room contract

Biome 2 mini boss encounter is for **Room 15**.

Room 15 rules from the reference:
- room type = MINI_BOSS
- wall border thickness = 2 tiles
- doors remain closed until mini boss is dead
- after mini boss death, wait **0.5 s** before exit opens
- base room spawn pattern = single central spawn
- base boss spawn time = **2.0 s**
- on mini boss death, spawn reward pickup at death position
- reward heal = 30% of base max HP, capped at base max HP
- overlap exit after clear returns to start scene / main menu

Use these exact values.

---

## 4. Adds support requirement

Even though the room reference lists the mini boss room’s baseline enemy list as the mini boss itself, this phase must add **Biome 2 mini boss encounter support including adds**, as requested by the user.

Implement adds support in a way that is:
- additive
- isolated to the Biome 2 mini boss encounter
- disabled outside the Biome 2 mini boss room
- deterministic
- compatible with the existing enemy spawn framework

Rules for adds support:
- adds must be normal existing enemy classes already present in `src/` supportable by the encounter system
- prefer Swarm / Flanker / Brute / Heavy as possible add candidates depending on the current code’s compatibility
- add spawning must not affect Biome 1 rooms
- add spawning must not alter the existing non-Biome-2 mini boss encounter flow

If the current codebase needs an encounter-script helper for timed boss events, add that helper rather than hardcoding everything into unrelated systems.

---

## 5. Determinism rules

Mini boss encounter and adds behavior must be deterministic:
- fixed event ordering
- fixed cooldown / timing values
- no random variance unless seeded explicitly through the project’s existing RNG conventions
- no nondeterministic iteration order

If adds are spawned by schedule, use explicit deterministic timings.

---

## 6. Reward / clear handling

Implement Biome 2 mini boss clear handling with the exact reference behavior:
- reward drop appears at mini boss death position
- reward collection heals 30% of base max HP
- reward heal cannot overheal beyond base max HP
- exit opens after `MINI_BOSS_DOOR_UNLOCK_DELAY_SEC = 0.5`
- overlap exit returns to main menu / start scene

Keep existing Biome 1 mini boss clear behavior intact unless a tiny shared hook is required.

---

## 7. Integration rule

If the current codebase requires minimal integration edits, limit them to:
- importing the Biome 2 mini boss variant / encounter helper
- recognizing room 15 as a Biome 2 boss encounter
- allowing boss encounter-specific adds scheduling
- allowing reward drop + exit unlock flow for the Biome 2 room

Do not redesign unrelated room-clear logic.

---

## 8. Out of scope for this phase

Do **not** add any Biome 3+ content, final boss content, or new player systems.
This phase is only for the additive Biome 2 mini boss encounter, including adds support.

---

## 9. Checklist

- [ ] Biome 2 mini boss support exists in `src/`
- [ ] Room 15 can run a Biome 2 mini boss encounter
- [ ] Adds support exists and is isolated to the Biome 2 mini boss encounter
- [ ] Reward heal drop on boss death follows the Biome 2 reference values
- [ ] Exit unlock delay is 0.5 s after boss death
- [ ] Existing Biome 1 mini boss behavior is preserved
- [ ] Any existing-file edits are minimal and additive only

---

**Stop after Phase 3. Wait for user confirmation before proceeding further.**
