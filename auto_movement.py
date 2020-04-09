import math
from abc import ABCMeta, abstractmethod
from typing import Tuple

from util import PrintUtil, get_current_time


class MoverFactory:
    @staticmethod
    def make_linear_mover(start_position: float, target_position: float, duration: float) -> 'AutomaticMovement':
        return AutomaticLinearMovement(start_position, target_position, duration)

    @staticmethod
    def make_sine_mover(start_position: float, duration: float, *amplitude_freqs: Tuple[float, float]) -> 'AutomaticMovement':
        return AutomaticSineMovement(start_position, duration, *amplitude_freqs)


class AutomaticMovement(metaclass=ABCMeta):
    class MovementState:
        def __init__(self, finished: bool):
            self.__finished = finished

        def has_finished(self) -> bool:
            return self.__finished

    def __init__(self, start_position: float, duration: float):
        self.start_pos = start_position
        self.start_time: float = 0.0
        self.duration = duration
        self.reset()

    def reset(self):
        self.start_time = get_current_time()

    def get_current_position_and_state(self) -> Tuple[float, MovementState]:
        if self.duration == 0:
            return self.start_pos, AutomaticMovement.MovementState(True)
        t = min(get_current_time() - self.start_time, self.duration)
        pos = self._get_current_position(t)
        PrintUtil.print_inplace(f'Current robot position: {pos:.3f}°')
        return pos, AutomaticMovement.MovementState(t == self.duration)

    @abstractmethod
    def _get_current_position(self, t: float) -> float:
        pass


class AutomaticLinearMovement(AutomaticMovement):
    """Linear movement from starting to target position within the specified duration"""

    def __init__(self, start_position: float, target_position: float, duration: float):
        super().__init__(start_position, duration)
        self.end_pos = target_position

    @staticmethod
    def lerp(start: float, end: float, normalized_t: float) -> float:
        """Linear interpolation between start and end with t in [0, 1]"""
        return start + (end - start) * normalized_t

    def _get_current_position(self, t: float) -> float:
        if math.fabs(self.duration - t) < 0.0001:
            t = self.duration
        current_pos = self.lerp(self.start_pos, self.end_pos, t / self.duration)
        return current_pos


class AutomaticSineMovement(AutomaticMovement):
    """Movement along a mixture of sines within a particular duration"""

    def __init__(self, start_position: float, duration: float, *amplitude_freqs: Tuple[float, float]):
        super().__init__(start_position, duration)
        self.sine_parameters = amplitude_freqs

    @staticmethod
    def sine(amplitude: float, freq: float, t: float) -> float:
        return math.sin(2.0 * math.pi * freq * t) * amplitude

    def _get_current_position(self, t: float) -> float:
        if math.fabs(self.duration - t) < 0.0001:
            t = self.duration
        current_pos = self.start_pos + sum(self.sine(amplitude, freq, t) for amplitude, freq in self.sine_parameters)
        return current_pos
