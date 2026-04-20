# rl_prompt_18 — Phase 5: guardrails and verification

**Sequence:** 18 of 18 — *Enforce SRS boundaries for RL integration.*

**Implementation (repo):** `tools/rl/write_tuned_params.py`, `tools/rl/verify_rl_constraints.py`; `ai_prompts/rl_integration_prompts/Phase5_Guardrails_and_Verification.md`.

---

## Objective

Automate checks that runtime gameplay stays within **offline RL** rules: no forbidden imports, read-only params, no structural/stat hacks, bounded config, deterministic contract.

## Scope

- **Included:** Validated config writer; verifier checks (no online learning in gameplay path, read-only runtime parameters, forbidden system edits, bounds, determinism, uncontrolled random imports).
- **Not included:** New game features.

## Changes required

- `verify_rl_constraints.py` must **fail loudly** with human-readable output when violated.

## Constraints

- Explicit guard list includes dungeon structure, hazard caps, boss logic, base player stats (per phase file).

## Implementation steps

1. Implement verification rules.
2. Integrate into dev/CI workflow as needed.
3. **STOP AFTER IMPLEMENTATION** per phase file.

## Deliverables

- Verifier script output suitable for pre-run gating.

## Sources

- `ai_prompts/rl_integration_prompts/Phase5_Guardrails_and_Verification.md`
