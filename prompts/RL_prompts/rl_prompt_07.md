# rl_prompt_07 — Progress-oriented reward shaping + `TimeoutPenaltyWrapper`

**Sequence:** 7 of 18 — *Reduce timeout-farming; add progress signals.*

**Implementation (repo):** `src/rl/reward.py` (additional terms), `src/rl/wrappers.py` (`TimeoutPenaltyWrapper`), wired in `train_ppo.py` / `eval_ppo.py` / `demo_ppo.py`; `src/rl/README_step6.md`.

---

## Objective

Add **progress-oriented** shaping on top of Step 3: timeout penalty when outer `TimeLimit` truncates, remove passive alive bonus, approach-to-enemy/door potentials, enemy damage reward, anti-idle, adjusted step clip—**without** changing manual gameplay.

## Scope

- **Included:** Constants (`R_TIMEOUT_PENALTY`, `R_APPROACH_*`, `R_ENEMY_DAMAGE_COEF`, `R_ANTI_IDLE_EXTRA`, `R_STEP_CLIP`, etc.); extra `RewardSnapshot` fields; wrapper **outside** `TimeLimit`.
- **Not included:** E/F interact/safe-heal terms (next prompt).

## Changes required

- `DungeonEnv.step()` runs before `TimeLimit` sets `truncated`; timeout penalty applied in `TimeoutPenaltyWrapper` after `TimeLimit` (see README).

## Constraints

- Manual gameplay unchanged; `rl/test_env.py` covers breakdown keys and timeout wrapper behavior.

## Implementation steps

1. Extend `reward.py` with new terms and breakdown keys.
2. Ensure wrapper order in PPO scripts matches README.
3. Run tests for finite reward and timeout component on truncation.

## Deliverables

- Clearer incentive to progress and engage combat/doors instead of stalling to the time cap.

## Sources

- `src/rl/README_step6.md` (through timeout penalty and tests)
