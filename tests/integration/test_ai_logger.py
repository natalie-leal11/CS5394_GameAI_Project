"""Prompt 27: AI logger."""

from __future__ import annotations

from game.ai.ai_logger import AILogger


def test_log_event_with_minimal_fields():
    log = AILogger(run_seed=None)
    log.log_event("custom", {"foo": 1})
    assert len(log.logs) == 1
    assert log.logs[0]["event"] == "custom"
    assert log.logs[0]["foo"] == 1


def test_missing_optional_field_no_crash():
    log = AILogger(run_seed=None)
    log.log_room({"room_index": 0})
    log.log_session_end({"victory_or_defeat": "aborted"})
    assert any(e.get("event") == "room_end" for e in log.logs)
    assert any(e.get("event") == "session_end" for e in log.logs)
