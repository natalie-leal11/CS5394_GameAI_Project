# CRITICAL REQUIREMENTS - 13 Room Rendering & Hazard Generation

### MANDATORY DIRECTIVE ###
You are an expert Python programmer using **Pygame**.

**CRITICAL**: Implement deterministic room rendering and hazard placement based strictly on the Parameters Spec. Do not modify biome structure or room counts.


## **MANDATORY**: OBJECTIVE

Implement:
- Room size system (Small / Medium / Large)
- Hazard placement (lava, slow terrain, walls)
- Safety validation rules
- Deterministic layout generation per seed


## **MANDATORY**: FILES TO CREATE OR MODIFY

- 'src/game/dungeon/room_layout_generator.py'
- 'src/game/dungeon/hazard_validator.py'
- 'src/game/dungeon/room_renderer.py'
- Modify 'room_controller.py' if needed

No other files may be modified


## **CRITICAL**: IMPLEMENTATION REQUIREMENTS

### **MANDATORY**: Room Sizes

Room sizes must be:

- Small: **8x8**
- Medium: **12x12**
- Large: **16x16**

Room size rules:
- Start, Elite, Boss -> Large
- Standard Combat, Safe -> Medium
- Ambush -> Small (more likely in later biomes)

### **MANDATORY**: Supported Tile Types

- Normal Floor
- Lava (damage over time)
- Slow Terrain (movement penatly)
- Wall (blocks movement)

Enemies must avoid lava if possible (simple rule).

### **MANDATORY**: Hazard Caps Per Biome

Biome 1:
- Lava: 0-5%
- Slow: 5-10%
- Walls: 10-15%
- Minimum Safe Area ≥ 70%

Biome 2:
- Lava: 5-15%
- Slow: 5-15%
- Walls: 15-20%
- Minimum Safe Area ≥ 60%

Biome 3:
- Lava: 15-25%
- Slow: 10-20@
- Walls: 20-25%
- Minimum Safe Area ≥ 50%

Biome 4: 
- Lava: 20-30%
- Slow: 10-20%
- Walls: 20-30%
- Minimum Safe Area ≥ 45%

Final Boss Arena Special Cap:
- Lava ≤ 20%
- Walls ≤ 20%
- Minimum Safe Area ≥ 65%

### **MANDATORY**: Seed Variability Rules

Within biome caps: 
- Lava may vary ±3-5%
- Walls may vary ±5%
- Slow terrain may vary ±5%

All variation must comefrom centralized seeded RNG.

### **MANDATORY**: Global Safety Constraints

Each generated room must satisfy:

- Player spawn tile is safe
- Exit tile is safe
- Safe rooms contain **0 lava**
- At least one **3x3 safe zone** exists
- Valid path exists from spawn -> exit
- Minimum safe area percentage enforced

If validation fails -> regenerate layout deterministically.

### Validation Requirements

Implement:

- Connectivity check (BFS or equivalent)
- Safe area percentage calculation
- Hazard percentage enforcement 
- Boss arena fairness override

### Rendering 
- Render tiles as colored rectangles (no assets required)
- Visually differentiate:
    - Lava (red)
    - Slow terrain (blue)
    - Walls (gray)
    - Safe tiles (neutral)
- Rendering must match generated layout exactly.

### **MANDATORY**: Determinism Rule

- Same seed + same room index -> identical layout.
- No randomness outside 'rng.py'.
- AI Director cannot modify hazard caps.


## **MANDATORY**: ARCHITECTURE CONSTRAINTS

- Layout generation separated from room progression.
- Hazard logic separated from combat logic.
- No AI Director logic inside layout generation. 


## **MANDATORY**: VERIFICATION

- [ ] Room sizes match type rules
- [ ] Hazard percentages stay within biome caps
- [ ] Safe rooms contain zero lava
- [ ] Connetivity always valid
- [ ] Final boss arena respects special caps
- [ ] Same seed reproduces identical layouts



### CRITICAL REMINDER ###
-30 rooms fixed 
- Biome boundaries fixed
- Hazard caps cannot be exceeded
- AI Director does not modify hazards
- Deterministic generation only