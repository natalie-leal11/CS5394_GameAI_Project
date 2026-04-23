# Phase 7 — Determinism and Replayability

Define deterministic guarantees and replay expectations for seed-controlled variation.

---

## Goal

Guarantee repeatable procedural outcomes for identical seed and input path.

---

## Determinism Guarantees

For same seed and same input path, system must reproduce:
- same `variant_id`
- same biome room-order outcomes in flexible slots
- same SAFE placement within legal bounds
- same encounter composition/count decisions within bounds
- same spawn ordering/timing realization
- same deterministic hazard/spawn placement realization within caps

---

## Replayability Model

Replayability is finite and controlled:
- three deterministic variant families (`0/1/2`)
- variation emerges from bounded slot/order/composition differences
- structure and fairness constraints remain stable across runs

---

## Boundaries

Determinism/replayability work must not:
- add online learning/adaptation loops
- feed logs into runtime decision changes
- relax existing fixed-room and cap constraints

---

## Verification Signals

Minimum replay checks should compare repeated runs on:
- run seed and variant id
- biome room orders
- room-level encounter specs
- spawn realization summaries

---

## Phase 7 Checklist

- [ ] Determinism contract is explicit
- [ ] Replay model matches finite variant design
- [ ] Verification signals are defined
- [ ] No scope expansion beyond seed-controlled variation

Stop after Phase 7.
