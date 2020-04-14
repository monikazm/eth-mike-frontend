import sys
import time


def get_current_time() -> float:
    return time.time_ns() / 1_000_000_000


class Timer:
    def __init__(self):
        self.end_time = None

    def start(self, duration: float):
        assert self.has_finished()
        self.end_time = get_current_time() + duration

    def is_active(self) -> bool:
        return not self.has_finished()

    def has_finished(self) -> bool:
        return self.end_time is None or get_current_time() >= self.end_time


class PrintUtil:
    _inplace = False

    @staticmethod
    def print_inplace(*text, **kwargs):
        """Print text by overwriting current line in terminal"""
        PrintUtil._inplace = True
        # Clear line
        print('\r', 79*' ', end='', **kwargs)
        sys.stdout.flush()

        # Update with new values
        print('\r', *text, end='', **kwargs)
        sys.stdout.flush()

    @staticmethod
    def print_normally(*text, **kwargs):
        """Print text on a new line"""
        if PrintUtil._inplace:
            print()
            PrintUtil._inplace = False
        print(*text, **kwargs)
