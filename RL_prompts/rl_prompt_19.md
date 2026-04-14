# rl_prompt_19 — Auto-grant single rewards and auto-pick multi-choice upgrades

**Sequence:** 19 of 19 — *Reduce RL UI friction for final submission.*

**Implementation (repo):** `src/game/scenes/game_scene.py` — `_try_apply_safe_room_f_heal`, `_rl_try_auto_safe_room_heal`, `_rl_auto_resolve_safe_room_upgrades`, `_apply_biome3_safe_room_upgrade_choice`, `_apply_biome4_safe_room_upgrade_choice` (RL-only; `_rl_controlled`).

---

## Objective

Simplify the RL agent’s interaction with **rewards and upgrade UI** so training and demos focus on **combat and room progression**, not menu navigation or key spam for routine pickups.

## Scope

- **Included:** Behavior when the game is driven by **RL** (`DungeonEnv` / `_rl_controlled` path or equivalent): automatically apply **single** rewards (room-clear heals, orb pickups, scripted single-choice rewards) without requiring the policy to press interact or navigate reward prompts; for **Realm / Biome 3 and 4** upgrade screens that present **multiple choices**, select an option using a **fixed, documented priority order** (e.g. health → attack → defence → speed, or as specified at implementation time).
- **Not included:** Changing **manual player** controls, UI layout, or reward **values** for human play; rewriting unrelated reward shaping in `reward.py` except where needed to align with auto-grant semantics.

## Changes required

- Wire **auto-grant** on the RL path for all **single** reward moments (no extra keypress for normal room-clear heal rewards; no opening upgrade UI for **single** safe-room rewards when only one outcome exists).
- Implement **auto-pick** for **multi-choice** upgrade UIs in **Biome 3 and 4** using the fixed priority rule (deterministic, reproducible).
- Keep human-play paths **unchanged**; branch on RL vs human only where the codebase already distinguishes control source.

## Constraints

- **No** change to manual-player behavior or default key bindings for human users.
- **Deterministic** auto-pick order (same seed + same offer → same choice).
- Document the priority list next to the code and in `RL_implementation/rl_implementation_report.md` after implementation.

## Implementation steps

1. Inventory reward and upgrade entry points (room clear, safe room, boss rewards, Realm/Biome 3–4 upgrade flows).
2. On RL-only paths, short-circuit single rewards to **grant immediately** without requiring interact/UI navigation.
3. For multi-choice upgrades in Biome 3/4, map options to the fixed priority and apply the highest-priority available choice automatically under RL control.
4. Regression-test: human playthrough unchanged; RL demo/train shows fewer stalled steps on reward UI.

## Deliverables

- Code changes (in a follow-up task) plus short update to RL README / report confirming behavior.
- This prompt serves as the **documentation** baseline before coding.

## Sources

- Course submission need for **practical RL simplification**; prior observation that RL **lost time** on reward and upgrade **UI interaction** relative to gameplay.
