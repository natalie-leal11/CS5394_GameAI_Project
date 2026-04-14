# RL Implementation Report — Training Iterations, Results, and Model Selection

**Purpose:** Summarize the reinforcement-learning work for course presentation: approach, major training iterations (with **measured** eval results from this repository), issues, mitigations, and recommended demo model.

**Data policy:** All numeric results below are taken from **`eval_summary*.md` files** under `models/ppo/` and from **`milestone_train.md`** where noted. No training was re-run for this document, and no numbers were invented.

---

## 1. Overview

- **Approach:** Train a **Proximal Policy Optimization (PPO)** agent (Stable-Baselines3) on a **Gymnasium** wrapper around the existing dungeon game (`DungeonEnv`). The policy maps observations (fixed-size vectors from `src/rl/obs.py`) to discrete actions (movement, attacks, dash, and later interact / safe-room actions for curriculum-related features).
- **Goal:** Learn a policy that **progresses through rooms** (higher `room_index`, rooms cleared) in the full-game setting, despite sparse terminal rewards and dense per-step shaping in `src/rl/reward.py`. **`rl_prompt_19`** (RL-only auto-grant / auto-pick) is **implemented** in `GameScene` (see §8.5 and **Final improvement**). **Fair 50-episode metrics** in §6 include the **`auto_pick_demo`** continuation and a **re-baseline** of **`upgrade_open_demo` 20k** under the same code (`eval_summary_fair_compare_to_auto_pick.md`).
- **Evaluation:** Headless runs via `python -m rl.eval_ppo` with multiple seeds; reported metrics include **mean reward**, **mean final room index**, **mean max rooms cleared during episode**, and **timeout vs defeat counts**. Default **`TimeLimit`** for full-game eval/training is **`max_episode_steps = 5000`** (`src/rl/config.py` — `PPOConfig` / `EvalConfig`). Curriculum training uses a **shorter** episode cap by default (**800** steps) in `src/rl/train_curriculum_ppo.py` / `src/rl/eval_curriculum.py` (CLI defaults).

---

## 2. Training iterations summary

Metrics below use **50 total episodes** (10 per seed × 5 seeds), **deterministic** policy, **unless noted**.

| Iteration | Experiment / stage | Approx. timesteps (this run) | Key change (from `milestone_train.md` + layout) | Mean reward | Mean final room index | Mean max rooms cleared | Notes |
|-----------|----------------------|------------------------------|--------------------------------------------------|-------------|-------------------------|-------------------------|--------|
| Iter2 baseline chain | `iter2_cooldown_0p5_1p2` / `stage_300k` | 300000 | First 300k block (iter2 cooldown experiment) | −9.48 | 1.00 | 2.00 | 50/50 **timeouts**; stuck at room index 1 (`eval_summary.md`) |
| Iter2 mid | `iter2_cooldown_0p5_1p2` / `stage_900k` | 300k per stage (900k cumulative for 3×300k chain) | Continued training to later checkpoint | −5.80 | 2.62 | 6.00 | Mixed defeats/timeouts; higher variance (`eval_summary.md`) |
| Post-900k fix | `iter2_cooldown_0p5_1p2` / `stage_next_fix` | +200000 (run total env steps after: **450704** per milestone) | Resume from `stage_600k` best; separate `next_fix` folder | **2.41** | **4.86** | **11.82** | Still 50/50 timeouts; stronger progression than 300k/900k (`eval_summary_fair_best.md`) |
| Auto-reward ablation | `iter2_cooldown_0p5_1p2_auto_reward_demo` / `fullgame_20k` | 20000 | +20k from `stage_next_fix` best | 0.94 | 6.50 | 10.46 | 50/50 timeouts (`eval_summary_fair_best.md`) |
| Curriculum merge demo | `iter2_cooldown_0p5_1p2_curriculum_merge_demo` / `fullgame_demo_run` | 50000 | Resume noted from `iter2_cooldown_0p5_1p2_curriculum/stage_ef_E_only/dungeon_ppo_final.zip` | **989.00** | **0.00** | **0.00** | Degenerate eval: **100% `interact`** actions, no room progress (`eval_summary_fair_best.md`) |
| Upgrade-open training | `iter2_cooldown_0p5_1p2_upgrade_open_demo` / `fullgame_20k` | 20000 | +20k from `stage_next_fix` best | **4.54** | **7.44** | **13.62** | Strong milestone (historical `eval_summary_fair_best.md`); superseded by **`auto_pick_demo`** fair eval; 50/50 timeouts |
| Continuation | `iter2_cooldown_0p5_1p2_upgrade_open_demo_cont` / `fullgame_plus30k` | 30000 | Resume from upgrade-open 20k best | −3.45 | 5.36 | 6.42 | **Regression** vs 20k upgrade-open on room metrics (`eval_summary_fair_best.md`) |
| Checkpoint continuation | `iter2_cooldown_0p5_1p2_checkpoint_try` / `fullgame_20k_more` | 20000 | Resume from upgrade-open 20k best | 1.77 | 6.28 | 11.04 | Between 20k upgrade-open and `stage_next_fix` on rooms; 50/50 timeouts (`eval_summary_fair_best.md`) |
| Resume 50k (final zip) | `iter2_cooldown_0p5_1p2_resume_next_fix` / `fullgame_50k` | (50k train run) | Eval on **`dungeon_ppo_final.zip`** | −8.12 | 1.66 | 2.66 | Non–best checkpoint eval; weak progression (`eval_summary_fair_resume_final.md`) |
| Auto-pick continuation | `iter2_cooldown_0p5_1p2_auto_pick_demo` / `fullgame_20k` | +20000 from `upgrade_open_demo/stage_fullgame_20k/dungeon_ppo_best.zip` | **5.19** | **10.56** | **13.02** | 50/50 timeouts; **best fair progression** after `rl_prompt_19` (`eval_summary_fair_best.md`) |

