from dataclasses import dataclass
from typing import List, Tuple

import math
import os
import pygame

from game.asset_loader import load_image, load_animation
from game.config import (
    PROJECT_ROOT,
    TILE_SIZE,
    SPAWN_TELEGRAPH_DURATION_SEC,
    SPAWN_TELEGRAPH_PULSES,
)
from systems.animation import AnimationState


@dataclass
class VfxInstance:
    world_pos: Tuple[float, float]
    frames: list[pygame.Surface]
    anim: AnimationState
    lifetime: float
    elapsed: float = 0.0

    def update(self, dt: float) -> bool:
        self.elapsed += dt
        self.anim.advance(dt)
        return self.elapsed < self.lifetime

    def draw(self, screen: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        surf = self.anim.current_surface()
        if surf is None:
            return
        cx, cy = camera_offset
        x = int(self.world_pos[0] - cx - surf.get_width() / 2)
        y = int(self.world_pos[1] - cy - surf.get_height() / 2)
        screen.blit(surf, (x, y))


@dataclass
class DamageNumber:
    """Floating damage text spawned from DamageEvent."""

    world_pos: Tuple[float, float]
    text: str
    color: Tuple[int, int, int]
    lifetime: float = 0.6
    elapsed: float = 0.0
    float_speed: float = -40.0  # px/sec upward in world space

    def update(self, dt: float) -> bool:
        self.elapsed += dt
        # Move upwards over time
        x, y = self.world_pos
        y += self.float_speed * dt
        self.world_pos = (x, y)
        return self.elapsed < self.lifetime

    def draw(self, screen: pygame.Surface, camera_offset: Tuple[float, float], font: pygame.font.Font) -> None:
        # Fade out over lifetime
        if self.elapsed >= self.lifetime:
            return
        t = max(0.0, min(1.0, self.elapsed / self.lifetime))
        alpha = int(255 * (1.0 - t))
        if alpha <= 0:
            return
        surf = font.render(self.text, True, self.color)
        surf = surf.convert_alpha()
        surf.set_alpha(alpha)
        cx, cy = camera_offset
        x = int(self.world_pos[0] - cx - surf.get_width() / 2)
        y = int(self.world_pos[1] - cy - surf.get_height() / 2)
        screen.blit(surf, (x, y))


@dataclass
class TelegraphInstance:
    """Telegraph tile that pulses before an enemy spawns."""

    world_pos: Tuple[float, float]
    surface: pygame.Surface
    duration: float
    pulses: int
    elapsed: float = 0.0

    def update(self, dt: float) -> bool:
        self.elapsed += dt
        return self.elapsed < self.duration

    def draw(self, screen: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        if self.elapsed >= self.duration:
            return
        t = max(0.0, min(1.0, self.elapsed / self.duration))
        # Map t → pulses using a sine wave for soft pulsing.
        phase = t * self.pulses * 2.0 * math.pi
        base_alpha = 90
        pulse_alpha = 110
        alpha = int(base_alpha + pulse_alpha * (0.5 * (1.0 + math.sin(phase))))
        surf = self.surface.copy()
        surf.set_alpha(alpha)
        cx, cy = camera_offset
        x = int(self.world_pos[0] - cx - surf.get_width() / 2)
        y = int(self.world_pos[1] - cy - surf.get_height() / 2)
        screen.blit(surf, (x, y))


class VfxManager:
    """Manages slash VFX, hit sparks, spawn telegraphs/portals, and floating damage numbers."""

    def __init__(self) -> None:
        self._instances: List[VfxInstance] = []
        self._damage_numbers: List[DamageNumber] = []
        self._telegraphs: List[TelegraphInstance] = []
        # Preload frames; keep VFX smaller than entities and strip background.
        slash_size = (32, 32)
        hit_size = (24, 24)
        self._slash_short_frames = [
            load_image(
                "assets/effects/slash/slash_short_01.png",
                size=slash_size,
                use_colorkey=True,
                colorkey_color=(255, 255, 255),
                near_white_threshold=0,
                corner_bg_tolerance=50,
                exact_size=True,
            ),
            load_image(
                "assets/effects/slash/slash_short_02.png",
                size=slash_size,
                use_colorkey=True,
                colorkey_color=(255, 255, 255),
                near_white_threshold=0,
                corner_bg_tolerance=50,
                exact_size=True,
            ),
        ]
        self._slash_long_frames = [
            load_image(
                "assets/effects/slash/slash_long_01.png",
                size=slash_size,
                use_colorkey=True,
                colorkey_color=(255, 255, 255),
                near_white_threshold=0,
                corner_bg_tolerance=50,
                exact_size=True,
            ),
            load_image(
                "assets/effects/slash/slash_long_02.png",
                size=slash_size,
                use_colorkey=True,
                colorkey_color=(255, 255, 255),
                near_white_threshold=0,
                corner_bg_tolerance=50,
                exact_size=True,
            ),
        ]
        self._hit_frames = [
            load_image(
                "assets/effects/hit/hit_spark_01.png",
                size=hit_size,
                use_colorkey=True,
                colorkey_color=(255, 255, 255),
                near_white_threshold=0,
                corner_bg_tolerance=50,
                exact_size=True,
            ),
            load_image(
                "assets/effects/hit/hit_spark_02.png",
                size=hit_size,
                use_colorkey=True,
                colorkey_color=(255, 255, 255),
                near_white_threshold=0,
                corner_bg_tolerance=50,
                exact_size=True,
            ),
        ]

        # Telegraph tiles (regular + elite gold) for Phase 5.
        telegraph_size = (TILE_SIZE, TILE_SIZE)
        self._telegraph_tile = load_image(
            "assets/effects/telegraphs/telegraph_tile_32x32.png",
            size=telegraph_size,
            use_colorkey=True,
            colorkey_color=(255, 255, 255),
            near_white_threshold=0,
            corner_bg_tolerance=50,
            exact_size=True,
        )
        self._telegraph_tile_elite = load_image(
            "assets/effects/telegraphs/telegraph_elite_gold_32x32.png",
            size=telegraph_size,
            use_colorkey=True,
            colorkey_color=(255, 255, 255),
            near_white_threshold=0,
            corner_bg_tolerance=50,
            exact_size=True,
        )

        # Spawn portal animation (Phase 5).
        portal_size = (TILE_SIZE * 2, TILE_SIZE * 2)
        self._portal_frames = load_animation(
            "assets/effects/spawn_portal",
            size=portal_size,
            use_colorkey=True,
            colorkey_color=(255, 255, 255),
            near_white_threshold=0,
            corner_bg_tolerance=50,
        )
        self._portal_fps = 12
        self._portal_lifetime = (len(self._portal_frames) / float(self._portal_fps)) if self._portal_frames else 0.0

        # Biome 4 Phase 2: spawn portal/telegraph/summon assets (lazy-loaded when first needed).
        self._use_biome4_spawn_visuals = False
        self._telegraph_tile_biome4 = None
        self._telegraph_tile_elite_biome4 = None
        self._portal_frames_biome4 = None
        self._portal_biome4_fps = 12
        self._portal_biome4_lifetime = 0.0
        self._summon_circle_frames_biome4 = None
        self._summon_circle_biome4_fps = 12
        self._summon_circle_biome4_lifetime = 0.0

        # Load damage-number font (font_damage.ttf), with a safe fallback.
        font_path = os.path.join(PROJECT_ROOT, "assets", "ui", "damage_numbers", "font_damage.ttf")
        try:
            self._font = pygame.font.Font(font_path, 22)
        except Exception:
            # Fallback to default font so the game never crashes if the TTF is missing.
            self._font = pygame.font.SysFont(None, 22)

    def spawn_slash(self, world_pos: Tuple[float, float], kind: str) -> None:
        if kind == "long":
            frames = self._slash_long_frames
        else:
            frames = self._slash_short_frames
        anim = AnimationState()
        anim.set_animation(frames, fps=12, loop=False)
        self._instances.append(VfxInstance(world_pos, frames, anim, lifetime=0.3))

    def spawn_hit_spark(self, world_pos: Tuple[float, float]) -> None:
        frames = self._hit_frames
        anim = AnimationState()
        anim.set_animation(frames, fps=16, loop=False)
        self._instances.append(VfxInstance(world_pos, frames, anim, lifetime=0.25))

    def set_biome4_spawn_visuals(self, use: bool) -> None:
        """When True, use Biome 4 spawn portal/telegraph assets (rooms 24-29)."""
        self._use_biome4_spawn_visuals = use
        if use and self._portal_frames_biome4 is None:
            self._ensure_biome4_spawn_assets()

    def _ensure_biome4_spawn_assets(self) -> None:
        """Lazy-load Biome 4 spawn assets from assets/effects/spawn/. Fail gracefully if missing."""
        if self._portal_frames_biome4 is not None:
            return
        spawn_dir = os.path.join(PROJECT_ROOT, "assets", "effects", "spawn")
        telegraph_size = (TILE_SIZE, TILE_SIZE)
        portal_size = (TILE_SIZE * 2, TILE_SIZE * 2)
        try:
            t_path = os.path.join(spawn_dir, "telegraph_tile_32x32.png")
            if os.path.isfile(t_path):
                self._telegraph_tile_biome4 = load_image(
                    "assets/effects/spawn/telegraph_tile_32x32.png",
                    size=telegraph_size,
                    use_colorkey=True,
                    colorkey_color=(255, 255, 255),
                    near_white_threshold=0,
                    corner_bg_tolerance=50,
                    exact_size=True,
                )
        except Exception:
            pass
        try:
            te_path = os.path.join(spawn_dir, "telegraph_elite_red_32x32.png")
            if os.path.isfile(te_path):
                self._telegraph_tile_elite_biome4 = load_image(
                    "assets/effects/spawn/telegraph_elite_red_32x32.png",
                    size=telegraph_size,
                    use_colorkey=True,
                    colorkey_color=(255, 255, 255),
                    near_white_threshold=0,
                    corner_bg_tolerance=50,
                    exact_size=True,
                )
        except Exception:
            pass
        frames = []
        for name in ("spawn_portal_64x64.png", "spawn_portal_anim_64x64.png"):
            p = os.path.join(spawn_dir, name)
            if os.path.isfile(p):
                try:
                    surf = load_image(
                        f"assets/effects/spawn/{name}",
                        size=portal_size,
                        use_colorkey=True,
                        colorkey_color=(255, 255, 255),
                        near_white_threshold=0,
                        corner_bg_tolerance=50,
                        exact_size=True,
                    )
                    if surf:
                        frames.append(surf)
                except Exception:
                    pass
        if frames:
            self._portal_frames_biome4 = frames
            self._portal_biome4_fps = 12
            self._portal_biome4_lifetime = len(frames) / float(self._portal_biome4_fps)
        # Summon circle (128x128) for Biome 4 elite / boss add summoning.
        summon_size = (128, 128)
        summon_frames = []
        for name in ("summon_circle_128x128.png", "summon_circle_anim_128x128.png"):
            p = os.path.join(spawn_dir, name)
            if os.path.isfile(p):
                try:
                    surf = load_image(
                        f"assets/effects/spawn/{name}",
                        size=summon_size,
                        use_colorkey=True,
                        colorkey_color=(255, 255, 255),
                        near_white_threshold=0,
                        corner_bg_tolerance=50,
                        exact_size=True,
                    )
                    if surf:
                        summon_frames.append(surf)
                except Exception:
                    pass
        if summon_frames:
            self._summon_circle_frames_biome4 = summon_frames
            self._summon_circle_biome4_fps = 12
            self._summon_circle_biome4_lifetime = len(summon_frames) / float(self._summon_circle_biome4_fps)

    def spawn_telegraph(
        self,
        world_pos: Tuple[float, float],
        is_elite: bool = False,
        duration_sec: float | None = None,
    ) -> None:
        """Spawn a tile telegraph for Phase 5 enemy spawns. Visual only: no collision."""
        surf = None
        if self._use_biome4_spawn_visuals:
            self._ensure_biome4_spawn_assets()
            surf = self._telegraph_tile_elite_biome4 if is_elite and self._telegraph_tile_elite_biome4 else self._telegraph_tile_biome4
        if surf is None:
            surf = self._telegraph_tile_elite if is_elite and self._telegraph_tile_elite is not None else self._telegraph_tile
        if surf is None:
            return
        duration = duration_sec if duration_sec is not None else SPAWN_TELEGRAPH_DURATION_SEC
        self._telegraphs.append(
            TelegraphInstance(
                world_pos=world_pos,
                surface=surf,
                duration=duration,
                pulses=SPAWN_TELEGRAPH_PULSES,
            )
        )

    def spawn_portal(self, world_pos: Tuple[float, float], is_elite: bool = False) -> None:
        """Spawn a portal animation at the spawn location (visual only). In Biome 4, elite spawns may use summon circle."""
        frames = self._portal_frames
        fps = self._portal_fps
        lifetime = self._portal_lifetime
        if self._use_biome4_spawn_visuals:
            self._ensure_biome4_spawn_assets()
            if is_elite and self._summon_circle_frames_biome4 and self._summon_circle_biome4_lifetime > 0.0:
                frames = self._summon_circle_frames_biome4
                fps = self._summon_circle_biome4_fps
                lifetime = self._summon_circle_biome4_lifetime
            elif self._portal_frames_biome4 and self._portal_biome4_lifetime > 0.0:
                frames = self._portal_frames_biome4
                fps = self._portal_biome4_fps
                lifetime = self._portal_biome4_lifetime
        if not frames or lifetime <= 0.0:
            return
        anim = AnimationState()
        anim.set_animation(frames, fps=fps, loop=False)
        self._instances.append(VfxInstance(world_pos, frames, anim, lifetime=lifetime))

    def spawn_damage_number(self, amount: float, world_pos: Tuple[float, float], is_player: bool) -> None:
        """Spawn a floating damage number.

        - Red for damage dealt to enemies.
        - Yellow for damage dealt to the player.
        """
        # Clamp to an integer value for readability.
        value = int(round(max(0.0, amount)))
        if value <= 0:
            return
        color = (255, 60, 60) if not is_player else (255, 230, 80)
        self._damage_numbers.append(DamageNumber(world_pos=world_pos, text=str(value), color=color))

    def spawn_floating_text(self, world_pos: Tuple[float, float], text: str, color: Tuple[int, int, int] = (80, 255, 120)) -> None:
        """Spawn floating text (e.g. '+30% Health') at world position; floats up and fades."""
        self._damage_numbers.append(DamageNumber(world_pos=world_pos, text=text, color=color))

    def update(self, dt: float) -> None:
        self._instances = [v for v in self._instances if v.update(dt)]
        self._damage_numbers = [n for n in self._damage_numbers if n.update(dt)]
        self._telegraphs = [t for t in self._telegraphs if t.update(dt)]

    def draw(self, screen: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        # Telegraphs and portals/hit VFX are drawn in the VFX layer (after entities, before UI).
        for t in self._telegraphs:
            t.draw(screen, camera_offset)
        for v in self._instances:
            v.draw(screen, camera_offset)
        # Draw damage numbers after VFX so text is on top.
        for n in self._damage_numbers:
            n.draw(screen, camera_offset, self._font)

