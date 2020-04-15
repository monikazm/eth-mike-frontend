import math
from typing import Tuple

from mike_simulator.auto_movement.mover_base import AutoMoverBase


class AutomaticSineMover(AutoMoverBase):
    """Movement along a mixture of sines within a particular duration"""

    def __init__(self, start_position: float, duration: float, *amplitude_freqs: Tuple[float, float]):
        super().__init__(start_position, duration)
        self.sine_parameters = amplitude_freqs

    @staticmethod
    def sine(amplitude: float, freq: float, normalized_t: float) -> float:
        return math.sin(2.0 * math.pi * freq * normalized_t) * amplitude

    def get_current_position(self, normalized_t: float) -> float:
        current_pos = self.start_pos
        for amplitude, freq in self.sine_parameters:
            current_pos += self.sine(amplitude, freq, normalized_t)
        return current_pos