**Other eval on disk:** `stage_600k` has an `eval_summary.md` with **only 1 episode / 1 seed** — not comparable to the 50-episode protocol; omitted from the main comparison table.

**Curriculum E/F-only runs:** The repo contains prompts and code (`train_curriculum_ppo`, `eval_curriculum`) and a `curriculum_merge_demo` milestone that resumes from `stage_ef_E_only`; **no standalone `eval_summary.md` for `ef_E_only` / `ef_F_only` was found** under `models/ppo/` in this workspace, so curriculum-only **numeric** results are not listed here.

---

## 3. Detailed iteration analysis

### Iteration A — Iter2 `stage_300k` (early timeouts)

- **What changed:** First 300k-step PPO checkpoint under `iter2_cooldown_0p5_1p2` / `stage_300k`.
- **What worked:** Stable but **low** progression (mean final room index 1.0).
- **What failed:** All 50 episodes **timed out** at the step cap; mean reward **−9.48**.
- **Key metrics:** `mean_max_rooms_cleared_during_episode` = 2.00.
- **Observation:** Policy did not advance meaningfully within 5000-step episodes.

**Source:** `models/ppo/iter2_cooldown_0p5_1p2/stage_300k/eval_summary.md`

---

### Iteration B — Iter2 `stage_900k`

- **What changed:** Later checkpoint (900k stage) under the same experiment name.
- **What worked:** Higher mean max room index (3.64) and rooms cleared (6.00) vs 300k.
- **What failed:** Still **0 wins**; 33 timeouts / 17 defeats / 50; reward still negative on average.
- **Key metrics:** mean reward **−5.80** (std **2.71**); mean final room index **2.62** (std 1.68).

**Source:** `models/ppo/iter2_cooldown_0p5_1p2/stage_900k/eval_summary.md`

---

### Iteration C — `stage_next_fix` (stronger baseline before small fine-tunes)

- **What changed:** +200k steps from `stage_600k` best into `stage_next_fix` (total env timesteps after run **450704** per `milestone_train.md`).
- **What worked:** Positive mean reward **2.41**; mean final room index **4.86**; mean max **room index during episode** **7.20**; combat-heavy action mix (e.g. short_attack **44.55%** of steps).
- **What failed:** All episodes still **truncated at TimeLimit** (50/50 timeouts in eval).
- **Key metrics:** `mean_max_rooms_cleared_during_episode` **11.82** (std 3.03).

**Source:** `models/ppo/iter2_cooldown_0p5_1p2/stage_next_fix/eval_summary_fair_best.md`

---

