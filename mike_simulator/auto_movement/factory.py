from typing import Tuple

from mike_simulator.auto_movement import AutoMover
from mike_simulator.auto_movement.movers import *


class AutoMoverFactory:
    @staticmethod
    def make_linear_mover(start_position: float, target_position: float, duration: float) -> AutoMover:
        return AutomaticLinearMover(start_position, target_position, duration)

    @staticmethod
    def make_sine_mover(start_position: float, duration: float, *amplitude_freqs: Tuple[float, float]) -> AutoMover:
        return AutomaticSineMover(start_position, duration, *amplitude_freqs)
