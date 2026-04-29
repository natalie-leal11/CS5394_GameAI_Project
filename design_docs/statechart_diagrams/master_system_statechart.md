# Master System Statechart

This consolidated diagram summarizes how the main game loop, scene navigation, gameplay phases, AI adaptation, and RL control interact.

```mermaid
stateDiagram-v2
    [*] --> AppBoot
    AppBoot --> StartScene: SceneManager.init()

    StartScene --> ControlsScene: Controls
    ControlsScene --> StartScene: Back/Esc
    StartScene --> SettingsScene: Settings
    SettingsScene --> StartScene: Back/Esc

    StartScene --> GameSession: Play/Enter
    StartScene --> AppExit: Quit/Esc->QUIT

    state GameSession {
        [*] --> ActivePlay

        ActivePlay --> Paused: Esc
        Paused --> ActivePlay: Esc/Resume
        Paused --> ReturnToMenu: Main Menu click

        ActivePlay --> StoryPanelOpen: E near altar (room 0)
        StoryPanelOpen --> ActivePlay: E/Esc closes panel

        ActivePlay --> LifeLossTransition: hp<=0 and lives remain
        LifeLossTransition --> ActivePlay: respawn complete

        ActivePlay --> DeathFlow: hp<=0 and no lives remain
        state DeathFlow {
            [*] --> Anim
            Anim --> Freeze: ~3.5s
            Freeze --> GameOver: ~1.5s
        }

        ActivePlay --> VictoryFlow: final boss defeat + final exit

        state AIDirectorLoop {
            [*] --> Evaluate
            Evaluate --> STRUGGLING: weak/critical signals
            Evaluate --> STABLE: neutral signals
            Evaluate --> DOMINATING: strong signals
            STRUGGLING --> Evaluate: next classify tick
            STABLE --> Evaluate: next classify tick
            DOMINATING --> Evaluate: next classify tick
        }
    }

    GameSession --> StartScene: ReturnToMenu
    GameSession --> StartScene: VictoryFlow timer done (non-RL)
    GameSession --> StartScene: DeathFlow.GameOver timer done (non-RL)

    state RLControl {
        [*] --> EnvReset
        EnvReset --> EpisodeRunning: SceneManager.switch_to_game()
        EpisodeRunning --> EpisodeTerminatedVictory: _victory_phase
        EpisodeRunning --> EpisodeTerminatedDefeat: _death_phase != None
        EpisodeTerminatedVictory --> EnvReset: env.reset()
        EpisodeTerminatedDefeat --> EnvReset: env.reset()
    }

    GameSession --> RLControl: rl_controlled=True
    RLControl --> StartScene: env.close() / exit training

    AppBoot --> RLControl: DungeonEnv.__init__ (RL path)
    AppExit --> [*]
```

## Reading Guide

- `GameSession` captures regular player runtime states.
- `AIDirectorLoop` is continuous during active gameplay and updates director tuning from player model classification.
- `RLControl` overlays an alternate control loop where terminal states persist until `env.reset()`.
