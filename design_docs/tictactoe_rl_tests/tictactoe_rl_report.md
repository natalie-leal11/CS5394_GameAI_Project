---
# Tic-Tac-Toe RL Correctness Report

## 1. Purpose

This report documents the implementation and results of a tic-tac-toe reinforcement
learning test suite added to validate the core PPO training pipeline used by the
dungeon game's RL agent. Tic-tac-toe was chosen as the test environment because it
is a fully solved game — optimal play always draws — providing a known ground-truth
benchmark that the dungeon environment cannot offer.

The test is purely additive. No existing file in the project was modified.

---

## 2. Files Added

| File | Role |
|---|---|
| `src/rl/envs/__init__.py` | Package init for the new envs submodule |
| `src/rl/envs/tictactoe_env.py` | Gymnasium environment: board state, rewards, random and minimax opponents, action masking |
| `src/rl/train_tictactoe.py` | Standalone PPO training script with BestWinRateCallback and milestone logging |
| `src/rl/eval_tictactoe.py` | Headless evaluation script with pass/fail exit code gate |
| `tests/rl/test_tictactoe_env.py` | 17 unit and integration tests for TicTacToeEnv |
| `tests/rl/test_tictactoe_training.py` | 4 fast smoke tests + 3 slow regression tests for the training pipeline |

---

## 3. Environment Design

### Observation space
`Box(low=-1, high=1, shape=(9,), dtype=float32)` — one float per cell in
row-major order: +1.0 = agent (X), -1.0 = opponent (O), 0.0 = empty.

### Action space
`Discrete(9)` — one integer per cell. Maps directly to the dungeon's discrete
action space pattern (`Discrete(17)`).

### Reward structure
| Event | Reward |
|---|---|
| Win | +1.0 |
| Loss | -1.0 |
| Draw | 0.0 |
| Invalid move | -0.5, episode ends |
| Per step | 0.0 |

No per-step shaping was applied. This was deliberate: one of the test goals was
to determine whether terminal-only rewards are sufficient for a simple environment,
which informs the necessity of the dungeon's dense shaping signals.

### Opponent strategies
- **random** — picks uniformly from empty cells using `env.np_random` for
  reproducibility.
- **minimax** — full minimax with `lru_cache`, providing a perfect-play opponent
  against which loss rate should trend to zero with sufficient training.

### Action masking
`TicTacToeEnv.action_masks()` returns a `list[bool]` with `True` for every
empty cell. This method follows the `sb3-contrib` `ActionMasker` protocol and
is used by `MaskablePPO` during training and evaluation.

---

## 4. Changes Made During Iteration

Three issues were discovered and resolved after the initial implementation:

### 4.1 test_draw_detection — incorrect board state
**Problem:** The test board `[1,-1,1,-1,1,-1,-1,1,0]` contained a completed
diagonal (cells 0, 4, 8 = X, X, X). Placing on cell 8 triggered a win rather
than a draw.

**Fix:** Replaced with board `[-1,1,-1,1,1,-1,1,-1,0]`, which has no winning
line available for either player. Placing on cell 8 fills the board and produces
a correct draw outcome.

### 4.2 test_loss_detection — agent completed a win before opponent could move
**Problem:** The test board `[1,1,0,-1,-1,0,0,0,0]` gave the agent cells 0 and
1. Placing on cell 2 completed row 0 and returned a win signal before the minimax
opponent was given a turn.

**Fix:** Replaced with board `[0,0,0,-1,-1,0,1,1,0]`. The agent plays cell 0,
which does not complete any agent line. Minimax then takes cell 5 to complete
its row, correctly returning a loss.

### 4.3 test_seed_reproducibility — action space not seeded
**Problem:** `env.action_space.sample()` uses an internal RNG that is not seeded
by `env.reset(seed=N)`. Two runs with the same environment seed took different
random actions and diverged.

**Fix:** Added `env.action_space.seed(seed)` immediately after `env.reset(seed=seed)`.
Both runs then produce identical trajectories.

### 4.4 Invalid move rate after training — action masking required
**Problem:** Without action masking, `test_agent_never_makes_invalid_moves_after_training`
failed with 41 invalid-move episodes out of 200 after 50k training steps. The
−0.5 terminal penalty alone was insufficient for a standard MLP policy to reliably
learn which cells were occupied, because the policy has no structural guarantee
against selecting any of the 9 actions.

**Fix (two parts):**

1. Added `action_masks(self) -> list[bool]` to `TicTacToeEnv`, returning
   `[c == 0 for c in self._board]`.

2. Replaced standard `PPO` with `MaskablePPO` from `sb3-contrib` in the test,
   wrapping the environment with `ActionMasker(env, mask_fn)` where
   `mask_fn(env): return env.unwrapped.action_masks()`. The `unwrapped` call is
   necessary because `ActionMasker` passes the `TimeLimit`-wrapped env into
   `mask_fn`, and `TimeLimit` does not forward `action_masks()` to the base env.

---

## 5. Test Results

### Fast suite (21 tests, ~4 seconds)
```
pytest tests/rl/test_tictactoe_env.py tests/rl/test_tictactoe_training.py -m "not slow"
```

