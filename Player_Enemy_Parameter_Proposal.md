# Player and Enemy Parameter Proposal
* If approved, to be added to AI_Dungeon_Parameters_discussion.md

## 9) Player Characteristics & Combat Paramters
This section desfines baseline player combat behavior and interaction rules. These values prevent ambiguity during implementation and must remain deterministic at runtime. 

All numerical values below are **initial tuning defaults** and may be adjusted later without architectural changes.

### 9.1 Player Core Stats
| Parameter | Initial Value | Rule |
|------:|------------|------:|
| Base Max HP | 100 | Fixed requirement |
| Move Speed | 220 px/sec | Scaled by delta-time |
| Collision Radius | 16 px | Used for hit detection |
| Contact Damage Allowed | Yes | Only in combat rooms |

### 9.2 Dash Mechanics
| Parameters | Initial Value |
| ----- | -------:|
| Dash Speed Multiplier | 2.2x more speed |
| Dash Duration | 0.18 sec |
| Dash Cooldown | 1.0 sec |


**Rules**
- Dash cannot stack.
- Dash cannot exceed room bounds.
- Dash behavior must use deterministic timers.

### 9.3 Player Attacks

#### 9.3.1 Short Range Attack (Melee)
| Parameter | Initial Value |
| ---- | ----: |
| Damage Range | 8-12 |
| Cooldown | 0.50 sec |
| Hitbox Range | 50 px |
| Hitbox Width | 70 px arc/rectangle |
| Knockback | 8 px |

**Role:** Sustained DPS. 

#### 9.3.2 Long-Range Attack (Projectile)
| Parameter | Initial Value | 
| --- | ----: |
| Damage Range | 15-25 |
| Cooldown | 0.80 sec |
| Projectile Speed | 520 px/sec |
| Lifetime | 1.2 sec |
| Radius | 6 px |
| Max Active Projectiles | 3 |

**Role:** Burst + spacing tool.

### 9.4 Block & Parry System
| Parameter | Initial Value |
| ---- | ----: |
| Block Reduction | 60% |
| Parry Reduction | 100% |
| Parry Timing Window | 120 ms |

**Rules**
- If hit occurs during parry window -> 100% reduction.
- If blocking outside window -> 60% reduction.
- If not blocking -> full damage.
- No randomness permitted in damage reduction calculations.

### 9.5 Hit Feedback 
| Mechanic | Initial Value |
| ---- | ----: |
| Enemy Knockback | 8 px |
| Player Knockback | 12 px |
| Hit Flash Duration | 0.10 sec |
| Stun | Disabled (MVP) |

## 10 Enemy Archetypes & Combat Roles
Enemy behavior is inspired by role-based combat archetyppes, adapted for deterministic room-based encounters. 

Enemies must:
- Remain confined to the current room.
- Use simple chase/attack logic.
- Not use advanced AI (no patrol, hiding, sound detection).
- Remain deterministic.

### 10.1 Swarm (Small Melee)
**Role:** Surround + pressure.
| Parameter | Value |
| ---- | ----: |
| HP | 30 |
| Speed | 190 px/sec |
| Damage | 8 |
| Attack Cooldown | 1.2 sec |

**Expected Hit to Kill**
- Short (~10 dmg midpoint) -> ~3 hits
- Long (~20 dmg midpoint) -> ~2 hits

### 10.2 Flanker (Fast Attacker)
**Role:** Angle disruption
| Parameter | Value |
| ---- | ----: |
| HP | 40 |
| Speed | 260 px/sec |
| Damage | 10 |
| Dash Cooldown | 3 sec |

**Behavior**
- Circles player briefly. 
- Dashes inward.
- Retreats slightly.

### 10.3 Brute (Telegraphed Heavy Strike)
**Role:** Runish mistimed movement.
| Parameter | Value |
| ---- | ----:|
| HP | 110 |
| Speed | 120 px/sec |
| Damage | 16 |
| Windup | 2.0 sec |
| Cooldown | 4.0 sec |

### 10.4 Heavy (Area Control)
**Role:** Space denial.
| Parameter | Value |
| ---- | ----: |
| HP | 160 |
| Speed | 100 px/sec | 
| Damage | 18 |
| AoE Radius | 70 px |
| Cooldown | 3.5 sec |

### 10.5 Ranged Suppressor 
**Role:** Projectile pressure.
| Parameter | Value | 
| ---- | ----: | 
| HP | 60 |
| Speed | 150 px/sec |
| Projectile Damage | 10 |
| Fire Interval | 1.5 sec |

**Behavior**
- Fires toward player.
- Minimal chase behavior.

### 10.6 Elite Modifier System
Elite enemies modify exxisting archetypes.
| Modifier | Value |
| ---- | ----: |
| HP Bonus | +40% |
| Damage Bonus | +20% |
| Visual Indicator | Glow / Size increase |
| Max Elites per Run | 3 |

**Optional Elite Abilities:**
- Speed burst.
- Shockwave on death.
- Rage below 30% HP.

### 10.7 Mini Boss
| Parameter | Value |
| ---- | ----: |
| HP | 600-700 |
| Abilities | 2-3 simple behaviors |
| Summon Trigger | At 50% HP |

Used mid-run to spike difficulty.

### 10.8 Final Boss
| Parameter | Value |
| ---- | ----: |
| HP | 1200 |
| Speed | 140 px/sec |
| Damage | 20 |
| Phases | 2 |

**Phase 2:**
- Increased agression.
- Reduced cooldowns.
- One summon event.

All transitions must be deterministic.


## 11) Player-to-Enemy Balance Matrix
Use midpoint player damaage values: 
| Enemy | HP | Short Hits | Long Hits | Role |
| ---- | ---- | ---- | ---- | ---- |
| Swarm | 30 | 3 | 2 | Pressure |
| Flanker | 40 | 4 | 2 | Disruption |
| Brute | 110 | 11 | 6 | Punish |
| Heavy | 160 | 16 | 8 | Area control |
| Mini Boss | 650 | 65 | 33 | Mid Spike |
| Final Boss | 1200 | 120 | 60 | Final test |

These are pacing targets, not guarantees. 

## 12) Determinism & Balance Guarantees
The following must always hold: 
- Player HP = 100
- Short damage range = 8-12
- Long damage range = 15-25
- Enemy stats remain within defined tiers
- AI Director does not override base combat rules
- All randomnes centralized in seeded RNG
- AI Director contains no randomness