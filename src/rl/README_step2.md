# Step 2: Observation vector (`build_observation`)

## Shape

- **Dimension:** `OBS_DIM = 36` (see `src/rl/obs.py`)
- **Dtype:** `float32`
- **Gym `Box`:** `low=-1`, `high=1` (flags/ratios mostly in `[0,1]`; signed channels use `[-1,1]`)

## Feature order (index → meaning)

### A — Player (0–15)

| Idx | Name | Normalization |
|-----|------|----------------|
| 0 | HP ratio | `hp / max_hp` → [0,1] |
| 1 | Max HP | `max_hp / _MAX_PLAYER_HP_UPPER` → [0,1] (see below) |
| 2 | Lives | `lives / PLAYER_LIVES_INITIAL` → [0,1] |
| 3 | Life index | `life_index / (len(PLAYER_MAX_HP_BY_LIFE)-1)` → [0,1] |
| 4 | Player x | `world_x / room.pixel_width` (else `LOGICAL_W`) → [0,1] |
| 5 | Player y | `world_y / room.pixel_height` (else `LOGICAL_H`) → [0,1] |
| 6 | Velocity x | `vx / (PLAYER_MOVE_SPEED*3)` → [-1,1] |
| 7 | Velocity y | same scale → [-1,1] |
| 8–9 | Facing x,y | clamp to [-1,1] |
| 10 | Dash active | 0/1 |
| 11 | Dash cooldown | `dash_cooldown_timer / PLAYER_DASH_COOLDOWN_SEC` → [0,1] |
| 12 | Long attack CD | `long_attack_cooldown_timer / PLAYER_LONG_ATTACK_COOLDOWN_SEC` → [0,1] |
| 13 | Block | `is_blocking()` or `state=="block"` → 0/1 |
| 14 | Parry | `is_parry_active()` or `state=="parry"` → 0/1 |
| 15 | Invulnerable | `invulnerable_timer / 3.0` → [0,1] (cap 3 s) |

### B — Room / progression (16–24)

| Idx | Name | Notes |
|-----|------|--------|
| 16 | Room index | `current_room_index / (total_campaign_rooms()-1)` |
| 17 | Biome | `biome_index / 4` |
| 18 | Room type | stable enum order → [0,1] |
| 19 | Enemies alive | count (combat-relevant) / 24 (cap; Step 2.1) |
| 20 | Cleared / doors | `_room_cleared_flag OR _doors_unlocked` → 0/1 |
| 21 | Boss room | `MINI_BOSS` or `FINAL_BOSS` → 0/1 |
| 22 | Campaign progress | `(current_room_index+1) / total_campaign_rooms()` |
| 23 | Victory | `_victory_phase` → 0/1 |
| 24 | Defeat | `_death_phase is not None` → 0/1 |

### C — Nearest enemy (25–31)

Nearest among `_enemies` with: not `inactive`, not training dummy, `hp>0`, `state != "death"`.

| Idx | Name | Notes |
|-----|------|--------|
| 25 | Has enemy | 0/1 |
| 26 | Distance | `dist / hypot(LOGICAL_W, LOGICAL_H)` → [0,1] |
| 27–28 | Rel position | `(enemy - player) / distance_scale` → [-1,1] |
| 29 | Enemy HP ratio | `hp / max_hp` |
| 30 | Enemy type | stable string/class map → [0,1] |
| 31 | Near threat | 1 if `dist < 400` px else 0 |

### D — Hazard / reserve (32–34)

| Idx | Name | Notes |
|-----|------|--------|
| 32 | Near hazard tile | 8-neighbor has lava or slow |
| 33 | In hazard tile | current tile lava or slow |
| 34 | Reserve heal CD | `reserve_heal_cooldown_timer / RESERVE_HEAL_USE_COOLDOWN_SEC` → [0,1] |

### E — Local density (35) — Step 2.1

| Idx | Name | Notes |
|-----|------|--------|
| 35 | Local swarm density | combat enemies within **280 px** / **12** (cap), clamp [0,1] |

## Normalization (Step 2.1)

- **Max HP (feature 1):**  
  `_MAX_PLAYER_HP_UPPER = max(PLAYER_MAX_HP_BY_LIFE) × SAFE_ROOM_OVERHEAL_CAP_RATIO × 1.2`  
  Covers overheal cap from config plus slack for safe-room / upgrade effective HP; result clamped to `[0,1]`.

- **Alive enemy count (19):** `alive_n / 24`, clamp `[0,1]`. Cap 24 is a safe upper bound for simultaneous hostiles (reinforcements, adds).

- **Local density (35):** count of combat enemies within **280 px** of player (same order of magnitude as GameScene “near enemy” checks), divided by **12**, clamp `[0,1]`.

## Approximations

- **Velocity scale:** `3× PLAYER_MOVE_SPEED` (dash headroom).
- **Invuln cap:** 3 s (not only `PLAYER_RESPAWN_INVULN_SEC`).
- **Engagement distance:** 400 px heuristic for feature 31.

## Private fields

`obs.py` does **not** read private `Player` timers (`_short_attack_timer`, etc.). It uses public APIs/helpers where listed (`is_blocking`, `is_parry_active`).

## Revert

Remove `src/rl/obs.py`, restore placeholder in `env.py`, and shrink `observation_space` if rolling back Step 2 only.
