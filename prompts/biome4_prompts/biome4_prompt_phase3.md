# Phase 3 — Incremental Coding Prompt
# Additive Final Boss Support in `src/` for Biome 4

Implement **only** the following. Stop when this phase is complete.

---

## 1. Scope

- **Phase 3 deliverables:** additive Final Boss support inside `src/` for Room 29, including boss state machine, boss attacks, boss phase change, boss add summoning, boss UI, arena flow, death flow, and victory handling.
- **Architecture rule:** extend the existing boss / spawn / room-clear / projectile / UI pipeline rather than replacing it.

---

## 2. Additive-only implementation rule

Preferred approach:
- add a dedicated boss module such as `src/entities/final_boss.py`
- add a dedicated boss encounter helper if needed
- add only small, backwards-compatible hooks into existing room-clear, projectile, and HUD logic

Do NOT:
- rewrite the current mini boss system broadly
- redesign the combat engine
- redesign player systems
- modify unrelated biome logic

Any existing-file edits must be:
- minimal
- additive
- isolated to Final Boss support

---

## 3. Final Boss room contract

Biome 4 final boss encounter is for **Room 29**.

Room 29 rules:
- room type = FINAL_BOSS
- wall border thickness = 2 tiles
- doors remain closed until boss is dead
- after boss death, wait **0.5 s** before exit opens
- base boss spawn pattern = single central spawn
- base boss spawn time = **2.0 s**
- after death, trigger victory flow
- final boss reward heal = 40% of base max HP, capped at base max HP
- arena hazard caps must respect Phase 1 reserved metadata

Use these exact values.

---

## 4. Final Boss assets

Boss animation folder:

`src/assets/entities/enemies/final_boss/`

Animations:

- `idle_1.png` → `idle_4.png`
- `walk_1.png` → `walk_6.png`
- `attack1_1.png` → `attack1_6.png`
- `attack2_1.png` → `attack2_6.png`
- `special_1.png` → `special_6.png`
- `summon_1.png` → `summon_6.png`
- `phase_change_1.png` → `phase_change_8.png`
- `hit_1.png` → `hit_3.png`
- `death_1.png` → `death_10.png`

Boss size:
- **128×128**

---

## 5. Final Boss stats

Implement Final Boss with:

- HP = 480
- contact damage = 18
- fireball damage = 20
- lava wave damage = 22
- meteor damage = 18
- teleport strike damage = 24
- attack cooldown = 1.4 s
- movement speed = 85 px/s
- stop distance from player = 170 px
- preferred fireball range = 220–420 px
- preferred wave range = 140–260 px
- preferred teleport trigger range = 120–320 px

Use config/constants where appropriate.
Do not hardcode everywhere.

---

## 6. Final Boss abilities

Implement these boss attacks only:

### Attack-to-animation mapping
- **Fireball attack** uses `attack1`
- **Lava wave attack** uses `attack2`
- **Meteor rain attack** uses `special`
- **Teleport strike** uses teleport effect + `attack2` or nearest compatible slam frame flow
- **Summon adds** uses `summon`
- **Phase transition** uses `phase_change`
- **Hit reaction** uses `hit`
- **Death flow** uses `death`

Do not guess alternate animation bindings unless the current engine requires a narrowly documented compatibility fallback.

### A. Fireball attack
Use:

`src/assets/entities/projectiles/`

- `boss_fireball_24x24.png`
- `boss_fireball_anim_24x24.png`
- `boss_fireball_trail_24x24.png`

Rules:
- deterministic projectile speed
- projectile speed = 280 px/s
- projectile lifetime = 3.0 s
- projectile damage = 20
- cast telegraph = 0.5 s
- reuse existing projectile collision system

### B. Lava wave attack
Use:

- `src/assets/entities/projectiles/boss_wave_attack_64x64.png`

Rules:
- boss launches wave in straight line
- damage = 22
- telegraph = 0.75 s using `boss_wave_line_256x64.png`
- reuse existing projectile / collision / telegraph logic where possible

### C. Meteor rain attack
Use:

