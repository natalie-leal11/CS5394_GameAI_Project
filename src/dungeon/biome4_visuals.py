# Biome 4 Phase 2: Visual / hazard / VFX integration.
# Loads and provides props, hazard overlays, backgrounds. No gameplay logic.
# All paths under assets/ (project root). Fail gracefully if assets missing.

from __future__ import annotations

import os
import random
from typing import TYPE_CHECKING

from game.asset_loader import load_image, load_animation
from game.config import PROJECT_ROOT, TILE_SIZE, BIOME4_START_INDEX

if TYPE_CHECKING:
    from dungeon.room import Room

# --- Paths (assets/ relative to project root) ---------------------------------

PROPS_DIR = "assets/tiles/biome4/props"
HAZARDS_DIR = "assets/tiles/biome4/hazards"
BG_BIOME4_ROOM = "assets/backgrounds/biome4_room_bg.png"
BG_FINAL_BOSS_ARENA = "assets/backgrounds/final_boss_arena_bg.png"
SPAWN_DIR = "assets/effects/spawn"
ELITES_DIR = "assets/effects/elites"
TELEGRAPHS_DIR = "assets/effects/telegraphs"
BOSS_FX_DIR = "assets/effects/boss"
PARTICLES_DIR = "assets/effects/particles"

# Prop filenames (as present in repo). Indices 0,1,2,4 = solid (block movement); 3 = lava_crack overlay only.
PROP_PATHS = [
    "biome4_obsidian_pillar_32x32.png",
    "biome4_broken_statue_32x32.png",
    "biome4_spike_block_32x32.png",
    "biome4_lava_crack_overlay_32x32.png",
    "biome4_large_rock_cluster_64x64.png",
]
PROP_SIZES = [(32, 32), (32, 32), (32, 32), (32, 32), (64, 64)]
SOLID_PROP_INDICES = (0, 1, 2, 4)  # pillar, statue, spike, rock_cluster; 3 = lava_crack non-blocking

# Hazard overlay naming: lava_bubble_1..4, lava_flow_1..6, magma_pool_1..4
LAVA_BUBBLE_COUNT = 4
LAVA_FLOW_COUNT = 6
MAGMA_POOL_COUNT = 4


