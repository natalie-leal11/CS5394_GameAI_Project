# Phase 9 — Logging and Determinism

Add deterministic AI-side logging and verification boundaries for Director behavior.

---

## Goal

Support offline analysis and deterministic verification without affecting runtime gameplay decisions.

---

## Required AI-Side Log Content

Log enough context to inspect Director behavior:
- run seed
- room index, biome index, room type
- player state
- selected directive values
- safe-room bias context and offered-option context
- room outcome summaries used for analysis
- end-of-run AI summary

Use local file logs only (JSON/JSONL style is acceptable).

---

## Determinism Verification Scope

Provide lightweight verification that confirms:
- same seed + same input path -> same directive sequence
- same seed + same input path -> same safe-room bias outcomes
- same seed + same input path -> same encounter adjustment outcomes

Keep verification lightweight and implementation-aligned.

---

## Hard Boundaries

Logs and checks must not:
- feed back into runtime decision-making
- mutate gameplay state
- require online services
- introduce runtime learning

---

## Phase 9 Checklist

- [ ] Per-room Director decisions are inspectable
- [ ] End-of-run AI summary is produced
- [ ] Determinism checks exist and are bounded
- [ ] Logging remains offline-only and non-influential to runtime behavior

Stop after Phase 9.
