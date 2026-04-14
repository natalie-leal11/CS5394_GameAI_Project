"""Prompt 40b: PPO CLI smoke."""
import subprocess
import sys
from pathlib import Path

def test_train_ppo_help_exits_zero():
    root = Path(__file__).resolve().parents[2]
    src = root / "src"
    r = subprocess.run([sys.executable, "-m", "rl.train_ppo", "--help"], cwd=src, capture_output=True)
    assert r.returncode == 0

def test_eval_ppo_help():
    root = Path(__file__).resolve().parents[2]
    src = root / "src"
    r = subprocess.run([sys.executable, "-m", "rl.eval_ppo", "--help"], cwd=src, capture_output=True)
    assert r.returncode == 0
