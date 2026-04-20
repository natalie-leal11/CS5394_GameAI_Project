# rl_prompt_08 — Interact (E) and safe-room heal (F) reward shaping

**Sequence:** 8 of 18 — *Curriculum-aligned actions 10 / 11.*

**Implementation (repo):** `src/rl/reward.py` (delta/event terms), `src/rl/action_map.py` (actions 10/11), metrics on `MetricsTracker.run`, `GameScene` hooks; `src/rl/README_step6.md` (Step 12 section).

---

## Objective

Add **small delta/event-only** rewards for RL actions **10 = interact (E)** and **11 = safe_room_heal (F)** with success/failure counters, supporting curriculum scenarios without changing PPO architecture or observation size.

## Scope

- **Included:** `R_BENEFIT_INTERACT`, `R_BENEFIT_SAFE_ROOM_HEAL_EXTRA`, failed interact/heal penalties, per-step caps; breakdown keys `benefit_interact`, `benefit_safe_heal`, `failed_interact`, `failed_safe_heal`.
- **Not included:** `train_curriculum_ppo` wiring (separate prompt).

## Changes required

- Increment success/fail counters from gameplay when E/F are used (e.g. story close, altar panel, heal applied vs spam).

## Constraints

- Delta/event-only; caps to limit exploit via spam.

## Implementation steps

1. Wire metrics from `GameScene` for RL E/F usage.
2. Add reward terms and breakdown entries.
3. Keep consistent with `action_map.py`.

## Deliverables

- Shaping signal for curriculum **interact** and **safe heal** training/eval.

## Sources

- `src/rl/README_step6.md` (“Step 12: Interact (E) and safe-room heal (F) shaping”)
