# Step 4 — PPO training (Stable-Baselines3)

Minimal, reversible scaffolding to train and evaluate PPO on `DungeonEnv`. Manual gameplay is unchanged (separate entry points).

## Dependencies

Install from the repository root (includes SB3 and TensorBoard):

```text
pip install -r requirements.txt
```

Main packages: `stable-baselines3`, `tensorboard`, `gymnasium`, `numpy`, `pygame`.

## Paths

Defaults (created automatically):

| Purpose | Path |
|--------|------|
| Saved models | `models/ppo/` |
| Checkpoints | `models/ppo/checkpoints/` |
| TensorBoard | `logs/ppo/tensorboard/` |

Artifacts:

- `models/ppo/dungeon_ppo_final.zip` — final weights after training
- `models/ppo/dungeon_ppo_latest.zip` — copy of final (same as final when training completes successfully)
- `models/ppo/checkpoints/dungeon_ppo_ckpt_*_steps.zip` — periodic checkpoints (if enabled)

## How to run (from `src/`)

Put `src` on the module path by running commands **from the `src` directory**:

```bash
cd src
```

### Train (headless)

```bash
python -m rl.train_ppo
```

Options (see `--help`):

- `--timesteps N` — total training timesteps (default in `rl.config.PPOConfig`)
- `--seed N`
- `--no-time-limit` — do not wrap with `TimeLimit`
- `--max-episode-steps N` — `TimeLimit` cap for training (default **5000** in `PPOConfig`)
- `--n-envs N` — parallel rollout envs for SB3 `make_vec_env` (default **1**)
- `--models-dir`, `--logs-dir`, `--checkpoint-freq`
- `--resume-model PATH` — **continuation training**: load a saved PPO `.zip` (e.g. `dungeon_ppo_latest.zip`, `dungeon_ppo_final.zip`, or a `checkpoints/dungeon_ppo_ckpt_*_steps.zip`) and run **`learn()` for `--timesteps` more** without reinitializing weights. Use this for long runs split across sessions.

**Resume example** (from `src/`; adds 300k more timesteps on top of existing weights):

```bash
python -m rl.train_ppo --timesteps 300000 --resume-model ../models/ppo/dungeon_ppo_latest.zip
```

After each run (fresh or resume), the script still writes `dungeon_ppo_final.zip` and `dungeon_ppo_latest.zip`, and periodic checkpoints when `--checkpoint-freq` is a positive number. When resuming, `learn(..., reset_num_timesteps=False)` so TensorBoard’s step counter continues.

TensorBoard:

```bash
tensorboard --logdir ../logs/ppo/tensorboard
```

### Evaluate (headless)

```bash
python -m rl.eval_ppo --model ../models/ppo/dungeon_ppo_final.zip
```

Multi-seed (recommended for less noisy aggregates; total episodes = `episodes × number of seeds`):

```bash
python -m rl.eval_ppo --model ../models/ppo/dungeon_ppo_final.zip --seeds 0 1 2 3 4 --episodes 10
```

**Options** (see `--help`): `--seed` (single base), `--seeds` (list of bases), `--deterministic` / `--no-deterministic`.

**Reported summary:** mean/std reward, mean/std episode length, wins, defeats, timeouts (truncation) count, **mean_final_room_index**, **mean_max_room_index_during_episode** (max `room_index` seen in the episode), **mean_max_rooms_cleared_during_episode** (from `info["rooms_cleared"]` each step). `info` also includes `rooms_cleared` and `room_index` each step (see `DungeonEnv._build_info`).

### Demo (visible window)

```bash
python -m rl.demo_ppo --model ../models/ppo/dungeon_ppo_final.zip
```

Same environment as training; only `render_mode="human"`. For a longer run (e.g. more time to watch the agent), use `--max-episode-steps N` (see below).

## TimeLimit

The base `DungeonEnv` does **not** set `truncated=True` (it stays `False` unless you add wrappers).

For PPO, training and evaluation wrap the env with Gymnasium’s **`TimeLimit`**, then **`rl.wrappers.TimeoutPenaltyWrapper`** (Step 6: adds a timeout penalty when `truncated=True`; see `README_step6.md`). Both are applied in `train_ppo.py`, `eval_ppo.py`, `demo_ppo.py` — **not** inside `DungeonEnv`:

- **Default** `max_episode_steps` is **5000** for **training** (`PPOConfig`), **eval** (`EvalConfig`), and **demo** (`DemoConfig`), so defaults stay aligned. Adjust in `config.py` or per script: `train_ppo` / `eval_ppo` / `demo_ppo` each accept `--max-episode-steps N`.
- For **longer on-screen visualization**, raise the cap only for demo, e.g. `python -m rl.demo_ppo --max-episode-steps 50000`.
- **Why**: Gives finite episodes with `truncated=True` when the cap is hit, so rollouts end even if the agent never wins/dies, which stabilizes on-policy updates and avoids infinitely long episodes.

Use `--no-time-limit` only if you trained without `TimeLimit` and need a matching setup.

## Config

Edit defaults in `src/rl/config.py` (`PPOConfig`, `EvalConfig`, `DemoConfig`).

## Notes

- **SB3** uses `MlpPolicy`, `make_vec_env` with configurable **`n_envs`** (default **1** = single `DummyVecEnv`; larger values use SB3’s vector env stack), and `device="auto"`.
- **After `terminated=True`**, reset the environment before continuing (SB3’s `learn()` handles this internally; custom loops should call `reset()`).
- **Manual game**: run the game as before; RL scripts do not change default player entry points.
