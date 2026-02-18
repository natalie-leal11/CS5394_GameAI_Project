"""
Run scene: player movement, dash, attacks. Q → Defeat, E → Victory.
"""
from __future__ import annotations
import math
import pygame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.game.entities.boss import Boss

from src.game import config
from src.game.scenes.base_scene import BaseScene
from src.game.entities.player import Player, DASH_TRAIL_FADE_SEC
from src.game.entities.projectiles import Projectile
from src.game.dungeon.dungeon_generator import generate_dungeon_plan
from src.game.dungeon.room_controller import RoomController
from src.game.systems.movement import update_player_movement
from src.game.systems.combat import (
    update_attack_cooldowns,
    try_short_attack,
    try_long_attack,
    update_projectiles,
    apply_damage,
    resolve_damage_to_player,
    point_in_rect,
)
from src.game.systems.spawner import spawn_encounter
from src.game.entities.enemy_base import Enemy
from src.game.entities.enemies import update_enemy_chase, tick_attack_cooldowns
from src.game.ai.metrics_tracker import MetricsTracker
from src.game.ai.ai_director import get_directives
from src.game.ai.difficulty_params import get_default_difficulty_params
from src.game.entities.pickups import heal_in_safe_room, generate_three_upgrades, apply_upgrade
from src.game.systems.hud import draw_rest_room_hud
from src.game.dungeon.room_types import SAFE_REST, MINI_BOSS, FINAL_BOSS
from src.game.entities.boss import Boss, create_mini_boss, create_final_boss
from src.game import rng