- `boss_meteor_64x64.png`
- `boss_meteor_anim_64x64.png`
- `boss_meteor_trail_32x32.png`
- `boss_meteor_impact_128x128.png`

Telegraph with:

`src/assets/effects/telegraphs/`

- `boss_meteor_target_96x96.png`

Rules:
- deterministic impact positions
- use visible telegraph before impact
- damage = 18
- meteor telegraph duration = 1.0 s
- meteor timing must be deterministic
- use 3 target zones per cast unless the active-enemy/projectile cap logic requires a lower bounded count

### D. Teleport strike
Use:

`src/assets/effects/boss/`

- `boss_teleport_flash_64x64.png`
- `boss_teleport_smoke_64x64.png`
- `boss_teleport_anim_64x64.png`

Rules:
- teleport to a nearby valid position
- do not teleport into walls / doors / invalid tiles
- maintain fair distance from player
- warning delay = 0.6 s before strike lands
- after teleport, perform slam / strike attack using existing damage system
- damage = 24

---

## 7. Boss attack loop / behavior rules

Final Boss must not choose attacks randomly without control. Use a deterministic weighted rotation or scripted priority loop.

Recommended behavior:
- if player is far away, prefer **Fireball**
- if player is mid-range and in front arc, prefer **Lava Wave**
- if player has stayed mobile and distant for extended time, use **Meteor Rain**
- if player is close or flanking repeatedly, use **Teleport Strike**
- after Phase 2 starts, increase Meteor / Teleport usage modestly but deterministically

Boss fairness rules:
- no attack should fire with zero warning
- boss must idle briefly after initial spawn
- boss AI must not chain more than 2 high-pressure attacks back-to-back without a short recovery window

Timing rules:
- boss spawn idle delay = 0.75 s
- minimum recovery between completed attacks = 0.6 s
- do not overlap teleport strike with meteor cast
- phase change must interrupt the normal attack loop cleanly

---

## 8. Explicit exclusion rule

Do **NOT** implement the **grab / claw mechanic** in this version.

Ignore all grab behavior and grab assets even if present elsewhere.

No player immobilization logic.
No hold-for-2-seconds logic.

---

## 9. Phase change rule

At **50% HP**, the Final Boss must:

- trigger `phase_change` animation
- become briefly invulnerable during transition
- summon adds
- then resume attack pattern with increased pressure

Use:

- `phase_change_1.png` → `phase_change_8.png`

Phase transition rules:
- invulnerability duration = animation duration or 2.0 s max, whichever the current boss framework supports more cleanly
- HP does not reset
- after phase change, reduce attack cooldown slightly to `1.2 s`
- after phase change, meteor and teleport can appear more often, but still deterministically

This phase change must be deterministic.

---

## 10. Add summoning rule

At phase change, summon:

- 2 Swarm
- 1 Flanker

Use:

`src/assets/effects/spawn/`

- `spawn_portal_64x64.png`
- `spawn_portal_anim_64x64.png`
- `summon_circle_128x128.png`
- `summon_circle_anim_128x128.png`

Rules:
- adds spawn in ring around boss
- deterministic placement
- adds count toward current active enemy system
- add spawning must not affect earlier biome rooms

---

## 11. Boss telegraphs

Use:

`src/assets/effects/telegraphs/`

- `boss_attack_circle_128x128.png`
- `boss_attack_circle_anim_128x128.png`
- `boss_wave_line_256x64.png`
- `boss_meteor_target_96x96.png`

Rules:
- attacks must be visibly telegraphed
- telegraph timing must be deterministic
- reuse existing telegraph rendering pipeline wherever possible

Recommended mapping:
- `boss_attack_circle_*` for general cast warning or teleport strike area
- `boss_wave_line_*` for Lava Wave
- `boss_meteor_target_*` for Meteor Rain

---

## 12. Boss spawn / death effects

Use:

`src/assets/effects/boss/`

### Spawn
- `boss_spawn_portal_256x256.png`
- `boss_spawn_portal_anim_256x256.png`
- `boss_spawn_explosion_128x128.png`

### Death
- `boss_death_explosion_256x256.png`
- `boss_death_energy_128x128.png`
- `boss_death_particles.png`

