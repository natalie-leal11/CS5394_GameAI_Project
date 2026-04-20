PHASE 5 — Guardrails and Verification

Goal
Enforce the SRS boundaries for RL integration.

Create files:

tools/rl/write_tuned_params.py
tools/rl/verify_rl_constraints.py

Requirements

1. write_tuned_params.py may write a validated config file for future runs
2. verify_rl_constraints.py must check:
   - no online learning is imported into runtime gameplay
   - runtime parameters are read-only
   - RL scope does not modify forbidden systems
   - config values remain within defined bounds
   - deterministic runtime contract is preserved

Verification should explicitly guard against changes to:
- dungeon structure
- hazard caps
- boss logic
- base player stats

Also check that runtime modules do not import uncontrolled random functions.

Deliverable behavior

- produce human-readable verification output
- fail loudly if a forbidden condition is detected

STOP AFTER IMPLEMENTATION