class Biome4Visuals:
    """Cache for Biome 4 assets. Lazy load; missing assets are None or empty lists."""

    _instance: Biome4Visuals | None = None

    def __init__(self) -> None:
        self._bg_room: any = None
        self._bg_boss: any = None
        self._props: list[any] = []  # list of (surf, w, h) or (surf,) per prop type
        self._lava_bubble: list = []
        self._lava_flow: list = []
        self._magma_pool: list = []
        self._particle_ash: any = None
        self._particle_ember: any = None
        self._particle_ember_glow: any = None
        self._loaded = False

    @classmethod
    def get(cls) -> Biome4Visuals:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        sz = (TILE_SIZE, TILE_SIZE)
        full_w, full_h = 960, 640  # LOGICAL_W, LOGICAL_H

        # Backgrounds (optional)
        try:
            self._bg_room = load_image(BG_BIOME4_ROOM, size=(full_w, full_h))
        except Exception:
            self._bg_room = None
        try:
            self._bg_boss = load_image(BG_FINAL_BOSS_ARENA, size=(full_w, full_h))
        except Exception:
            self._bg_boss = None

        # Props
        for i, name in enumerate(PROP_PATHS):
            path = os.path.join(PROPS_DIR, name)
            size = PROP_SIZES[i] if i < len(PROP_SIZES) else (32, 32)
            try:
                if os.path.isfile(os.path.join(PROJECT_ROOT, path)):
                    surf = load_image(
                        path,
                        size=size,
                        use_colorkey=True,
                        colorkey_color=(255, 255, 255),
                        corner_bg_tolerance=40,
                    )
                    self._props.append(surf)
                else:
                    self._props.append(None)
            except Exception:
                self._props.append(None)
        while len(self._props) < len(PROP_PATHS):
            self._props.append(None)

        # Hazard overlays (optional; folder may not exist)
        base = os.path.join(PROJECT_ROOT, HAZARDS_DIR)
        if os.path.isdir(base):
            for i in range(1, LAVA_BUBBLE_COUNT + 1):
                p = os.path.join(base, f"lava_bubble_{i}.png")
                if os.path.isfile(p):
                    try:
                        self._lava_bubble.append(load_image(p, size=sz))
                    except Exception:
                        pass
            for i in range(1, LAVA_FLOW_COUNT + 1):
                p = os.path.join(base, f"lava_flow_{i}.png")
                if os.path.isfile(p):
                    try:
                        self._lava_flow.append(load_image(
                            p, size=sz,
                            use_colorkey=True,
                            colorkey_color=(255, 255, 255),
                            corner_bg_tolerance=40,
                        ))
                    except Exception:
                        pass
            for i in range(1, MAGMA_POOL_COUNT + 1):
                p = os.path.join(base, f"magma_pool_{i}.png")
                if os.path.isfile(p):
                    try:
                        self._magma_pool.append(load_image(
                            p, size=sz,
                            use_colorkey=True,
                            colorkey_color=(255, 255, 255),
                            corner_bg_tolerance=40,
                        ))
                    except Exception:
                        pass

        # Optional particles (fail gracefully)
        try:
            p = os.path.join(PARTICLES_DIR, "ash_particle_8x8.png")
            if os.path.isfile(os.path.join(PROJECT_ROOT, p)):
                self._particle_ash = load_image(
                    p, size=(8, 8),
                    use_colorkey=True,
                    colorkey_color=(255, 255, 255),
                    corner_bg_tolerance=40,
                )
        except Exception:
            pass
        try:
            p = os.path.join(PARTICLES_DIR, "ember_particle_8x8.png")
            if os.path.isfile(os.path.join(PROJECT_ROOT, p)):
                self._particle_ember = load_image(
                    p, size=(8, 8),
                    use_colorkey=True,
                    colorkey_color=(255, 255, 255),
                    corner_bg_tolerance=40,
                )
        except Exception:
            pass
        try:
            p = os.path.join(PARTICLES_DIR, "ember_glow_16x16.png")
            if os.path.isfile(os.path.join(PROJECT_ROOT, p)):
                self._particle_ember_glow = load_image(
                    p, size=(16, 16),
                    use_colorkey=True,
                    colorkey_color=(255, 255, 255),
                    corner_bg_tolerance=40,
                )
        except Exception:
            pass

    def get_background_for_room(self, room_index: int) -> any:
        """Return backdrop surface for Biome 4 room, or None. Room 29 = boss arena."""
        self.ensure_loaded()
        if room_index == BIOME4_START_INDEX + 5:  # 29 = final boss
            return self._bg_boss
        return self._bg_room

    def get_lava_overlay_frame(self, tx: int, ty: int, frame_index: int) -> any:
        """Return one overlay surface for a lava tile: pick variant by (tx, ty), frame by frame_index. For Biome 4 only."""
        self.ensure_loaded()
        variant = (tx + ty) % 3  # 0=bubble, 1=flow, 2=magma
        if variant == 0 and self._lava_bubble:
            idx = frame_index % len(self._lava_bubble)
            return self._lava_bubble[idx]
        if variant == 1 and self._lava_flow:
            idx = frame_index % len(self._lava_flow)
            return self._lava_flow[idx]
        if variant == 2 and self._magma_pool:
            idx = frame_index % len(self._magma_pool)
            return self._magma_pool[idx]
        return None

    def get_slow_overlay_frame(self, tx: int, ty: int, frame_index: int) -> any:
        """Optional slow-tile overlay; can reuse magma or None."""
        return self.get_lava_overlay_frame(tx, ty, frame_index)

    def get_prop_placements(
        self,
        room: Room,
        room_index: int,
        door_tiles: set[tuple[int, int]],
        seed: int,
    ) -> list[tuple[any, float, float, int]]:
        """Return list of (surface, world_x, world_y, prop_type) for props. Avoids spawn and door tiles. prop_type 0–4; 3 = lava_crack (non-blocking)."""
        self.ensure_loaded()
        out: list[tuple[any, float, float, int]] = []
        border = room.wall_border()
        r0, r1 = border, room.height - border
        c0, c1 = border, room.width - border
        spawn_tx, spawn_ty = room.spawn_tile
        blocked = door_tiles | {(spawn_tx, spawn_ty)}
        for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            blocked.add((spawn_tx + dx, spawn_ty + dy))
        for (tx, ty) in list(door_tiles):
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    blocked.add((tx + dx, ty + dy))

        candidates = []
        for ty in range(r0, r1):
            for tx in range(c0, c1):
                if (tx, ty) in blocked:
                    continue
                if room.is_tile_in_wall_band(tx, ty):
                    continue
                candidates.append((tx, ty))

        rng = random.Random(seed + room_index * 10000)
        rng.shuffle(candidates)
        n_props = rng.randint(3, min(8, len(candidates)))
        prop_indices = rng.sample(range(len(candidates)), min(n_props, len(candidates)))
        for idx in prop_indices:
            tx, ty = candidates[idx]
            prop_type = rng.randint(0, len(self._props) - 1) if self._props else 0
            surf = self._props[prop_type] if prop_type < len(self._props) and self._props[prop_type] else None
            if surf is None:
                continue
            wx, wy = room.world_pos_for_tile(tx, ty)
            sw, sh = surf.get_size()
            out.append((surf, wx - sw / 2, wy - sh / 2, prop_type))
        return out