class RunScene(BaseScene):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self.player = Player(
            x=config.WIDTH / 2.0,
            y=config.HEIGHT / 2.0,
            radius=16.0,
        )
        self._bounds = (0.0, 0.0, float(config.WIDTH), float(config.HEIGHT))
        self._projectiles: list[Projectile] = []
        self._short_attack_rect: tuple[float, float, float, float] | None = None  # for visual
        self._short_attack_damage: int = 0  # damage rolled when attack started
        plan = generate_dungeon_plan(42)
        self.room_controller = RoomController(plan)
        self._room_enemies: list[Enemy] = []
        self._dungeon_seed = 42
        self._metrics = MetricsTracker(seed=self._dungeon_seed)
        self._difficulty_params = get_default_difficulty_params()
        self._room_enter_time = 0.0
        self._safe_room_options: list | None = None
        self._safe_room_heal_amount: int = 0
        self._room_boss: Boss | None = None
        self._run_start_time: float = 0.0

    def on_enter(self) -> None:
        """Reset run when entering from menu (full run reset on loss)."""
        self.player = Player(x=config.WIDTH / 2.0, y=config.HEIGHT / 2.0, radius=16.0)
        self._projectiles.clear()
        self._short_attack_rect = None
        self._short_attack_damage = 0
        plan = generate_dungeon_plan(self._dungeon_seed)
        self.room_controller = RoomController(plan)
        self._room_enemies.clear()
        self._metrics = MetricsTracker(seed=self._dungeon_seed)
        self._room_enter_time = 0.0
        self._safe_room_options = None
        self._room_boss = None
        self._run_start_time = pygame.time.get_ticks() / 1000.0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_q:
            self.manager.switch_to("end")  # Defeat
        elif event.key == pygame.K_e:
            self.manager.switch_to("end")  # Victory
        elif event.key == pygame.K_j:
            result = try_short_attack(self.player)
            if result is not None:
                damage, rect = result
                self._short_attack_damage = damage
                self._short_attack_rect = rect
        elif event.key == pygame.K_k:
            try_long_attack(self.player, self._projectiles)
        elif event.key == pygame.K_l:
            current_time = pygame.time.get_ticks() / 1000.0
            self.player.parry_press_time = current_time
        elif event.key == pygame.K_n and self.room_controller.can_advance():
            self.room_controller.advance()
            self._room_enemies.clear()
            self._safe_room_options = None
            self._room_boss = None
        elif self._safe_room_options and len(self._safe_room_options) >= 1:
            if event.key == pygame.K_1:
                apply_upgrade(self.player, self._safe_room_options[0][0], self._safe_room_options[0][2])
                self.room_controller.mark_current_room_cleared()
                self._safe_room_options = None
            elif event.key == pygame.K_2 and len(self._safe_room_options) >= 2:
                apply_upgrade(self.player, self._safe_room_options[1][0], self._safe_room_options[1][2])
                self.room_controller.mark_current_room_cleared()
                self._safe_room_options = None
            elif event.key == pygame.K_3 and len(self._safe_room_options) >= 3:
                apply_upgrade(self.player, self._safe_room_options[2][0], self._safe_room_options[2][2])
                self.room_controller.mark_current_room_cleared()
                self._safe_room_options = None

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        block_held = keys[pygame.K_l]
        move_x = (1.0 if keys[pygame.K_d] else 0.0) - (1.0 if keys[pygame.K_a] else 0.0)
        move_y = (1.0 if keys[pygame.K_s] else 0.0) - (1.0 if keys[pygame.K_w] else 0.0)
        if move_x != 0 or move_y != 0:
            s = math.sqrt(move_x * move_x + move_y * move_y)
            self.player.facing_x = move_x / s
            self.player.facing_y = move_y / s
        dash_requested = keys[pygame.K_LSHIFT] or keys[pygame.K_SPACE]
        current_time = pygame.time.get_ticks() / 1000.0
        update_player_movement(
            self.player,
            move_x,
            move_y,
            dash_requested,
            self._bounds,
            dt,
            current_time,
        )
        update_attack_cooldowns(self.player, dt)
        if self.player.short_attack_active_remaining <= 0:
            self._short_attack_rect = None
        if self.player.parry_flash_remaining > 0:
            self.player.parry_flash_remaining -= dt
            if self.player.parry_flash_remaining < 0:
                self.player.parry_flash_remaining = 0.0
        update_projectiles(self._projectiles, dt)

        # Safe room: heal and show 3 upgrade options (select 1)
        if self.room_controller.get_current_room_type() == SAFE_REST and not self.room_controller.is_current_room_cleared():
            if self._safe_room_options is None:
                heal_in_safe_room(self.player)
                self._safe_room_heal_amount = int(self.player.max_hp * 0.25)
                hp_pct = self._metrics.hp_percent(self.player.hp, self.player.max_hp)
                directives = get_directives(
                    hp_pct, self._metrics.death_count,
                    self.room_controller.get_current_room_type(),
                    (self.room_controller.get_room_index() // 8) + 1,
                    self._difficulty_params,
                )
                self._safe_room_options = generate_three_upgrades(
                    self._dungeon_seed,
                    self.room_controller.get_room_index(),
                    directives["director_state"],
                )

        # Spawn boss when entering mini_boss or final_boss room
        rt = self.room_controller.get_current_room_type()
        if rt == MINI_BOSS and self._room_boss is None:
            rng.set_seed(self._dungeon_seed + self.room_controller.get_room_index() * 100)
            hp = rng.randint(600, 700)
            self._room_boss = create_mini_boss(config.WIDTH / 2.0, config.HEIGHT / 2.0 - 40, hp=hp)
            self._room_enter_time = current_time
            self._metrics.start_room(self.player.hp, current_time)
        if rt == FINAL_BOSS and self._room_boss is None:
            self._room_boss = create_final_boss(config.WIDTH / 2.0, config.HEIGHT / 2.0 - 40)
            self._room_enter_time = current_time
            self._metrics.start_room(self.player.hp, current_time)

        # Spawn enemies when entering combat room (lock until cleared). Use AI Director directives.
        if self.room_controller.requires_combat_clear() and len(self._room_enemies) == 0 and self._room_boss is None:
            hp_pct = self._metrics.hp_percent(self.player.hp, self.player.max_hp)
            directives = get_directives(
                hp_pct,
                self._metrics.death_count,
                self.room_controller.get_current_room_type(),
                (self.room_controller.get_room_index() // 8) + 1,
                self._difficulty_params,
            )
            self._room_enemies = spawn_encounter(
                self._dungeon_seed,
                self.room_controller.get_room_index(),
                self.room_controller.get_current_room_type(),
                self._bounds,
                enemy_count=directives["enemy_count"],
                archetype_mix=directives["archetype_mix"],
                elite_count=directives["elite_count"],
            )
            self._room_enter_time = current_time
            self._metrics.start_room(self.player.hp, current_time)

        # Boss update: chase and tick
        if self._room_boss is not None:
            update_enemy_chase(self._room_boss, self.player.x, self.player.y, self._bounds, dt)
            self._room_boss.tick(dt)

        # Enemy chase and cooldowns
        for e in self._room_enemies:
            update_enemy_chase(e, self.player.x, self.player.y, self._bounds, dt)
        tick_attack_cooldowns(self._room_enemies, dt)

        # Loss: player HP 0 -> full run reset (go to end)
        if self.player.hp <= 0:
            total_time = current_time - self._run_start_time
            self._metrics.record_run_end(win=False, total_run_time=total_time)
            self.manager.run_result = False
            self.manager.switch_to("end")
            return

        # Projectile vs enemy and vs boss
        for p in self._projectiles:
            if not p.is_alive():
                continue
            for e in self._room_enemies:
                if not e.is_alive():
                    continue
                dist = math.sqrt((p.x - e.x) ** 2 + (p.y - e.y) ** 2)
                if dist < e.radius + p.radius:
                    e.take_damage(p.damage)
                    p.lifetime_remaining = 0
                    break
            if self._room_boss is not None and self._room_boss.is_alive():
                dist = math.sqrt((p.x - self._room_boss.x) ** 2 + (p.y - self._room_boss.y) ** 2)
                if dist < self._room_boss.radius + p.radius:
                    self._room_boss.take_damage(p.damage)
                    p.lifetime_remaining = 0
                    break

        # Short attack hitbox vs enemies (use damage rolled at attack start)
        if self._short_attack_rect is not None and self._short_attack_damage > 0:
            left, top, w, h = self._short_attack_rect
            for e in self._room_enemies:
                if not e.is_alive():
                    continue
                if point_in_rect(e.x, e.y, left, top, w, h):
                    apply_damage(e, self._short_attack_damage, 0.0)
                    break
            if self._room_boss is not None and self._room_boss.is_alive():
                if point_in_rect(self._room_boss.x, self._room_boss.y, left, top, w, h):
                    self._room_boss.take_damage(self._short_attack_damage)
                    self._short_attack_rect = None
                    self._short_attack_damage = 0

        # Boss vs player (melee)
        if self._room_boss is not None and self._room_boss.is_alive():
            dist = math.sqrt((self.player.x - self._room_boss.x) ** 2 + (self.player.y - self._room_boss.y) ** 2)
            if dist < self.player.radius + self._room_boss.radius + 15 and self._room_boss.attack_cooldown_remaining <= 0:
                resolve_damage_to_player(self.player, self._room_boss.damage, current_time, block_held)
                self._room_boss.attack_cooldown_remaining = self._room_boss.attack_cooldown_base

        # Enemy melee vs player
        for e in self._room_enemies:
            if not e.is_alive():
                continue
            dist = math.sqrt((self.player.x - e.x) ** 2 + (self.player.y - e.y) ** 2)
            if dist < self.player.radius + e.radius + 10 and e.attack_cooldown_remaining <= 0:
                resolve_damage_to_player(self.player, e.damage, current_time, block_held)
                e.attack_cooldown_remaining = 1.2 if e.archetype == "swarm" else 1.0

        # Remove dead enemies; check boss dead
        self._room_enemies = [e for e in self._room_enemies if e.is_alive()]
        if self._room_boss is not None and not self._room_boss.is_alive():
            clear_time = current_time - self._room_enter_time
            hp_pct = self._metrics.hp_percent(self.player.hp, self.player.max_hp)
            directives = get_directives(
                hp_pct, self._metrics.death_count,
                self.room_controller.get_current_room_type(),
                (self.room_controller.get_room_index() // 8) + 1,
                self._difficulty_params,
            )
            self._metrics.record_room_complete(
                self.room_controller.get_room_index(),
                self.room_controller.get_current_room_type(),
                (self.room_controller.get_room_index() // 8) + 1,
                "boss",
                1,
                0,
                self.player.hp,
                clear_time,
                directives["director_state"],
            )
            if self._room_boss.is_final_boss:
                total_time = current_time - self._run_start_time
                self._metrics.record_run_end(win=True, total_run_time=total_time)
                self.manager.run_result = True
                self.manager.switch_to("end")
                self._room_boss = None
                return
            self.room_controller.mark_current_room_cleared()
            self._room_boss = None
        if self.room_controller.requires_combat_clear() and len(self._room_enemies) == 0 and self._room_boss is None:
            clear_time = current_time - self._room_enter_time
            hp_pct = self._metrics.hp_percent(self.player.hp, self.player.max_hp)
            directives = get_directives(
                hp_pct,
                self._metrics.death_count,
                self.room_controller.get_current_room_type(),
                (self.room_controller.get_room_index() // 8) + 1,
                self._difficulty_params,
            )
            self._metrics.record_room_complete(
                self.room_controller.get_room_index(),
                self.room_controller.get_current_room_type(),
                (self.room_controller.get_room_index() // 8) + 1,
                directives["chosen_encounter_type"],
                directives["enemy_count"],
                directives["elite_count"],
                self.player.hp,
                clear_time,
                directives["director_state"],
            )
            self.room_controller.mark_current_room_cleared()

        # Prune old trail entries (0.2s fade)
        self.player.trail = [
            (x, y, t) for x, y, t in self.player.trail
            if current_time - t < DASH_TRAIL_FADE_SEC
        ]

    def render(self, screen: pygame.Surface) -> None:
        screen.fill((30, 25, 20))
        current_time = pygame.time.get_ticks() / 1000.0

        # Safe room: draw upgrade choice HUD
        if self._safe_room_options is not None:
            draw_rest_room_hud(screen, self._safe_room_options, self._safe_room_heal_amount)
            # Still draw player and HUD below

        # Dash trail (faint, 0.2s fade)
        for x, y, t in self.player.trail:
            age = current_time - t
            if age >= DASH_TRAIL_FADE_SEC:
                continue
            alpha = int(80 * (1.0 - age / DASH_TRAIL_FADE_SEC))
            s = pygame.Surface((self.player.radius * 2, self.player.radius * 2))
            s.set_alpha(alpha)
            s.fill((60, 140, 160))
            blit_rect = s.get_rect(center=(int(x), int(y)))
            screen.blit(s, blit_rect)

        # Short attack hitbox (long attack visually distinct: projectile)
        if self._short_attack_rect is not None:
            left, top, w, h = self._short_attack_rect
            pygame.draw.rect(screen, (200, 220, 100), (left, top, w, h), 2)

        # Projectiles (long attack)
        for p in self._projectiles:
            if not p.is_alive():
                continue
            pygame.draw.circle(screen, (220, 200, 80), (int(p.x), int(p.y)), int(p.radius))

        # Boss (mini or final)
        if self._room_boss is not None and self._room_boss.is_alive():
            color = (180, 60, 80) if self._room_boss.hit_flash_remaining <= 0 else (255, 180, 180)
            if self._room_boss.phase2_invuln_remaining > 0:
                color = (200, 200, 255)  # invuln tint
            pygame.draw.circle(
                screen,
                color,
                (int(self._room_boss.x), int(self._room_boss.y)),
                int(self._room_boss.radius),
            )
            if self._room_boss.is_final_boss:
                pygame.draw.circle(screen, (255, 200, 80), (int(self._room_boss.x), int(self._room_boss.y)), int(self._room_boss.radius) + 4, 3)

        # Enemies (room-confined; elite = glow)
        for e in self._room_enemies:
            if not e.is_alive():
                continue
            if e.elite:
                pygame.draw.circle(screen, (180, 100, 255), (int(e.x), int(e.y)), int(e.radius) + 4, 2)
            color = (220, 80, 60) if e.hit_flash_remaining <= 0 else (255, 200, 200)
            pygame.draw.circle(screen, color, (int(e.x), int(e.y)), int(e.radius))

        # Player (blue/teal accent)
        color = (40, 180, 200)
        if self.player.parry_flash_remaining > 0:
            color = (255, 255, 255)  # parry brief white flash
        pygame.draw.circle(
            screen,
            color,
            (int(self.player.x), int(self.player.y)),
            int(self.player.radius),
        )

        # HUD: HP, room, hint
        font = pygame.font.Font(None, 28)
        hp_text = font.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, (220, 220, 220))
        screen.blit(hp_text, (10, 10))
        room_type = self.room_controller.get_current_room_type()
        room_text = font.render(
            f"Room {self.room_controller.get_room_index() + 1}/30: {room_type}",
            True, (200, 200, 200),
        )
        screen.blit(room_text, (10, 36))
        if self.room_controller.can_advance():
            next_hint = font.render("N: next room", True, (120, 255, 120))
            screen.blit(next_hint, (10, 62))
        hint = font.render(
            "WASD move | SHIFT dash | J melee K projectile | L block/parry | Q E end",
            True, (160, 160, 160),
        )
        screen.blit(hint, (10, config.HEIGHT - 24))
