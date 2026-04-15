# rl_prompt_20 — RL-only full health automation (orbs, safe-room, reserve)

**Sequence:** 20 of 20 — *Extend RL simplification: health handling without manual interaction.*

**Implementation (repo):** `src/game/scenes/game_scene.py` — `_rl_auto_reward` (normal-room heal orbs), `_try_apply_safe_room_f_heal` / `_rl_try_auto_safe_room_heal` (safe-room heal), `_rl_try_auto_reserve_heal` (reserve / extra heal auto-use), `_rl_auto_resolve_safe_room_upgrades` (unchanged). All gated by `_rl_controlled`.

---

## Objective

Make **health-related** gameplay **fully automatic** for RL-driven runs so the policy does **not** spend steps or actions on **collecting heal orbs**, **pressing F** in safe rooms, or **pressing H** for reserve heals when the game design already intends those benefits—while leaving **manual player** controls and **reward shaping** (`reward.py`) unchanged.

## Scope

- **Included:** When `GameScene._rl_controlled` is True:
  - **Normal-room heal rewards** (room-clear orbs, boss / mini-boss rewards in the shared reward list): **auto-apply** without overlap requirement (existing `_rl_auto_reward` path).
  - **Safe-room heal:** same effect as manual **F**, via shared helper **`_try_apply_safe_room_f_heal`**; **RL auto** calls **`_rl_try_auto_safe_room_heal`** each frame when eligible (no KEYDOWN).
  - **Reserve / extra heal:** after **cooldown tick**, **`_rl_try_auto_reserve_heal`** may consume the front of **`reserve_heal_pool`** when **missing HP ≥ front chunk** (matches intentional “beneficial full chunk” use; partial heals still use manual **H** if desired).
- **Not included:** Changes to **PPO**, **curriculum**, **combat**, **reward.py** weights, **manual** key bindings, or **non-health** upgrade logic beyond **existing** `rl_prompt_19` auto-pick.

## Constraints

- **No** change to manual-player behavior or default key bindings.
- **No** new reward terms; automation is **GameScene** / control-path only.
- **Deterministic** auto-pick for upgrades remains as in **`rl_prompt_19`**.
- Reserve auto-use must **not** spam failed consumes: only when **off cooldown** and **missing HP** is at least the **current front** reserve chunk.

## Implementation notes

- **Normal-room orbs:** In the reward-collection loop, treat RL as always in range for uncollected heal rewards (`_rl_auto_reward`).
- **Safe-room:** Proximity for RL can treat heal as available anywhere in SAFE (as before); **`_try_apply_safe_room_f_heal`** is shared by **F** KEYDOWN and **RL auto**.
- **Reserve:** Mirror **`H`** success path (`try_consume_reserve_heal`, cooldown, metrics, `_rl_log_heal_applied`); run **after** `reserve_heal_cooldown_timer` decrement for the frame.
- **Upgrades:** **`_rl_auto_resolve_safe_room_upgrades`** and **`_rl_ensure_safe_room_upgrade_state_exposed`** stay **intact**; heal auto runs first so upgrade flow still follows.

## Deliverables / expected report style

- Short update in **`RL_implementation/rl_implementation_report.md`**: subsection **“RL Health Automation Update”** (what auto-applies, what is unchanged for humans).
- Optional training continuation (e.g. +20k from current best) under a **new** experiment folder; **fair eval** (50 episodes, 5 seeds) recorded in `eval_summary_fair_best.md` next to the new checkpoint.

## Sources

- Course submission need to **reduce interaction dependency** for RL and improve **room progression** signal.
- Builds on **`rl_prompt_19`** (auto-grant / auto-pick).
