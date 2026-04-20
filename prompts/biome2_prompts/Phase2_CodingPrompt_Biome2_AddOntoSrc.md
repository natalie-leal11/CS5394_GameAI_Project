# Phase 2 — Incremental Coding Prompt
# Additive Biome 2 Room Sequence Support in `src/`

Implement **only** the following. Do not add Biome 2 mini boss behavior yet beyond whatever room metadata is needed to declare room 15 as a mini boss room. Stop when this phase is complete.

---

## 1. Scope

- **Phase 2 deliverables:** additive Biome 2 room sequence support for rooms **8–15** inside the existing `src/` codebase.
- **Source of truth:** `Biome2_Rooms_And_Rules_Reference.md`.
- **Architecture rule:** extend the current dungeon/room pipeline instead of replacing it.

---

## 2. Additive-only implementation rule

Preferred approach:
- create a dedicated Biome 2 room-definition module such as `src/dungeon/biome2_rooms.py`
- create a Biome 2 sequence helper/registry such as `src/dungeon/biome2_sequence.py`
- add only narrow integration hooks if existing room-loading code requires them

Do not rewrite the current Biome 1 room pipeline.
Do not remove or renumber existing Biome 1 rooms.

---

## 3. Required room order

Implement Biome 2 room support using the exact fixed order below when `BEGINNER_TEST_MODE = True`:

- **Room 8** → COMBAT
- **Room 9** → COMBAT
- **Room 10** → AMBUSH
- **Room 11** → SAFE
- **Room 12** → COMBAT
- **Room 13** → ELITE
- **Room 14** → AMBUSH
- **Room 15** → MINI_BOSS

When `BEGINNER_TEST_MODE = False`, implement seed-based shuffled order for:
- COMBAT
- COMBAT
- COMBAT
- AMBUSH
- AMBUSH
- SAFE
- ELITE

then append:
- MINI_BOSS as room 15

Use deterministic seed-driven ordering only.

---

## 4. Room-level rules

Implement the following Biome 2 room metadata and sequence rules from the reference:

### Wall border thickness
- **B = 2 tiles:** COMBAT, SAFE, ELITE, MINI_BOSS
- **B = 4 tiles:** AMBUSH only

### Door rules
- COMBAT / AMBUSH / ELITE doors start closed and open only after clear + unlock delay
- SAFE doors are open immediately
- MINI_BOSS exit opens only after mini boss death + unlock delay

### Unlock delays
- `DOOR_UNLOCK_DELAY_SEC = 0.5`
- `MINI_BOSS_DOOR_UNLOCK_DELAY_SEC = 0.5`

### Spawn pattern summary
- COMBAT → Spread
- AMBUSH → Ambush
- ELITE → Triangle
- MINI_BOSS → Single
- SAFE → no enemies

---

## 5. Exact Biome 2 room contents

Encode the exact Biome 2 room data from the reference document:

### Room 8 — Combat 1
- Swarm at 0.0 s
- Flanker at 0.4 s
- Brute at 0.8 s

### Room 9 — Combat 2
- Flanker at 0.0 s
- Brute at 0.4 s
- Heavy at 0.8 s

### Room 10 — Ambush 1
- Swarm + Flanker
- both use 1.5 s telegraph
- Ambush pattern

### Room 11 — Safe Room
- no enemies
- safe room heal pickup exists

### Room 12 — Combat 3
- Swarm at 0.0 s
- Brute at 0.4 s
- Brute at 0.8 s
- Heavy at 1.2 s

### Room 13 — Elite Room
- Brute (elite) at 0.0 s
- Swarm (elite) at 0.4 s
- Swarm (non-elite) at 0.8 s
- Triangle pattern
- elite spacing = 150 px total

### Room 14 — Ambush 2
- Swarm + Flanker
- both use 1.5 s telegraph
- Ambush pattern

### Room 15 — Mini Boss Room
- Mini Boss only at 2.0 s for this phase’s room metadata

---

## 6. Healing rules to encode in room metadata

Add Biome 2 metadata/support for the following values so later gameplay phases can consume them cleanly:

- clear-heal drop chance = 25%
- clear-heal amount = 30% of base max HP
- clear-heal cap = 100% of base max HP
- safe room heal amount = 30% of base max HP
- safe room overheal cap = 130% of base max HP
- safe room pickup usable once per room visit
- mini boss reward heal amount = 30% of base max HP
- mini boss reward cap = 100% of base max HP

Do not redesign existing healing systems in this phase.
Prefer adding clean room/biome metadata and narrow hooks.

---

## 7. Spawn-rule metadata to encode

Add Biome 2 support for the following global spawn rules from the reference:

- minimum distance from player = 150 px
- minimum tiles from wall = 3
- minimum tiles from door = 3
- minimum distance between enemies = 90 px
- elite extra spacing = 60 px
- no spawns in corners
- no spawns in door tiles or within 3 tiles of doors
- spawn slot delay = 0.4 s

Do not rewrite the whole spawn system if a metadata-driven extension is enough.

---

## 8. Integration rule

If the current room controller / room factory / game scene needs a narrow additive entry point to recognize Biome 2 rooms, do the smallest possible backwards-compatible change.

Do not alter existing Biome 1 room order.
Do not break room 0–7 behavior.

---

## 9. Out of scope for this phase

Do **not** implement full Biome 2 mini boss combat logic or add-spawn behavior yet.
Only define room 15 metadata sufficiently for the room sequence.

---

## 10. Checklist

- [ ] Biome 2 room definition module exists
- [ ] Rooms 8–15 are defined additively
- [ ] `BEGINNER_TEST_MODE=True` uses the exact fixed room order
- [ ] Non-beginner mode uses deterministic shuffled order + room 15 mini boss
- [ ] Heavy appears in room 9 and room 12 metadata
- [ ] Safe room, elite room, ambush rooms, and mini boss room metadata are encoded
- [ ] Existing Biome 1 room behavior is preserved
- [ ] Mini boss combat behavior is not fully implemented yet

---

**Stop after Phase 2. Wait for user confirmation before proceeding to Phase 3.**
