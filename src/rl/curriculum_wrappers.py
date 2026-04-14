"""
Gymnasium wrappers for E/F curriculum pretraining (focused episodes, success bonus).

# RL-only path — safe to remove if RL is abandoned
"""

from __future__ import annotations

from typing import Any

import gymnasium as gym
import numpy as np


class CurriculumSuccessWrapper(gym.Wrapper):
    """
    Tracks ``rl_interact_success_count`` / ``rl_safe_room_heal_success_count`` from metrics,
    adds a one-time success bonus, and terminates the episode when the intended signal fires.
    """

    def __init__(
        self,
        env: gym.Env,
        *,
        default_scenario: str | None,
        success_bonus: float = 3.0,
    ) -> None:
        super().__init__(env)
        self._default_scenario = default_scenario
        self._success_bonus = float(success_bonus)
        self.scenario: str | None = None
        self._prev_interact_ok: int = 0
        self._prev_heal_ok: int = 0

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None) -> tuple[Any, dict[str, Any]]:
        options = dict(options or {})
        scen = options.get("curriculum_scenario", self._default_scenario)
        if scen is None:
            raise ValueError("curriculum_scenario required (pass options or default_scenario)")
        self.scenario = str(scen)
        options["curriculum_scenario"] = self.scenario
        obs, info = self.env.reset(seed=seed, options=options)
        self._sync_prev_from_metrics()
        info["curriculum_scenario"] = self.scenario
        return obs, info

    def _game_scene(self) -> Any:
        base = self.env.unwrapped
        return getattr(base, "_game_scene", None)

    def _sync_prev_from_metrics(self) -> None:
        gs = self._game_scene()
        run = None
        if gs is not None:
            mt = getattr(gs, "_metrics", None)
            run = getattr(mt, "run", None) if mt is not None else None
        self._prev_interact_ok = int(getattr(run, "rl_interact_success_count", 0)) if run is not None else 0
        self._prev_heal_ok = int(getattr(run, "rl_safe_room_heal_success_count", 0)) if run is not None else 0

    def step(self, action: Any) -> tuple[Any, float, bool, bool, dict[str, Any]]:
        obs, reward, terminated, truncated, info = self.env.step(action)
        gs = self._game_scene()
        run = None
        if gs is not None:
            mt = getattr(gs, "_metrics", None)
            run = getattr(mt, "run", None) if mt is not None else None
        ri = int(getattr(run, "rl_interact_success_count", 0)) if run is not None else 0
        sh = int(getattr(run, "rl_safe_room_heal_success_count", 0)) if run is not None else 0
        success = False
        scen = self.scenario or ""
        if scen == "interact" and ri > self._prev_interact_ok:
            success = True
        if scen == "safe_heal" and sh > self._prev_heal_ok:
            success = True
        self._prev_interact_ok = ri
        self._prev_heal_ok = sh
        if success:
            reward = float(reward) + self._success_bonus
            terminated = True
        info["curriculum_success"] = success
        if self.scenario is not None:
            info["curriculum_scenario"] = self.scenario
        return obs, float(reward), terminated, truncated, info


class CurriculumScenarioSamplerWrapper(gym.Wrapper):
    """Each episode picks ``interact`` or ``safe_heal`` at random (42% / 58% by default)."""

    def __init__(self, env: gym.Env, *, rng: np.random.Generator | None = None, p_interact: float = 0.5) -> None:
        super().__init__(env)
        self._rng = rng or np.random.default_rng()
        self._p_interact = float(p_interact)

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None) -> tuple[Any, dict[str, Any]]:
        options = dict(options or {})
        if "curriculum_scenario" not in options:
            options["curriculum_scenario"] = (
                "interact" if self._rng.random() < self._p_interact else "safe_heal"
            )
        return self.env.reset(seed=seed, options=options)