def get_biome4_background(room_index: int) -> any:
    """Convenience: return Biome 4 backdrop surface for room index, or None."""
    return Biome4Visuals.get().get_background_for_room(room_index)


def get_biome4_prop_placements(
    room: Room,
    room_index: int,
    door_tiles: set[tuple[int, int]],
    seed: int,
) -> list[tuple[any, float, float, int]]:
    """Convenience: return list of (surf, world_x, world_y, prop_type) for Biome 4 props. prop_type 3 = lava_crack (non-blocking)."""
    return Biome4Visuals.get().get_prop_placements(room, room_index, door_tiles, seed)


# --- Room 29 / Phase 3: loadable boss FX and projectiles (no behavior in Phase 2) ---

def load_boss_fx_teleport() -> list:
    """Load boss teleport VFX frames from assets/effects/boss/. Returns list of surfaces or [] if missing."""
    try:
        from game.asset_loader import load_animation
        frames = load_animation(
            BOSS_FX_DIR + "/teleport", size=(64, 64),
            use_colorkey=True,
            colorkey_color=(255, 255, 255),
            corner_bg_tolerance=40,
        )
        return frames if frames else []
    except Exception:
        return []


def load_boss_fx_spawn() -> list:
    """Load boss spawn VFX from assets/effects/boss/. Returns list of surfaces or []."""
    try:
        from game.asset_loader import load_animation
        frames = load_animation(
            BOSS_FX_DIR + "/spawn", size=(128, 128),
            use_colorkey=True,
            colorkey_color=(255, 255, 255),
            corner_bg_tolerance=40,
        )
        return frames if frames else []
    except Exception:
        return []


def load_boss_fx_death() -> list:
    """Load boss death VFX from assets/effects/boss/. Returns list of surfaces or []."""
    try:
        from game.asset_loader import load_animation
        frames = load_animation(
            BOSS_FX_DIR + "/death", size=(128, 128),
            use_colorkey=True,
            colorkey_color=(255, 255, 255),
            corner_bg_tolerance=40,
        )
        return frames if frames else []
    except Exception:
        return []


def load_boss_projectile(name: str, size: tuple[int, int] = (24, 24)) -> any:
    """Load a boss projectile image from assets/entities/projectiles/ (e.g. boss_fireball_24x24.png). Returns surface or None."""
    try:
        path = f"assets/entities/projectiles/{name}"
        if os.path.isfile(os.path.join(PROJECT_ROOT, path)):
            return load_image(
                path, size=size,
                use_colorkey=True,
                colorkey_color=(255, 255, 255),
                corner_bg_tolerance=40,
            )
    except Exception:
        pass
    return None


def load_boss_telegraph(name: str, size: tuple[int, int] | None = None) -> any:
    """Load a boss telegraph image from assets/effects/telegraphs/ for Phase 3. Returns surface or None.
    e.g. boss_attack_circle_128x128.png, boss_wave_line_256x64.png, boss_meteor_target_96x96.png"""
    try:
        path = f"assets/effects/telegraphs/{name}"
        full = os.path.join(PROJECT_ROOT, path)
        if os.path.isfile(full):
            return load_image(
                path, size=size,
                use_colorkey=True,
                colorkey_color=(255, 255, 255),
                corner_bg_tolerance=40,
            )
    except Exception:
        pass
    return None


def load_boss_fx_image(name: str, size: tuple[int, int]) -> any:
    """Load a single boss FX image from assets/effects/boss/ (e.g. boss_teleport_flash_64x64.png). Returns surface or None."""
    try:
        path = f"{BOSS_FX_DIR}/{name}"
        full = os.path.join(PROJECT_ROOT, path)
        if os.path.isfile(full):
            return load_image(
                path, size=size,
                use_colorkey=True,
                colorkey_color=(255, 255, 255),
                corner_bg_tolerance=40,
            )
    except Exception:
        pass
    return None