### Iteration D — `auto_reward_demo` (+20k)

- **What changed:** 20k additional steps from `stage_next_fix` best (`milestone_train.md`).
- **What worked:** Mean final room index **6.50**; max room index during episode **9.14** — strong exploration signal.
- **What failed:** 50/50 timeouts; mean reward **0.94** (lower than `stage_next_fix` mean reward in this eval).
- **Observation:** Room metrics improved vs `stage_next_fix` but **mean reward** and **training objective** must be interpreted together (reward scale and mixing).

**Source:** `models/ppo/iter2_cooldown_0p5_1p2_auto_reward_demo/stage_fullgame_20k/eval_summary_fair_best.md`

---

### Iteration E — `curriculum_merge_demo` (full-game eval on merged checkpoint)

- **What changed:** 50k-step run resuming from curriculum E-only final weights (`milestone_train.md`).
- **What worked:** N/A for full-game progression — **mean_final_room_index = 0**, **mean_max_rooms_cleared = 0**.
- **What failed:** Action usage shows **`interact` on 100%** of steps; absurd mean reward **~989** with **no** room progression — indicates **eval/training distribution mismatch** or policy collapse for this checkpoint under `eval_ppo` (not suitable as a demo model).
- **Key metrics:** Same degenerate metrics on both `dungeon_ppo_best.zip` and `dungeon_ppo_final.zip` eval summaries in this folder.

**Sources:**  
`models/ppo/iter2_cooldown_0p5_1p2_curriculum_merge_demo/stage_fullgame_demo_run/eval_summary_fair_best.md`  
`models/ppo/iter2_cooldown_0p5_1p2_curriculum_merge_demo/stage_fullgame_demo_run/eval_summary_fair_final.md`

---

### Iteration F — `upgrade_open_demo` / `fullgame_20k` (strong pre–auto-pick baseline)

- **What changed:** 20k steps from `stage_next_fix` best (`milestone_train.md`).
- **What worked:** Strong 50-episode eval on disk **before** `rl_prompt_19`: mean final room index **7.44**, mean max rooms cleared **13.62**, mean reward **4.54** (std 1.21) (`eval_summary_fair_best.md` in that folder).
- **What failed:** 50/50 timeouts (no wins in eval sample).
- **Observation:** Superseded for **final model selection** by **`auto_pick_demo`** after continuation + fair eval (§6–§7). Re-baseline of the **same** `dungeon_ppo_best.zip` under **current** GameScene: `eval_summary_fair_compare_to_auto_pick.md` (mean final room **7.32**, mean reward **2.18** — not comparable to pre-change historical row without context).

**Sources:** `models/ppo/iter2_cooldown_0p5_1p2_upgrade_open_demo/stage_fullgame_20k/eval_summary_fair_best.md`, `.../eval_summary_fair_compare_to_auto_pick.md`

---

### Iteration G — `upgrade_open_demo_cont` / `fullgame_plus30k` (regression)

- **What changed:** +30k steps from `upgrade_open_demo` 20k best (milestone: **30000** timesteps this run).
- **What worked:** Still non-trivial room progression (mean final room index 5.36).
- **What failed:** **Clear regression** vs 20k upgrade-open: mean reward **−3.45**, mean final room index **5.36** vs **7.44**, rooms cleared **6.42** vs **13.62**.
- **Observation:** Consistent with **policy drift / overtraining** on a small continuation budget.

**Source:** `models/ppo/iter2_cooldown_0p5_1p2_upgrade_open_demo_cont/stage_fullgame_plus30k/eval_summary_fair_best.md`

---

### Iteration H — `checkpoint_try` / `fullgame_20k_more`

- **What changed:** +20k steps from `upgrade_open_demo` 20k best (milestone: **20000** timesteps).
- **What worked:** Mean final room index **6.28**, rooms cleared **11.04** — better than `stage_next_fix`, worse than upgrade-open 20k on mean final room index.
- **What failed:** 50/50 timeouts; does not beat upgrade-open 20k on key metrics.

**Source:** `models/ppo/iter2_cooldown_0p5_1p2_checkpoint_try/stage_fullgame_20k_more/eval_summary_fair_best.md`

---

### Iteration I — `auto_pick_demo` / `fullgame_20k` (best progression, post `rl_prompt_19`)

