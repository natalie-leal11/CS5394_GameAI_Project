# `EnemyBase.update` — behavior implementation

This note describes how standard enemies (swarm, flanker, brute, heavy; subclasses may override) implement per-frame AI and motion in `src/entities/enemy_base.py`, primarily through `EnemyBase.update`.

## Role of `update`

Each frame, `update`:

- Ensures animations are loaded and skips work if the enemy is `inactive`.
- Handles damage flash timing, player-death idle mode, attack cooldown, death transition, and death animation completion.
- Runs a simple **chase → stop → attack** loop from distance to the player.
- Applies **wall slide** and **anti-stuck** steering (with a **Heavy-specific** deterministic sidestep instead of random stuck steering).
- Integrates **position**, **clamps** to the room (or global bounds), and **resolves overlap** with the player when the player is not dashing.
- Updates **Heavy stuck timing** and generic **stuck-frame** tracking, then advances **animation**.

Reference excerpt:

```462:628:src/entities/enemy_base.py
    def update(
        self,
        dt: float,
        player,
        room_rect: pygame.Rect | None = None,
        heavy_clearance_cb=None,
        heavy_retreat_cb=None,
    ) -> None:
        self._ensure_animations_loaded()
        if self.inactive:
            return
        if self.damage_flash_timer > 0.0:
            self.damage_flash_timer = max(0.0, self.damage_flash_timer - dt)
        if self._player_dead:
            # When player is dead, normal AI is paused; only idle animation is advanced.
            self._idle_during_player_death(dt)
            return

        # Tick attack cooldown
        if self.attack_cooldown_timer > 0.0:
            self.attack_cooldown_timer = max(0.0, self.attack_cooldown_timer - dt)

        if self.hp <= 0 and self.state != "death":
            self._set_state("death")

        if self.state == "death":
            _, finished = self._anim_state.advance(dt)
            if finished:
                self.inactive = True
            return

        # Simple chase AI towards player with separation / attack distance
        px, py = player.world_pos
        x, y = self.world_pos
        dx = px - x
        dy = py - y
        dist = math.hypot(dx, dy)
        vx, vy = 0.0, 0.0
        stop_dist = _enemy_stop_distance(self.enemy_type)
        engage_dist = _enemy_effective_stop_distance(self.enemy_type)
        ...
        self._anim_state.advance(dt)
```

**API note:** `heavy_clearance_cb` and `heavy_retreat_cb` are accepted so callers (e.g. `game_scene.py`) can pass Heavy-related hooks. **`EnemyBase.update` does not use them**; Heavy behavior in the base class is implemented inline (sidestep + stuck timer).

---

## 1. Setup and early exits

- **`_ensure_animations_loaded()`** — Lazily fills animation frames and initializes idle if needed.
- **`inactive`** — Enemies that finished the death animation skip all logic.
- **`damage_flash_timer`** — Counts down the brief red hit flash (visual feedback).
- **`_player_dead`** — When the player has died, normal AI is paused; only `_idle_during_player_death(dt)` runs so idle animation still advances.

---

## 2. Cooldowns and death

- **`attack_cooldown_timer`** — Decremented every frame. Actual strike timing/damage is handled elsewhere (e.g. combat / attack hitboxes) in coordination with `state == "attack"`.
- **HP ≤ 0** — Transitions to `"death"` once.
- **`state == "death"`** — Only advances the death animation; when it finishes, sets **`inactive = True`** and returns (no movement or chase).

---

## 3. Core chase vs engage behavior

Behavior is **pure pursuit** toward `player.world_pos`:

- **`stop_dist`** — From `_enemy_stop_distance(self.enemy_type)`. Used when **pushing** the enemy out of overlap with the player so spacing stays consistent with melee tuning.
- **`engage_dist`** — From `_enemy_effective_stop_distance`: base stop distance **plus** a per-type melee **engage buffer** (`ENEMY_MELEE_ENGAGE_BUFFER_*`). The enemy switches to **attack** when `dist <= engage_dist`, slightly **before** the raw stop distance, so windup and attack radius can line up with combat code.

