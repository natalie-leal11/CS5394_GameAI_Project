---
# Tic-Tac-Toe RL Test — Executive Summary

## What was built
A self-contained tic-tac-toe Gymnasium environment and PPO training pipeline
added to the project as a correctness test for the dungeon RL implementation.
Six new files. Zero changes to existing code.

## What was tested
- Environment contract (observation space, action space, rewards, termination)
- Gymnasium API compliance
- PPO initialisation, short training run, checkpoint save/reload
- Agent performance after training: win rate vs random, invalid move rate, loss rate vs minimax

## Final results
| Test | Outcome |
|---|---|
| 21 fast tests | All passed |
| Beats random baseline (win > 55%) | Passed |
| Zero invalid moves after training (MaskablePPO) | Passed |
| Holds against minimax (loss ≤ 10%) | Passed |

## Key finding
Standard PPO cannot reliably avoid invalid moves through penalty alone (41/200
episodes invalid at 50k steps). Action masking via MaskablePPO reduces this to
exactly zero. This directly supports adding action masking to DungeonEnv.

## Files
- Full report: `design_docs/tictactoe_rl_report.md`
- Environment: `src/rl/envs/tictactoe_env.py`
- Tests: `tests/rl/test_tictactoe_env.py`, `tests/rl/test_tictactoe_training.py`
