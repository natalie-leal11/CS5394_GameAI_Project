# RL Episode Statechart (Gymnasium)

```mermaid
stateDiagram-v2
    [*] --> EnvConstructed: DungeonEnv.__init__()
    EnvConstructed --> EpisodeReset: reset(seed, options)

    EpisodeReset --> Running: switch_to_game() + initial observation

    Running --> Running: step(action) while not terminal
    Running --> VictoryTerminal: GameScene._victory_phase == True
    Running --> DefeatTerminal: GameScene._death_phase != None

    VictoryTerminal --> EpisodeReset: next reset()
    DefeatTerminal --> EpisodeReset: next reset()

    EpisodeReset --> Closed: close()
    Running --> Closed: close()
    VictoryTerminal --> Closed: close()
    DefeatTerminal --> Closed: close()
    Closed --> [*]
```

## Transition Semantics

- `terminated=True` when victory or any death phase is active.
- `truncated=False` in `DungeonEnv.step()` (timeouts are wrapper-level when enabled).
- In RL-controlled mode, GameScene victory/defeat screens remain terminal until `env.reset()`.
