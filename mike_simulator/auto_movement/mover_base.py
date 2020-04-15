from abc import ABCMeta, abstractmethod
from typing import Tuple

from mike_simulator.auto_movement import AutoMover
from mike_simulator.util import get_current_time


class AutoMoverBase(AutoMover, metaclass=ABCMeta):
    def __init__(self, start_position: float, duration: float):
        self.start_pos = start_position
        self.start_time: float = get_current_time()
        self.duration = duration

    def get_current_position_and_state(self) -> Tuple[float, AutoMover.MovementState]:
        if self.duration == 0:
            return self.start_pos, AutoMover.MovementState(True)
        normalized_t = self.get_normalized_t(get_current_time() - self.start_time)
        pos = self.get_current_position(normalized_t)
        return pos, AutoMoverBase.MovementState(normalized_t == 1.0)

    def get_normalized_t(self, elapsed_time: float) -> float:
        """Convert elapsed time to a normalized time in range [0,1] based on the mover's duration."""
        return min(max(0.0, elapsed_time / self.duration), 1.0)

    @abstractmethod
    def get_current_position(self, normalized_t: float) -> float:
        pass
