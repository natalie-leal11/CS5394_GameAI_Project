# test_prompts/

Structured prompt hierarchy for generating the dungeon game's pytest suite.

**These are prompts, not tests.** When executed by an agent, each prompt
creates or extends a test file under `tests/<category>/`.

## Rules (enforced by every prompt)

- ONLY generate test code (pytest).
- NEVER modify code under `src/`.
- NEVER overwrite existing test files — additive only.
- Create folders/files if missing; extend if present.
- Use fixed seeds; keep tests fast (< 2 s each).
- Mock heavy systems (pyglet window, RL training, full `GameScene`).

## Layout

```
test_prompts/
  unit/          # 34 prompts
  integration/   # 13 prompts
  concurrency/   # 6 prompts
  regression/    # 6 prompts
  performance/   # 5 prompts
  error/         # 7 prompts
  rl/            # 8 prompts
```

Run prompts sequentially. Each one is self-contained; later prompts may
extend files created by earlier ones but never overwrite them.

After executing prompts, run:

```
pytest tests
```
