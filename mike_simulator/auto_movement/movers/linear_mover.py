from mike_simulator.auto_movement.mover_base import AutoMoverBase
from mike_simulator.util.helpers import lerp


class AutomaticLinearMover(AutoMoverBase):
    """Linear movement from starting to target position within the specified duration"""

    def __init__(self, start_position: float, target_position: float, duration: float):
        super().__init__(start_position, duration)
        self.end_pos = target_position

    def get_current_position(self, normalized_t: float) -> float:
        current_pos = lerp(self.start_pos, self.end_pos, normalized_t)
        return current_pos
