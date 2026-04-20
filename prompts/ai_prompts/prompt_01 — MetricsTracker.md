# prompt_01 — MetricsTracker: room boundaries, reset on transition, director inputs

**Target implementation:** `src/game/ai/metrics_tracker.py`, `src/game/ai/player_model.py`, consumers in `src/game/ai/ai_director.py`.

---

## Objective

Add a **maintenance prompt** for **run/room metrics**: when counters start/end, what resets on **room load**, and which fields the **AI Director** reads each frame—so logging and tuning stay consistent with implementation.

## Scope

- **Included:** `RoomResult` enum usage; time-in-room; damage dealt/taken rollups; interaction with `room_clear` and `death`.
- **Not included:** Online learning or policy updates.

## Prompt body (for Cursor)

Produce a **field-by-field** description of `RoomMetrics` / tracker state: which events increment which counters; idempotency (no double count on duplicate events); thread-safety assumptions (single game thread).

## Constraints

- Metrics must remain **cheap** (no per-frame heap churn in hot paths).
- Debug prints gated by existing config flags (e.g. `DEBUG_ROOM_HP_METRICS_PRINT`).

## Deliverables

- One-page summary table: metric name → update site → consumer (director / logger / tests).

## Sources

- `src/game/ai/metrics_tracker.py`, `src/game/ai/ai_director.py`, `src/game/ai/ai_logger.py`