Rules:
- boss spawn uses dramatic portal effect at room start
- boss death uses explosion / energy effect
- after boss death animation + death effect, unlock exit after 0.5 s

---

## 13. Arena background

Use:

`src/assets/backgrounds/final_boss_arena_bg.png`

Rules:
- integrate additively if the engine supports boss-arena backdrop overlays
- do not replace the tile renderer

---

## 14. Boss UI

Use:

`src/assets/ui/`

- `boss_health_bar_frame.png`
- `boss_health_bar_fill.png`
- `boss_name_banner.png`

Rules:
- show boss UI only during Room 29 encounter
- health fill reflects current boss HP
- reuse existing HUD rendering conventions where possible

---

## 15. Victory handling

Use:

`src/assets/ui/`

- `victory_screen_bg.png`
- `victory_banner.png`

Rules:
- after final boss death and room clear, trigger victory flow
- victory flow must reuse current end-of-run / scene transition system if available
- do not create a separate engine or menu architecture

## Boss attack pattern timing

Final Boss attacks follow the deterministic attack cycle defined above.

### Core timing constants

BOSS_SPAWN_IDLE_DELAY = 1.0 s
BOSS_ATTACK_COOLDOWN_PHASE1 = 2.2 s
BOSS_ATTACK_COOLDOWN_PHASE2 = 1.8 s
BOSS_ATTACK_RECOVERY = 0.8 s

These values are intentionally slower than a pure pressure boss so the fight remains playable.

---

### Boss spawn behavior

When the boss appears in Room 29:

1. Boss spawns using spawn portal effect.
2. Boss remains idle for **1.0 second**.
3. After the idle delay, the boss begins the **Phase 1 attack cycle**.

---

### Attack execution rule

For each attack in the cycle:

1. Wait until attack cooldown expires.
2. Play attack telegraph.
3. Execute attack animation and damage event.
4. Wait **0.8 s recovery** after the attack animation finishes.
5. Move to the **next attack in the cycle**.

The boss must never chain attacks with no recovery gap.

---

### Phase 1 attack timings

#### Fireball
- Telegraph = **0.7 s**
- Attack animation = normal cast timing
- Projectile launches after telegraph ends

#### Lava Wave
- Telegraph = **0.9 s**
- Wave launches after telegraph ends

#### Teleport Strike
- Warning telegraph = **0.8 s**
- Boss teleports after warning
- Slam damage happens shortly after teleport

#### Meteor Rain
- Spawn **3 telegraph targets**
- Telegraph duration = **1.2 s**
- Meteors fall after telegraph ends

---

### Phase transition

When boss HP ≤ 50%:

1. Interrupt current cycle.
2. Play **phase_change animation**.
3. Boss becomes invulnerable for **2.0 seconds**.
4. Summon adds.
5. Switch to **Phase 2 attack cycle**.
6. Continue from the first Phase 2 attack.

---

### Phase 2 attack timings

Phase 2 is faster, but still playable:

#### Fireball
- Telegraph = **0.6 s**

#### Lava Wave
- Telegraph = **0.8 s**

#### Teleport Strike
- Warning telegraph = **0.7 s**

#### Meteor Rain
- 3 telegraph targets
- Telegraph duration = **1.0 s**

---

### Playability rules

To keep the fight fair:

- Do not allow **Meteor Rain** immediately followed by **Teleport Strike** with no recovery gap
- Do not allow the boss to start a new attack while the previous telegraph is still active
- Boss must respect the recovery window after every attack
- Boss must not overlap Lava Wave and Meteor Rain at the same time
- Boss must not teleport directly on top of the player
- Teleport destination must keep at least **96 px** distance from player

## Phase 2 Difficulty Upgrade

When the Final Boss enters **Phase 2 (HP ≤ 50%)**, increase pressure using **speed, lower cooldowns, and controlled combo attacks** instead of only increasing HP.

### Phase 2 stat changes

