from mike_simulator.auto_movement.mover_base import AutoMoverBase


class AutomaticLinearMover(AutoMoverBase):
    """Linear movement from starting to target position within the specified duration"""

    def __init__(self, start_position: float, target_position: float, duration: float):
        super().__init__(start_position, duration)
        self.end_pos = target_position

    @staticmethod
    def lerp(start: float, end: float, normalized_t: float) -> float:
        """Linear interpolation between start and end with t in [0, 1]"""
        return start + (end - start) * normalized_t

    def get_current_position(self, normalized_t: float) -> float:
        current_pos = self.lerp(self.start_pos, self.end_pos, normalized_t)
        return current_pos