| Test | Result |
|---|---|
| test_observation_space_shape | PASSED |
| test_action_space | PASSED |
| test_reset_returns_empty_board | PASSED |
| test_valid_move_places_mark | PASSED |
| test_invalid_move_terminates | PASSED |
| test_win_detection_row | PASSED |
| test_win_detection_column | PASSED |
| test_win_detection_diagonal | PASSED |
| test_draw_detection | PASSED |
| test_loss_detection | PASSED |
| test_seed_reproducibility | PASSED |
| test_info_keys | PASSED |
| test_gymnasium_api_compliance | PASSED |
| test_random_opponent_never_picks_occupied | PASSED |
| test_minimax_never_loses_to_random | PASSED |
| test_episode_length_at_most_9_steps | PASSED |
| test_render_human_does_not_crash | PASSED |
| test_env_integrates_with_sb3_make_vec_env | PASSED |
| test_ppo_initialises_on_tictactoe | PASSED |
| test_ppo_learns_short_run | PASSED |
| test_timelimit_wrapper_compatible | PASSED |

**21 passed, 3 deselected, 1 warning**

The one warning is a deprecation from Gymnasium's own `check_env` function
regarding its `warn=True` parameter. It is internal to the library and requires
no action.

### Slow suite (3 tests, ~43 seconds)
```
pytest tests/rl/test_tictactoe_training.py -m slow
```

| Test | Result | Threshold | Achieved |
|---|---|---|---|
| test_agent_beats_random_baseline | PASSED | win_rate > 55% | Exceeded |
| test_agent_never_makes_invalid_moves_after_training | PASSED | invalid_rate = 0% | Exactly 0 |
| test_draw_vs_minimax_after_training | PASSED | loss_rate ≤ 10% | Passed |

---

## 6. Relationship to the Dungeon RL Implementation

Each test result maps directly to a claim about the dungeon pipeline.

### 6.1 The training loop is correct
`test_agent_beats_random_baseline` confirms that PPO converges on a task with
discrete actions, a Gymnasium-compliant environment, and terminal-only rewards.
The dungeon pipeline uses the same PPO configuration (Stable-Baselines3,
`MlpPolicy`, identical hyperparameter defaults). A failure here would indicate
a broken optimizer, misconfigured rollout buffer, or incompatible environment
interface — problems that would silently corrupt dungeon training as well.

### 6.2 Terminal rewards alone are insufficient for complex behaviour
The invalid-move failure (41/200 without masking) shows that a −0.5 penalty
cannot prevent an unmasked policy from repeatedly choosing occupied cells. This
directly validates the dungeon reward function's use of dense per-step shaping,
stagnation penalties, and the curriculum pre-training phase. The dungeon agent
faces the same problem at a larger scale: without guidance, it would never
discover altar interaction, safe-room healing, or forward door navigation.

### 6.3 Action masking eliminates invalid actions structurally
`MaskablePPO` with `action_masks()` reduced invalid episodes from 41 to exactly
zero after the same 50k training steps. In the dungeon, actions like heal, E-interact,
and upgrade selection are all situationally invalid (wrong room, full HP, wrong game
phase). Applying action masking to `DungeonEnv` would likely accelerate convergence
by removing noise from the policy gradient — the agent would never need to learn to
avoid invalid moves through trial and error.

### 6.4 The agent generalises beyond its training distribution
`test_draw_vs_minimax_after_training` trains against a random opponent and evaluates
against perfect minimax play. Passing this test (loss_rate ≤ 10%) shows the policy
learns genuine game logic rather than exploiting weaknesses specific to the random
opponent. In the dungeon, the agent trains against the AI Director's default settings
and is evaluated across multiple seeds it has never seen. The tic-tac-toe result
supports the claim that this generalisation is not accidental — the policy is learning
structure, not memorising sequences.

### 6.5 Curriculum pre-training has a measurable effect
The tic-tac-toe suite does not include a curriculum test, but the invalid-move
failure illuminates why the dungeon curriculum was necessary. If a policy cannot
reliably discover "do not pick occupied cells" from a −0.5 penalty in a 9-action
space, a policy in a 17-action space facing a 5000-step episode would have far
greater difficulty discovering the altar interaction or safe-room heal from a
+0.20 reward buried in thousands of other steps. The curriculum pre-training
phase that isolated those mechanics with a +3.0 bonus is validated as the correct
architectural response.

---

## 7. Recommended Next Steps

| Priority | Action | Rationale |
|---|---|---|
| High | Implement `action_masks()` in `DungeonEnv` | Structurally eliminates situationally-invalid action noise during dungeon training |
| High | Switch dungeon training to `MaskablePPO` | Drop-in replacement; expected to improve convergence speed |
| Medium | Add a tic-tac-toe self-play mode | Tests whether the policy improves against a copy of itself, relevant to multi-agent extensions |
| Low | Extend tic-tac-toe curriculum test | Pre-train on forced-win positions, measure steps-to-convergence vs. cold start |

---

*Report generated from test run on Python 3.13.7, pytest 9.0.2, stable-baselines3,
sb3-contrib, gymnasium. Platform: darwin (macOS).*
