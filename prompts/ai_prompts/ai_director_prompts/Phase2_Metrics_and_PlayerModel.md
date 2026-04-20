# Phase 2 — Metrics and Player Model Inputs for AI Director

Use existing deterministic telemetry and classification as Director inputs.

---

## Goal

Connect AI Director decisions to existing metrics summaries and PlayerModel state without expanding telemetry scope beyond current implementation/prompt definitions.

---

## Required Inputs

AI Director consumes:
- `MetricsTracker` room/run summary signals
- `PlayerModel` state classification:
  - `STRUGGLING`
  - `STABLE`
  - `DOMINATING`
- fixed thresholds/parameters from `difficulty_params.py`

---

## Metrics Input Scope (Use Existing Tracked Signals)

Use only supported tracked signals already defined in project prompts/implementation, including representative signals such as:
- hp percent and room-end hp context
- room clear time and recent clear trends
- room damage taken and recent hp-loss trends
- room outcomes (clean clear, damaged clear, near death, death)
- total/recent deaths
- healing dependency and recovery-related summary signals

Do not invent new telemetry systems for Director input.

---

## Player Model Dependency Contract

Director behavior must be driven by deterministic player state outputs:
- `STRUGGLING`: apply relief-oriented bounded directives
- `STABLE`: preserve baseline bounded directives
- `DOMINATING`: apply challenge-oriented bounded directives

Director reads classification only; PlayerModel remains separate and deterministic.

---

## Boundaries

This phase does not:
- apply encounter rewrites
- redesign safe-room UX
- alter combat logic

It only locks input contracts for later Director planning/wiring.

---

## Phase 2 Checklist

- [ ] Director input contract names metrics summary + player state
- [ ] Input scope stays within existing tracked data
- [ ] Player state mapping to high-level intent is explicit
- [ ] No new gameplay systems are introduced

Stop after Phase 2.
