# Stub logger for RL and debug. Phase 8 will add JSONL logging hooks.
# Game must NOT crash if logging is unavailable.

import sys
from pathlib import Path

_log_file = None


def init_logger(log_path=None):
    """Optional: open a log file for the run. No-op if path is None."""
    global _log_file
    if log_path is None:
        return
    try:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        _log_file = open(log_path, "a", encoding="utf-8")
    except OSError:
        _log_file = None


def log_line(line: str):
    """Append a line to the log file if open. No-op otherwise."""
    if _log_file is not None:
        try:
            _log_file.write(line.rstrip() + "\n")
            _log_file.flush()
        except OSError:
            pass


def debug(message: str):
    """Emit debug message to stderr when useful. Does not affect gameplay."""
    if __debug__:
        print(f"[DEBUG] {message}", file=sys.stderr)
