import time


class Timer:
    def __init__(self):
        self.end_time = None

    def start(self, duration: float):
        """Start a timer which finishes in 'duration' seconds"""
        assert self.has_finished()
        self.end_time = get_current_time() + duration

    def stop(self):
        self.end_time = None

    def is_active(self) -> bool:
        """Return whether timer is still running."""
        return not self.has_finished()

    def has_finished(self) -> bool:
        """Return whether time is not running (never started or already finished)."""
        return self.end_time is None or get_current_time() >= self.end_time


def get_current_time() -> float:
    """Get current time in fractional seconds."""
    return time.time_ns() / 1_000_000_000
