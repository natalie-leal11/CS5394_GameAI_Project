# rl_prompt_05 — PPO training (Stable-Baselines3): `train_ppo`, resume, checkpoints, TensorBoard

**Sequence:** 5 of 18 — *Core on-policy learning loop.*

**Implementation (repo):** `src/rl/train_ppo.py`, `src/rl/config.py` (`PPOConfig`), SB3 `MlpPolicy`, `models/ppo/`, `logs/ppo/`; documented in `src/rl/README_step4.md`.

---

## Objective

Train a PPO policy on `DungeonEnv` with **Stable-Baselines3**: configurable timesteps, seeds, vectorized envs, **resume** from `.zip` checkpoints, periodic **checkpoints**, and **TensorBoard** logging—without changing manual game entry points.

## Scope

- **Included:** `python -m rl.train_ppo`, `--timesteps`, `--resume-model` (continues `learn()` with `reset_num_timesteps=False`), `--checkpoint-freq`, `--models-dir` / `--logs-dir`, experiment/stage layout when used.
- **Not included:** Eval/demo UX (next prompt); reward formula changes.

## Changes required

- Install deps from `requirements.txt` (SB3, tensorboard, gymnasium, numpy, pygame).
- Train from `src/`; default artifacts: `dungeon_ppo_final.zip`, `dungeon_ppo_latest.zip`, optional `dungeon_ppo_ckpt_*_steps.zip`.

## Constraints

- Manual gameplay launch unchanged; SB3 device/policy choices per `config.py`.

## Implementation steps

1. Configure `PPOConfig` (e.g. `max_episode_steps` for wrapped env).
2. Run fresh or resume training per README examples.
3. Point TensorBoard at the run’s log directory.

## Deliverables

- Saved policy weights and training curves suitable for eval and longer runs.

## Sources

- `src/rl/README_step4.md` (train, resume, paths, TensorBoard)
