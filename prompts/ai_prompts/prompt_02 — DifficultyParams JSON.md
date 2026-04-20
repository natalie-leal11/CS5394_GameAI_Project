# prompt_02 — DifficultyParams JSON: schema, load, clamp, safe-room upgrade bias

**Target implementation:** `src/game/ai/difficulty_params.py`, `config/difficulty_params.json`, `src/game/ai/ai_director.py`.

---

## Objective

Prompt focused on the **runtime JSON contract** for difficulty: loading from `config/difficulty_params.json`, **clamping** invalid values, **immutable** defaults, and **upgrade bias** maps used by safe-room offers.

## Scope

- **Included:** `DifficultyParams` / `PlayerModelParams` fields; path resolution from project root; behavior when file is missing or malformed.
- **Not included:** Editing balance numbers without a design ticket.

## Prompt body (for Cursor)

Document each **numeric bound** referenced in code (elite probability, spawn delay, hazard intensity). Show **before/after** clamp example for an invalid JSON fragment. Link to **MetricsTracker** thresholds for struggling/dominating.

## Constraints

- Game must **never crash** on bad JSON; fall back to defaults with a warning.
- No silent expansion of bounds beyond Requirements Analysis caps.

## Deliverables

- Validation checklist for adding a **new** JSON field (code + JSON + test).

## Sources

- `src/game/ai/difficulty_params.py`, `config/difficulty_params.json`, `src/game/ai/ai_director.py`
