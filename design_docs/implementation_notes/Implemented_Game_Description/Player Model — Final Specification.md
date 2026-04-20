# Player Model — Final Specification (v3)

This document defines the **PlayerModel classification** used by the AI Director (`PlayerModel.classify` in `src/game/ai/player_model.py`).

The model maps metrics into one of:

- `STRUGGLING`
- `STABLE`
- `DOMINATING`

The system is:

- **deterministic** (no randomness)
- **percentage-based** (HP and HP-loss values are on a **0–100** percent scale, matching `MetricsTracker` / `hp_percent_current`)
- driven by **`DifficultyParams`** tunables in `src/game/ai/difficulty_params.py`
- intended for the **current single-life run** model (**no** multi-life logic)

**v3 change:** classification uses **explicit boolean rules**, not weighted struggle/dominate scores, margins, or early-run “force STABLE” behavior.

> **Diagrams:** `Player_Model_Diagram.png` and `Player_Model_Classification_Flow.png` in this folder may still illustrate older v2 ideas; treat this markdown as the source of truth for v3.

---

## 1. Overview

**Evaluation order (priority):**

1. **STRUGGLING** — if any STRUGGLING rule fires.
2. Else **DOMINATING** — if all DOMINATING baseline conditions hold **and** at least one strong performance signal holds.
3. Else **STABLE**.

**Operator summary:**

- **STRUGGLING:**  
  `(HP_critical) OR (recent_death) OR (two_or_more_weak_signals)`
- **DOMINATING:**  
  `(not struggling) AND (HP_high AND no_recent_death) AND (at_least_2_strong_performance_signals)`
- **STABLE:** neither STRUGGLING nor DOMINATING.

`struggle_score` and `dominate_score` on the result are **binary flags** (`1.0` / `0.0`) indicating whether that state was chosen, not weighted sums.

---

## 2. Shared definitions

### 2.1 Recent death

**Recent death** is true if **either**:

- `recent_death_flag` from `MetricsTracker` is true, **or**
- the **last** entry of `last_3_rooms_result` is `"death"` (death in the most recently completed room in the rolling window).

This matches “death in current run history / last room” for single-life play.

### 2.2 Average HP loss (last three rooms)

Let `avg_hp_loss_last3` be:

- If `last_3_rooms_hp_loss` is non-empty: arithmetic mean of those values (each value is **percent points** of HP lost in that room).
- Else: fall back to **`hp_lost_in_room`** for the last completed room (from the summary).

### 2.3 Bad rooms (for STRUGGLING weak signals)

Count results in `last_3_rooms_result` that are **`near_death`** or **`death`**.

### 2.4 Fast recent clears (for DOMINATING)

**Fast recent clears** is true only if:

- `last_3_rooms_clear_time` has **at least two** entries, **and**
- the average of those recorded clear times (seconds) is **≤** `player_model_fast_clear_avg_seconds`.

---

## 3. Global parameters (v3)

Defaults are in `DifficultyParams` (`difficulty_params.py`). All HP-related fields are **percent 0–100**.

| Parameter | Default | Role |
| --- | ---: | --- |
| `player_model_struggling_hp_critical_percent` | `25.0` | `hp_percent_current ≤` this ⇒ STRUGGLING (priority path) |
| `player_model_struggling_hp_weak_percent` | `40.0` | Weak signal: low current HP |
| `player_model_struggling_bad_rooms_min` | `2` | Weak signal: ≥ this many bad rooms in last 3 |
| `player_model_struggling_avg_hp_loss_min` | `30.0` | Weak signal: `avg_hp_loss_last3` ≥ this |
| `player_model_dominating_hp_min_percent` | `70.0` | Baseline: `hp_percent_current` ≥ this |
| `player_model_dominating_avg_hp_loss_max_percent` | `15.0` | Strong signal: `avg_hp_loss_last3` ≤ this |
| `player_model_dominating_clean_clears_min` | `2` | Strong signal: ≥ this many `clean_clear` in last 3 |
| `player_model_fast_clear_avg_seconds` | `55.0` | Strong signal: rolling avg clear time ≤ this (when ≥ 2 samples) |

**Current HP** for all rules is **`hp_percent_current`** (live value passed into the summary when available).

---

## 4. STRUGGLING (priority state)

STRUGGLING is true if **any** of the following holds.

### 4.1 Priority OR conditions

- **Critical HP:** `hp_percent_current ≤ player_model_struggling_hp_critical_percent` (default ≤ **25%**).
- **Recent death:** as in §2.1.