Branching:

1. If **`dist > engage_dist`** — Normalize `(dx, dy)`, scale by **`move_speed`**, set **`facing`**, state **`walk`**.
2. If **`dist` is extremely small** — **`idle`** (degenerate case).
3. If **`dist <= engage_dist`** — Zero velocity, state **`attack`** (“inside attack radius: stop moving”).

**Separation between enemies** is not implemented inside `update`. Helpers such as `enemy_min_separation` / `enemy_type_priority` exist on the module for other systems; they are not part of this method.

---

## 4. Heavy-only deterministic sidestep

For **`enemy_type == "heavy"`** (`_heavy_brute_move`), if the enemy is still beyond `engage_dist` and **`_heavy_brute_stuck_t`** has reached **`HEAVY_BRUTE_STUCK_TIME_SEC`**, the enemy takes **one frame** of motion along a **perpendicular** to the chase direction: `(-ny, nx)` or `(ny, -nx)` alternating via **`_heavy_brute_unstuck_flip`**, scaled by **`HEAVY_BRUTE_UNSTUCK_SPEED_MULT`**. The stuck timer is reset and the flip toggles. This is **deterministic** sidestepping instead of the random stuck steering used for other types.

After movement, if unstuck did not fire and the Heavy is still chasing, displacement from `start_pos` is measured: if below **`HEAVY_BRUTE_STUCK_DIST_PX`**, **`_heavy_brute_stuck_t`** accumulates **`dt`**; otherwise it resets.

---

## 5. Wall slide and generic anti-stuck

- **`_wall_collision_this_frame`** (set outside this method, e.g. by collision resolution) with non-zero velocity: rotate `(vx, vy)` by **45°** and renormalize to preserve speed (slide along wall), then clear the flag.
- Else if **`_stuck_frames >= STUCK_FRAME_COUNT`** and the enemy is **not** using the Heavy path above: **`apply_anti_stuck_velocity`** may apply a **random ±`STUCK_STEERING_ANGLE_DEG`** turn while keeping speed (see module-level helpers).

**Heavy** does not use the `_stuck_frames` escalation in the same way: `update_stuck_tracking` resets `_stuck_frames` for `enemy_type == "heavy"` when movement is low, so random stuck steering is effectively disabled for Heavies in favor of the sidestep timer.

---

## 6. Motion, bounds, and player overlap

- Stores **`velocity_xy`**, then **`world_pos += (vx, vy) * dt`**.
- Clamps position to **`ENEMY_MIN_X/Y`** … **`ENEMY_MAX_X/Y`**, or to **`room_rect`** when provided.
- If the player is **not** in a dash (`not getattr(player, "dash_active", False)`), overlapping movement hitboxes **push** the enemy so its center lies at **`stop_dist`** along the direction **from player to enemy** (avoids jumping through the player). **`engage_dist`** only selects walk vs attack; overlap resolution uses **`stop_dist`**.

---

## 7. Stuck tracking, contact damage, and animation

- **`update_stuck_tracking(self, start_pos)`** — If movement this frame was below **`STUCK_MOVEMENT_THRESHOLD_PX`** but velocity was non-zero, increments **`_stuck_frames`** (except Heavy, which forces `_stuck_frames = 0` in that case). Otherwise resets. Updates **`_last_world_pos`**.
- **Contact / touch damage** — Not applied in `update`. Comments and `_update_contact_damage` reflect Phase 4: damage comes from **explicit** melee/projectile hitboxes only.
- **`_anim_state.advance(dt)`** — Advances the current animation for the active `state`.

---

## Summary

`EnemyBase.update` implements a **small state-driven pursuer**: walk toward the player until within an **effective engage distance**, then **attack** with zero velocity; **death** ends AI after the death animation; **Heavy** adds **timed low-progress sidesteps**; **walls** trigger a fixed **45° slide**; other types can get **random steering** after sustained low movement; **room bounds** and **non-dash player overlap** keep placement valid. Callback parameters for Heavy clearance/retreat are reserved at the call site but unused in the base implementation.
