# RL prompts — index (implementation order)

This folder documents **prompts and specs that match what was implemented** for reinforcement learning in this project. Items **`rl_prompt_01`–`rl_prompt_12`** follow the **on-policy PPO agent pipeline** (environment → reward → training → evaluation → longer runs → milestone experiments → curriculum). Items **`rl_prompt_13`–`rl_prompt_18`** follow the **offline SRS integration** pack (difficulty schema through guardrails). Item **`rl_prompt_19`** documents a **post-training practical simplification**: auto-grant single rewards and auto-pick multi-choice upgrades on the RL path (see file for full spec).

Each `rl_prompt_XX.md` uses the same section template: **Objective**, **Scope**, **Changes required**, **Constraints**, **Implementation steps**, **Deliverables**, **Sources**, plus a short **Implementation (repo)** line pointing at code paths.

| # | File | What this step implemented |
|---|------|----------------------------|
| 1 | [rl_prompt_01.md](rl_prompt_01.md) | Gymnasium `DungeonEnv`, headless stepping, placeholder obs |
| 2 | [rl_prompt_02.md](rl_prompt_02.md) | Smoke test / `PYTHONPATH` runbook (`README` Step 1) |
| 3 | [rl_prompt_03.md](rl_prompt_03.md) | Real observation vector (`obs.py`, README Step 2) |
| 4 | [rl_prompt_04.md](rl_prompt_04.md) | Base per-step reward (`reward.py`, README Step 3) |
| 5 | [rl_prompt_05.md](rl_prompt_05.md) | **PPO training** — SB3 `train_ppo`, resume, checkpoints, TensorBoard |
| 6 | [rl_prompt_06.md](rl_prompt_06.md) | **PPO eval & demo** — `eval_ppo`, `demo_ppo`, `TimeLimit` / wrapper stack |
| 7 | [rl_prompt_07.md](rl_prompt_07.md) | Progress-oriented reward + `TimeoutPenaltyWrapper` (README Step 6) |
| 8 | [rl_prompt_08.md](rl_prompt_08.md) | E/F interact & safe-heal reward shaping (README Step 6 §12) |
| 9 | [rl_prompt_09.md](rl_prompt_09.md) | Long training runs (~1M) and results template (README Step 8) |
| 10 | [rl_prompt_10.md](rl_prompt_10.md) | Iteration 2 folder layout & milestone training (`iter2_cooldown_0p5_1p2`) |
| 11 | [rl_prompt_11.md](rl_prompt_11.md) | Per-milestone eval, demo, optional `compare_ppo_models` |
| 12 | [rl_prompt_12.md](rl_prompt_12.md) | Curriculum PPO + eval for scenarios E and F |
| 13 | [rl_prompt_13.md](rl_prompt_13.md) | Master prompt — offline RL integration (SRS) |
| 14 | [rl_prompt_14.md](rl_prompt_14.md) | Phase 1 — runtime parameter contract |
| 15 | [rl_prompt_15.md](rl_prompt_15.md) | Phase 2 — offline logging & dataset export |
| 16 | [rl_prompt_16.md](rl_prompt_16.md) | Phase 3 — offline reward evaluation utilities |
| 17 | [rl_prompt_17.md](rl_prompt_17.md) | Phase 4 — runtime loader integration |
| 18 | [rl_prompt_18.md](rl_prompt_18.md) | Phase 5 — guardrails & verification |
| 19 | [rl_prompt_19.md](rl_prompt_19.md) | Auto-grant single rewards & auto-pick multi-choice upgrades (RL path; final submission simplification) |

**Reading order for “how PPO was implemented”:** start at **`rl_prompt_01`** and read through **`rl_prompt_12`**. PPO itself is **`rl_prompt_05`** (training) and **`rl_prompt_06`** (evaluation and wrapper stack around the env).

---

*Former single-file content was split into `rl_prompt_01.md`–`rl_prompt_18.md`; **`rl_prompt_19.md`** was added for the auto-grant / auto-pick simplification. This file is the table of contents only.*