### 4.2 Two weak signals

Otherwise, count **weak signals** (each is true/false):

1. **Weak HP:** `hp_percent_current ≤ player_model_struggling_hp_weak_percent` (default ≤ **40%**).
2. **Bad rooms:** number of `near_death` / `death` in last 3 ≥ `player_model_struggling_bad_rooms_min` (default **2**).
3. **High average loss:** `avg_hp_loss_last3 ≥ player_model_struggling_avg_hp_loss_min` (default **30%**).

If **at least two** of these three are true, STRUGGLING is triggered.

### 4.3 Decision label

`reasons` typically include `decision:struggling` plus tags such as `hp<=critical`, `recent_death`, or `weak_signals_<n>` (where `n` is the weak-signal count when the two-weak path fired).

---

## 5. DOMINATING

Evaluated **only if** STRUGGLING is false.

### 5.1 Baseline (both required)

- `hp_percent_current ≥ player_model_dominating_hp_min_percent` (default **≥ 70%**).
- **Not** recent death (§2.1).

### 5.2 Strong performance (at least two required)

Count how many of these are true (0–3); **DOMINATING** requires the count to be **≥ 2**:

- **Clean clears:** count of `clean_clear` in last 3 ≥ `player_model_dominating_clean_clears_min` (default **2**).
- **Low average HP loss:** `avg_hp_loss_last3 ≤ player_model_dominating_avg_hp_loss_max_percent` (default **15%**).
- **Fast recent clears:** §2.4.

### 5.3 Decision label

`reasons` typically include `decision:dominating`, `strong_signals_<n>` (where `n` is 2 or 3), plus any of `clean_clears`, `low_avg_hp_loss`, `fast_recent_clears` that applied.

---

## 6. STABLE

If the player is **not** STRUGGLING and **not** DOMINATING, the state is **STABLE** (`decision:stable`).

This is the default **middle** state when rules above do not apply.

---

## 7. Output structure

`PlayerClassificationResult` (Python) contains:

| Field | Meaning |
| --- | --- |
| `player_state` | `STRUGGLING`, `STABLE`, or `DOMINATING` |
| `reasons` | Tuple of strings (decision tag + optional tags) |
| `score_breakdown` | Dict of floats: predicate flags **0.0/1.0**, plus `weak_signal_count`, `avg_hp_loss_last3` |
| `struggle_score` | `1.0` if `player_state == STRUGGLING`, else `0.0` |
| `dominate_score` | `1.0` if `player_state == DOMINATING`, else `0.0` |

Example `score_breakdown` keys (non-exhaustive):  
`struggle_critical`, `recent_death`, `weak_hp`, `weak_bad_rooms`, `weak_avg_loss`, `weak_signal_count`, `struggle_from_two_weak`, `avg_hp_loss_last3`, `baseline_dom_hp`, `strong_clean`, `strong_low_avg_loss`, `fast_recent_clears`, `strong_performance`.

---

## 8. Data sources

Primary inputs come from **`MetricsTracker`** / `RunMetrics` via `build_player_model_summary`, including:

- `hp_percent_current` (classification uses this for all HP thresholds)
- `hp_lost_in_room`, `last_3_rooms_hp_loss`, `last_3_rooms_result`, `last_3_rooms_clear_time`
- `recent_death_flag`

Fields such as `struggling_rooms_count` and `dominating_rooms_count` remain on the summary for other uses but **do not** affect v3 classification.

---

## 9. Determinism

- No randomness: same summary + same `DifficultyParams` ⇒ same `player_state`.
- No hidden mutable state beyond storing the last `player_state` on the `PlayerModel` instance for `get_state()`.

---

## 10. Design summary

| State | Intent |
| --- | --- |
| **STRUGGLING** | Should trigger **fast** when HP is critically low, after a death in the last room, or when **two** stress signals align (low HP, repeated bad rooms, or high recent HP loss). |
| **DOMINATING** | Should feel **earned**: high current HP, no recent death, and **at least two** strong performance signals among clean clears, very low average loss, and fast clears. |
| **STABLE** | Default when neither high-priority struggle nor full dominate criteria are met. |

---

## 11. Version history

- **v3:** Percentage-only rules; STRUGGLING priority; STABLE fallback; removed weighted scores and early-run STABLE lock.
- **v2:** Weighted struggle/dominate axes, min scores, margin, performance gate, early rooms STABLE (superseded).
