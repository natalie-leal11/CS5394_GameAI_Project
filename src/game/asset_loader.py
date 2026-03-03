# Canonical asset loading API. All image/animation loading must use this module.
# Call only after pygame.display.set_mode() has been called (convert_alpha requirement).

import os
import re
import pygame
from pathlib import Path

from game.config import (
    PLACEHOLDER_IMAGE,
    PROJECT_ROOT,
    TILE_SIZE,
    PLAYER_SIZE,
    BRUTE_SIZE,
    MINI_BOSS_SIZE,
    DEBUG_ASSET_LOADER,
)
from game.logger import debug


def _natural_sort_key(s: str):
    """Sort so frame_01, frame_02, ..., frame_10 order numerically."""
    parts = re.split(r"(\d+)", s)
    return [int(x) if x.isdigit() else x for x in parts]


def _load_surface(path: str) -> pygame.Surface | None:
    """Load image from path; return None on failure. Does not scale or convert.
    Relative paths are resolved from PROJECT_ROOT so assets load regardless of cwd.
    """
    try:
        if os.path.isabs(path):
            p = path
        else:
            p = os.path.normpath(os.path.join(PROJECT_ROOT, path))
        if not os.path.isfile(p):
            return None
        return pygame.image.load(p)
    except (pygame.error, OSError):
        return None


def _make_near_white_transparent(surface: pygame.Surface, threshold: int) -> None:
    """Set alpha to 0 for pixels where R,G,B are all >= threshold (removes white/near-white edges)."""
    if threshold < 0 or threshold > 255:
        return
    w, h = surface.get_size()
    for y in range(h):
        for x in range(w):
            r, g, b, a = surface.get_at((x, y))
            if r >= threshold and g >= threshold and b >= threshold:
                surface.set_at((x, y), (r, g, b, 0))


def _pixel_near_color(r: int, g: int, b: int, color: tuple[int, int, int], tolerance: int) -> bool:
    """True if (r,g,b) is within per-channel tolerance of color."""
    r0, g0, b0 = color
    return (
        abs(r - r0) <= tolerance
        and abs(g - g0) <= tolerance
        and abs(b - b0) <= tolerance
    )


def _make_colors_near_transparent(
    surface: pygame.Surface, colors: list[tuple[int, int, int]], tolerance: int
) -> None:
    """Set alpha to 0 for pixels within tolerance of any of the given RGB colors (removes all corner backgrounds)."""
    if tolerance <= 0 or not colors:
        return
    w, h = surface.get_size()
    for y in range(h):
        for x in range(w):
            r, g, b, a = surface.get_at((x, y))[:4]
            for c in colors:
                if _pixel_near_color(r, g, b, c, tolerance):
                    surface.set_at((x, y), (r, g, b, 0))
                    break


def _strip_border_background(surface: pygame.Surface, edge_min_coverage: float = 0.5, tolerance: int = 6) -> None:
    """
    Additional heuristic for sprites with a solid box:
    - Look only at border pixels (top/bottom rows + left/right columns).
    - If one color dominates the border, assume it's a flat background and
      strip it across the image.
    """
    w, h = surface.get_size()
    if w == 0 or h == 0:
        return
    border_coords: list[tuple[int, int]] = []
    for x in range(w):
        border_coords.append((x, 0))
        if h > 1:
            border_coords.append((x, h - 1))
    for y in range(1, max(1, h - 1)):
        border_coords.append((0, y))
        if w > 1:
            border_coords.append((w - 1, y))
    counts: dict[tuple[int, int, int], int] = {}
    for (x, y) in border_coords:
        r, g, b, a = surface.get_at((x, y))[:4]
        if a <= 0:
            continue
        key = (r, g, b)
        counts[key] = counts.get(key, 0) + 1
    if not counts:
        return
    dom_color, dom_count = max(counts.items(), key=lambda kv: kv[1])
    coverage = dom_count / float(len(border_coords))
    if coverage < edge_min_coverage:
        return
    _make_colors_near_transparent(surface, [dom_color], tolerance)


def _strip_flat_background(surface: pygame.Surface, min_coverage: float = 0.4, tolerance: int = 6) -> None:
    """
    Heuristic: if a single near-grey color covers a large portion of the sprite,
    treat it as a flat background and make it transparent.

    This is primarily used for enemy sprites that shipped with a solid grey box.
    """
    w, h = surface.get_size()
    if w == 0 or h == 0:
        return
    total_pixels = w * h
    counts: dict[tuple[int, int, int], int] = {}
    for y in range(h):
        for x in range(w):
            r, g, b, a = surface.get_at((x, y))[:4]
            if a <= 0:
                continue
            key = (r, g, b)
            counts[key] = counts.get(key, 0) + 1
    if not counts:
        return
    # Most frequent opaque color
    (dom_color, dom_count) = max(counts.items(), key=lambda kv: kv[1])
    coverage = dom_count / float(total_pixels)
    if coverage < min_coverage:
        return
    r, g, b = dom_color
    # Only strip if it's approximately grey (R≈G≈B); avoid nuking colorful sprites.
    if abs(r - g) > 10 or abs(r - b) > 10 or abs(g - b) > 10:
        return
    _make_colors_near_transparent(surface, [dom_color], tolerance)


