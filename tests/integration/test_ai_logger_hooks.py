"""AILogger: append events, room rows, clear buffer."""

from __future__ import annotations

from game.ai.ai_logger import AILogger


def test_logger_receives_director_events():
    log = AILogger(run_seed=None, verbose=False)
    log.log_event("director_tick", {"room_index": 2, "note": "test"})
    assert log.logs[-1]["event"] == "director_tick"
    assert log.logs[-1]["room_index"] == 2


def test_logger_receives_metrics_events():
    log = AILogger(run_seed=None, verbose=False)
    log.log_room({"room_index": 1, "room_result": "clean_clear", "seed": 42})
    assert log.logs[-1].get("event") == "room_end"
    assert log.logs[-1]["room_index"] == 1


def test_logger_flush_on_room_transition():
    log = AILogger(run_seed=None, verbose=False)
    log.log_room({"room_index": 0})
    log.clear()
    assert log.logs == []
