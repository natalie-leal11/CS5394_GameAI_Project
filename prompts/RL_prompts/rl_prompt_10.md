# rl_prompt_10 — Iteration 2 PPO experiment layout (`iter2_cooldown_0p5_1p2`)

**Sequence:** 10 of 18 — *Milestone training without overwriting artifacts.*

**Implementation (repo):** `src/rl/experiment_layout.py`, `train_ppo` `--experiment` / `--stage`; folder trees under `models/ppo/iter2_cooldown_0p5_1p2/`, `logs/ppo/...`, `demos/ppo/...`; `src/rl/README_step11_iteration2.md`.

---

## Objective

Run **iteration 2** experiments after the configured short/long attack cooldowns in `game.config`, using **separate directories per stage** (300k / 600k / 900k) so checkpoints, TensorBoard, eval summaries, and demos are not overwritten.

## Scope

- **Included:** Fresh 300k run; resume 300k for 600k and 900k from prior `dungeon_ppo_best.zip` (fallback `dungeon_ppo_final.zip`); `milestone_train.md` auto-write; `--eval-freq` / `--eval-episodes` as documented.
- **Not included:** Changing unrelated legacy model paths outside this experiment name.

## Changes required

- `train_ppo --experiment iter2_cooldown_0p5_1p2 --stage 300k|600k|900k` with `--timesteps 300000` each stage; resume paths per README table.

## Constraints

- Add **300k** timesteps per stage; preserve per-stage artifact checklist.

## Implementation steps

1. Run stage 300k from scratch.
2. Run 600k and 900k resuming from previous stage best.
3. Keep TensorBoard logdirs separate per stage.

## Deliverables

- Three isolated milestone folders with models and logs.

## Sources

- `src/rl/README_step11_iteration2.md` (folder structure, train commands, resume table)
