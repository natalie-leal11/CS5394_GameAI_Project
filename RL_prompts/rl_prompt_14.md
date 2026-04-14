# rl_prompt_14 — Phase 1: runtime parameter contract (schema + JSON)

**Sequence:** 14 of 18 — *Typed difficulty config, read-only at runtime.*

**Implementation (repo):** `src/game/ai/difficulty_params.py`, `config/difficulty_params.json`; specs in `Phase1_Runtime_Params_Contract.md` and `Implement Phase 1-Runtime Parameter Contract for RL integration..md`.

---

## Objective

Create the **read-only** runtime parameter schema and default JSON for AI systems: numerical, deterministic, loaded from file (not learned online).

## Scope

- **Included:** Typed model; fields such as struggling/stable/dominating thresholds, enemy multiplier, elite/ambush bias, reinforcement probability, healing bias (per phase files); nested JSON in extended variant (`player_model`, `director`, `rewards`, `metrics`, `combat`).
- **Not included:** Wiring into gameplay in the narrow “schema only” variant; online RL.

## Changes required

- Phase short file: create `difficulty_params.py` + `difficulty_params.json`; **STOP AFTER FILE CREATION** (no gameplay wire yet).
- Extended variant: dataclass-style schema, `from_dict`, basic validation; **do not** modify `ai_director.py` / PlayerModel until loader phase.

## Constraints

- Runtime mutation forbidden; no learning at runtime; follow SRS offline RL scope.

## Implementation steps

1. Define schema and defaults.
2. Load and validate JSON in isolation.
3. Document immutability during gameplay.

## Deliverables

- Loadable schema + config; no unintended behavior change until later phases integrate.

## Sources

- `ai_prompts/rl_integration_prompts/Phase1_Runtime_Params_Contract.md`
- `ai_prompts/rl_integration_prompts/Implement Phase 1-Runtime Parameter Contract for RL integration..md`
