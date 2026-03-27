# Lightweight AI debug overlay (Phase 1–3). Read-only; top-left; toggle F3 from GameScene.

from __future__ import annotations

import pygame


class DebugOverlay:
    def __init__(self, game_scene) -> None:
        self.game_scene = game_scene
        self.enabled = False
        self._font = pygame.font.SysFont("consolas", 16)

    def toggle(self) -> None:
        self.enabled = not self.enabled

    def draw(self, screen: pygame.Surface) -> None:
        if not self.enabled:
            return

        director = getattr(self.game_scene, "ai_director", None)
        player_model = getattr(self.game_scene, "player_model", None)
        room_controller = getattr(self.game_scene, "_room_controller", None)

        # Safe seed (Phase 3: no bare game_scene.seed)
        seed = getattr(self.game_scene, "seed", None)
        if seed is None:
            metrics = getattr(self.game_scene, "metrics_tracker", None)
            if metrics is None:
                metrics = getattr(self.game_scene, "_metrics", None)
            if metrics:
                seed = getattr(metrics, "run_seed", "N/A")
                if seed == "N/A":
                    run = getattr(metrics, "run", None)
                    if run is not None:
                        seed = getattr(run, "run_seed", "N/A")
            else:
                seed = "N/A"

        if room_controller is not None:
            room_idx = str(getattr(room_controller, "current_room_index", "N/A"))
        else:
            room_idx = "N/A"

        if player_model is not None and callable(getattr(player_model, "get_state", None)):
            ps_raw = player_model.get_state()
            ps_s = str(ps_raw) if ps_raw is not None else "N/A"
        else:
            ps_s = "N/A"

        diff: object = "N/A"
        enemy_adj: object = "N/A"
        reinf: object = "N/A"
        pressure: object = "N/A"
        trial_on = False
        if director is not None and callable(getattr(director, "get_debug_state", None)):
            dbg = director.get_debug_state()
            diff = dbg.get("difficulty", "N/A")
            ea = dbg.get("enemy_adjustment_effective", dbg.get("enemy_adjustment", "N/A"))
            if isinstance(ea, int):
                enemy_adj = f"{ea:+d}"
            else:
                enemy_adj = ea
            reinf = dbg.get("reinforcement_chance", "N/A")
            pressure = dbg.get("pressure_level", "N/A")
            trial_on = bool(dbg.get("trial_phase", False))

        lines = [
            "AI DEBUG",
            f"Seed: {seed}",
            f"Room: {room_idx}",
            f"Player State: {ps_s}",
            f"Director Difficulty: {diff}",
            f"Enemy Adjustment: {enemy_adj}",
            f"Reinforcement Chance: {reinf}",
            f"Pressure: {pressure}",
        ]
        if trial_on:
            lines.append("Trial Phase")
        if director is not None and room_controller is not None:
            try:
                ri = int(getattr(room_controller, "current_room_index", -1))
            except (TypeError, ValueError):
                ri = -1
            if 16 <= ri <= 23:
                lines.append(
                    f"B3: comp={getattr(director, 'composition_bias_b3', '?')} "
                    f"rng={getattr(director, 'ranged_bias_b3', '?')} "
                    f"hz={getattr(director, 'hazard_tune_factor_b3', '?')}"
                )
            elif 24 <= ri:
                lines.append(
                    f"B4: boss={getattr(director, 'boss_pressure', '?')} "
                    f"pace={getattr(director, 'pacing_bias', '?')} "
                    f"hz={getattr(director, 'hazard_tune_factor_b4', '?')}"
                )

        text_color = (0, 255, 0)
        line_h = 18
        pad = 8
        surfaces = [self._font.render(line, True, text_color) for line in lines]
        max_w = max(s.get_width() for s in surfaces)
        total_h = len(surfaces) * line_h
        bg = pygame.Surface((max_w + pad * 2, total_h + pad * 2), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 120))
        screen.blit(bg, (0, 0))
        y = pad
        for surf in surfaces:
            screen.blit(surf, (pad, y))
            y += line_h
