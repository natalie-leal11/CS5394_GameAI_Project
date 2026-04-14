# rl_prompt_04 — Per-step reward shaping (`reward.py`)

**Sequence:** 4 of 18 — *Scalar signal for PPO before advanced shaping.*

**Implementation (repo):** `src/rl/reward.py`; documented in `src/rl/README_step3.md`.

---

## Objective

Define **per-step** reward from before/after `SceneManager.update(dt)` snapshots: terminal win/loss, room clear/forward progress, kills, damage/heal, stall, step cost, clipping, and `info["reward_breakdown"]`.

## Scope

- **Included:** Constants (e.g. `R_VICTORY`, `R_DEFEAT`, kill/clear/entry, damage/heal caps, stall, `R_STEP_CLIP`), one-time vs repeating rules.
- **Not included:** Step 6 progress potentials, timeout wrapper penalty, E/F terms (later prompts).

## Changes required

- Reward computation must not mutate gameplay; breakdown components sum to returned step reward (within float noise).

## Constraints

- Tunables live in `reward.py`; follow README tables for component behavior.

## Implementation steps

1. Implement `compute_step_reward` / `RewardSnapshot` per codebase.
2. Populate `info["reward_breakdown"]` for debugging and analysis.
3. Align train/eval with the same reward path.

## Deliverables

- Interpretable training signal and breakdown keys for TensorBoard/log analysis.

## Sources

- `src/rl/README_step3.md`
