# Biome 4 spec cross-check

**Scope:** Compared **`docs/biome4_full_spec.md`** to the codebase.

- **`docs/biome4_full_spec.md`:** **Not present** in the repository. This cross-check uses **`Implemented Game Description/biome4_full_spec.md`** (the only `biome4_full_spec.md` found). If `docs/biome4_full_spec.md` is added later, re-run verification against that file.

---

## Mismatches (spec ↔ code)

- **§2 “Shuffled non-Beginner” COMBAT lineups:** Spec implies fallback (Swarm, Flanker, Ranged, Heavy) for COMBAT except “Beginner-exclusive” local 0/1. **Code** (`get_biome4_spawn_specs`) always applies **local index first**: `room_idx == 0` + COMBAT → 4-enemy lineup; `room_idx == 1` + COMBAT → Brute/Ranged/Heavy — **regardless of `BEGINNER_TEST_MODE`**. Those branches are **not** Beginner-only. Shuffled COMBAT at **local 0** still gets the “Room 24” composition; at **local 1** the “Room 25” composition.

- **§2 last bullet (SAFE not at 28):** Spec says player gets “**standard safe heal + single upgrade flow** (same as other safe rooms for non–Room-28)”. **Code:** Biome 4 SAFE not at index 28 has **no** 1/2/3 upgrade panel (that is **`BIOME3_SAFE_ROOM_INDEX` = 21** only). After H, **`_safe_room_upgrade_pending`** is cleared by **keys 1 or 2 with no stat upgrades** (`game_scene`). That is **not** “single upgrade flow”.

- **§7 Fireball config name:** Spec writes **`FINAL_BOSS_FIREBALL_MAX`**. **Config** defines **`FINAL_BOSS_FIREBALL_RANGE_MIN`** / **`FINAL_BOSS_FIREBALL_RANGE_MAX`** (both unused in boss logic). Wrong identifier in spec.

- **§7 Teleport strike damage:** Spec suggests damage is mainly `_teleport_strike_damage_frame`. **`apply_enemy_attacks`** still uses **`_enemy_attack_params("final_boss")`** → **`FINAL_BOSS_ATTACK_RADIUS`** (40) and **`FINAL_BOSS_ATTACK_OFFSET`** (50): player must be within **40 px** of the offset attack point; **`enemy.damage`** (24) applies. Spec understates radius/offset involvement.

- **§7 Spawn delay (`BOSS_SPAWN_IDLE_DELAY`):** Spec/config **0.6 s**. **`FinalBoss.update`**: in state **`spawn_idle`**, **`_set_state("idle")`** runs **every frame** of that branch, so **`state` becomes `idle` on the first update** and **`_spawn_idle_timer` is no longer decremented**. **Observed behavior:** boss leaves `spawn_idle` immediately (delay **not** enforced as written). Spec treats 0.6 s as real; implementation diverges.

- **§10 / §2 framing “Room 28”:** Dual-upgrade (2 picks, keys 1–4) runs only when **`current_room_index == BIOME4_SAFE_ROOM_INDEX` (28)** **and** the player uses H there (**room must be SAFE** for H heal). In **shuffled** Biome 4, if SAFE is **not** campaign room 28, **that dual-upgrade path never runs** for any SAFE room. Spec partially notes non-28 behavior in §10 but does not clearly state that **shuffle can remove dual-upgrade entirely**.

---

## Missing values / facts (in spec, should name for accuracy)

- **`FINAL_BOSS_FIREBALL_CAST_COOLDOWN`:** Config value is **`2`** (integer), not `2.0` in source.

- **Teleport strike RNG seed:** Spec gives formula **`SEED + room_index * 1000 + int(_time*10)`**. **Code:** **`random.Random(SEED + room_index * 1000 + int(self._time * 10))`** — same idea; spec omits that this is the **`Random` seed per call**, not a single global draw.

- **Elite multipliers:** Spec cites **×1.4 / ×1.2**; **code** uses **`ENEMY_ELITE_HP_MULT`** / **`ENEMY_ELITE_DAMAGE_MULT`** from config (currently 1.4 and 1.2). Fine if config unchanged; spec does not name these symbols.

- **`_adds_spawned`:** Set **`True`** on phase change; **never read** elsewhere — spec does not mention this unused flag.

---

## Ambiguities (spec wording vs code)

- **“Room 24 / 25 / … (local N) — when type X and fixed Beginner mapping”:** Tables mix **campaign position in Beginner order** with **local index**. After shuffle, **campaign 24** may be SAFE, not COMBAT; headings read as if room number equals composition. Clearer: tie compositions to **`get_biome4_spawn_specs(room_idx, room_type)`** branches.

- **§7 Chase movement:** Spec ties chase to **`dist > STOP_DISTANCE`** and **`_attack_recovery_timer <= 0`**. Boss can still be under **`attack_cooldown_timer`** while moving; spec does not say whether cooldown blocks movement (it does **not** block chase in code).

- **§7 “Wall passage” for lava wave:** Spec argues both “no `ignore_obstacles`” and “no obstacle resolution”. Accurate but redundant; could be read as implying different behavior for fireball vs lava — only **fireball** sets **`ignore_obstacles=True`** (for any future wall checks); **lava** has no wall stop in **`Projectile.update`**.

- **Victory overlay timing:** **Update** comment says “0–2 full victory / 2–5 black”; **draw** uses **`_victory_timer < 2.0`** for banner, else black + bg. Aligned, but “full victory screen” vs “banner only” (first 2s) is vague.

- **`make_room` vs `room_order_biome4`:** Spec says seed passed from **`make_room`** — **`build_room` / room factory** in **`dungeon/room.py`** calls **`room_order_biome4(seed)`** with **`SEED`** when **`seed` param default** matches; worth naming **`make_room_campaign_room`** or actual function if spec is tightened.

---

## Items verified as consistent (no issue listed above)

- `BIOME4_ROOM_COUNT`, `BIOME4_START_INDEX`, `room_order_biome4` fixed vs shuffle, FINAL_BOSS last.
- `get_biome4_spawn_specs` ELITE/AMBUSH fallbacks vs room_idx 2/3 special cases (same lists where applicable).
- FINAL_BOSS hazard caps (10% / 15% / 65%), boss spawn delay **2.0 s**, center tile spawn.
- Phase cycles, revive HP/delay/invuln, meteor telegraph durations, contact damage rects, reward heal **40%**, victory **5.0 s** → start menu.
- §14 unused config entries (`FINAL_BOSS_FINAL_DEATH_DELAY_SEC`, rush, unused fireball/meteor range config, etc.).

---

*Generated by cross-checking spec against current `src/` tree. No spec file was modified.*
