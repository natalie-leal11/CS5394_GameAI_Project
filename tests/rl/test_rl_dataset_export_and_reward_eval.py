"""
`game.rl` offline dataset + reward eval — lightweight smoke (read-only, tmp files).
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("game.rl.dataset_export")
from game.rl.reward_eval import InsufficientDataError, evaluate_from_paths, evaluate_offline_reward


def test_module_importable() -> None:
    import game.rl.dataset_export  # noqa: F401, PLC0415
    import game.rl.reward_eval  # noqa: F401, PLC0415


def test_evaluate_from_paths_run_csv_victory(tmp_path: Path) -> None:
    p = tmp_path / "runs.csv"
    p.write_text(
        "run_id,seed,final_outcome,rooms_cleared,total_rooms_logged\n"
        "a,1,victory,1,1\n",
        encoding="utf-8",
    )
    b = evaluate_from_paths(None, p)
    assert b.decisive_runs == 1
    assert b.wins == 1
    assert 0.0 <= b.empirical_win_rate <= 1.0
    assert b.overall_reward is not None and isinstance(b.overall_reward, float)


def test_run_rows_all_missing_outcome_raises() -> None:
    with pytest.raises(InsufficientDataError, match="final_outcome"):
        evaluate_offline_reward(
            [],
            [
                {
                    "run_id": "x",
                    "final_outcome": "",
                    "rooms_cleared": "0",
                    "total_rooms_logged": "0",
                }
            ],
        )


def test_load_run_dataset_rejects_unsupported_format(tmp_path: Path) -> None:
    from game.rl import reward_eval

    bad = tmp_path / "x.txt"
    bad.write_text("a\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported run dataset format"):
        reward_eval.load_run_dataset(bad)