- `FINAL_BOSS_MOVE_SPEED_PHASE2 = 120 px/s`
- `FINAL_BOSS_ATTACK_COOLDOWN_PHASE2 = 1.4 s`
- `FINAL_BOSS_ATTACK_RECOVERY_PHASE2 = 0.5 s`

These values replace the slower Phase 1 pacing and make the boss more aggressive.

---

## Phase 2 simultaneous pressure rule

Phase 2 may use **one major attack + one support pressure action** at the same time.

Allowed support pressure actions:
- continue moving / chasing during Fireball pressure
- cast **1 single Fireball** during Meteor Rain telegraph window
- continue forward chase during Lava Wave pressure

This makes the fight harder without becoming unreadable.

---

## Allowed combo attacks in Phase 2

### 1. Meteor Rain + Fireball
Rules:
- Meteor Rain remains the **major attack**
- during the meteor telegraph window, the boss may cast **1 single Fireball**
- do not cast more than 1 Fireball during the same Meteor Rain sequence

### 2. Lava Wave + Chase Pressure
Rules:
- after launching Lava Wave, the boss may continue moving toward the player
- this is movement pressure only, not an immediate second damaging wave

### 3. Fireball + Movement
Rules:
- the boss may continue repositioning while maintaining Fireball pressure
- this should not interrupt projectile logic

---

## Disallowed unfair combos

To keep the fight difficult but playable, the following combinations are **not allowed**:

- Teleport Strike + Meteor impact at the same moment
- Lava Wave + Meteor Rain together
- Teleport Strike + Lava Wave overlap
- multiple Fireballs during one Meteor Rain cast
- Teleport Strike + immediate contact damage burst stacking unfairly on the same frame

---

## Updated Phase 2 attack cycle

Phase 2 attack cycle becomes:

1. Teleport Strike
2. Fireball
3. Meteor Rain + 1 Fireball
4. Lava Wave + Chase Pressure
5. Teleport Strike

After the fifth attack, the cycle repeats.

This deterministic cycle replaces random attack selection.

---

## Phase 2 combo timing rules

### Meteor Rain + Fireball
- meteor telegraph duration = `1.0 s`
- exactly **3 meteor targets**
- during that telegraph window, cast **1 Fireball**
- meteors land after telegraph ends

### Lava Wave + Chase Pressure
- lava wave telegraph duration = `0.8 s`
- boss launches wave
- boss may immediately resume movement pressure after wave release

### Fireball + Movement
- fireball telegraph duration = `0.6 s`
- boss may reposition during or immediately after projectile release depending on current movement framework compatibility

---

## Playability safeguard

Even in Phase 2:
- all telegraphs must remain visible
- recovery windows must still be respected
- boss must not overlap more than **2 pressure sources** at once
- combo attacks must remain deterministic and repeatable for testing

## Final Boss Revival:
Add a final revive phase to the Biome 4 Final Boss encounter.

Required behavior:
- When the Final Boss reaches 0 HP in its normal final phase, it does NOT end the fight immediately.
- Instead, trigger a short revive sequence and bring the boss back one last time.

Revive phase rules:
1. On first death:
   - play boss death animation/effect start
   - wait `2.0 s`
   - boss revives at room center
   - revive HP = `50`
   - boss gets `1.5 s` invulnerability after revive
   - do not trigger victory flow yet
   - do not unlock any doors yet
   - the room exit must remain closed during the revive sequence

2. Revive phase stats:
   - `FINAL_BOSS_REVIVE_HP = 50`
   - `FINAL_BOSS_MOVE_SPEED_REVIVE = 135 px/s`
   - `FINAL_BOSS_ATTACK_COOLDOWN_REVIVE = 1.1 s`
   - `FINAL_BOSS_ATTACK_RECOVERY_REVIVE = 0.4 s`
   - `FINAL_BOSS_CONTACT_DAMAGE_REVIVE = 15`

3. Revive phase attack pattern:
   - Teleport Strike
   - Fireball
   - Meteor Rain + 1 Fireball
   - repeat deterministically

4. Revive phase restrictions:
   - do not summon adds again
   - do not run another full phase_change sequence
   - do not reset the full boss fight
   - do not restore boss to full HP
   - do not add claw / grab mechanic

