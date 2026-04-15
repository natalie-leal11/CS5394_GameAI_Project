# rl_prompt_13 — Master prompt: preliminary offline RL integration (SRS-bound)

**Sequence:** 13 of 18 — *Academic contract for offline difficulty tuning (separate from on-policy PPO stack).*

**Implementation (repo):** Phases 1–5 prompts and tooling under `src/game/ai/`, `src/game/rl/`, `tools/rl/`, `config/difficulty_params.json` per master sketch; `ai_prompts/rl_integration_prompts/RL_Integration_MasterPrompt.md`.

---

## Objective

Define the **preliminary, offline-only** RL support layer: tune numerical parameters for AI Director–class systems from logged data—**without** online learning, **without** mutating gameplay during a run, aligned with SRS and existing architecture.

## Scope

- **Included:** Read-only runtime parameter schema, logging export, offline reward evaluation, loader integration, guardrails; modular file layout; phase order Phase1→…→Phase5.
- **Not included:** In-game policy execution; dungeon/biome/boss structural changes.

## Changes required

- Follow `AI_Dungeon_SRS.pdf`, existing `src`, prior AI integration packs; use additive modules (no monolithic collapse).

## Constraints

- **No** online learning; **no** RL modifying gameplay mid-run; no changes to dungeon structure, room count, biomes, hazard caps, boss logic, base player stats; runtime deterministic; **phase-based prompts only**.

## Implementation steps

1. Resolve ambiguity with SRS first.
2. Execute phases sequentially (see `rl_prompt_14`–`rl_prompt_18`).
3. Stop after each phase when the phase prompt says so.

## Deliverables

- Offline pipeline artifacts per phases: schema/config, dataset export, offline evaluator, loader, verification scripts.

## Sources

- `ai_prompts/rl_integration_prompts/RL_Integration_MasterPrompt.md`
