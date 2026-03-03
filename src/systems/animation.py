# Advance frame index by dt; FPS and loop/non-loop per state. Used by player and later entities.

from typing import Any


class AnimationState:
    """Holds current animation: frames, FPS, loop. Advances by dt and returns current frame index and finished flag."""

    def __init__(self):
        self._frames: list[Any] = []
        self._fps = 10
        self._loop = True
        self._frame_index = 0
        self._elapsed = 0.0

    def set_animation(self, frames: list[Any], fps: int | float, loop: bool) -> None:
        self._frames = frames if frames else []
        self._fps = max(0.001, float(fps))
        self._loop = loop
        self._frame_index = 0
        self._elapsed = 0.0

    def advance(self, dt: float) -> tuple[int, bool]:
        """
        Advance by dt. Returns (current_frame_index, finished).
        finished is True when a non-loop animation just reached its last frame.
        """
        if not self._frames:
            return 0, False
        self._elapsed += dt
        frame_duration = 1.0 / self._fps
        # How many frames to advance
        n = int(self._elapsed / frame_duration)
        self._elapsed -= n * frame_duration
        if self._loop:
            self._frame_index = (self._frame_index + n) % len(self._frames)
            return self._frame_index, False
        # Non-loop
        self._frame_index = min(self._frame_index + n, len(self._frames) - 1)
        finished = self._frame_index >= len(self._frames) - 1 and n > 0
        return self._frame_index, finished

    @property
    def current_frame_index(self) -> int:
        if not self._frames:
            return 0
        return min(self._frame_index, len(self._frames) - 1)

    def current_surface(self):
        """Return the current frame surface, or None if no frames."""
        if not self._frames:
            return None
        return self._frames[self.current_frame_index]

    def reset(self) -> None:
        self._frame_index = 0
        self._elapsed = 0.0