5. Visual behavior:
   - reuse existing boss spawn / teleport / death VFX where compatible
   - boss should visibly reappear after the revive delay
   - preserve deterministic timing

6. Door / victory rules:
   - the exit door must remain locked after the boss’s first death
   - the exit door must remain locked throughout the revive phase
   - only after the revived boss is killed for the final time may the exit door unlock
   - after the revived boss’s final death, wait `0.5 s`
   - then trigger the true final death flow
   - then display the victory screen
   - victory flow must only occur after the revived boss is fully defeated

7. Final death behavior:
   - when revive phase HP reaches 0, then play the true final death flow
   - trigger boss death VFX
   - unlock exit after `0.5 s`
   - trigger victory flow only after this final death

Implementation rules:
- keep the current final boss architecture
- extend the existing boss state machine additively
- do not redesign combat, UI, or scene systems
- keep deterministic behavior
- use config/constants for all revive-phase parameters

## Heavy Enemy Spawn:
Fix the Heavy enemy spawn / movement issue in Biome 4 and earlier biomes if the same spawn logic is shared.

Problem:
- Heavy enemy sometimes spawns too close to wall corners
- it gets stuck on the wall corner and cannot reposition correctly
- this makes the encounter look broken and reduces pressure

Required fix:
1. Prevent Heavy from spawning on or too near wall corners
2. Prevent Heavy from spawning too close to wall tiles
3. If Heavy reaches a corner and movement is blocked, it must recover and move away instead of staying stuck
4. Reuse the existing spawn and movement systems; do not redesign enemy architecture

Implementation rules:
- add a corner-exclusion check to spawn validation
- reject spawn points that are within the configured minimum wall distance or inside corner-blocked regions
- for Heavy specifically, require a larger corner/wall clearance than smaller enemies because its body size is 88x88
- if the current spawn point fails validation, fall back to the next valid spawn point in deterministic order
- if Heavy becomes movement-blocked near a corner for a short time window, apply a deterministic unstuck behavior:
  - try a small retreat vector away from the nearest wall/corner
  - then resume pathing toward the player
- do not teleport the Heavy randomly
- do not break deterministic seed behavior

Recommended constraints:
- Heavy must spawn at least 2 tiles away from wall corners
- Heavy must spawn at least 1 extra tile farther from walls than normal enemies if shared spawn logic supports per-enemy spacing
- corner tiles and adjacent blocked diagonals should be treated as invalid spawn zones for Heavy

Success criteria:
- Heavy never spawns clipped into wall corners
- Heavy does not remain stuck at corners
- existing enemy behavior for Swarm / Flanker / Brute / Ranged remains preserved unless they use the same shared fix safely

---

### Recommended result

This gives the player:

- enough time to read telegraphs
- enough time to dash away
- a harder second phase
- a boss that feels dangerous but not unfair

## 16. Determinism rules

Final Boss encounter must be deterministic:
- fixed event ordering
- fixed cooldowns
- fixed projectile speeds
- deterministic summon positions
- no uncontrolled randomness
- seeded behavior only where the current project already allows seeded randomness

---

## 17. Out of scope for this phase

Do **not** add:
- new player skills
- grab mechanic
- online learning
- new biome systems
- post-game meta progression

This phase is only for additive Final Boss support in Biome 4.

---

## 18. Checklist

- [ ] `src/entities/final_boss.py` exists
- [ ] Room 29 can run a Final Boss encounter
- [ ] Fireball attack works
- [ ] Lava wave attack works
- [ ] Meteor rain attack works
- [ ] Teleport strike works
- [ ] Grab / claw mechanic is not implemented
- [ ] Boss uses explicit attack-to-animation mapping
- [ ] Boss attack loop and recovery windows are deterministic
- [ ] Phase change at 50% HP works
- [ ] Adds spawn deterministically at phase change
- [ ] Boss health bar UI works
- [ ] Boss death flow + victory flow work
- [ ] Existing Biomes 1–3 and earlier boss behavior are preserved

---

**Stop after Phase 3. Wait for user confirmation before proceeding further.**
