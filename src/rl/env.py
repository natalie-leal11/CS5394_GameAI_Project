"""
Gymnasium wrapper around the existing GameScene (fixed-dt stepping, optional headless draw skip).

# RL-only path — safe to remove if RL is abandoned
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

# Project imports: src/ must be on sys.path (same pattern as src/game/main.py)
_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import pygame  # noqa: E402

from game.config import BACKGROUND_COLOR, FPS, LOGICAL_H, LOGICAL_W  # noqa: E402
from game.scene_manager import SceneManager  # noqa: E402
from game.ai.difficulty_params import load_difficulty_params_json  # noqa: E402

from rl.headless import init_pygame_surface, maybe_init_dummy_video_driver  # noqa: E402
from rl.obs import OBS_DIM, build_observation  # noqa: E402
from rl.reward import RewardState, build_reward_snapshot, compute_step_reward  # noqa: E402


class DungeonEnv(gym.Env):
    """
    One env.step = one fixed simulation tick (1/FPS seconds), same as manual play semantics.

    metadata / render_mode:
    - None: headless (no GameScene.draw work when _rl_skip_draw is set; see headless.py)
    - "human": visible window + normal draw path
    """

    metadata = {"render_modes": [None, "human"], "render_fps": FPS}

    def __init__(self, render_mode: str | None = None):
        super().__init__()
        self.render_mode = render_mode
        maybe_init_dummy_video_driver()
        self._screen: pygame.Surface | None = None
        self._logical_surface: pygame.Surface | None = None
        self._clock: pygame.time.Clock | None = None
        self._closed = False

        self._scene_manager: SceneManager | None = None
        self._game_scene = None

        # 0–9: movement, attacks, dash, block/parry; 10–16: interact, safe heal, reserve, safe choices (action_map)
        self.action_space = spaces.Discrete(17)
        self.observation_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(OBS_DIM,),
            dtype=np.float32,
        )

        self._bootstrap_pygame_and_scene()

    def _bootstrap_pygame_and_scene(self) -> None:
        human = self.render_mode == "human"
        self._screen = init_pygame_surface(human_window=human)
        self._clock = pygame.time.Clock()
        self._logical_surface = pygame.Surface((LOGICAL_W, LOGICAL_H))

        difficulty_params = load_difficulty_params_json()
        self._scene_manager = SceneManager(difficulty_params=difficulty_params)
        self._scene_manager.init()
        gs = self._scene_manager._game_scene  # noqa: SLF001 — internal access for RL bootstrap
        gs._rl_controlled = True  # RL hook (reversible)
        gs._rl_skip_draw = self.render_mode is None  # RL hook (reversible)
        self._game_scene = gs
        self._reward_state = RewardState()
        self._prev_reward_snapshot = build_reward_snapshot(gs)
        # Human-window close (pygame.QUIT) — RL action path unchanged; only event drain in step().
        self._demo_quit_requested = False

    @property
    def _fixed_dt(self) -> float:
        return 1.0 / float(FPS)

    def _build_info(self, reward_breakdown: dict[str, float] | None = None) -> dict[str, Any]:
        info: dict[str, Any] = {}
        gs = self._game_scene
        if gs is None:
            return info
        rc = getattr(gs, "_room_controller", None)
        if rc is not None:
            info["room_index"] = int(rc.current_room_index)
        pl = getattr(gs, "_player", None)
        if pl is not None:
            info["player_hp"] = float(getattr(pl, "hp", 0.0))
            info["lives_remaining"] = int(getattr(pl, "lives", 0))
        mt = getattr(gs, "_metrics", None)
        if mt is not None:
            run = getattr(mt, "run", None)
            if run is not None:
                info["rooms_cleared"] = int(getattr(run, "rooms_cleared", 0))
        info["rl_action"] = int(getattr(gs, "_rl_action", 0))
        if reward_breakdown is not None:
            info["reward_breakdown"] = reward_breakdown
        return info

    def _episode_terminated(self) -> bool:
        gs = self._game_scene
        if gs is None:
            return True
        if bool(getattr(gs, "_victory_phase", False)):
            return True
        if getattr(gs, "_death_phase", None) is not None:
            return True
        return False

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        super().reset(seed=seed)
        if seed is not None:
            np.random.seed(seed)

        assert self._scene_manager is not None
        # Fresh run with optional deterministic dungeon seed; optional curriculum micro-scenario (E/F).
        opts = dict(options or {})
        curriculum = opts.get("curriculum_scenario")
        if curriculum is not None:
            curriculum = str(curriculum)
        self._scene_manager.switch_to_game(
            run_seed_override=seed,
            rl_curriculum_scenario=curriculum,
        )
        self._demo_quit_requested = False
        # RL hook: clear prior episode action so first frame is not stale vs. GameScene.reset()
        self._game_scene._rl_action = 0
        self._reward_state.reset()
        # Curriculum warps room/player on first update(); run that once so obs matches the scenario.
        if curriculum is not None:
            gs = self._game_scene
            gs._ensure_room()
            gs._ensure_player()
            gs._maybe_apply_rl_curriculum()
        self._prev_reward_snapshot = build_reward_snapshot(self._game_scene)
        obs = build_observation(self._game_scene)
        return obs, self._build_info()

    def step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        if self._closed:
            raise RuntimeError("DungeonEnv.step called after close()")

        assert self._scene_manager is not None
        assert self._game_scene is not None
        assert self._logical_surface is not None

        a = int(np.clip(action, 0, int(self.action_space.n) - 1))
        self._game_scene._rl_action = a  # RL hook (reversible)

        prev_snap = self._prev_reward_snapshot

        # Human mode: drain pygame queue so F3 reaches GameScene.handle_event (AI Director debug overlay).
        # Do not forward other KEYDOWN/MOUSE events — they would mix keyboard state with RL actions.
        if self.render_mode == "human" and self._scene_manager is not None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._demo_quit_requested = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
                    self._scene_manager.handle_event(event)
        else:
            # Headless: keep internal pygame state fresh without dispatching gameplay keys.
            pygame.event.pump()

        dt = self._fixed_dt
        self._scene_manager.update(dt)

        obs = build_observation(self._game_scene)
        curr_snap = build_reward_snapshot(self._game_scene)
        terminated = self._episode_terminated()
        reward, r_breakdown = compute_step_reward(
            prev_snap,
            curr_snap,
            self._reward_state,
            terminated=terminated,
            action=a,
        )
        self._prev_reward_snapshot = curr_snap

        truncated = False
        info = self._build_info(reward_breakdown=r_breakdown)

        if self.render_mode == "human":
            self.render()

        return obs, reward, terminated, truncated, info

    def render(self) -> None:
        if self.render_mode != "human":
            return
        if self._closed or self._screen is None or self._logical_surface is None:
            return
        self._logical_surface.fill(BACKGROUND_COLOR)
        co = getattr(self._scene_manager.current, "camera_offset", (0, 0))
        self._scene_manager.draw(self._logical_surface, co)
        win_w, win_h = self._screen.get_size()
        scaled = pygame.transform.smoothscale(self._logical_surface, (win_w, win_h))
        self._screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        gs = self._game_scene
        if gs is not None:
            gs._rl_controlled = False  # RL hook (reversible)
            gs._rl_skip_draw = False
        try:
            pygame.quit()
        except Exception:
            pass
        self._screen = None
        self._logical_surface = None
        self._clock = None
        self._scene_manager = None
        self._game_scene = None