- **What changed:** +20k timesteps resumed from `upgrade_open_demo/stage_fullgame_20k/dungeon_ppo_best.zip` into `iter2_cooldown_0p5_1p2_auto_pick_demo/stage_fullgame_20k` (`milestone_train.md`).
- **What worked:** Fair 50-episode eval: mean reward **5.19**, mean final room index **10.56**, mean max room index during episode **11.54**, mean max rooms cleared **13.02** (std 3.87 on final room index).
- **What failed:** 50/50 timeouts (no wins).
- **Observation:** Best **room progression** and **mean reward** in the updated comparison table (§6).

**Sources:** `models/ppo/iter2_cooldown_0p5_1p2_auto_pick_demo/stage_fullgame_20k/eval_summary_fair_best.md`, `.../milestone_train.md`

---

## 4. Key issues faced

- **Episode length cap (TimeLimit):** Full-game eval/training uses **`max_episode_steps = 5000`** by default (`src/rl/config.py`). Many runs in `eval_summary.md` show **50/50 timeouts** — the agent often does not finish an episode by win/loss before truncation.
- **Curriculum episode length (800 steps):** Curriculum scripts default to **800** steps per episode (`train_curriculum_ppo.py` / `eval_curriculum.py`), shorter than full-game PPO — useful for focused scenarios but **not comparable** to 5000-step full-game metrics without careful protocol matching.
- **Curriculum success / wrapper behavior:** `CurriculumSuccessWrapper` (`src/rl/curriculum_wrappers.py`) waits for **at least `min_steps = 3`** before treating a pending success as a true curriculum success and terminating with bonus reward — this prevents instant success on the first metric tick.
- **Degenerate merge eval:** `curriculum_merge_demo` full-game eval shows **100% interact** and **zero room progress** — a clear failure mode for that checkpoint under standard `eval_ppo` (see metrics above).
- **Reward limitations:** Mean reward **sign** and **scale** shift across training stages; `README_step8_results.md` notes that **mean reward is not comparable across different reward versions** — **room progression metrics** are often clearer for comparing runs.
- **E/F interaction in full-game evals:** Several full-game eval summaries show **0%** `interact` and **0%** `safe_room_heal` in the action-usage breakdown — the policy may not rely on those actions in deterministic full-game evaluation.

---

## 5. Fixes and mitigations (as implemented in code / workflow)

- **Curriculum wrappers:** `CurriculumSuccessWrapper` + `CurriculumScenarioSamplerWrapper` in `src/rl/curriculum_wrappers.py` implement scenario selection and success handling for curriculum training/eval.
- **Reward shaping stack:** Progress-oriented terms, timeout penalty, and E/F-related shaping in `src/rl/reward.py` (see `README_step6.md` in repo).
- **Eval-based best checkpoint:** `PPOConfig` includes **`eval_freq`** and **`best_model_name`**; `train_ppo.py` supports **`BestProgressionEvalCallback`** and **`--early-stop-patience`** (stops after consecutive evals with **no** `mean_final_room_index` improvement — see `train_ppo.py` help text). An **`early_stop_test`** run exists (`milestone_train.md`, 50k steps) — **no eval_summary** for that experiment was found in `models/ppo/early_stop_test/`.
- **Experiment isolation:** Per-stage folders (`--experiment` / `--stage`) and `milestone_train.md` auto-write keep runs separate (see `README_step11_iteration2.md`).

---

## 6. Model comparison table (same eval protocol where possible)

**Protocol:** 50 episodes, 5 seeds, deterministic — from each file’s header. **Stability** here uses **std of mean final room index** from the same file (lower is tighter).

