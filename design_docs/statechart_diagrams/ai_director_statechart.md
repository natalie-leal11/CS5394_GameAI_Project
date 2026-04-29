# AI Director Statechart

This statechart models how player performance classification drives AI Director outputs.

```mermaid
stateDiagram-v2
    [*] --> EvaluateSummary: room-end/current-run metrics input

    EvaluateSummary --> STRUGGLING: critical HP OR recent death OR weak signals >= 2
    EvaluateSummary --> DOMINATING: high HP + no recent death + strong signals >= 2
    EvaluateSummary --> STABLE: otherwise

    STRUGGLING --> EvaluateSummary: next classification cycle
    DOMINATING --> EvaluateSummary: next classification cycle
    STABLE --> EvaluateSummary: next classification cycle

    state STRUGGLING {
        [*] --> LowPressure
        LowPressure: enemy_adjustment < 0
        LowPressure: reinforcement reduced
        LowPressure: hazard tune < 1.0
        LowPressure: composition safer/lighter
    }

    state STABLE {
        [*] --> MediumPressure
        MediumPressure: neutral adjustment
        MediumPressure: balanced composition
        MediumPressure: hazard tune = 1.0
    }

    state DOMINATING {
        [*] --> HighPressure
        HighPressure: enemy_adjustment > 0
        HighPressure: reinforcement increased
        HighPressure: hazard tune > 1.0
        HighPressure: composition aggressive/harder
    }
```

## Life-Phase Visibility Override

The final visible player state used by the director is constrained by life phase:

- Life 3 always forces `STRUGGLING`.
- Life 2 can only be `STABLE` or `STRUGGLING`.
- Life 1 allows `DOMINATING`, `STABLE`, or `STRUGGLING`.
