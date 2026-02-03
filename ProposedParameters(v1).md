Date: February 2nd, 2026

1. Dungeon Parameters
Number of rooms:
- Total rooms per run: 30
- Branching paths exist but total progession length is constant

Types of rooms: 
- Start room - No combat, introduces the run
- Corridor / Transition - Between rooms to choose path
- Combat Room - Standard enemy encounter
- Ambush Room - Enemies trigger immediatly on entry
- Safe / Rest Room - No enemies; revcovery and upgrades
- Elite Room - Stronger enemy groups or reinforcements
- Boss Room - Final encounter of the run

Room Sizes:
- Small 8x8 tiles (ambush - tight combat, high pressure)
- Medium 12x12 tiles (standard combats, safe/rest)
- Large 16x16 tiles (start room, elite or boos encounters)
* If we wish to keep things more consistent all rooms could be medium. 

Types of Blocks in Rooms:
- Normal Floor - Standard movement 
- Lava - High damage over time, avoided by enemies
- Slow terrain(mud/water) - Reduced movement speed
- Walls - Block movement

2. Enemy parameters
Types of Enemies:
- Melee Enemy - Close-range, high pressure. High health, low damage
- Fast Enemy - Flanks and pressures the player
- Heavy Enemy - Slow, high health, area attacks
- Elite Variant - Modified versions with high stats or abilities

Enemy Strength: 
- Strenghth scales with dungeon depths
- Scaling factors: 
    - Health: +10-15% per dungeon tier
    - Damage: +8-12% per tier

Enemy Characteristics:
- Health
- Armor
- Movement Speed
- Aggression Level
- Awarenes radius (room-limited)


Enemy Attacks
- Melee damage: 6-12 per hit
- Ranged damage: 10-18 per hit
- Elite attacks: 
    - Area slams
    - Rapid milti-hit attacks
    - Temporary buffs

Calling Allies
- Global limit: 3 times per run
- Triggered when:
    - Enemy is near defeat
    - Encounter instesity is high
- Ally call results in: 
    - Small group of enemies 
    One stronger enemy

3. Safe Rooms & Power-Ups
Safe Rooms:
- Frequency: 1 every 4-6 rooms
- Functions: 
    - Partial health restore
    - Rest point (checkpoint)
    - Upgrade selection

Power-Ups: Player chooses one upgrade per safe room
- Health Upgrade: +15-25% max health
- Speed Boost: +10% movement speed
- Attack Boost: +10=15% damage
- Cooldown Reduction: Faster attacks
- Defense Boost: Reduced incoming damage

4. Player Characteristcs: 
Player Attacks: 
- Short-range attack
    - Fast, low damage
    - Good for crowd control
- Long-range attack
    - Slower, higher damage
    - Limited by cooldown or resource

Movement & Defense:
- Dash / Jump
    - Avoid attacks
    - Cross hazards
- Block / Parry
    - Reduces / negated damage
    - Perfect timing grants bonus

Player Damage Values
- Base health: 100
- Short attack damage: 8-12
- Long attack damage: 15-25
- Block reduction: 60-100% (timing-based)

5. Game Ending Conditions
Win Conditions
- Defeat the final boss
- Complete the dungeon run

Loss Conditions
- Player health reaches zero
- Run ends (roguelike reset)

6. Narrative & Story Design
Narrative Style - Minimal, atmospheric storytelling

Story Premise: 
- The dungeon is a sentient construct that adapts to intruders. Each run represents another attempt by the dungeon to eliminate the player. 
- The AI Director is the dungeon's will. It is measuring, responding, correcting. 

Event-Based Narrative System:
The game defines explicit, deterministic events, such as:
    - Player enters ambush room
    - Player health drops below 20%
    - Player defeats multiple rooms without damage
    - Ally call is triggered
    - Player dies