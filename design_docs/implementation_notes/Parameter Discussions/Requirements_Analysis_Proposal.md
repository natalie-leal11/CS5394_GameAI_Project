# Requirements Analysis Proposal 
All of these can be our initial trials, and adjust later on if necessary. 

Once agreed upon, I can update prompts and create new version of guide to showcase these requirements. And then we'll decide how to divide and proceed. 

## A) Global Questions

### Spawn Safety Rules

Minimum safe distance from player spawn: 128 px sounds good

-> We could adjust this number if it seems too close or far. According to the following speeds we have:
    - Swarm: 190 px/sec
    - Flanker: 260 px/sec
    - Brute: 120 px/sec
    - Heavy: 100 px/sec
    - Final Boss: 140 px/sec

Minimum distance between enemies at spawn: 64 px is a good start, I think.

Yes, enforce "no spawn on hazards". Always

### Engage Rules

Enemy AI becomes active 0.75 sec "entry grace"

### Attack Distance Rules

Short Attack Distance - 50 px

Long Attack Distance - 520 px/sec x 1.2 sec lifetime = ~624 px max travel ?

Melee Enemy Attack Range - 1 tile (32 px)

### Spawn Visualization

Yes, all spawn should use telegraph. Small "portal" effect could be cool.

Telegraph duration:  ~0.5

### Deterministic Spawn Points

We could use predefined spawn anchor points
    - 8-12 anchors 
    - Corners, edges, midpoints
    - If anchors are blocked by hazards/walls, fall back to the next valid anchor in a deterministic order

## B) Room 0 - Start Room

### Purpose

Yes, Room 0 should be strictly non-combat. 

### Story Interaction

I think a book with the story could be really cool. The altar with the book could be in the center of the room, where the player could get a more in-depth story, as well as a quick run-down of a run-structure. 

I think it should be optional, so the player does not have to sit through the story for every run. 

### Allowed Actions

Yes, we could have a "dummy" corner in which the player gets a to try the controls.

### Exit Condition

Exit always open

## C) Combat Room 

### Enemy Spawn Moment 

Spawn with telegraph after entry

### Enemy Initial State

If we make the telegraph spawn 0.5 sec, then we could make the enemy idle for 0.5 sec as well, which gives the player 1.0 sec before combat. ?

### Positions

I think mixed anchor points could be good, to add controlled randomness to the game. 

### No-Clumping Rule

Maybe enforce at spawn only, no steering for now.

### Room Lock

Doors lock immediately and then telegraph starts could be a good visual. 

## D) Ambush Room

### Ambush Trigger

Trigger after player moves to center

### Spawn Style

Same as others, portals

### Ambush Wave Structure 

We could have one wave for the first two biome, and the option for 2 waves on the last 2 biomes.

### Player Fairness

Yes, 3x3 safe zone with no spawns for 1.5 second.

## E) Safe / Rest Room

### Healing Format

Both. Healing founttain (primary) + optional 1-2 pickups

### Pickup Rules

If pickups exist, allow multiple (but cap total value per room)

### Preview UI

Yes, tooltip on approach

### Placement 

- Fountain: near center
- Pickups/upgrades: away from door

### Upgrade Choice

3 choice like Hades, AI Director may bias choices (but must remain deterministic from seed + metrics snapshot)

## F) Corridor / Transition Room

## Purpose

Non-combat always 

***(Do these count for the 30 rooms? Should we put a cap on how many corridors we should have in a run? To avoid too many "safe" rooms?)

## Choice

We can default one path for the first biome, and introduce fork choice starting Biome 2

## Loot
Small loot allowed (to avoid making the room redundant). Maybe 15% chance to spawn loot.

## G) Elite Room

### Elite Entry

Elite + 2-3 normal enemies

### Telegraph

Yes, stronger telegraph with gold aura

### Summon Rule

We could start with trigger at 50%, but then when we apply more RL, we could make it director based. 

### Summon Spawn

Portals near edges

### Caps

Yes, cap max active enemies at 10. If after multiple rooms, it seems too easy, we can up the cap. 

## H) Biome-by_Biome

### Biome 1 (Rooms 0-7)

Change Elite to 0

Enemies should mostly consist of swarm and flanker, maybe one brute?

I think we can have at most one ambush room, maybe?

Yes, spawns should avoid hazards completely. 

### Biome 2 (Rooms 8-15)

I think we should change to Elite = 1, and it should be rooms, not enemies.

From here on out, the ambushes can be "hard ambushes"

### Biome 3 (Rooms 16-23)

Yes, we should change to Elite = 2, if we mean rooms.

I don't think enemies should gain raw stat boosts. Instead increase the pressure through spaawn density, reinforcements, or hazard clustering. 

### Biome 4 (Rooms 24-29)

Elite Rooms. Maybe we should change it, since we only have 5 rooms to work with. We could make rooms 25 and 27 elite? Or if we want to keep 4, we could make it occurrences. What do you think?

Yes, I think having room 28 fixed as a Safe Room could be good.

## I) Enemy-by-Enemy 

### Swarm

Attack range maybe 32 px?

I think since their purpose is pressure, have them chase directly.

Max spawn: 6 ?

### Flanker

Circle time: 0.8-1.2 sec then lunge

Dash distance: ~96 px

Telegraph: 0.35 sec "lean back" + red line indicator ?

### Brute

Slam radius - 55px (ensure smaller than heavy)

Slam telegraph: red circle, duration 0.6 sec

### Heavy

AoE radius: 70 px 

Yes, AoE slam should pushback player

No armor. Just high HP

### Ranged

I think this should be a rare enemy to spawn. If at all, what do you think? 

Minimun distance: ~192 px

Projectile speed: ~1.2 sec ? we should set it so dodging is possible

Projectile Telegraph: wind-up flash 0.25 sec

## J) Mini Boss

### Arena Setup

Spawn center

Summon 50%

Spawn 3 enemies from a summon (should they all be swarm? or change enemy type?) 

Let the summons appear on the edges

### Phase / Pattern

2 patterns

### Reward

Drop guaranteed healing + maybe 1 optional upgrade

## K) Final Boss 

### Spawn & Intro

Appear after short cineamatic (0.8-1.2 sec maybe) with control lock

### Phase Transition

Sure, roar and glow is fine. Creates a clear signal to the player

### Summon Rule

Yes, the option to summon at phase 2. What do you think? Is letting the final boss summon too hard? 

### Summon Type

If summon, give option to summon 1 elite or 2 normal

### Summon Placement

Yes, at edges on the opposite side of the player

### Fairness

Yes, guarantee one safe zone remains in boss arena after summons

## L) Healing Drops & Loot

### Healing Drops

Small chance of healing dropping after combat. Maybe 25% change in Biome 1 and 2, and 35% in Biome 3 and 4. 

### Drop types:

Small heal only for combat rooms; big heal resered for Safe/Mini Boss rewards

### Pickup Rules

Press key to pickup

### UI preview

Tooltip on approach

## M) Implementation

Yes, we should definitely have predifined spawn anchors per room. 

We could have some spawn groups. How many do you think we would need to create? To keep the game interesting enough

Yes, we should have a deterministic function. 



