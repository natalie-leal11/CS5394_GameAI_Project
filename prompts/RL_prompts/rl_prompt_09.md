# rl_prompt_09 — Long runs: resume toward ~1M steps and results reporting

**Sequence:** 9 of 18 — *Multi-session training and documented outcomes.*

**Implementation (repo):** Same `train_ppo` / `eval_ppo` / `demo_ppo` flow; guidance in `src/rl/README_step8_results.md`.

---

## Objective

Continue training in chunks until roughly **~1M total** environment steps using `dungeon_ppo_latest.zip` (or chosen checkpoint), and **record** results using the README template (metadata, eval table, optional demo notes, comparison table, metric interpretation).

## Scope

- **Included:** Cumulative step arithmetic, repeated `learn()` calls, overwriting final/latest zips; eval/demo commands; interpretation of `mean_final_room_index` vs max-during-episode, timeouts, reward comparability.
- **Not included:** Changing reward hyperparameters or env in this doc (documentation-only workflow).

## Changes required

- Resume with `--resume-model`; add timesteps in blocks (e.g. 300k + 200k) to approach target total.

## Constraints

- Compare runs only when **TimeLimit** / eval settings match.

## Implementation steps

1. Track approximate cumulative timesteps (TensorBoard / SB3 logs).
2. After each chunk, refresh eval with multi-seed command from README.
3. Paste summary into the report template; optional demo notes.

## Deliverables

- Filled milestone report and comparable progression metrics across runs.

## Sources

- `src/rl/README_step8_results.md`
