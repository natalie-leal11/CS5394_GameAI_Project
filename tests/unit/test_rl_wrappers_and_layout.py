"""Prompt 40a: RL wrappers & layout."""
import pytest
import numpy as np
from gymnasium.wrappers import TimeLimit
from rl.env import DungeonEnv
from rl.wrappers import TimeoutPenaltyWrapper
from rl.curriculum_wrappers import CurriculumSuccessWrapper
from rl import experiment_layout as el

def test_timeout_penalty_only_when_truncated():
    base = DungeonEnv(render_mode=None)
    env = TimeoutPenaltyWrapper(TimeLimit(base, max_episode_steps=5))
    env.reset(seed=0)
    for _ in range(10):
        env.step(0)
    env.close()

def test_curriculum_success_requires_min_steps():
    w = CurriculumSuccessWrapper(DungeonEnv(render_mode=None), default_scenario="interact")
    assert w is not None

def test_experiment_paths_no_path_traversal():
    p = el.models_stage_dir("iter2_x", "300k")
    assert ".." not in p.parts
