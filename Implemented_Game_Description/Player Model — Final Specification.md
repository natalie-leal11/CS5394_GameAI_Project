# Player Model — Final Specification (v2)

This document defines the **PlayerModel classification system** used by the AI Director.

The PlayerModel evaluates player performance using tracked metrics and classifies the player into one of:

- `STRUGGLING`
- `STABLE`
- `DOMINATING`

The system is:
- deterministic
- parameter-driven
- based only on `MetricsTracker` data
- free of randomness

---

# 1. Overview

The PlayerModel computes two scores:

- `struggle_score`
- `dominate_score`

Each score is calculated using weighted signals.

The final classification is determined using:
- score thresholds
- score comparison
- preference margin
- additional gating rules

---

# 2. Global Parameters

These values must be defined in `difficulty_params.py`.

| Parameter | Value |
|---|---:|
| `player_model_weighted_min_score` | `2.0` |
| `player_model_weighted_preference_margin` | `0.35` |
| `player_model_early_rooms_stable_count` | `2` |

---

# 3. Early Run Rule

For early gameplay stability:


IF rooms_cleared < player_model_early_rooms_stable_count
AND recent_death_flag == False

THEN:
player_state = STABLE
decision = "stable_early_run"


- Scores are still computed for debugging purposes
- Prevents unstable classification during onboarding

---

# 4. STRUGGLING State

## Signals (Struggle Axis)

Each signal contributes its weight if true.

| Signal | Condition | Weight |
|---|---|---:|
| `recent_death` | `recent_death_flag == True` OR last of `last_3_rooms_result == "death"` | `1.15` |
| `low_hp` | `hp_percent_current < 0.30` OR `hp_percent_end_room < 0.30` | `1.00` |
| `repeated_near_death_or_death` | ≥ 2 of last 3 results are `near_death` or `death` | `1.20` |
| `high_recent_avg_hp_loss` | avg(`last_3_rooms_hp_loss`) > `0.22` | `1.00` |
| `struggling_rooms_share` | `rooms_cleared >= 2` AND `struggling_rooms_count / rooms_cleared >= 0.45` | `1.05` |
| `high_healing_per_room` | `total_healing_received / rooms_cleared > 45` | `0.70` |

---

## Decision Rule


IF struggle_score >= min_score
AND (
dominate_score < min_score
OR
(struggle_score - dominate_score) >= preference_margin
)
THEN:
player_state = STRUGGLING


---

# 5. DOMINATING State

## Signals (Dominate Axis)

| Signal | Condition | Weight |
|---|---|---:|
| `no_recent_death` | `recent_death_flag == False` | `0.80` |
| `hp_comfortable` | both HP values ≥ 0.75 | `1.10` |
| `mostly_clean_clear` | ≥ 2 of last 3 are `clean_clear` | `1.15` |
| `low_damage_and_loss` | damage ≤ 45 AND avg HP loss ≤ 0.08 | `1.10` |
| `fast_recent_clears` | avg of last clear times ≤ 55 sec | `1.00` |
| `dominating_rooms_share` | `dominating_rooms_count / rooms_cleared >= 0.40` | `1.05` |

---

## Performance Gate (IMPORTANT)

To prevent false positives:

At least ONE must be true:
- `mostly_clean_clear`
- `low_damage_and_loss`
- `fast_recent_clears`

Stored as:

d_performance_gate = 1.0 if any true else 0.0


---

## Decision Rule


IF dominate_score >= min_score
AND performance_gate == True
AND (
struggle_score < min_score
OR
(dominate_score - struggle_score) >= preference_margin
)
THEN:
player_state = DOMINATING


---

# 6. STABLE State

STABLE is not signal-based.

## Conditions

### Case 1 — Weak Evidence

struggle_score < min_score
AND dominate_score < min_score


---

### Case 2 — Mixed Evidence

struggle_score >= min_score
AND dominate_score >= min_score


Result:

player_state = STABLE
decision = "stable_mixed_evidence"


---

### Case 3 — No Clear Winner

ABS(struggle_score - dominate_score) < preference_margin


---

### Case 4 — Early Run
(see section 3)

---

# 7. Score Computation

Each axis is computed as:


score = SUM(weight_i for each signal_i that is TRUE)


---

# 8. Output Structure

PlayerModel returns:

```json
{
  "player_state": "STRUGGLING | STABLE | DOMINATING",
  "struggle_score": float,
  "dominate_score": float,
  "decision": "stable_early_run | stable_mixed_evidence | struggling | dominating",
  "reasons": [list of triggered signals],
  "score_breakdown": {
    "signal_name": weight_applied_or_0,
    "d_performance_gate": 0.0 or 1.0
  }
}
9. Data Sources

All inputs come from MetricsTracker, including:

hp_percent_current
hp_percent_end_room
damage_taken_in_room
last_3_rooms_result
last_3_rooms_hp_loss
last_3_rooms_clear_time
rooms_cleared
struggling_rooms_count
dominating_rooms_count
total_healing_received
recent_death_flag
10. Determinism Rules
No randomness allowed
Same seed + same gameplay → same classification
No external state mutation
Pure function of metrics + params
11. Design Summary
STRUGGLING

Triggered by:

low HP
deaths
high damage intake
heavy healing dependence
DOMINATING

Triggered by:

high HP
clean clears
low damage
fast clears
consistent performance

Requires real performance evidence (not just “no death”).

STABLE

Fallback when:

early game
weak signals
mixed signals
no clear dominance
12. Final Notes
System is tuned for smooth difficulty adaptation
Avoids overreaction in early rooms
Prevents false domination classification
Ensures fair and explainable AI behavior