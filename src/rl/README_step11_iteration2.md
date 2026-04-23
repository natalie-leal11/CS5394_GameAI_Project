# Step 11 — Iteration 2 PPO experiment layout (`iter2_cooldown_0p5_1p2`)

Isolated training after **short attack cooldown = 0.5 s** and **long attack cooldown = 1.2 s** (`game.config`). This workflow uses **separate folders per milestone** so checkpoints, TensorBoard logs, eval summaries, and human-demo notes are **not overwritten** between 300k / 600k / 900k.

## Folder structure (under repo root)

```text
models/ppo/iter2_cooldown_0p5_1p2/
  stage_300k/          # first 300k timesteps (fresh PPO)
    checkpoints/       # SB3 periodic checkpoints (optional)
    dungeon_ppo_best.zip
    dungeon_ppo_final.zip
    dungeon_ppo_latest.zip
    milestone_train.md # auto-written by train_ppo when using --experiment/--stage
    eval_summary.md    # from eval_ppo --experiment/--stage (optional)
  stage_600k/          # next 300k (resume from stage_300k best or final)
  stage_900k/          # next 300k (resume from stage_600k best or final)

logs/ppo/iter2_cooldown_0p5_1p2/
  stage_300k/tensorboard/...
  stage_600k/tensorboard/...
  stage_900k/tensorboard/...

demos/ppo/iter2_cooldown_0p5_1p2/
  demo_300k/demo_run.md
  demo_600k/demo_run.md
  demo_900k/demo_run.md
```

Create demo directories as needed (or they are created when writing `demo_run.md`).

**Previous experiments** (e.g. `models/ppo/dungeon_ppo_best.zip` outside this tree) are untouched if you only use `--experiment iter2_cooldown_0p5_1p2`.

---

## Which model to resume?

| Stage | Resume from (recommended) | Fallback |
|-------|-----------------------------|----------|
| 600k | `stage_300k/dungeon_ppo_best.zip` | `stage_300k/dungeon_ppo_final.zip` if no best was saved |
| 900k | `stage_600k/dungeon_ppo_best.zip` | `stage_600k/dungeon_ppo_final.zip` |

**Always add 300k more timesteps** per stage (`--timesteps 300000`). SB3 continues `num_timesteps` from the loaded zip.

---

## Commands (from `src/`)

Paths below use `../` relative to `src/`; adjust if your cwd differs.

### 1) Fresh training — 300k (stage 1)

```bash
python -m rl.train_ppo --experiment iter2_cooldown_0p5_1p2 --stage 300k --timesteps 300000 --eval-freq 50000 --eval-episodes 8
```

Writes models to `models/ppo/iter2_cooldown_0p5_1p2/stage_300k/`, logs to `logs/ppo/iter2_cooldown_0p5_1p2/stage_300k/`, and `milestone_train.md` in the stage folder.

### 2) Resume — reach 600k total (stage 2)

```bash
python -m rl.train_ppo --experiment iter2_cooldown_0p5_1p2 --stage 600k --timesteps 300000 --resume-model ../models/ppo/iter2_cooldown_0p5_1p2/stage_300k/dungeon_ppo_best.zip --eval-freq 50000 --eval-episodes 8
```

### 3) Resume — reach 900k total (stage 3)

```bash
python -m rl.train_ppo --experiment iter2_cooldown_0p5_1p2 --stage 900k --timesteps 300000 --resume-model ../models/ppo/iter2_cooldown_0p5_1p2/stage_600k/dungeon_ppo_best.zip --eval-freq 50000 --eval-episodes 8
```

---

## Eval (headless) per milestone

After each stage completes, evaluate **best** or **final** (your choice):

```bash
python -m rl.eval_ppo --model ../models/ppo/iter2_cooldown_0p5_1p2/stage_300k/dungeon_ppo_best.zip --experiment iter2_cooldown_0p5_1p2 --stage 300k --episodes 10 --seeds 0 1 2 3 4
```

Repeat with `--stage 600k` / `--stage 900k` and the matching model path.  
`--experiment` + `--stage` writes **`eval_summary.md`** into that stage’s **models** folder (unless you pass `--summary-out` explicitly).

---

## Human demo per milestone (non-overwriting)

Each milestone gets its own **`demo_{stage}/`** folder. Use **`--experiment`** and **`--stage`** so `demo_run.md` defaults there:

```bash
python -m rl.demo_ppo --model ../models/ppo/iter2_cooldown_0p5_1p2/stage_300k/dungeon_ppo_best.zip --experiment iter2_cooldown_0p5_1p2 --stage 300k --notes "qualitative notes after 300k"
```

```bash
python -m rl.demo_ppo --model ../models/ppo/iter2_cooldown_0p5_1p2/stage_600k/dungeon_ppo_best.zip --experiment iter2_cooldown_0p5_1p2 --stage 600k
```

```bash
python -m rl.demo_ppo --model ../models/ppo/iter2_cooldown_0p5_1p2/stage_900k/dungeon_ppo_best.zip --experiment iter2_cooldown_0p5_1p2 --stage 900k
```

**Video:** not recorded automatically; add a link or file path in the **Notes** section of `demo_run.md` or in `--notes`.

---

## Optional: multi-checkpoint comparison

```bash
python -m rl.compare_ppo_models ../models/ppo/iter2_cooldown_0p5_1p2/stage_300k/dungeon_ppo_best.zip ../models/ppo/iter2_cooldown_0p5_1p2/stage_600k/dungeon_ppo_best.zip ../models/ppo/iter2_cooldown_0p5_1p2/stage_900k/dungeon_ppo_best.zip --episodes 10
```

---

## CLI reference (Step 11 additions)

| Script | Flags |
|--------|--------|
| `train_ppo` | `--experiment NAME --stage 300k` sets `models/ppo/NAME/stage_300k` and `logs/ppo/NAME/stage_300k` unless `--models-dir` / `--logs-dir` override. Writes `milestone_train.md` in `models_dir` unless `--write-run-summary` points elsewhere. |
| `eval_ppo` | `--experiment` + `--stage` → default `--summary-out` = `models/.../stage_{stage}/eval_summary.md` |
| `demo_ppo` | `--experiment` + `--stage` → default `--summary-out` = `demos/ppo/.../demo_{stage}/demo_run.md` |

`rl/experiment_layout.py` defines path helpers and `DEFAULT_EXPERIMENT_NAME`.

---

## Preserved artifacts checklist

- [ ] `stage_300k/milestone_train.md` after training  
- [ ] `stage_300k/eval_summary.md` after eval  
- [ ] `demo_300k/demo_run.md` after human demo  
- Repeat for 600k and 900k  

Nothing in this layout overwrites `stage_300k` when you train `stage_600k` — separate directories per stage.
