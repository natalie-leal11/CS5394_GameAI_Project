# OUTPUT RULE

Generate ONLY the coding prompt for the requested phase.

Do NOT:

- output explanations
- output analysis
- output the full game code
- output multiple phases at once

After finishing the requested phase:

STOP and wait for user confirmation.


# PHASE EXECUTION RULE

Only implement the phase explicitly requested by the user.

If the user asks for:

Phase 1 → implement ONLY Phase 1.

Do NOT implement Phase 2 or Phase 3.

After generating the Phase implementation prompt:

STOP immediately.

Wait for explicit confirmation from the user before continuing.



# MASTER PROMPT — Dungeon Geeks (Biome 3 Integration)

Biome 3 must be implemented **inside the existing engine** and must extend the current systems used by **Biome 1 and Biome 2**.

Do NOT create a separate engine.

Biome 3 must integrate directly into the current `src/` architecture.

The following systems already exist and must be reused:

- player
- combat
- entity system
- asset loader
- room generation
- UI / HUD
- dungeon pipeline

Biome 3 must follow the same architecture patterns used in Biome 1 and Biome 2.

Only additive changes are allowed.


# IMPLEMENTATION GOAL

Add support for:

- Ranged enemy
- Biome 3 room sequence (rooms 16–23)
- Biome 3 mini boss encounter

# REUSE EXISTING SYSTEMS RULE

Biome 3 must reuse the same systems already used by Biome 1 and Biome 2.

Reuse these existing systems wherever possible:

- room generation / room controller
- door logic
- enemy spawn pipeline
- combat system
- projectile collision system
- HUD / UI
- tile renderer
- asset loader
- safe room interaction logic
- heal drop logic

Do NOT create replacement systems for any of the above.

Biome 3 should be added by extending the existing architecture, not by rebuilding parallel versions.



# PHASE ORDER

Phase 1 → Ranged enemy + projectile support  
Phase 2 → Biome 3 room sequence  
Phase 3 → Mini boss encounter  

After each phase:

STOP and wait for confirmation.



# ENVIRONMENT RULE (Important)

Biome 3 **must use the same tile system used by Biome 1 and Biome 2**.

Do NOT introduce a separate biome3 room background.

Rooms must render using the existing tile renderer.

Allowed additions for Biome 3 visual flavor:

- volcanic cracks
- lava floor decals
- magma rock props

Example assets:

assets/tiles/volcanic/
assets/props/lava_crack.png
assets/props/magma_rock.png

These must be used as **overlays on top of existing tiles**, not as a new room background.

## Tile and Wall Rendering Rule

Biome 3 must use the same floor tiles and wall tiles used by Biome 1 and Biome 2.

Do NOT introduce new wall tile sets.

Reuse the existing dungeon wall rendering system.

This includes:

- existing wall tiles
- wall thickness rules
- door placement rules
- room boundary generation

Biome 3 rooms must be rendered using the same tile grid and tile renderer already used by Biome 1 and Biome 2.

Only environmental overlays may be added for Biome 3 atmosphere, such as:

- lava cracks
- magma rock props
- volcanic decals

These must be rendered as overlays on top of the existing tiles, not as replacements.

# PHASE 1 — RANGED ENEMY

Create a new enemy type.

File:

src/entities/ranged.py


## Ranged Enemy Stats

enemy_type = "ranged"

base HP = 28  
base damage = 8  
size = 64×64

attack cooldown = 1.2 s  
projectile speed = 260 px/s  
projectile lifetime = 3.0 s  
projectile damage = 8


## Behavior

Ranged enemies must:

- maintain distance from player
- fire projectiles
- reuse existing enemy update pipeline
- reuse existing hitbox system
- reuse combat damage system

Do NOT redesign enemy architecture.


## Projectile Assets

assets/entities/projectiles/fireball_16x16.png  
assets/entities/projectiles/fireball_trail_16x16.png


Projectiles must use:

- deterministic speed
- fixed lifetime
- existing collision system


## Enemy Animation Assets

assets/entities/enemies/biome3/ranged/

idle_1.png → idle_4.png  
walk_1.png → walk_4.png  
attack_1.png → attack_4.png  
hit_1.png → hit_2.png  
death_1.png → death_6.png



## Registration Rule

Register the ranged enemy in the same spawn tables used by:

