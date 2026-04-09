# Step 8 — Resume training to ~1M and report results

No changes to reward, PPO hyperparameters, or `DungeonEnv` here — only **how to continue training** and **how to record outcomes**.

## 1. Reaching ~1M total training steps (resume)

Your saved policy is in `models/ppo/dungeon_ppo_latest.zip` (or `dungeon_ppo_final.zip`). Each `python -m rl.train_ppo ... --resume-model ...` call runs **`learn()` for `--timesteps` more** — those are **additional** environment steps on top of what the checkpoint already saw.

**Rough math (example):**

| Approx. cumulative before | Add with `--timesteps` | Approx. cumulative after |
|---------------------------|-------------------------|---------------------------|
| ~500k | `300000` | ~800k |
| ~800k | `200000` | ~1M |

Adjust the numbers to match what you see in TensorBoard (`total_timesteps` in logs) or the last line of a training run.

**From `src/`:**

```bash
cd src
```

**Continue once (+300k):**

```bash
python -m rl.train_ppo --timesteps 300000 --resume-model ../models/ppo/dungeon_ppo_latest.zip
```

**If you need another block to pass ~1M total:**

```bash
python -m rl.train_ppo --timesteps 300000 --resume-model ../models/ppo/dungeon_ppo_latest.zip
```

(or use `200000` / `500000` instead to hit a round total.)

After each run, `dungeon_ppo_final.zip` and `dungeon_ppo_latest.zip` are overwritten with the **new** end state — always resume from **`dungeon_ppo_latest.zip`** (or a named backup you copy yourself).

---

## 2. Evaluation (headless, after training)

From `src/`:

```bash
python -m rl.eval_ppo --model ../models/ppo/dungeon_ppo_final.zip --episodes 10 --seed 0
```

**More stable aggregates** (50 episodes total = 10 × 5 seeds):

```bash
python -m rl.eval_ppo --model ../models/ppo/dungeon_ppo_final.zip --seeds 0 1 2 3 4 --episodes 10 --deterministic
```

**Stochastic policy** (sometimes closer to training behavior):

```bash
python -m rl.eval_ppo --model ../models/ppo/dungeon_ppo_final.zip --seeds 0 1 2 3 4 --episodes 10 --no-deterministic
```

Copy the printed **summary** block into the template below.

---

## 3. Demo (visible window)

From `src/`:

```bash
python -m rl.demo_ppo --model ../models/ppo/dungeon_ppo_final.zip
```

Use the same `--model` path as the checkpoint you want to watch.

---

## 4. Result report template (fill in)

### Run metadata

| Field | Value |
|-------|-------|
| **Date** | |
| **Model file** | e.g. `models/ppo/dungeon_ppo_final.zip` |
| **Approx. total training timesteps** (cumulative, after resume) | e.g. 800k / 1M |
| **Eval command** | paste exact command |

### Eval summary (from `eval_ppo` console)

| Metric | Value |
|--------|-------|
| **mean_reward** (std) | |
| **mean_episode_length** (std) | |
| **wins** | |
| **defeats** | |
| **timeouts** (truncated) / total episodes | |
| **mean_final_room_index** (std) | |
| **mean_max_room_index_during_episode** (std) | |
| **mean_max_rooms_cleared_during_episode** (std) | |

### Optional — demo notes

| Question | Notes |
|----------|--------|
| Leaves room 0? | |
| Movement / door seeking? | |
| Combat engagement? | |
| Obvious failure modes (stuck, idle, etc.)? | |

### Comparison (fill numbers from prior experiments)

| Stage | Approx. timesteps | mean_final_room_index | mean_reward | timeouts / total |
|-------|-------------------|------------------------|-------------|------------------|
| **100k** (Step 6.1 ref) | ~100k | ~2.9 | ~−7.9 | 10/10 |
| **500k** (Step 6.2 ref) | ~500k | ~7.0 | ~−4.1 | 10/10 |
| **Latest run (this report)** | | | | |

---

## 5. How to interpret results (brief)

- **mean_final_room_index** vs **mean_max_room_index_during_episode**: final is where the episode ended; max-during-episode catches backtracking. Higher usually means broader exploration.
- **mean_max_rooms_cleared_during_episode**: should track campaign progress; compare across runs with the **same** `TimeLimit` / eval settings.
- **timeouts**: With a fixed `max_episode_steps`, many runs still ending in truncation is normal until the policy finishes faster or wins — compare **fraction** of timeout and **episode length** vs cap.
- **mean_reward**: Not comparable across different reward versions; **within** the same reward (Step 6+), higher is generally better, but **room metrics** are often clearer for progression.
- **Multi-seed eval** (`--seeds`): Reduces variance from a single seed; report **std** lines when present.

---

## 6. Revert

Remove this file if you do not want Step 8 reporting docs in the repo.
