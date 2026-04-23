# rl_prompt_17 — Phase 4: runtime loader integration

**Sequence:** 17 of 18 — *Load JSON at startup; read-only in game.*

**Implementation (repo):** `src/game/ai/difficulty_params_loader.py`, `src/game/main.py`, wiring into AI Director / Player Model / metrics / rewards / combat per narrow prompt; `Phase4_Runtime_Loader_Integration.md` and `Implement Phase 1-Runtime Parameter Contract for RL integration.md` (body = Phase 4).

---

## Objective

Load `config/difficulty_params.json` **once** at startup, validate against the schema, pass **read-only** `DifficultyParams` into AI systems, preserve determinism (same file + seed + inputs).

## Scope

- **Included:** Loader + startup wiring; replace hardcoded numerics with `params.*` buckets (`director`, `player_model`, `metrics`, `rewards`, `combat`) per narrow implementation prompt.
- **Not included:** Learning loops; runtime write-back to disk; random parameter edits.

## Changes required

- Narrow variant: replace listed constants in `ai_director.py`, `player_model.py`, `metrics_tracker.py`, reward-related config usage, combat multipliers—without changing mechanics beyond numeric sourcing.
- Verify: default JSON preserves behavior; logs still valid.

## Constraints

- Immutable after load; **STOP after integration** per narrow prompt.

## Implementation steps

1. Implement `load_difficulty_params_json()` and validation.
2. Thread params into constructors.
3. Replace hardcoded values per mapping; run smoke tests.

## Deliverables

- Integrated read-only params and file change report.

## Sources

- `ai_prompts/rl_integration_prompts/Phase4_Runtime_Loader_Integration.md`
- `ai_prompts/rl_integration_prompts/Implement Phase 1-Runtime Parameter Contract for RL integration.md`