- Swarm
- Flanker
- Brute
- Heavy



# PHASE 2 — BIOME 3 ROOM SEQUENCE


Biome 3 contains rooms:

16 → 23



## Test Mode

If:

BEGINNER_TEST_MODE = True

Room order is fixed:

16 Combat  
17 Combat  
18 Ambush  
19 Combat  
20 Elite  
21 Safe  
22 Combat  
23 Mini Boss



## Seed Mode

If:

BEGINNER_TEST_MODE = False

Shuffle rooms:

16–22

Room 23 must **always remain Mini Boss**.



## Wall Thickness

Combat = 2 tiles  
Elite = 2 tiles  
Safe = 2 tiles  
Mini Boss = 2 tiles  
Ambush = 4 tiles



## Door Unlock Delay

DOOR_UNLOCK_DELAY_SEC = 0.5



# ROOM CONTENTS


### Room 16 — Combat

Swarm (0.0s)  
Flanker (0.4s)  
Ranged (0.8s)


### Room 17 — Combat

Flanker (0.0s)  
Ranged (0.4s)  
Brute (0.8s)


### Room 18 — Ambush

Swarm + Flanker + Ranged  

Pattern:

Ambush ring

Ambush ring definition:

spawn enemies in a circle around the player  
radius = 160 px


### Room 19 — Combat

Brute (0.0s)  
Ranged (0.4s)  
Heavy (0.8s)


### Room 20 — Elite

Brute (elite)  
Ranged (elite)  
Swarm


Triangle spawn pattern:

3 spawn points forming a triangle  
centered on room center  
side length = 200 px



### Room 21 — Safe Room

No enemies.


Contains:

- heal pickup
- upgrade selection



### Room 22 — Combat

Swarm (0.0s)  
Flanker (0.4s)  
Ranged (0.8s)  
Heavy (1.2s)



### Room 23 — Mini Boss

Single center spawn:

spawn boss at room center.



# HEALING RULES


Combat clear drop

chance = 35%  
heal = 30% base HP  
cap = 100%


Safe room heal

heal = 30%  
overheal cap = 130%  
usable once


Mini boss reward

heal = 30%  
cap = 100%



# SPAWN RULES

Minimum distance from player

150 px

Enemy spacing

90 px

Elite spacing bonus

60 px

No spawn near:

- walls
- doors
- corners



# PHASE 3 — MINI BOSS


File:

src/entities/biome3_miniboss.py



## Assets

assets/entities/enemies/biome3/miniboss/

idle_1 → idle_4  
move_1 → move_6  
attack1_1 → attack1_4  
attack2_1 → attack2_4  
summon_1 → summon_4  
phase_change_1 → phase_change_6  
hit_1 → hit_2  
death_1 → death_8



## Boss Behavior

Spawn time = 2.0 s


### Phase System

Phase 1 → normal attacks  

Phase 2 (50% HP) → summon adds



### Adds Composition

Adds are fixed:

2 Swarm  
1 Flanker



### Spawn Pattern

Adds spawn in a ring around boss.



### Boss Death

Spawn heal pickup.

heal = 30% base HP  
cap = 100%



Door unlock delay = 0.5 s



# SAFE ROOM UPGRADES

Safe room shows **3 upgrades**.

Player chooses **one**.


Upgrade pool:

Health Upgrade  
+20% max HP  
Icon: assets/ui/hud/icon_health_24x24.png


Speed Boost  
+10% movement speed  
Icon: assets/ui/hud/icon_speed_24x24.png


Attack Boost  
+12% attack damage  
Icon: assets/ui/hud/icon_attack_24x24.png


Defense Boost  
-12% incoming damage  
Icon: assets/ui/hud/icon_defence_24x24.png



Upgrade selection must be deterministic using the seeded RNG.



# BIOME 3 ENEMY REFERENCE

Swarm  
Flanker  
Brute  
Heavy  
Ranged  
Mini Boss



Enemy sizes:

Swarm → 60×60  
Flanker → 48×48  
Brute → 80×80  
Heavy → 88×88  
Ranged → 64×64  
Mini Boss → 96×96



# COMPLETION CHECKLIST

Biome 3 is complete when:

- ranged enemy works
- projectile system works
- rooms 16–23 exist
- safe room upgrades work
- mini boss encounter works
- deterministic seed behavior preserved