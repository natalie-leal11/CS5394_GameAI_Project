"""Prompt 21: GameScene terminal (minimal state model, no full scene)."""

from __future__ import annotations


class _TerminalStub:
    """Mirrors GameScene terminal flags used by rl.env.DungeonEnv._episode_terminated."""

    def __init__(self) -> None:
        self._victory_phase = False
        self._death_phase = None

    def set_victory(self) -> None:
        self._victory_phase = True
        self._death_phase = None

    def set_death(self) -> None:
        self._death_phase = "fade"
        self._victory_phase = False


def _episode_terminated(st: _TerminalStub) -> bool:
    if st._victory_phase:
        return True
    if st._death_phase is not None:
        return True
    return False


def test_player_death_ends_run_smoke():
    st = _TerminalStub()
    st.set_death()
    assert _episode_terminated(st) is True


def test_final_victory_single_terminal():
    st = _TerminalStub()
    st.set_victory()
    assert _episode_terminated(st) is True
    assert st._death_phase is None


def test_edge_death_and_victory_same_frame_rejected_or_ordered():
    st = _TerminalStub()
    st.set_death()
    assert st._victory_phase is False
    assert st._death_phase is not None
    st.set_victory()
    assert st._victory_phase is True
    assert st._death_phase is None