def _convert_and_scale(
    surface: pygame.Surface,
    size: tuple[int, int] | None = None,
    use_colorkey: bool = False,
    colorkey_color: tuple[int, int, int] = (255, 255, 255),
    near_white_threshold: int = 0,
    corner_bg_tolerance: int = 0,
    exact_size: bool = False,
    strip_flat_bg: bool = False,
) -> pygame.Surface:
    """Apply convert_alpha, optional colorkey, scale, then transparency.
    If exact_size=True, final surface is exactly (tw, th); otherwise fit inside preserving aspect ratio.
    """
    out = surface.convert_alpha()
    if use_colorkey:
        out.set_colorkey(colorkey_color, pygame.RLEACCEL)
    if size is not None:
        w, h = out.get_size()
        tw, th = size
        if w != tw or h != th:
            if exact_size:
                out = pygame.transform.smoothscale(out, (tw, th))
            else:
                scale_w = tw / w if w else 1
                scale_h = th / h if h else 1
                scale = min(scale_w, scale_h)
                nw = max(1, int(w * scale))
                nh = max(1, int(h * scale))
                out = pygame.transform.smoothscale(out, (nw, nh))
            if DEBUG_ASSET_LOADER:
                debug(f"Scaled to {out.get_size()} (requested {size}, exact={exact_size})")
    if near_white_threshold > 0:
        _make_near_white_transparent(out, near_white_threshold)
    if corner_bg_tolerance > 0 and out.get_width() and out.get_height():
        w, h = out.get_width(), out.get_height()
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        corner_colors = []
        seen = set()
        for (cx, cy) in corners:
            c = out.get_at((cx, cy))[:3]
            if c not in seen:
                seen.add(c)
                corner_colors.append(c)
        _make_colors_near_transparent(out, corner_colors, corner_bg_tolerance)
    if strip_flat_bg:
        _strip_flat_background(out)
        _strip_border_background(out)
    return out


def _make_placeholder(size: tuple[int, int] | None = None) -> pygame.Surface:
    """Create a fallback surface so the game never crashes on missing assets."""
    size = size or (TILE_SIZE, TILE_SIZE)
    s = pygame.Surface(size)
    s.fill((80, 80, 80))
    s = s.convert_alpha()
    return s


def load_image(
    path: str,
    size: tuple[int, int] | None = None,
    use_colorkey: bool = False,
    colorkey_color: tuple[int, int, int] = (255, 255, 255),
    near_white_threshold: int = 0,
    corner_bg_tolerance: int = 0,
    exact_size: bool = False,
    strip_flat_bg: bool = False,
) -> pygame.Surface:
    """
    Load a single image. Use this for all image loading (no direct pygame.image.load elsewhere).
    Relative paths are resolved from PROJECT_ROOT. exact_size=True scales to exact (w,h) for UI.
    """
    surf = _load_surface(path)
    if surf is None:
        surf = _load_surface(PLACEHOLDER_IMAGE)
    if surf is None:
        surf = _make_placeholder(size)
        if DEBUG_ASSET_LOADER:
            debug(f"Missing and no placeholder: {path}")
    else:
        surf = _convert_and_scale(
            surf, size=size, use_colorkey=use_colorkey, colorkey_color=colorkey_color,
            near_white_threshold=near_white_threshold,
            corner_bg_tolerance=corner_bg_tolerance,
            exact_size=exact_size,
            strip_flat_bg=strip_flat_bg,
        )
        if DEBUG_ASSET_LOADER and size:
            debug(f"Loaded {path} -> {surf.get_size()}")
    return surf


def load_animation(
    folder_path: str,
    size: tuple[int, int] | None = None,
    use_colorkey: bool = False,
    colorkey_color: tuple[int, int, int] = (255, 255, 255),
    near_white_threshold: int = 0,
    corner_bg_tolerance: int = 0,
    strip_flat_bg: bool = False,
) -> list[pygame.Surface]:
    """
    Load animation frames from a folder. Frames are naturally sorted (0..10 not 0,1,10,2).
    folder_path should be the directory containing frame_01.png, frame_02.png, etc.
    """
    if folder_path and not os.path.isabs(folder_path):
        folder_path = os.path.normpath(os.path.join(PROJECT_ROOT, folder_path))
    frames = []
    if not folder_path or not os.path.isdir(folder_path):
        frames.append(_make_placeholder(size))
        return frames

    entries = []
    for name in os.listdir(folder_path):
        if name.endswith((".png", ".jpg", ".jpeg", ".gif")):
            entries.append(name)
    entries.sort(key=_natural_sort_key)

    for name in entries:
        path = os.path.join(folder_path, name)
        surf = _load_surface(path)
        if surf is None:
            surf = _load_surface(PLACEHOLDER_IMAGE)
        if surf is None:
            surf = _make_placeholder(size)
        else:
            surf = _convert_and_scale(
                surf, size=size, use_colorkey=use_colorkey, colorkey_color=colorkey_color,
                near_white_threshold=near_white_threshold,
                corner_bg_tolerance=corner_bg_tolerance,
                strip_flat_bg=strip_flat_bg,
            )
        frames.append(surf)
        if DEBUG_ASSET_LOADER and size:
            debug(f"Frame {path} -> {surf.get_size()}")

    if not frames:
        frames.append(_make_placeholder(size))
    return frames
