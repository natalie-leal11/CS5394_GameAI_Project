# Phase 8 — Logging and Testing

Define offline logging and lightweight testing for seed determinism verification.

---

## Goal

Provide enough seed-focused telemetry to verify reproducibility and bounded variation behavior.

---

## Required Seed Log Content

Log enough to validate seed behavior:
- run seed
- variant id (`run_seed % 3`)
- per-biome room-order summary (including SAFE location)
- per-room type and encounter composition summary
- per-room spawn pattern/ordering/position summaries
- deterministic hazard realization summary within caps
- end-of-run marker

Use local file logs only.

---

## Testing Scope (Lightweight)

Add or run lightweight deterministic checks:
- same seed repeated -> same logged procedural outputs
- different seeds -> only seed-controlled sections differ
- fixed structure invariants unchanged (milestones/room counts/caps)

No large framework rewrite required.

---

## Hard Boundaries

Logging/testing must not:
- influence gameplay runtime decisions
- introduce non-deterministic runtime behavior
- redesign unrelated systems

---

## Phase 8 Checklist

- [ ] Seed logs include run/variant and room-level procedural summaries
- [ ] Repeat-run determinism checks are defined
- [ ] Fixed invariants are checked
- [ ] Logging/testing is offline-only and non-influential to gameplay

Stop after Phase 8.
