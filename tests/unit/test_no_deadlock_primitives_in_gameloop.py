"""Prompt 40c: Deadlock static guard."""
from pathlib import Path

def test_no_threading_lock_import_in_game_scene_hot_path_static():
    root = Path(__file__).resolve().parents[2]
    gs = root / "src" / "game" / "scenes" / "game_scene.py"
    text = gs.read_text(encoding="utf-8", errors="replace")
    assert "threading.Lock" not in text
