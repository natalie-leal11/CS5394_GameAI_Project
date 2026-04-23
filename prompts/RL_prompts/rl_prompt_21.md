# RL Environment Bug Fix + Stability Patch

**Title:** RL Environment Bug Fix + Stability Patch (`rl_prompt_21`)

---

## Objective

Stabilize **RL-only** behavior in `GameScene` so training and evaluation reflect **intended** environment semantics: safe-room heal and upgrades complete reliably, combat-room heal rewards are not lost to ordering, and the agent is not **soft-stuck** at a door after a clear. This is a **simulation correctness** patch — **not** a reward-function or PPO change.

---

## Scope

- **File:** `src/game/scenes/game_scene.py` (RL branches guarded by `_rl_controlled` where applicable).
- **In scope:**
  - **Safe-room auto heal:** Same effect as manual **F** without depending on proximity/UI timing; correct `_safe_room_heal_done` and upgrade exposure.
  - **Upgrade flow:** `_safe_room_upgrade_pending` / `_rl_auto_resolve_safe_room_upgrades()` run consistently until picks are exhausted.
  - **Normal-room rewards:** Heal entries in `_rewards` are processed **before** `load_room` clears the list (auto-collect for RL unchanged in spirit; ordering fixed).
  - **Room transition:** RL-only watchdog if doors fail to open after the normal post-clear delay.
- **Out of scope:** `reward.py`, PPO core, curriculum scripts, manual player input paths, pathfinding/movement redesign.

---

## Constraints

- Do **not** modify `src/rl/reward.py`, PPO hyperparameters, or curriculum logic.
- Manual play must remain **bit-for-bit equivalent** on non-RL paths (no behavior change unless behind `_rl_controlled`).
- Do **not** delete or overwrite unrelated experiment folders; one controlled **20k** continuation under a **new** experiment name.

---

## Expected behavior

| Area | Expected |
|------|-----------|
| SAFE room (RL) | Heal applies automatically when eligible; heal anchor position initialized if needed; upgrade UI state stays aligned; auto-pick runs after heal in the same update when applicable. |
| Combat rooms (RL) | Room-clear / boss heal orbs in `_rewards` are collected in the same frame they are spawned (before door transition / room load). |
| Doors (RL) | After room clear, if the normal unlock delay has passed but no door is open, doors are forced open so progression is possible without changing movement code. |

---

## Relation to prior prompts

- Builds on **`rl_prompt_19`** (auto-grant / auto-pick) and **`rl_prompt_20`** (health automation) by fixing **ordering and edge cases**, not by changing reward weights or policy code.