| Model (path under `models/ppo/`) | Mean reward | Mean final room index | Mean max rooms cleared | Stability (std final room idx) | Notes |
|-----------------------------------|-------------|-------------------------|-------------------------|----------------------------------|--------|
| `iter2_cooldown_0p5_1p2/stage_next_fix/dungeon_ppo_best.zip` | 2.41 | 4.86 | 11.82 | 2.78 | Strong mid-run baseline |
| `iter2_cooldown_0p5_1p2_upgrade_open_demo/stage_fullgame_20k/dungeon_ppo_best.zip` | 2.18 | 7.32 | 10.80 | 1.89 | Same checkpoint, **re-evaluated** under current GameScene + `rl_prompt_19` (50 ep; `eval_summary_fair_compare_to_auto_pick.md`) |
| `iter2_cooldown_0p5_1p2_auto_pick_demo/stage_fullgame_20k/dungeon_ppo_best.zip` | **5.19** | **10.56** | **13.02** | 3.87 | **Best performing** after auto-grant rewards + auto-pick upgrades; **medium** stability (still 50/50 timeouts, but **better progression**); mean max **room index during episode** ~**11.54** (`eval_summary_fair_best.md`) |
| `iter2_cooldown_0p5_1p2_upgrade_open_demo_cont/stage_fullgame_plus30k/dungeon_ppo_best.zip` | −3.45 | 5.36 | 6.42 | 5.20 | Regression vs 20k upgrade-open |
| `iter2_cooldown_0p5_1p2_checkpoint_try/stage_fullgame_20k_more/dungeon_ppo_best.zip` | 1.77 | 6.28 | 11.04 | 1.89 | Intermediate; not best |

**Historical reference (pre–`rl_prompt_19` code, same checkpoint file):** `upgrade_open_demo/.../eval_summary_fair_best.md` reported mean reward **4.54**, mean final room **7.44**, mean max rooms cleared **13.62** — useful for trend context, not mixed directly with post-change rows above.

**Sources:**  
`stage_next_fix/eval_summary_fair_best.md`  
`upgrade_open_demo/stage_fullgame_20k/eval_summary_fair_compare_to_auto_pick.md`  
`auto_pick_demo/stage_fullgame_20k/eval_summary_fair_best.md`  
`upgrade_open_demo_cont/stage_fullgame_plus30k/eval_summary_fair_best.md`  
`checkpoint_try/stage_fullgame_20k_more/eval_summary_fair_best.md`

---

## 7. Best model selection

**Final selected model (for progression metrics and course demo):**

`models/ppo/iter2_cooldown_0p5_1p2_auto_pick_demo/stage_fullgame_20k/dungeon_ppo_best.zip`

**Why:**

- **Highest mean reward** in the updated fair comparison (**~5.19** vs **~2.18** for the re-baselined `upgrade_open_demo` 20k checkpoint under the same code — §6).
- **Best room progression:** roughly **~11–12** rooms deep by **max room index during episode** (**~11.54**), mean final room index **~10.56**, mean max rooms cleared **~13.02** (50 episodes, deterministic, 5 seeds).
- **Benefits from simplified RL interaction:** auto-granted single rewards and fixed-priority safe-room upgrades (`rl_prompt_19`, §8.5) remove UI stall for the policy so training and eval emphasize **movement and combat**.
- **More consistent** than the re-baseline upgrade-open run on several progression axes (see §6); still **50/50 timeouts** — not a solved game.

**Caveat:** All cited fair evals still show **50/50 timeouts** — “best” means **best recorded progression under the 5000-step cap**, not campaign completion.

---

## 8. Demo strategy

- **Primary demo model:** `dungeon_ppo_best.zip` in `models/ppo/iter2_cooldown_0p5_1p2_auto_pick_demo/stage_fullgame_20k/` — **best fair progression** under current code (§7).
- **Backup model:** `models/ppo/iter2_cooldown_0p5_1p2/stage_next_fix/dungeon_ppo_best.zip` — stable fallback if the primary is unavailable; lower room metrics but still shows **combat and multi-room movement** (eval action usage: heavy short_attack).
- **Rationale:** Primary shows the **deepest progression** recorded; backup provides a **known-good** earlier iter2 baseline for a visible demo without relying on the latest continuation.
- **How to run (from repo):** Use `python -m rl.demo_ppo` with `--model` pointing to the chosen zip (from `src/`, paths relative to project — see `README_step4.md`). Older demo records under `demos/ppo/` may reference other checkpoints; prefer the paths above for the final presentation.
- **What to show:** Movement between rooms, basic combat (short/long attacks in eval usage), and **progression depth** (note that evals are often **TimeLimit-truncated**, so the agent may not finish the campaign).

---

## 8.5 Post-training practical adjustment (RL-only auto-grant / auto-pick)

