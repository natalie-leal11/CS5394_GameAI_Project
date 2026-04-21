# Phase 8 — Incremental Coding Prompt
# RL Logging Hooks

Implement **only** the following. Do not add RL training or runtime policy updates. Stop when this phase is complete.

---

## 1. Scope

- **Phase 8 deliverables:** JSONL logging for all required events (enemy_spawn, enemy_death, damage_dealt, damage_taken, room_clear, elite_spawn, mini_boss_spawn); logging must not affect gameplay performance; optional integration of AI Director (load params from ai/params_biome1.json, clamp to bounds) and metrics_tracker (player_hp_ratio, rooms_cleared, time_in_room_sec, etc.) for use by AI Director. RL is offline only—no training at runtime.
- **Source of truth:** Requirements_Analysis_Biome1.md and the master prompt (promptForpromptDungeon-v1.md). Event names and schema must match.
- **Architecture:** Extend `src/game/logger.py` or add `src/ai/` with `logger.py` / RL log writer; add `ai/metrics_tracker.py` and `ai/ai_director.py` as specified in the master prompt. Do not restructure beyond adding these hooks and modules.

---

## 2. JSONL log format (mandatory)

- **File:** One JSONL file per run (e.g. `logs/run_<run_id>.jsonl` or path from config). Each line is one JSON object.
- **Events to log:**
  - **enemy_spawn** — type (swarm/flanker/brute), room_id, timestamp; optional: elite (bool), position.
  - **enemy_death** — type, room_id, timestamp; optional: elite, killer (player/other).
  - **damage_dealt** — amount, source (player/enemy type), target (enemy/player), timestamp; optional: room_id.
  - **damage_taken** — amount, by (player/enemy), from (enemy type/contact/lava), timestamp; optional: room_id.
  - **room_clear** — room_id, timestamp; optional: duration_sec.
  - **elite_spawn** — type, room_id, timestamp.
  - **mini_boss_spawn** — room_id, timestamp.
- **Example line (master prompt):**
  `{"event": "enemy_spawn", "type": "swarm", "room_id": 3, "timestamp": 123.45}`
- **Rules:** Logging must **NOT** affect gameplay performance (e.g. write async or buffer and flush; no blocking on I/O in hot path). Game must not crash if log file cannot be opened; fallback to no-op or stderr.

---

## 3. Where to hook

- **enemy_spawn:** In spawn system (Phase 5) or when enemy is added to room; include room_id when available.
- **enemy_death:** When enemy HP reaches 0 and entity is removed (Phase 3/4).
- **damage_dealt / damage_taken:** In combat system (Phase 4) whenever damage is applied; record amount, source, target.
- **room_clear:** When last enemy in room dies (and optionally when player exits); include room_id.
- **elite_spawn:** When an elite enemy is spawned (Phase 3/5).
- **mini_boss_spawn:** When mini boss is spawned (Phase 6).

---

## 4. metrics_tracker.py (AI Director inputs)

- **Purpose:** Provide a snapshot of metrics the AI Director can read. No training; read-only for director.
- **Metrics at minimum:** player_hp_ratio (0–1), rooms_cleared, time_in_room_sec, damage_taken_recent (rolling window), damage_dealt_recent (rolling window), deaths_this_run (optional), encounter_outcome (win/loss per room).
- **Update:** Metrics tracker is updated from game events (damage, room clear, death). Expose a function or object that returns current snapshot for the director.

---

## 5. AI Director and params_biome1.json (optional for Phase 8)

- **Load:** At startup or room load, try to load `ai/params_biome1.json`. If file missing, use DEFAULT_PARAMS from config.py. Game must not crash on missing or invalid file.
- **Clamp:** All parameters must be clamped to bounds from Requirements (e.g. elite_probability 0–0.30, max_enemies_per_room 3–8, spawn_delay_ms 400–1500, etc.). Invalid values → log warning and replace with default.
- **Schema (example from master prompt):** enemy_weights (swarm, flanker, brute; sum 1.0), elite_probability, max_enemies_per_room, spawn_delay_ms, hazard_intensity, mini_boss_room_index.
- **Use:** AI Director outputs directives (enemy_pack, elite_enabled, spawn_delay_ms, hazard_intensity, mini_boss_trigger) deterministically from SEED, run_id, room_index, and current metrics snapshot. Phase 7 spawn system and room controller can use these directives to decide composition and pacing. If AI Director is not fully wired in Phase 8, at least implement load_tuned_params() and expose params to spawn/room logic.

---

## 6. Determinism and safety

- **No runtime training:** The game must NOT train or update policies during gameplay. Runtime only loads tuned parameters from config/JSON.
- **RL bounds:** RL must never override Requirements Analysis bounds (e.g. lava 6 HP/sec, max enemies per room); it can only tune within them.

---

## 7. config.py additions

- DEFAULT_PARAMS (dict or path) for when params_biome1.json is missing. Bounds for clamping (elite_probability max 0.30, etc.). Log file path or prefix.

---

## 8. Checklist (satisfy before considering Phase 8 done)

- [ ] All seven event types logged in JSONL format with required fields; example line matches schema.
- [ ] Hooks in place for spawn, death, damage, room clear, elite spawn, mini boss spawn.
- [ ] Logging does not affect gameplay performance; no crash on log failure.
- [ ] metrics_tracker exposes player_hp_ratio, rooms_cleared, time_in_room_sec, damage windows, encounter_outcome.
- [ ] params_biome1.json loaded and clamped; load_tuned_params() or equivalent exists; game safe if file missing.
- [ ] No RL training at runtime; only offline-style logging and parameter loading.

---

**Phase 8 complete. All phases (1–8) are now defined. Do not add new phases unless the master prompt is updated.**
