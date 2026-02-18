"""
Room type constants. Only these may appear in the dungeon plan.
"""
START = "start"
CORRIDOR = "corridor"
COMBAT = "combat"
AMBUSH = "ambush"
SAFE_REST = "safe_rest"
ELITE = "elite"
MINI_BOSS = "mini_boss"
FINAL_BOSS = "final_boss"

ALL_TYPES = (
    START,
    CORRIDOR,
    COMBAT,
    AMBUSH,
    SAFE_REST,
    ELITE,
    MINI_BOSS,
    FINAL_BOSS,
)

# Milestone indices (fixed)
START_INDEX = 0
MINI_BOSS_INDICES = (7, 15, 23)
FINAL_BOSS_INDEX = 29
TOTAL_ROOMS = 30

# Biome ranges (inclusive)
BIOME_1_RANGE = (0, 7)   # 0-7
BIOME_2_RANGE = (8, 15)  # 8-15
BIOME_3_RANGE = (16, 23) # 16-23
BIOME_4_RANGE = (24, 29) # 24-29
