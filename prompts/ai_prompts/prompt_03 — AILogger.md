# prompt_03 — AILogger: JSONL events, flush policy, room transitions

**Target implementation:** `src/game/ai/ai_logger.py`, `src/game/logger.py`, hooks from `src/game/scenes/game_scene.py` and combat/spawn.

---

## Objective

Single prompt for **AI / RL JSONL logging**: which **event types** are emitted, **batching vs flush** on room change, and **failure** behavior when disk is unavailable.

## Scope

- **Included:** Event schema keys; correlation with `run_id` / `seed`; optional compression or rotation (if present).
- **Not included:** TensorBoard or PPO training logs.

## Prompt body (for Cursor)

Enumerate **all** `log_*` call sites in gameplay code and map them to JSONL **event** names. Specify whether flush is **sync** or **buffered** and the maximum buffer size before forced flush.

## Constraints

- Logging must not block the **frame** for long I/O; document async/buffer strategy.
- If AI systems are disabled, logger must no-op cheaply.

## Deliverables

- Example **three-line** JSONL excerpt from a single room transition (sanitized numbers).

## Sources

- `src/game/ai/ai_logger.py`, `src/game/logger.py`, `src/game/scenes/game_scene.py`
