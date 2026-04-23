"""
Evaluate E/F curriculum success rates (deterministic policy optional).

# RL-only path — safe to remove if RL is abandoned

Example::

    cd src
    python -m rl.eval_curriculum --model ../models/ppo/iter2_cooldown_0p5_1p2_curriculum/stage_ef200k/dungeon_ppo_final.zip \\
        --scenario both --episodes 200 --seed 0

Writes ``curriculum_eval_summary.md`` next to the model when ``--experiment`` and ``--stage`` are set.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import gymnasium as gym
import numpy as np
from gymnasium.wrappers import TimeLimit
from stable_baselines3 import PPO

from rl.config import EvalConfig
from rl.curriculum_wrappers import CurriculumScenarioSamplerWrapper, CurriculumSuccessWrapper
from rl.env import DungeonEnv
from rl.experiment_layout import curriculum_eval_summary_path, models_curriculum_stage_dir
from rl.wrappers import TimeoutPenaltyWrapper


def _make_eval_env(cfg: EvalConfig, scenario: str) -> gym.Env:
    e: gym.Env = DungeonEnv(render_mode=None)
    if scenario == "both":
        e = CurriculumScenarioSamplerWrapper(e)
        e = CurriculumSuccessWrapper(e, default_scenario=None, success_bonus=0.0)
    else:
        e = CurriculumSuccessWrapper(e, default_scenario=scenario, success_bonus=0.0)
    if cfg.use_time_limit:
        e = TimeLimit(e, max_episode_steps=cfg.max_episode_steps)
        e = TimeoutPenaltyWrapper(e)
    return e


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Eval E/F curriculum success rates.")
    p.add_argument("--model", type=Path, required=True, help="Path to trained .zip (PPO).")
    p.add_argument(
        "--scenario",
        type=str,
        choices=("interact", "safe_heal", "both"),
        default="both",
        help="Must match how the model was trained for meaningful numbers.",
    )
    p.add_argument("--episodes", type=int, default=50, help="Number of eval episodes.")
    p.add_argument("--seed", type=int, default=0, help="Base seed for env.reset(seed=...).")
    p.add_argument("--deterministic", action="store_true", help="Use deterministic policy.predict.")
    p.add_argument("--max-episode-steps", type=int, default=800, help="TimeLimit (match training).")
    p.add_argument("--experiment", type=str, default=None, help="With --stage, sets default summary path.")
    p.add_argument("--stage", type=str, default=None, help="Stage label under curriculum tree.")
    p.add_argument("--summary-out", type=Path, default=None, help="Write markdown report to this path.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    model_path = Path(args.model)
    if not model_path.is_file():
        print(f"[eval_curriculum] model not found: {model_path.resolve()}", file=sys.stderr)
        raise SystemExit(1)

    cfg = EvalConfig()
    cfg.max_episode_steps = int(args.max_episode_steps)
    cfg.use_time_limit = True

    env = _make_eval_env(cfg, args.scenario)
    model = PPO.load(str(model_path), env=env, device="auto")

    rng = np.random.default_rng(int(args.seed))
    by_scen: dict[str, dict[str, float]] = {
        "interact": {"ok": 0.0, "n": 0.0, "steps_sum": 0.0},
        "safe_heal": {"ok": 0.0, "n": 0.0, "steps_sum": 0.0},
    }
    total_steps = 0
    successes = 0

    for ep in range(int(args.episodes)):
        obs, info = env.reset(seed=int(rng.integers(0, 2**31 - 1)))
        scen = str(info.get("curriculum_scenario", args.scenario))
        if args.scenario != "both":
            scen = args.scenario
        steps = 0
        while True:
            action, _ = model.predict(obs, deterministic=bool(args.deterministic))
            obs, _r, term, trunc, info = env.step(action)
            steps += 1
            total_steps += 1
            if term or trunc:
                ok = bool(info.get("curriculum_success", False))
                if ok:
                    successes += 1
                if scen in by_scen:
                    by_scen[scen]["n"] += 1.0
                    if ok:
                        by_scen[scen]["ok"] += 1.0
                    by_scen[scen]["steps_sum"] += float(steps)
                break

    env.close()

    n = float(args.episodes)
    overall_rate = successes / n if n else 0.0
    lines = [
        "# Curriculum eval (E/F)",
        "",
        f"- **Model:** `{model_path.resolve()}`",
        f"- **Scenario mode:** `{args.scenario}`",
        f"- **Episodes:** {args.episodes}",
        f"- **Deterministic:** {bool(args.deterministic)}",
        f"- **Max episode steps:** {cfg.max_episode_steps}",
        "",
        f"- **Overall success rate:** {overall_rate:.3f}",
        f"- **Mean steps per episode:** {total_steps / n if n else 0.0:.1f}",
        "",
    ]
    for key in ("interact", "safe_heal"):
        b = by_scen[key]
        if b["n"] <= 0:
            lines.append(f"## {key}")
            lines.append("")
            lines.append("- *(no episodes labeled)*")
            lines.append("")
            continue
        rate = b["ok"] / b["n"]
        mean_steps = b["steps_sum"] / b["n"]
        lines.append(f"## {key}")
        lines.append("")
        lines.append(f"- **Success rate:** {rate:.3f} ({int(b['ok'])}/{int(b['n'])})")
        lines.append(f"- **Mean steps (success+fail):** {mean_steps:.1f}")
        lines.append("")

    report = "\n".join(lines)
    print(report)

    out: Path | None = args.summary_out
    if out is None and args.experiment and args.stage:
        out = curriculum_eval_summary_path(args.experiment, args.stage)
    if out is not None:
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"[eval_curriculum] wrote {out.resolve()}")

    # Also echo default curriculum models dir for discoverability
    if args.experiment and args.stage:
        print(f"[eval_curriculum] curriculum stage dir: {models_curriculum_stage_dir(args.experiment, args.stage).resolve()}")


if __name__ == "__main__":
    main()