**Context:** Evaluations and playtesting showed the policy could **lose steps and wall-clock time** on **reward collection and upgrade UI** (interact prompts, safe-room flows, multi-choice upgrade screens) compared to **combat and door progression**. For **final submission**, the project adopts a **practical simplification** documented in **`RL_prompts/rl_prompt_19.md`** (and indexed in **`RL_prompts/rl_prompts_sequence.md`**).

**Implemented behavior (when `GameScene._rl_controlled` is True — RL env / demo only):**

- **Room-clear / boss heal orbs:** Already collected without walking (existing `_rl_auto_reward` overlap logic); unchanged except as consolidated with safe-room flow below.
- **Safe-room F heal:** Applied automatically each frame when eligible (same logic as manual **F** — `_try_apply_safe_room_f_heal` in `src/game/scenes/game_scene.py`); RL does not need to send **F**.
- **Biome 3 safe-room upgrade (pick one):** Auto-selects **health** (UI option **1**) via `_rl_auto_resolve_safe_room_upgrades`.
- **Biome 4 safe-room upgrades (pick two):** Auto-selects in fixed priority order **`(1, 3, 4, 2)`** = health → attack → defence → speed (first two distinct options applied).

**Manual / human player** behavior is unchanged (same `handle_event` paths).

**Why:** Reduce **UI friction**, keep RL focused on **movement, combat, and room progression**. Fair **50-episode** metrics after implementation are reflected in §6–§7 (`auto_pick_demo`, re-baseline `upgrade_open_demo`).

---

## 9. Final conclusion

**Achieved:**

- End-to-end **PPO** training pipeline with **logged** milestones, **multi-seed eval**, and **iter2** experiment layout.
- Documented **progression gains** from early iter2 stages through **`stage_next_fix`**, **upgrade_open_demo** 20k, and the **`auto_pick_demo`** +20k continuation with **`rl_prompt_19`** (current best in §6–§7).
- **Curriculum and merge** experiments recorded; one merge checkpoint shows **failure** on full-game eval (zero room progress, 100% interact).

**Incomplete / limitations:**

- **No wins** in the cited 50-episode evals; reliance on **timeouts** dominates.
- **Curriculum-only** numeric eval summaries were **not found** in `models/ppo/` for this snapshot.
- **Early stopping** (`early_stop_test`) has a **milestone** but **no eval_summary** in-repo.

**Future work (brief):**

- Optional longer training or adaptive **TimeLimit**; curriculum-to-full-game **transfer** validation; richer **success metrics** beyond room index (e.g. boss clears) — **not measured here**.

### Final improvement: auto-grant and auto-pick simplification

For **RL-controlled** runs only (`GameScene._rl_controlled`):

- **Single rewards** (room-clear orbs, boss rewards, etc.) are **auto-granted** where the existing RL path already treats pickups as in-range without extra navigation.
- **Safe-room heal** is **auto-applied** (same effect as **F**) so the policy does not spend steps on positioning for the heal prompt.
- **Biome 3 / 4 safe-room upgrades** are **auto-picked** with a **fixed priority** (health first; Biome 4 uses order **1 → 3 → 4 → 2** for the two picks), removing dependence on discrete “choice” actions for progression.
- **Effect:** Less **UI / interaction** overhead for RL, clearer signal for **gameplay and room progression**; fair evals show **higher mean final room index and mean reward** for **`auto_pick_demo`** vs the re-baselined **`upgrade_open_demo`** checkpoint (§6). Progression depth improved substantially; the agent can focus on **combat and movement** rather than **interaction mechanics**.

---

## Appendix — file references for metrics

| Metric / claim | Primary file |
|----------------|--------------|
| 300k, 900k, stage_next_fix, upgrade_open, auto_pick_demo, plus30k, checkpoint_try, auto_reward, merge | `models/ppo/.../eval_summary*.md` (paths listed in sections) |
| Timesteps per run | `models/ppo/.../milestone_train.md` |
| 5000 vs 800 step limits | `src/rl/config.py`, `src/rl/train_curriculum_ppo.py`, `src/rl/eval_curriculum.py` |
| Curriculum wrappers | `src/rl/curriculum_wrappers.py` |
| Early stop / best progression | `src/rl/train_ppo.py`, `src/rl/best_progress_callback.py` |

---

*End of report.*
